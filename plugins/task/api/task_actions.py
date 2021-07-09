from flask import request

from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser, str2bool, get

from ..models.tasks import Task
from ..models.results import Results


class TaskActionApi(RestResource):
    _get_rules = (
        dict(name="offset", type=int, default=0, location="args"),
        dict(name="limit", type=int, default=0, location="args"),
        dict(name="search", type=str, default="", location="args"),
        dict(name="sort", type=str, default="", location="args"),
        dict(name="order", type=str, default="", location="args"),
        dict(name="name", type=str, location="args"),
        dict(name="filter", type=str, location="args")
    )

    result_rules = (
        dict(name="ts", type=int, location="json"),
        dict(name="results", type=str, location="json"),
        dict(name="stderr", type=str, location="json")
    )

    def __init__(self):
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self._result_parser = build_req_parser(rules=self.result_rules)
        self.get_parser = build_req_parser(rules=self._get_rules)

    def get(self, task_id, action):
        task = Task.query.filter_by(task_id=task_id).first()
        if action in ("suspend", "delete", "activate"):
            getattr(task, action)()
        if action == "results":
            args = self.get_parser.parse_args(strict=False)
            reports = []
            total, res = get(task.project_id, args, Results, additional_filter={"task_id": task_id})
            for each in res:
                reports.append(each.to_json())
            return {"total": total, "rows": reports}
        return {"message": "Done", "code": 200}

    def post(self, task_id, action):
        task = Task.query.filter_by(task_id=task_id).first()
        project_id = task.project_id
        if action == "edit":
            for key, value in request.form.items():
                if key in ["id", "task_id", "zippath", "last_run"]:
                    continue
                elem = getattr(task, key, None)
                if value in ["None", "none", ""]:
                    value = None
                if elem != value:
                    setattr(task, key, value)
                task.commit()
        elif action == "results":
            data = self._result_parser.parse_args(strict=False)
            task.set_last_run(data["ts"])
            result = Results(
                task_id=task_id,
                project_id=project_id,
                ts=data["ts"],
                results=data["results"],
                log=data["stderr"]
            )
            result.insert()
        return {"message": "Ok", "code": 201}
