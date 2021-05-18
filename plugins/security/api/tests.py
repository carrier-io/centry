from sqlalchemy import and_
from uuid import uuid4
from json import loads

from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser, get

from ..models.api_tests import SecurityTestsDAST
from ..models.security_results import SecurityResultsDAST
from ..models.security_thresholds import SecurityThresholds
from .utils import exec_test


class SecurityTestsApi(RestResource):
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
        dict(name="name", type=str, location='form'),
        dict(name="project_name", type=str, location='form'),
        dict(name="test_env", type=str, location='form'),
        dict(name="urls_to_scan", type=str, location='form'),
        dict(name="urls_exclusions", type=str, location='form'),
        dict(name="scanners_cards", type=str, location='form'),
        # dict(name="reporting_cards", type=str, location='form'),
        dict(name="reporting", type=str, location='form'),
        dict(name="run_test", type=str, location='form'),
        dict(name="processing", type=str, location='form')
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
        total, res = get(project_id, args, SecurityTestsDAST)
        for each in res:
            reports.append(each.to_json())
        return {"total": total, "rows": reports}

    def delete(self, project_id: int):
        args = self.delete_parser.parse_args(strict=False)
        project = self.rpc.project_get_or_404(project_id=project_id)
        query_result = SecurityTestsDAST.query.filter(
            and_(SecurityTestsDAST.project_id == project.id, SecurityTestsDAST.id.in_(args["id[]"]))
        ).all()
        for each in query_result:
            each.delete()
        return {"message": "deleted"}

    def post(self, project_id: int):
        """
        Post method for creating and running test
        """
        args = self.post_parser.parse_args(strict=False)

        run_test = loads(args.pop("run_test"))
        test_uid = str(uuid4())

        project = self.rpc.project_get_or_404(project_id=project_id)

        test = SecurityTestsDAST(
            project_id=project.id,
            project_name=args["project_name"],
            test_uid=test_uid,
            name=args["name"],
            test_environment=args["test_env"],
            urls_to_scan=loads(args["urls_to_scan"]),
            urls_exclusions=loads(args["urls_exclusions"]),
            scanners_cards=loads(args["scanners_cards"]),
            reporting=loads(args["reporting"]),
            processing=loads(args["processing"])
        )
        test.insert()

        threshold = SecurityThresholds(
            project_id=project.id,
            test_name=args["name"],
            test_uid=test.test_uid,
            critical=-1,
            high=-1,
            medium=-1,
            low=-1,
            info=-1,
            critical_life=-1,
            high_life=-1,
            medium_life=-1,
            low_life=-1,
            info_life=-1
        )
        threshold.insert()

        if run_test:
            security_results = SecurityResultsDAST(
                project_id=project.id,
                test_id=test.id,
                test_uid=test_uid,
                test_name=args["name"]
            )
            security_results.insert()

            event = []
            event.append(test.configure_execution_json("cc"))

            response = exec_test(project.id, event)

            # security_results.set_test_status("Finished")

            return response

        return test.to_json(exclude_fields=("id",))
