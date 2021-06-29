import json
import platform
import shutil
from asyncio.proactor_events import _ProactorBasePipeTransport
from functools import wraps
from io import BytesIO
from pathlib import Path
from typing import Optional, AsyncIterable
from zipfile import ZipFile

import asyncio

from aiohttp import ClientSession, ClientResponse
from pylon.core.tools import log

from .utils.plugin import Plugin


# some windows asyncio patches
def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != 'Event loop is closed':
                raise
    return wrapper


if platform.system() == 'Windows':
    _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class FetchError(Exception):
    def __init__(self, response: ClientResponse):
        msg = f'Fetch error {response.status} on url {response.url}'
        log.exception(msg)
        super().__init__(msg)


class CloneError(Exception):
    def __init__(self, stderr: str):
        msg = f'Fetch error {stderr}'
        log.exception(msg)
        super().__init__(msg)


class GitMixin:
    async def clone_callback(self, plugin: Plugin):
        raise NotImplementedError

    async def clone_github_repo(
            self,
            plugin: Plugin,
            git_user: str = 'carrier-io',
            url_template: str = 'https://github.com/{git_user}/{plugin.name}.git',
            clone_args: Optional[list] = None
    ):
        if not clone_args:
            clone_args = ['-q']
        clone_url = url_template.format(git_user=git_user, plugin=plugin)
        proc = await asyncio.create_subprocess_exec(
            'git', 'clone', clone_url, plugin.path, *clone_args,
            stderr=asyncio.subprocess.PIPE
        )
        err = await proc.stderr.read()
        await proc.wait()
        if err:
            raise CloneError(err.decode('utf-8'))
        await self.clone_callback(plugin)


class WebMixin:
    @staticmethod
    async def fetch_txt(url: str) -> str:
        async with ClientSession() as client:
            async with client.get(url) as response:
                if response.ok:
                    return await response.text()
                raise FetchError(response)

    @staticmethod
    async def download_plugin_zip(url: str, plugin: Plugin) -> None:
        async with ClientSession() as client:
            async with client.get(url) as response:
                if response.ok:
                    tmp_bytes = BytesIO(await response.read())
                    zip_file = ZipFile(tmp_bytes)
                    zip_file.extractall(plugin.directory)
                    src = Path(plugin.directory, zip_file.namelist()[0])
                    try:
                        src.rename(plugin.path)
                    except (FileExistsError, OSError):
                        shutil.copytree(src, plugin.path, dirs_exist_ok=True)
                        shutil.rmtree(src)


class PluginDownloader(WebMixin, GitMixin):
    def __init__(self, market_data: dict):
        self.market_data = market_data
        self.plugins_to_download = set()
        self.tasks = list()

    async def clone_plugin(self, plugin: Plugin):
        log.info('Plugin clone called %s', plugin)
        self.tasks.append(asyncio.create_task(
            self.clone_github_repo(plugin, git_user='Aspect13'),
            name=f'Task_clone_repo_{plugin.name}'
        ))
        self.plugins_to_download.add(plugin)

    async def clone_callback(self, plugin: Plugin):
        plugin.reload_metadata()
        async for dependency in self.resolve_dependencies(plugin):
            self.tasks.append(asyncio.create_task(
                self.clone_plugin(dependency),
                name=f'Task_clone_plugin_{dependency.name}'
            ))


    async def download_plugin(self, plugin: Plugin) -> int:
        log.info('Plugin download called %s', plugin)
        try:
            meta = await self.fetch_txt(self.market_data[plugin.name]['metadata'])
            plugin.metadata = json.loads(meta)
        except (KeyError, FetchError):
            log.error('PLUGIN {} NOT FOUND'.format(plugin.name))
            return 404
        # plugin.path.mkdir()
        self.tasks.append(asyncio.create_task(
            self.download_plugin_zip(self.market_data[plugin.name]['data'], plugin),
            name=f'Task_download_plugin_data_{plugin.name}'
        ))

        self.plugins_to_download.add(plugin)
        async for dependency in self.resolve_dependencies(plugin):
            self.tasks.append(asyncio.create_task(
                self.download_plugin(dependency),
                name=f'Task_download_plugin_{dependency.name}'
            ))
        return 200



    async def resolve_dependencies(self, plugin: Plugin) -> AsyncIterable[Plugin]:
        for parent_plugin in plugin.metadata['depends_on']:
            parent_plugin = Plugin(parent_plugin)
            if not parent_plugin.status_downloaded:
                if parent_plugin in self.plugins_to_download:
                    print('!AAAAAAAAAAAA!!!', 'ALREADY ASKED FOR DWNLD', parent_plugin)
                yield parent_plugin
                # yield asyncio.create_task(
                #     self.download_plugin(parent_plugin),
                #     name=f'Task_download_plugin_{plugin.name}'
                # )

    async def gather_tasks(self):
        while pending := [task for task in self.tasks if not task.done()]:
            await asyncio.gather(*pending)


class PluginUpdater(WebMixin):
    def __init__(self, market_data):
        self.market_data = market_data
        self.plugins_to_update = set()
        self.tasks = list()
        self._downloader = None

    @property
    def downloader(self):
        if not self._downloader:
            self._downloader = PluginDownloader(market_data=self.market_data)
        return self._downloader

    async def check_for_updates(self, plugins_list):
        for p in plugins_list:
            plugin = p
            if isinstance(p, str):
                plugin = Plugin(p)
            try:
                meta = await self.fetch_txt(self.market_data[plugin.name]['metadata'])
                repo_plugin_meta = json.loads(meta)
                if float(plugin.version) < float(repo_plugin_meta['version']):
                    plugin.metadata = repo_plugin_meta
                    plugin.status_downloaded = False
                    self.plugins_to_update.add(plugin)
            except (KeyError, FetchError):
                pass

    async def run_update(self):
        for i in self.plugins_to_update:
            await self.downloader.download_plugin(i)
        await self.downloader.gather_tasks()


async def run_downloader(plugins_list, plugin_repo) -> PluginDownloader:
    repo_data = json.loads(await WebMixin.fetch_txt(plugin_repo))

    downloader = PluginDownloader(market_data=repo_data)

    for p in plugins_list:
        plugin = p
        if isinstance(p, str):
            plugin = Plugin(p)
        if not plugin.status_downloaded:
            await downloader.download_plugin(plugin)
        # async for task in downloader.resolve_dependencies(plugin):
        #     downloader.tasks.append(task)
    return downloader


async def run_updater(plugins_list, plugin_repo) -> PluginUpdater:
    repo_data = json.loads(await WebMixin.fetch_txt(plugin_repo))
    updater = PluginUpdater(market_data=repo_data)
    await updater.check_for_updates(plugins_list)
    return updater


async def run_cloner(plugins_list) -> PluginDownloader:
    # repo_data = json.loads(await WebMixin.fetch_txt(plugin_repo))

    downloader = PluginDownloader(market_data=dict())

    for p in plugins_list:
        plugin = p
        if isinstance(p, str):
            plugin = Plugin(p)
        if not plugin.status_downloaded:
            await downloader.clone_plugin(plugin)
    # async for task in downloader.resolve_dependencies(plugin):
    #     downloader.tasks.append(task)
    return downloader