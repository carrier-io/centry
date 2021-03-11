#     Copyright 2020 getcarrier.io
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
import logging
from json import dumps
from typing import Optional, Union, Tuple
from datetime import datetime
from flask_restful import Resource

from plugins.base.utils.api_utils import build_req_parser
from plugins.base.connectors.auth import (SessionProject, SessionUser, superadmin_required)

from ..connectors.secrets import (initialize_project_space, remove_project_space,
                                  set_project_secrets, set_project_hidden_secrets)

from ..connectors.influx import create_project_databases, drop_project_databases

from plugins.base.constants import (POST_PROCESSOR_PATH, CONTROL_TOWER_PATH, APP_IP, APP_HOST,
                                    EXTERNAL_LOKI_HOST, INFLUX_PORT, LOKI_PORT,
                                    INFLUX_PASSWORD, INFLUX_USER, GF_API_KEY, RABBIT_USER,
                                    RABBIT_PASSWORD, REDIS_PASSWORD)

from ..models.project import Project
from ..models.statistics import Statistic
from ..models import quota


class ProjectAPI(Resource):
    get_rules = (
        dict(name="offset", type=int, default=None, location="args"),
        dict(name="limit", type=int, default=None, location="args"),
        dict(name="search", type=str, default="", location="args")
    )
    post_rules = (
        dict(name="name", type=str, location="json"),
        dict(name="owner", type=str, default=None, location="json"),
        dict(name="plugins", type=list, default=None, location="json"),
        dict(name="vuh_limit", type=int, default=500, location="json"),
        dict(name="storage_space_limit", type=int, default=100, location="json"),
        dict(name="data_retention_limit", type=int, default=30, location="json")
    )

    def __init__(self):
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self._parser_get = build_req_parser(rules=self.get_rules)
        self._parser_post = build_req_parser(rules=self.post_rules)

    def get(self, project_id: Optional[int] = None) -> Union[Tuple[dict, int], Tuple[list, int]]:
        args = self._parser_get.parse_args()
        offset_ = args["offset"]
        limit_ = args["limit"]
        search_ = args["search"]
        return Project.list_projects(project_id, search_, limit_, offset_), 200

    @superadmin_required
    def post(self, project_id: Optional[int] = None) -> Tuple[dict, int]:
        data = self._parser_post.parse_args()
        name_ = data["name"]
        owner_ = data["owner"]
        vuh_limit = data["vuh_limit"]
        plugins = data["plugins"]
        storage_space_limit = data["storage_space_limit"]
        data_retention_limit = data["data_retention_limit"]
        project = Project(
            name=name_,
            plugins=plugins,
            project_owner=owner_
        )
        project_secrets = {}
        project_hidden_secrets = {}
        project.insert()
        SessionProject.set(project.id)  # Looks weird, sorry :D
        quota.create(project.id, vuh_limit, storage_space_limit, data_retention_limit)

        statistic = Statistic(
            project_id=project.id,
            start_time=str(datetime.utcnow()),
            vuh_used=0,
            performance_test_runs=0,
            sast_scans=0,
            dast_scans=0,
            ui_performance_test_runs=0,
            public_pool_workers=0,
            tasks_executions=0
        )
        statistic.insert()

        pp_args = {
            "funcname": "post_processor",
            "invoke_func": "lambda_function.lambda_handler",
            "runtime": "Python 3.7",
            "env_vars": dumps({
                "jmeter_db": "{{secret.jmeter_db}}",
                "gatling_db": "{{secret.gatling_db}}",
                "comparison_db": "{{secret.comparison_db}}"
            })
        }
        from flask import current_app
        pp = current_app.context.rpc_manager.call_function('task_create', project.to_json(), POST_PROCESSOR_PATH, pp_args)
        cc_args = {
            "funcname": "control_tower",
            "invoke_func": "lambda.handler",
            "runtime": "Python 3.7",
            "env_vars": dumps({
                "token": "{{secret.auth_token}}",
                "galloper_url": "{{secret.galloper_url}}",
                "GALLOPER_WEB_HOOK": '{{secret.post_processor}}',
                "project_id": '{{secret.project_id}}',
                "loki_host": '{{secret.loki_host}}'
            })
        }
        cc = current_app.context.rpc_manager.call_function('task_create', project.to_json(), CONTROL_TOWER_PATH, cc_args)
        project_secrets["galloper_url"] = APP_HOST
        project_secrets["project_id"] = project.id
        project_hidden_secrets["post_processor"] = f'{APP_HOST}{pp["webhook"]}'
        project_hidden_secrets["post_processor_id"] = pp["task_id"]
        project_hidden_secrets["redis_host"] = APP_IP
        project_hidden_secrets["loki_host"] = EXTERNAL_LOKI_HOST.replace("https://", "http://")
        project_hidden_secrets["influx_ip"] = APP_IP
        project_hidden_secrets["influx_port"] = INFLUX_PORT
        project_hidden_secrets["loki_port"] = LOKI_PORT
        project_hidden_secrets["redis_password"] = REDIS_PASSWORD
        project_hidden_secrets["rabbit_host"] = APP_IP
        project_hidden_secrets["rabbit_user"] = RABBIT_USER
        project_hidden_secrets["rabbit_password"] = RABBIT_PASSWORD
        project_hidden_secrets["control_tower_id"] = cc["task_id"]
        project_hidden_secrets["influx_user"] = INFLUX_USER
        project_hidden_secrets["influx_password"] = INFLUX_PASSWORD
        project_hidden_secrets["jmeter_db"] = f'jmeter_{project.id}'
        project_hidden_secrets["gatling_db"] = f'gatling_{project.id}'
        project_hidden_secrets["comparison_db"] = f'comparison_{project.id}'
        project_hidden_secrets["telegraf_db"] = f'telegraf_{project.id}'
        project_hidden_secrets["gf_api_key"] = GF_API_KEY

        project_vault_data = {
            "auth_role_id": "",
            "auth_secret_id": ""
        }
        try:
            project_vault_data = initialize_project_space(project.id)
        except:
            current_app.logger.warning("Vault is not configured")
        project.secrets_json = {
            "vault_auth_role_id": project_vault_data["auth_role_id"],
            "vault_auth_secret_id": project_vault_data["auth_secret_id"],
        }
        project.commit()
        set_project_secrets(project.id, project_secrets)
        set_project_hidden_secrets(project.id, project_hidden_secrets)
        create_project_databases(project.id)
        # set_grafana_datasources(project.id)
        return {"message": f"Project was successfully created"}, 200

    def put(self, project_id: Optional[int] = None) -> Tuple[dict, int]:
        data = self._parser_post.parse_args()
        if not project_id:
            return {"message": "Specify project id"}, 400
        project = Project.get_or_404(project_id)
        project.name = data["name"]
        project.project_owner = data["owner"]
        package = data["package"].lower()
        project.dast_enabled = False if data["dast_enabled"] == "disabled" else True
        project.sast_enabled = False if data["sast_enabled"] == "disabled" else True
        project.performance_enabled = False if data["performance_enabled"] == "disabled" else True
        project.package = package
        project.commit()
        if package == "custom":
            getattr(quota, "custom")(project.id, data["perf_tests_limit"], data["ui_perf_tests_limit"],
                                     data["sast_scans_limit"], data["dast_scans_limit"], -1,
                                     data["storage_space_limit"], data["data_retention_limit"],
                                     data["tasks_count_limit"], data["task_executions_limit"])
        else:
            getattr(quota, package)(project.id)

        return project.to_json(exclude_fields=Project.API_EXCLUDE_FIELDS)

    def delete(self, project_id: int) -> Tuple[dict, int]:
        drop_project_databases(project_id)
        Project.apply_full_delete_by_pk(pk=project_id)
        remove_project_space(project_id)
        return {"message": f"Project with id {project_id} was successfully deleted"}, 200
