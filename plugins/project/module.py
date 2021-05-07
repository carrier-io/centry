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
    """ Galloper module """

    def __init__(self, settings, root_path, context):
        self.settings = settings
        self.root_path = root_path
        self.context = context

    def init(self):
        """ Init module """
        log.info("Initializing module Projects")
        init_db()
        from .api.project import ProjectAPI
        from .api.projectsession import ProjectSessionAPI
        from .api.statistics import StatisticAPI
        from .api.quota import QuotaAPI
        add_resource_to_api(self.context.api, ProjectAPI, "/project", "/project/<int:project_id>")
        add_resource_to_api(self.context.api, ProjectSessionAPI, "/project-session",
                            "/project-session/<int:project_id>")
        add_resource_to_api(self.context.api, StatisticAPI, "/statistic/<int:project_id>")
        add_resource_to_api(self.context.api, QuotaAPI, "/quota/<int:project_id>")

        from plugins.project.rpc_worker import (
            prj_or_404, list_projects, get_project_statistics, get_storage_quota,
            check_quota, add_task_execution
        )
        self.context.rpc_manager.register_function(prj_or_404, name='project_get_or_404')
        self.context.rpc_manager.register_function(list_projects, name='project_list')
        self.context.rpc_manager.register_function(get_project_statistics, name='project_statistics')
        self.context.rpc_manager.register_function(add_task_execution)
        self.context.rpc_manager.register_function(get_storage_quota, name='project_get_storage_space_quota')
        self.context.rpc_manager.register_function(check_quota, name='project_check_quota')

        bp = flask.Blueprint(  # pylint: disable=C0103
            'project', 'plugins.project',
            root_path=self.root_path,
            url_prefix=f'{self.context.url_prefix}/'
        )
        bp.add_url_rule("/join/<url_id>", "project_join", self.project_join)
        print('BSBSBSBSBSBSBSB', bp)
        self.context.app.register_blueprint(bp)



    def deinit(self):  # pylint: disable=R0201
        """ De-init module """
        log.info("De-initializing module")
    #

    def project_join(self, url_id):
        from flask import session
        from flask import make_response
        from redis import Redis
        from plugins.base.constants import REDIS_PASSWORD
        from plugins.base.constants import REDIS_USER
        from plugins.base.constants import REDIS_HOST
        from plugins.base.constants import REDIS_PORT
        from plugins.project.models.keycloak_mixin import current_user_id, current_user_email
        from flask import redirect
        from flask import url_for

        try:
            user_id = current_user_id()
            user_email = current_user_email()
        except KeyError:
            session['X-Forwarded-Uri'] = request.url
            return redirect(url_for('auth_root.login'))
        # print('url_id url_idurl_idurl_idurl_id', url_id)
        # print('url_id url_idurl_idurl_idurl_id', self.context.rpc_manager.call.auth_check_auth(request.headers.get("Authorization", "")))
        # if not self.context.rpc_manager.call.auth_check_auth(request.headers.get("Authorization", "")):
        #     print('R urLLLLLLLLLLLLLL', request.url)


        with Redis(db=7,
                   password=REDIS_PASSWORD, username=REDIS_USER,
                   host=REDIS_HOST, port=REDIS_PORT
                   ) as redis_client:
            import json
            group_keycloak_id, invitee_email = json.loads(redis_client.get(f'join_url:{url_id}'))
            print('GCKID:::::::', group_keycloak_id, 'eml', invitee_email)
            if not group_keycloak_id:
                return make_response('Link invalid or expired', 404)
            if invitee_email.lower() != user_email.lower():
                return make_response('Invitation link is email-bound. Wrong user email', 403)
            self.context.rpc_manager.call.auth_manager_add_users_to_groups(
                realm='carrier',
                token=self.context.rpc_manager.call.auth_manager_get_token(),
                users=[user_id],
                groups=[group_keycloak_id],
            )
            # SessionProject.set()

            return redirect(url_for('theme.index'))
