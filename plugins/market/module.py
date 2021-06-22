#!/usr/bin/python3
# coding=utf-8

#   Copyright 2021 getcarrier.io
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

""" Module """
import asyncio
import shutil
from collections import defaultdict
from os import getenv
from pathlib import Path
from types import MappingProxyType
from pkg_resources import VersionConflict

import flask  # pylint: disable=E0401
import jinja2  # pylint: disable=E0401

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401
from pylon.core.tools import storage
from pylon.core.tools.storage import get_development_config
from pylon.main import CORE_DEVELOPMENT_MODE

from .downloader import run_downloader, run_updater
from .requirement_resolver import update_pending_requirements, add_entries, resolve_version_conflicts
from .utils.plugin import Plugin


class Module(module.ModuleModel):
    """ Pylon module """
    name = 'market'

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context
        self.rpc_prefix = f'{self.name}_'

        if CORE_DEVELOPMENT_MODE and not settings:
            src = Path(self.context.settings['development']['modules'], self.name, 'config.yml')
            dst = Path(self.context.settings['development']['config'], f'{self.name}.yml')
            if not dst.exists():
                try:
                    shutil.copy(src, dst)
                except FileNotFoundError:
                    ...
            self.settings = get_development_config(self.context.settings, self.name)

    def init(self):
        """ Init module """
        log.info('Initializing module Market')

        Plugin.directory = Path(self.context.settings['development']['modules'])

        me = Plugin(self.name)
        me._register_in_global()

        self.check_updates()

        plugins_to_download = self.plugin_list
        try:
            plugins_to_download.extend(self.settings['preordered_plugins'])
        except KeyError:
            ...
        try:
            plugins_to_download.extend(getenv('PREORDERED_PLUGINS').split(','))
        except AttributeError:
            ...

        self.download_plugins(set(plugins_to_download))

        req_status = self.check_requirements()

        if req_status['attention']:
            if self.settings['requirements']['raise_on_attention']:
                raise VersionConflict(req_status['attention'])
            else:
                for i in req_status['attention'].values():
                    for plugin, requirement in map(lambda y: (y['plugin'], y['requirement']), i):
                        plugin.installer(package=requirement)
        if req_status['conflict']:
            raise VersionConflict(req_status['conflict'])

        for i in req_status['safe'].values():
            for plugin, requirement in map(lambda y: (y['plugin'], y['requirement']), i):
                plugin.installer(package=requirement)

        self.copy_configs()

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info('De-initializing module Market')

    @property
    def plugin_list(self):
        return storage.list_development_modules(self.context.settings)

    def download_plugins(self, plugin_list):
        loop = asyncio.get_event_loop()
        downloader = loop.run_until_complete(
            run_downloader(
                plugins_list=plugin_list,
                plugin_repo=self.settings['plugin_repo']
            )
        )
        loop.run_until_complete(downloader.gather_tasks())

    def check_updates(self):
        loop = asyncio.get_event_loop()
        updater = loop.run_until_complete(
            run_updater(
                plugins_list=self.plugin_list,
                plugin_repo=self.settings['plugin_repo']
            )
        )
        if updater.plugins_to_update:
            if self.settings['auto_update_plugins']:
                log.info(f'Plugin updates found: {updater.plugins_to_update}, downloading...')
                loop.run_until_complete(updater.run_update())
            else:
                log.warning(f'Plugin updates found: {updater.plugins_to_update}')

    def check_requirements(self):
        add_entries(self.plugin_list)
        req_status = MappingProxyType({
            'safe': defaultdict(list),
            'attention': defaultdict(list),
            'conflict': defaultdict(list)
        })
        pending_requirements = defaultdict(list)
        for plugin in map(Plugin, self.plugin_list):
            log.info('Checking requirements for %s', plugin)
            update_pending_requirements(plugin, pending_requirements, req_status)
        resolve_version_conflicts(pending_requirements, req_status)

        return req_status

    def copy_configs(self):
        '''
        Need to teach pylon to read settings from inside plugin, now just copy it in config folder under plugin name
        '''
        for p in self.plugin_list:
            src = Path(self.context.settings['development']['modules'], p, 'config.yml')
            dst = Path(self.context.settings['development']['config'], f'{p}.yml')
            if not dst.exists():
                try:
                    shutil.copy(src, dst)
                except FileNotFoundError:
                    ...
