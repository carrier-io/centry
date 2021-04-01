from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser

from ..models.statistics import Statistic
from ..models.quota import ProjectQuota


class StatisticAPI(RestResource):
    result_rules = (
        dict(name="ts", type=int, location="json"),
        dict(name="results", type=str, location="json"),
        dict(name="stderr", type=str, location="json")
    )

    def __init__(self):
        super().__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self._result_parser = build_req_parser(rules=self.result_rules)

    def get(self, project_id: int):
        statistic = Statistic.query.filter_by(project_id=project_id).first().to_json()
        quota = ProjectQuota.query.filter_by(project_id=project_id).first().to_json()
        stats = {}
        for each in ["performance_test_runs", "ui_performance_test_runs", "sast_scans", "dast_scans", "storage_space",
                     "tasks_count", "tasks_executions"]:

            stats[each] = {"current": statistic[each], "quota": quota[each]}
        stats["data_retention_limit"] = {"current": 0, "quota": quota["data_retention_limit"]}
        return stats
