from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser, get, str2bool
from ..models.security_results import SecurityResultsDAST


class SecurityResultsApi(RestResource):
    _get_rules = (
        dict(name="offset", type=int, default=0, location="args"),
        dict(name="limit", type=int, default=0, location="args"),
        dict(name="search", type=str, default="", location="args"),
        dict(name="sort", type=str, default="", location="args"),
        dict(name="order", type=str, default="", location="args"),
        dict(name="name", type=str, location="args"),
        dict(name="filter", type=str, location="args")
    )

    def __init__(self):
        super(SecurityResultsApi, self).__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self._parser_get = build_req_parser(rules=self._get_rules)

    def get(self, project_id: int):
        args = self._parser_get.parse_args(strict=False)
        reports = []
        total, res = get(project_id, args, SecurityResultsDAST)
        for each in res:
            reports.append(each.to_json())
        return {"total": total, "rows": reports}
