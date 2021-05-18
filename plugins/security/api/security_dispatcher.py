from sqlalchemy import and_

from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser
from ..models.api_tests import SecurityTestsDAST
from ..models.security_thresholds import SecurityThresholds


class SecuritySeedDispatcher(RestResource):
    _get_rules = (
        dict(name="type", type=str, location="args"),
    )

    def __init__(self):
        super().__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self.get_parser = build_req_parser(rules=self._get_rules)

    def get(self, project_id: int, seed: str):
        """ Get config for seed """
        args = self.get_parser.parse_args(strict=False)
        project = self.rpc.project_get_or_404(project_id=project_id)

        test_type = seed.split("_")[0]
        test_id = seed.split("_")[1]

        if test_type == "dast":
            _filter = and_(
                SecurityTestsDAST.project_id == project.id, SecurityTestsDAST.test_uid == test_id
            )
            test = SecurityTestsDAST.query.filter(_filter).first()
        #
        # if test_type == "sast":
        #     _filter = and_(
        #         SecurityTestsSAST.project_id == project.id, SecurityTestsSAST.test_uid == test_id
        #     )
        #     test = SecurityTestsSAST.query.filter(_filter).first()
        #
        try:
            thresholds = SecurityThresholds.query.filter(SecurityThresholds.test_uid == test_id).first().to_json(
                exclude_fields=("id", "project_id", "test_name", "test_uid"))
        except AttributeError:
            thresholds = {}
        return test.configure_execution_json(args.get("type"), thresholds=thresholds)
