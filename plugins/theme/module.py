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

import flask  # pylint: disable=E0401
import jinja2  # pylint: disable=E0401

from flask import request, render_template

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401

from .components.commons.navbar import render_navbar
from .components.commons.page import render_page


mock_config = {
    "username": "User",
    "default_chapter": "Performance",
    "regions": [
        "default",
        "us-east",
        "us-west",
        "eu-central"
    ],
    "active_project": "Carrier",
    "active_project_id": 4,
    "projects": [
        {"name": "PMI", "id": 1},
        {"name": "Alfresco", "id": 2},
        {"name": "Verifone 2Checkout", "id": 3}
    ],
    "integrations": [
        "rp", "ado", "email"
    ],
    "project_structure": {
        "chapters": [
            {
                "title": "Manage Project", "link": "?chapter=Manage%20Project",
                "nav": [
                    {"title": "Users", "link": "#", "active": True},
                    {"title": "Quotas", "link": "#"},
                    {"title": "Integrations", "link": "#"},
                    {"title": "Plugins", "link": "#"}
                ]
            },
            {
                "title": "Dashboards", "link": "?chapter=Dashboards",
                "nav": [
                    {"title": "Dashboards", "link": "#"},
                    {"title": "Data Explorer", "link": "#"},
                    {"title": "Group Projects", "link": "#", "active": True},
                ]
            },
            {
                "title": "Security", "link": "?chapter=Security",
                "nav": [
                    {"title": "Overview", "link": "#", "active": True},
                    {"title": "Static", "link": "#"},
                    {"title": "Dynamic", "link": "#"},
                    {"title": "Infrastructure", "link": "#"},
                    {"title": "Results", "link": "#"},
                    {"title": "Thresholds", "link": "#"},
                    {"title": "Bug Bar", "link": "#"}
                ]
            },
            {
                "title": "Performance", "link": "?chapter=Performance",
                "nav": [
                    {"title": "Overview", "link": "?chapter=Performance&module=Overview&page=overview", "active": True},
                    {"title": "Backend", "link": "?chapter=Performance&module=Backend&page=create_test"},
                    {"title": "Visual", "link": "?chapter=Performance&module=Visual&page=visual"},
                    {"title": "Results", "link": "?chapter=Performance&module=Results&page=reports"},
                    {"title": "Thresholds", "link": "?chapter=Performance&module=Thresholds&page=thresholds"}
                ]
            }
        ]
    }
}


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
        # Register event listener
        # self.context.event_manager.register_listener("base.index", self.base_event)

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing module")

    def index(self):
        chapter = request.args.get('chapter', '')
        return render_template("base.html", active_chapter=chapter, config=mock_config)

    def project_wizard(self):
        return render_template("project_wizard.html")



