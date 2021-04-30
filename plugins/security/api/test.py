from sqlalchemy import and_

from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser

from ..models.api_tests import SecurityTestsDAST
from ..models.security_results import SecurityResultsDAST
from .utils import exec_test


class SecurityTestApi(RestResource):
    _post_rules = (
        dict(name="test_name", type=str, required=False, location='json'),
    )

    def __init__(self):
        super(SecurityTestApi, self).__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self.post_parser = build_req_parser(rules=self._post_rules)

    def post(self, project_id, test_id):
        """ Run test """
        args = self.post_parser.parse_args(strict=False)
        project = self.rpc.project_get_or_404(project_id=project_id)

        if isinstance(test_id, int):
            _filter = and_(
                SecurityTestsDAST.project_id == project.id, SecurityTestsDAST.id == test_id
            )
        else:
            _filter = and_(
                SecurityTestsDAST.project_id == project.id, SecurityTestsDAST.test_uid == test_id
            )
        test = SecurityTestsDAST.query.filter(_filter).first()

        event = list()
        event.append(test.configure_execution_json("cc"))
        #
        security_results = SecurityResultsDAST(
            project_id=project.id,
            test_id=test.id,
            test_uid=test.test_uid,
            test_name=args["test_name"],
        )
        security_results.insert()

        if args.get("type") == "config":
            return event[0]

        response = exec_test(project.id, event)

        # security_results.set_test_status("Finished")

        return response
