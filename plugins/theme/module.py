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
import logging
import flask  # pylint: disable=E0401
import jinja2  # pylint: disable=E0401

from flask import request, render_template, redirect, url_for

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401

from .components.commons.navbar import render_navbar
from .components.commons.page import render_page, render_test
from plugins.base.connectors.auth import SessionProject


class Module(module.ModuleModel):
    """ Galloper module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context

    def init(self):
        """ Init module """
        log.info("Initializing module")
        bp = flask.Blueprint(  # pylint: disable=C0103
            "theme", "plugins.theme.plugin",
            root_path=self.root_path,
            url_prefix=f"{self.context.url_prefix}/"
        )
        bp.jinja_loader = jinja2.ChoiceLoader([
            jinja2.loaders.PackageLoader("plugins.theme", "templates"),
        ])
        bp.add_url_rule("/", "index", self.index)
        bp.add_url_rule("/project/create", "create_project", self.project_wizard)
        # Register in app
        self.context.app.register_blueprint(bp)
        # Register template slot callback
        self.context.slot_manager.register_callback("navbar", render_navbar)
        self.context.slot_manager.register_callback("page_content", render_page)
        self.context.slot_manager.register_callback("create_backend_test", render_test)
        # Register event listener
        # self.context.event_manager.register_listener("base.index", self.base_event)

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing module")

    def index(self):
        chapter = request.args.get('chapter', '')
        session_project = SessionProject.get()
        logging.info(session_project)
        if not session_project:
            return redirect(url_for('theme.create_project'))
        project_config = self.context.app.config["rpc"].call("project", "get_or_404", project_id=session_project)
        return render_template("base.html", active_chapter=chapter, config=project_config)

    def project_wizard(self):
        return render_template("project_wizard.html")
