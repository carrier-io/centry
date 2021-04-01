from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser
from ..models.quota import ProjectQuota
from ..models.project import Project


class QuotaAPI(RestResource):
    result_rules = (
        dict(name="quota", type=str, location="args"),
    )

    def __init__(self):
        super().__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self._result_parser = build_req_parser(rules=self.result_rules)

    def get(self, project_id: int):
        project = Project.get_or_404(project_id)
        args = self._result_parser.parse_args()
        return ProjectQuota.check_quota_json(project.id, args.get("quota"))

