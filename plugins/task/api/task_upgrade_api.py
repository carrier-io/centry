from flask_restful import Resource
from sqlalchemy import and_

from plugins.base.data_utils.file_utils import File
from plugins.base.utils.api_utils import upload_file
from plugins.base.utils.api_utils import build_req_parser
from plugins.base.constants import POST_PROCESSOR_PATH, CONTROL_TOWER_PATH, APP_HOST, REDIS_PASSWORD, \
    APP_IP, EXTERNAL_LOKI_HOST, INFLUX_PORT, LOKI_PORT, RABBIT_USER, RABBIT_PASSWORD, INFLUX_PASSWORD, INFLUX_USER

from ..models.tasks import Task

class TaskUpgradeApi(Resource):
    _get_rules = (dict(name="name", type=str, location="args"),)

    def __init__(self):
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self.get_parser = build_req_parser(rules=self._get_rules)

    @staticmethod
    def create_cc_task(project):
        upload_file(bucket="tasks", f=File(CONTROL_TOWER_PATH), project=project)
        task = Task.query.filter(and_(Task.task_name == "control_tower", Task.project_id == project.id)).first()
        setattr(task, "zippath", "tasks/control-tower.zip")
        task.commit()

    @staticmethod
    def create_pp_task(project):
        upload_file(bucket="tasks", f=File(POST_PROCESSOR_PATH), project=project)
        task = Task.query.filter(and_(Task.task_name == "post_processor", Task.project_id == project.id)).first()
        setattr(task, "zippath", "tasks/post_processing.zip")
        task.commit()

    def get(self, project_id):
        from flask import current_app
        project = current_app.config["CONTEXT"].rpc_manager.call.project_get_or_404(project_id=project_id)
        args = self.get_parser.parse_args(strict=False)
        if args['name'] not in ['post_processor', 'control_tower', 'all']:
            return {"message": "You shall not pass", "code": 400}, 400
        secrets = current_app.config["CONTEXT"].rpc_manager.call.project_get_hidden_secrets(project_id=project.id)
        project_secrets = {}
        if args['name'] == 'post_processor':
            self.create_pp_task(project)
        elif args['name'] == 'control_tower':
            self.create_cc_task(project)
        elif args['name'] == 'all':
            self.create_pp_task(project)
            self.create_cc_task(project)
            project_secrets["galloper_url"] = APP_HOST
            project_secrets["project_id"] = project.id
            secrets["redis_host"] = APP_IP
            secrets["loki_host"] = EXTERNAL_LOKI_HOST.replace("https://", "http://")
            secrets["influx_ip"] = APP_IP
            secrets["influx_port"] = INFLUX_PORT
            secrets["influx_user"] = INFLUX_USER
            secrets["influx_password"] = INFLUX_PASSWORD
            secrets["loki_port"] = LOKI_PORT
            secrets["redis_password"] = REDIS_PASSWORD
            secrets["rabbit_host"] = APP_IP
            secrets["rabbit_user"] = RABBIT_USER
            secrets["rabbit_password"] = RABBIT_PASSWORD
            secrets = current_app.config["CONTEXT"].rpc_manager.call.project_set_secrets(
                project_id=project.id,
                secrets=project_secrets
            )
        else:
            return {"message": "go away", "code": 400}, 400
        current_app.config["CONTEXT"].rpc_manager.call.project_set_hidden_secrets(
            project_id=project.id,
            secrets=secrets
        )
        return {"message": "Done", "code": 200}
