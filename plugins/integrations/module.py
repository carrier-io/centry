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
import json
from functools import partial

import flask  # pylint: disable=E0401
import jinja2  # pylint: disable=E0401
from flask import request, make_response, session, redirect, Response

from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401

from plugins.integrations.api.validation import IntegrationsApi
from plugins.integrations.components.integrations_list import render_integrations
from plugins.integrations.init_db import init_db
from plugins.integrations.rpc import register, get_integration, get_project_integrations, \
    get_project_integrations_by_name
from plugins.shared.utils.api_utils import add_resource_to_api


class Module(module.ModuleModel):
    """ Pylon module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context
        self.rpc_prefix = 'integrations'
        self.integrations = dict()

    def init(self):
        """ Init module """
        log.info('Initializing module integrations')
        init_db()


        # rpc_manager
        self.context.rpc_manager.register_function(
            partial(register, self.integrations, self.context.slot_manager),
            name=f'{self.rpc_prefix}_register'
        )
        self.context.rpc_manager.register_function(
            partial(get_integration, self.integrations),
            name=f'{self.rpc_prefix}_get_integration'
        )
        self.context.rpc_manager.register_function(
            lambda: self.integrations,
            name=f'{self.rpc_prefix}_list'
        )
        self.context.rpc_manager.register_function(
            lambda: set((i.section for i in self.integrations.values())),
            name=f'{self.rpc_prefix}_sections'
        )
        self.context.rpc_manager.register_function(
            get_project_integrations,
            name=f'{self.rpc_prefix}_get_project_integrations'
        )
        self.context.rpc_manager.register_function(
            get_project_integrations_by_name,
            name=f'{self.rpc_prefix}_get_project_integrations_by_name'
        )



        # blueprint endpoints
        bp = flask.Blueprint(
            'integrations', 'plugins.integrations',
            root_path=self.root_path,
            url_prefix=f'{self.context.url_prefix}/integr'
        )

        bp.jinja_loader = jinja2.ChoiceLoader([
            jinja2.loaders.PackageLoader("plugins.integrations", "templates"),
        ])

        bp.add_url_rule('/', 'get_registered', self.get_registered, methods=['GET'])
        # Register in app
        self.context.app.register_blueprint(bp)




        add_resource_to_api(
            self.context.api, IntegrationsApi,
            '/integrations/<string:integration_name>',
            '/integrations/<int:project_id>'
        )

        self.context.slot_manager.register_callback('integrations', render_integrations)

    def get_registered(self):
        from plugins.shared.connectors.auth import SessionProject
        SessionProject.set(1)
        # return {k: v.json() for k, v in self.integrations.items()}
        # response = make_response(json.dumps(self.integrations, indent=2, default=lambda o: o.json(indent=2, default=lambda o: str(type(o)))), 200)
        # print(str({k: v.dict(by_alias=True) for k, v in self.integrations.items()}))
        response = make_response({k: v.json(indent=2, exclude={'integration_callback'}) for k, v in self.integrations.items()}, 200)
        response.headers['Content-Type'] = 'application/json'

        print('test rpc')
        print(self.context.rpc_manager.call.integrations_list())
        print(self.context.rpc_manager.call.integrations_sections())

        return response


    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info('De-initializing module integrations')
        self.integrations = dict()
