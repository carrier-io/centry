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

from .init_db import init_db

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401
from plugins.base.utils.api_utils import add_resource_to_api


class Module(module.ModuleModel):
    """ Task module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context

    def init(self):
        """ Init module """
        log.info("Initializing module Security")
        init_db()
        from .api.tests import SecurityTestsApi
        from .api.test import SecurityTestApi
        from .api.security_results_api import SecurityResultsApi
        from .api.security_dispatcher import SecuritySeedDispatcher
        from .api.security_findings_api import FindingsAPI
        from .api.update_test_status import TestStatusUpdater
        from .api.get_loki_url import GetLokiUrl
        from .api.security_report_api import SecurityReportAPI
        add_resource_to_api(
            self.context.api, GetLokiUrl,
            "/security/<int:project_id>/get_url",
            resource_class_kwargs={"settings": self.settings}
        )
        add_resource_to_api(
            self.context.api,
            SecurityTestsApi,
            "/security/<int:project_id>/dast"
        )
        add_resource_to_api(
            self.context.api, SecurityTestApi,
            "/security/<int:project_id>/dast/<int:test_id>",
            "/security/<int:project_id>/dast/<string:test_id>"
        )
        add_resource_to_api(
            self.context.api, SecurityResultsApi,
            "/security/<int:project_id>/dast/results"
        )
        add_resource_to_api(
            self.context.api, SecuritySeedDispatcher,
            "/tests/<int:project_id>/security/<string:seed>"
        )
        add_resource_to_api(
            self.context.api, FindingsAPI,
            "/security/<int:project_id>/findings/<int:test_id>"
        )
        add_resource_to_api(
            self.context.api, TestStatusUpdater,
            "/security/<int:project_id>/update_status/<int:test_id>",
            "/security/<int:project_id>/update_status/<string:test_id>"
        )
        add_resource_to_api(
            self.context.api, SecurityReportAPI,
            "/security/<int:project_id>"
        )

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing module")
