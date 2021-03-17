from flask import request
from flask_restful import Resource

from plugins.base.utils.api_utils import build_req_parser, str2bool

from .utils import run_task
from ..models.tasks import Task


class TaskApi(Resource):
    _get_rules = (
        dict(name="exec", type=str2bool, default=False, location="args"),
    )

    _put_rules = (
        dict(name="invoke_func", type=str, location='form'),
        dict(name="region", type=str, location='form'),
        dict(name="env_vars", type=str, location='form')
    )

    def __init__(self):
        self.__init_req_parsers()
        from flask import current_app
        self.app = current_app

    def __init_req_parsers(self):
        self.get_parser = build_req_parser(rules=self._get_rules)
        self.put_parser = build_req_parser(rules=self._put_rules)

    def _get_task(self, project_id, task_id):
        return self.app.config["CONTEXT"].rpc_manager.call.project_get_or_404(project_id=project_id), \
               Task.query.filter_by(task_id=task_id).first()

    def get(self, project_id: int, task_id: str):
        args = self.get_parser.parse_args(strict=False)
        project, task = self._get_task(project_id, task_id)
        if args.get("exec"):
            return self.app.config["CONTEXT"].rpc_manager.call.project_unsecret(
                value=task.to_json(), project_id=project_id)
        return task.to_json()

    def post(self, project_id: int, task_id: str):
        project, task = self._get_task(project_id, task_id)
        event = request.get_json()
        return run_task(project.id, event, task.task_id)

    def put(self, project_id: int, task_id: str):
        args = self.put_parser.parse_args(strict=False)
        project, task = self._get_task(project_id, task_id)
        task.task_handler = args.get("invoke_func")
        task.region = args.get("region")
        task.env_vars = args.get("env_vars")
        task.commit()
        return task.to_json()

    def delete(self, project_id: int, task_id: str):
        project, task = self._get_task(project_id, task_id)
        task.delete()
        return {}
