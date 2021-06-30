from sqlalchemy import and_, func

from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser
from ..models.security_results import SecurityResultsDAST
from ..models.security_reports import SecurityReport


class TestStatusUpdater(RestResource):
    _put_rules = (
        dict(name="test_status", type=dict, location="json"),
    )

    def __init__(self):
        super().__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self._parser_put = build_req_parser(rules=self._put_rules)

    def put(self, project_id: int, test_id: int):
        args = self._parser_put.parse_args(strict=False)
        test_status = args.get("test_status")

        if not test_status:
            return {"message": "There's no enough parameters"}, 400

        if isinstance(test_id, int):
            _filter = and_(
                SecurityResultsDAST.project_id == project_id, SecurityResultsDAST.id == test_id
            )
        else:
            _filter = and_(
                SecurityResultsDAST.project_id == project_id, SecurityResultsDAST.test_uid == test_id
            )
        test = SecurityResultsDAST.query.filter(_filter).first()
        test.set_test_status(test_status)

        if test_status["status"].lower().startswith("finished"):
            if isinstance(test_id, int):
                _filter = and_(
                    SecurityReport.project_id == project_id, SecurityReport.id == test_id
                )
            else:
                _filter = and_(
                    SecurityReport.project_id == project_id, SecurityReport.test_uid == test_id
                )
            counted_severity = SecurityReport.query.with_entities(
                SecurityReport.severity,
                func.count(SecurityReport.severity)
            ).filter(_filter).group_by(SecurityReport.severity).all()

            counted_statuses = SecurityReport.query.with_entities(
                SecurityReport.status,
                func.count(SecurityReport.status)
            ).filter(_filter).group_by(SecurityReport.status).all()

            for severity in counted_severity:
                setattr(test, severity[0].lower(), severity[1])

            for status in counted_statuses:
                setattr(test, status[0].lower().replace(" ", "_"), status[1])
            test.commit()

        return {"message": f"Status for test_id={test_id} of project_id: {project_id} updated"}, 200
