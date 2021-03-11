from flask import request
from flask_restful import Resource

from plugins.base.utils.api_utils import build_req_parser, str2bool

from .utils import run_task
from ..models.tasks import Task


class TaskApi(Resource):
    _get_rules = (
        dict(name="exec", type=str2bool, default=False, location="args"),
    )

    def __init__(self):
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self.get_parser = build_req_parser(rules=self._get_rules)

    def get(self, project_id: int, task_id: str):
        from flask import current_app
        current_app.config["CONTEXT"].rpc_manager.call.project_get_or_404(project_id=project_id)
        args = self.get_parser.parse_args(strict=False)
        task = Task.query.filter_by(task_id=task_id).first()
        if args.get("exec"):
            return current_app.config["CONTEXT"].rpc_manager.call.project_unsecret(
                value=task.to_json(), project_id=project_id)
        return task.to_json()

    def post(self, project_id: int, task_id: str):
        from flask import current_app
        project = current_app.config["CONTEXT"].rpc_manager.call.project_get_or_404(project_id=project_id)
        task = Task.query.filter_by(task_id=task_id).first()
        event = request.get_json()
        return run_task(project.id, event, task.task_id)
