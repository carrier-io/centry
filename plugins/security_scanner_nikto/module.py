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
from pathlib import Path

import flask  # pylint: disable=E0401
import jinja2  # pylint: disable=E0401
from flask import request, render_template, redirect, url_for
from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401

from .components.render_nikto import render_nikto_card


class Module(module.ModuleModel):
    """ Galloper module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context

    def init(self):
        """ Init module """
        log.info("Initializing module")
        bp = flask.Blueprint(
            "nikto", "plugins.security_scanner_nikto.plugin",
            static_folder=str(Path(__file__).parents[0] / "static"),
            static_url_path='/nikto/static/'
        )
        bp.jinja_loader = jinja2.ChoiceLoader([
            jinja2.loaders.PackageLoader("plugins.security_scanner_nikto", "templates"),
        ])
        # Register in app
        self.context.app.register_blueprint(bp)
        # Register template slot callback
        self.context.slot_manager.register_callback("security_scanners", render_nikto_card)

        from .rpc_worker import get_scanner_parameters
        self.context.rpc_manager.register_function(get_scanner_parameters, name='nikto')

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing module")
