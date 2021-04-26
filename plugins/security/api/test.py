from flask import current_app
from sqlalchemy import and_

from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser, get, str2bool
from plugins.task.api.utils import run_task
from plugins.project.models.statistics import Statistic
from ..models.api_tests import SecurityTestsDAST


class SecurityTestApi(RestResource):
    # _get_rules = (
    #     dict(name="raw", type=int, default=0, location="args"),
    #     dict(name="type", type=str, default='cc', location="args"),
    #     dict(name="exec", type=str2bool, default=False, location="args"),
    # )

    _put_rules = (
        dict(name="dast_settings", type=str, required=False, location='json'),
        dict(name="region", type=str, required=False, location='json')
    )

    _post_rules = (  # _put_rules + (
        # dict(name="test_type", type=str, required=False, location='json'),
        # dict(name="runner", type=str, required=False, location='json'),
        dict(name="type", type=str, default=None, required=False, location='json'),
    )

    def __init__(self):
        super(SecurityTestApi, self).__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        # self.get_parser = build_req_parser(rules=self._get_rules)
        self.put_parser = build_req_parser(rules=self._put_rules)
        self.post_parser = build_req_parser(rules=self._post_rules)

    # def get(self, project_id, test_id):
    #     """ Get test data """
    #     args = self.get_parser.parse_args(strict=False)
    #     project = self.rpc.get_or_404(project_id=project_id)
    #     #
    #     if isinstance(test_id, int):
    #         _filter = and_(
    #             SecurityTestsDAST.project_id == project.id, SecurityTestsDAST.id == test_id
    #         )
    #     else:
    #         _filter = and_(
    #             SecurityTestsDAST.project_id == project.id, SecurityTestsDAST.test_uid == test_id
    #         )
    #     test = SecurityTestsDAST.query.filter(_filter).first()
    #     #
    #     if args.raw:
    #         return test.to_json()
    #     #
    #     if args["type"] == "docker":
    #         message = test.configure_execution_json(args.get("type"), execution=args.get("exec"))
    #     else:  # type = cc
    #         message = [{"test_id": test.test_uid}]
    #     #
    #     return {"config": message}

    # def put(self, project_id, test_id):
    #     """ Update test data """
    #     from json import loads
    #     args = self.put_parser.parse_args(strict=False)
    #     project = self.rpc.get_or_404(project_id=project_id)
    #     #
    #     if isinstance(test_id, int):
    #         _filter = and_(
    #             SecurityTestsDAST.project_id == project.id, SecurityTestsDAST.id == test_id
    #         )
    #     else:
    #         _filter = and_(
    #             SecurityTestsDAST.project_id == project.id, SecurityTestsDAST.test_uid == test_id
    #         )
    #     task = SecurityTestsDAST.query.filter(_filter).first()
    #     #
    #     if args.get("dast_settings", None):
    #         task.dast_settings = {
    #             "project_name": project.name,
    #             **loads(args["dast_settings"]),
    #         }
    #     if args.get("region"):
    #         task.region = args.get("region")
    #     #
    #     task.commit()
    #     return task.to_json()

    def post(self, project_id, test_id):
        """ Run test """
        args = self.post_parser.parse_args(strict=False)
        project = self.rpc.get_or_404(project_id=project_id)
        #
        if isinstance(test_id, int):
            _filter = and_(
                SecurityTestsDAST.project_id == project.id, SecurityTestsDAST.id == test_id
            )
        else:
            _filter = and_(
                SecurityTestsDAST.project_id == project.id, SecurityTestsDAST.test_uid == test_id
            )
        test = SecurityTestsDAST.query.filter(_filter).first()
        #
        execution = bool(args["type"] and args["type"] == "config")
        #
        event = list()
        event.append(test.configure_execution_json("cc", execution=execution))
        #
        if args["type"] and args["type"] == "config":
            return event[0]
        #
        response = run_task(project.id, event)
        response["redirect"] = f"/task/{response['task_id']}/results"
        #
        statistic = Statistic.query.filter_by(project_id=project_id).first()
        statistic.dast_scans += 1
        statistic.commit()
        #
        return response
