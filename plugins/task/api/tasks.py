from werkzeug.datastructures import FileStorage

from plugins.base.utils.restApi import RestResource
from plugins.base.data_utils.file_utils import File
from plugins.base.utils.api_utils import build_req_parser, get
from plugins.task.models.tasks import Task

from .utils import create_task


class TasksApi(RestResource):
    _get_rules = (
        dict(name="offset", type=int, default=0, location="args"),
        dict(name="limit", type=int, default=0, location="args"),
        dict(name="search", type=str, default="", location="args"),
        dict(name="sort", type=str, default="", location="args"),
        dict(name="order", type=str, default="", location="args"),
        dict(name="name", type=str, location="args"),
        dict(name="filter", type=str, location="args")
    )

    _post_rules = (
        dict(name="file", type=FileStorage, required=False, location='files'),
        dict(name="url", type=str, required=False, location='form'),
        dict(name="funcname", type=str, location='form'),
        dict(name="invoke_func", type=str, location='form'),
        dict(name="runtime", type=str, location='form'),
        dict(name="region", type=str, location='form'),
        dict(name="env_vars", type=str, location='form')
    )

    def __init__(self):
        super().__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self.get_parser = build_req_parser(rules=self._get_rules)
        self.post_parser = build_req_parser(rules=self._post_rules)

    def get(self, project_id: int):
        args = self.get_parser.parse_args(strict=False)
        reports = []
        total, res = get(project_id, args, Task)
        for each in res:
            reports.append(each.to_json())
        return {"total": total, "rows": reports}

    def post(self, project_id: int):
        args = self.post_parser.parse_args(strict=False)
        project = self.rpc.project_get_or_404(project_id=project_id)
        if args.get("file"):
            file = args["file"]
            if file.filename == "":
                return {"message": "file not selected", "code": 400}, 400
        elif args.get("url"):
            file = File(args.get("url"))
        else:
            return {"message": "Task file is not specified", "code": 400}, 400
        # TODO: we need to check on storage quota here
        task_id = create_task(project, file, args).task_id
        return {"file": task_id, "code": 0}, 200
