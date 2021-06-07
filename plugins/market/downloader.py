import json
import platform
import shutil
from asyncio.proactor_events import _ProactorBasePipeTransport
from functools import wraps
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import asyncio

from aiohttp import ClientSession
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


class WebMixin:
    @staticmethod
    async def fetch_txt(url: str) -> str:
        async with ClientSession() as client:
            async with client.get(url) as response:
                return await response.text()

    @staticmethod
    async def download_plugin_zip(url: str, plugin: Plugin) -> None:
        async with ClientSession() as client:
            async with client.get(url) as response:
                if response.ok:
                    tmp_bytes = BytesIO(await response.read())
                    zip_file = ZipFile(tmp_bytes)
                    zip_file.extractall(plugin.directory)
                    try:
                        Path(plugin.directory, zip_file.namelist()[0]).rename(plugin.path)
                    except FileExistsError:
                        shutil.rmtree(plugin.path)
                        Path(plugin.directory, zip_file.namelist()[0]).rename(plugin.path)


class PluginDownloader(WebMixin):
    def __init__(self, market_data: dict):
        self.market_data = market_data
        self.plugins_to_download = set()
        self.tasks = list()

    async def download_plugin(self, plugin: Plugin) -> int:
        log.info('Plugin download called %s', plugin)
        try:
            meta = await self.fetch_txt(self.market_data[plugin.name]['metadata'])
            plugin.metadata = json.loads(meta)
        except KeyError:
            log.error('PLUGIN {} NOT FOUND'.format(plugin.name))
            return 404
        # plugin.path.mkdir()
        self.tasks.append(asyncio.create_task(
            self.download_plugin_zip(self.market_data[plugin.name]['data'], plugin),
            name=f'Task_download_plugin_data_{plugin.name}'
        ))

        self.plugins_to_download.add(plugin)
        async for task in self.resolve_dependencies(plugin):
            self.tasks.append(task)
        return 200

    async def resolve_dependencies(self, plugin: Plugin):
        for parent_plugin in plugin.metadata['depends_on']:
            parent_plugin = Plugin(parent_plugin)
            if not parent_plugin.status_downloaded:
                yield asyncio.create_task(
                    self.download_plugin(parent_plugin),
                    name=f'Task_download_plugin_{plugin.name}'
                )

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
            plugin = Plugin(p)
            try:
                meta = await self.fetch_txt(self.market_data[plugin.name]['metadata'])
                repo_plugin_meta = json.loads(meta)
                if float(plugin.version) < float(repo_plugin_meta['version']):
                    plugin.metadata = repo_plugin_meta
                    plugin.status_downloaded = False
                    self.plugins_to_update.add(plugin)
            except KeyError:
                pass

    async def run_update(self):
        for i in self.plugins_to_update:
            await self.downloader.download_plugin(i)
        await self.downloader.gather_tasks()


async def run_downloader(plugins_list, plugin_repo):
    repo_data = json.loads(await WebMixin.fetch_txt(plugin_repo))

    downloader = PluginDownloader(market_data=repo_data)

    for p in plugins_list:
        plugin = Plugin(p)
        if not plugin.status_downloaded:
            await downloader.download_plugin(plugin)
        async for task in downloader.resolve_dependencies(plugin):
            downloader.tasks.append(task)
    return downloader


async def run_updater(plugins_list, plugin_repo):
    repo_data = json.loads(await WebMixin.fetch_txt(plugin_repo))
    updater = PluginUpdater(market_data=repo_data)
    await updater.check_for_updates(plugins_list)
    return updater

