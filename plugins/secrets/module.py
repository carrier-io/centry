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
from pylon.core.tools import log  # pylint: disable=E0611,E0401
from pylon.core.tools import module  # pylint: disable=E0611,E0401
from plugins.base.utils.api_utils import add_resource_to_api


class Module(module.ModuleModel):
    """ Galloper module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context

    def init(self):
        """ Init module """
        log.info("Initializing module Secrets")
        from .api.secrets import SecretsAPI
        from .api.secret import SecretApi
        add_resource_to_api(self.context.api, SecretsAPI, "/secrets/<int:project_id>")
        add_resource_to_api(self.context.api, SecretApi, "/secrets/<int:project_id>/<string:secret>")

        from .connectors.secrets import unsecret, get_project_hidden_secrets, set_project_secrets, \
            set_project_hidden_secrets, get_project_secrets, initialize_project_space, remove_project_space

        self.context.rpc_manager.register_function(unsecret, name="unsecret_key")
        self.context.rpc_manager.register_function(initialize_project_space, name="init_project_space")
        self.context.rpc_manager.register_function(remove_project_space)
        self.context.rpc_manager.register_function(get_project_secrets, name="get_secrets")
        self.context.rpc_manager.register_function(get_project_hidden_secrets, name="get_hidden")
        self.context.rpc_manager.register_function(set_project_hidden_secrets, name='project_set_hidden_secrets')
        self.context.rpc_manager.register_function(set_project_secrets, name='project_set_secrets')

    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing module")
    #

