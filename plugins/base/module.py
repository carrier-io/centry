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
from datetime import datetime

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401

from .config import Config
from .connectors.vault import init_vault
from .db_manager import db_session
from .init_db import init_db


class Module(module.ModuleModel):
    """ Galloper module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context

    def init(self):
        """ Init module """
        log.info("Initializing module")
        self.context.app.config.from_object(Config())
        init_db()
        init_vault()  # won't do anything if vault is not available

        @self.context.app.teardown_appcontext
        def shutdown_session(exception=None):
            db_session.remove()

        @self.context.app.template_filter("ctime")
        def convert_time(ts):
            try:
                return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
            except:
                return "Not Executed"

        @self.context.app.template_filter("is_zero")
        def return_zero(val):
            try:
                return round(val[0] / val[1], 2)
            except:
                return 0

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing module")
