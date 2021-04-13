from sqlalchemy import and_
from uuid import uuid4
from werkzeug.datastructures import FileStorage
from json import loads
from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser, str2bool, get, upload_file

from ..models.api_tests import ApiTests
from .utils import compile_tests


class TestsApi(RestResource):
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
        dict(name="file", type=FileStorage, location='files'),
        dict(name="local_path", type=str, location='form'),
        dict(name="git", type=str, location='form'),
        dict(name="name", type=str, location='form'),
        dict(name="entrypoint", type=str, location='form'),
        dict(name="parallel", type=int, location='form'),
        dict(name="region", type=str, location='form'),
        dict(name="reporting", type=str, location='form'),
        dict(name="emails", type=str, location='form'),
        dict(name="runner", type=str, location='form'),
        dict(name="compile", type=str2bool, location='form'),
        dict(name="params", type=str, location='form'),
        dict(name="env_vars", type=str, location='form'),
        dict(name="customization", type=str, location='form'),
        dict(name="cc_env_vars", type=str, location='form')
    )

    _delete_rules = (
        dict(name="id[]", type=int, action="append", location="args"),
    )

    def __init__(self):
        super().__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self.get_parser = build_req_parser(rules=self._get_rules)
        self.post_parser = build_req_parser(rules=self._post_rules)
        self.delete_parser = build_req_parser(rules=self._delete_rules)

    def get(self, project_id: int):
        args = self.get_parser.parse_args(strict=False)
        reports = []
        total, res = get(project_id, args, ApiTests)
        for each in res:
            reports.append(each.to_json())
        return {"total": total, "rows": reports}

    def delete(self, project_id: int):
        args = self.delete_parser.parse_args(strict=False)
        project = self.rpc.project_get_or_404(project_id=project_id)
        query_result = ApiTests.query.filter(
            and_(ApiTests.project_id == project.id, ApiTests.id.in_(args["id[]"]))
        ).all()
        for each in query_result:
            each.delete()
        return {"message": "deleted"}

    def post(self, project_id: int):
        args = self.post_parser.parse_args(strict=False)
        project = self.rpc.project_get_or_404(project_id=project_id)
        if args.get("git"):
            file_name = ""
            bucket = ""
            git_settings = loads(args["git"])
        else:
            git_settings = {}
            file_name = args["file"].filename
            bucket = "tests"
            upload_file(bucket, args["file"], project, create_if_not_exists=True)

        if args["compile"] and args["runner"] in ["v3.1", "v2.3"]:
            compile_tests(project.id, file_name, args["runner"])

        test = ApiTests(project_id=project.id,
                        test_uid=str(uuid4()),
                        name=args["name"],
                        parallel=args["parallel"],
                        region=args["region"],
                        bucket=bucket,
                        file=file_name,
                        git=git_settings,
                        local_path=args["local_path"],
                        entrypoint=args["entrypoint"],
                        runner=args["runner"],
                        reporting=loads(args["reporting"]),
                        params=loads(args["params"]),
                        env_vars=loads(args["env_vars"]),
                        customization=loads(args["customization"]),
                        cc_env_vars=loads(args["cc_env_vars"]))
        test.insert()
        return test.to_json(exclude_fields=("id",))