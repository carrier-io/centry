import hashlib

from flask import request

from sqlalchemy import and_, func, or_

from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser
from ..models.security_reports import SecurityReport
from ..models.security_details import SecurityDetails
from ..models.security_results import SecurityResultsDAST


class FindingsAPI(RestResource):

    _get_rules = (
        dict(name="type", type=str, location="args"),
    )

    # _get_rules = (
    #     dict(name="offset", type=int, default=0, location="args"),
    #     dict(name="limit", type=int, default=0, location="args"),
    #     dict(name="search", type=str, default="", location="args"),
    #     dict(name="sort", type=str, default="", location="args"),
    #     dict(name="order", type=str, default="", location="args"),
    #     dict(name="name", type=str, location="args"),
    #     dict(name="filter", type=str, location="args")
    # )

    _post_rules = (
        dict(name="status", type=str, location="form"),
    )

    put_rules = (
        dict(name="severity", type=str, location="json"),
        dict(name="status", type=str, location="json"),
        dict(name="issues_id", type=list, default=[], location="json")
    )

    def __init__(self):
        super(FindingsAPI, self).__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self._parser_get = build_req_parser(rules=self._get_rules)
        self._parser_post = build_req_parser(rules=self._post_rules)
        self._parser_put = build_req_parser(rules=self.put_rules)

    def get(self, project_id: int, test_id: int):

        args = self._parser_get.parse_args(strict=False)

        filter_ = []
        filter_.append(SecurityReport.project_id == project_id)
        filter_.append(SecurityReport.report_id == test_id)

        if args.get("type"):
            filter_.append(SecurityReport.status == args["type"])
        filter_ = and_(*tuple(filter_))
        issues = SecurityReport.query.filter(filter_).all()
        results = []
        for issue in issues:
            _res = issue.to_json()
            _res["details"] = SecurityDetails.query.filter_by(id=_res["details"]).first().details
            results.append(_res)
        return results

    def post(self, project_id: int, test_id: int):
        finding_db = None
        for finding in request.json:
            md5 = hashlib.md5(finding["details"].encode("utf-8")).hexdigest()
            hash_id = SecurityDetails.query.filter(
                and_(SecurityDetails.project_id == project_id, SecurityDetails.detail_hash == md5)
            ).first()
            if not hash_id:
                hash_id = SecurityDetails(detail_hash=md5, project_id=project_id, details=finding["details"])
                hash_id.insert()
            # Verify issue is false_positive or ignored
            finding["details"] = hash_id.id
            finding['project_id'] = project_id
            finding['report_id'] = test_id
            entrypoints = ""
            if finding.get("endpoints"):
                for each in finding.get("endpoints"):
                    if isinstance(each, list):
                        entrypoints += "<br />".join(each)
                    else:
                        entrypoints += f"<br />{each}"
            finding["endpoints"] = entrypoints
            issue = SecurityReport.query.filter(and_(
                SecurityReport.project_id == project_id,
                SecurityReport.issue_hash == finding['issue_hash'])).first()
            if issue:
                finding['severity'] = issue.severity
            if not (finding.get("false_positive") == 1 or finding.get("excluded_finding") == 1):
                issues = SecurityReport.query.filter(
                    and_(SecurityReport.project_id == project_id,
                         SecurityReport.issue_hash == finding["issue_hash"],
                         or_(SecurityReport.status == "False_Positive",
                             SecurityReport.status == "Ignored")
                         )).all()
                false_positive = sum([1 for issue in issues if issue.status == "False_Positive"])
                excluded_finding =sum([1 for issue in issues if issue.status == "Ignored"])
                finding["status"] = "False_Positive" if false_positive > 0 else "Not_defined"
                finding["status"] = "Ignored" if excluded_finding > 0 else "Not_defined"
                # TODO: wrap this to try-except or delete from requests
                try:
                    finding.pop("false_positive")
                    finding.pop("excluded_finding")
                    finding.pop("info_finding")
                except:
                    pass
            finding_db = SecurityReport(**finding)
            finding_db.add()
        if finding_db:
            finding_db.commit()

    def put(self, project_id: int, test_id: int):

        args = self._parser_put.parse_args(strict=False)
        issues = args.get("issues_id")
        accept_message = {"message": "accepted"}

        if args.get("severity"):
            update_value = {"severity": args["severity"]}
        elif args.get("status"):
            update_value = {"status": args["status"].replace(" ", "_")}
        else:
            return {"message": "Action is invalid"}, 400

        for issue_id in issues:
            issue_hash = SecurityReport.query.filter(
                and_(
                    SecurityReport.project_id == project_id,
                    SecurityReport.id == issue_id,
                    SecurityReport.report_id == test_id
                )
            ).first().issue_hash

            SecurityReport.query.filter(
                and_(
                    SecurityReport.project_id == project_id,
                    SecurityReport.issue_hash == issue_hash,
                    SecurityReport.report_id == test_id
                )
            ).update(update_value)
            SecurityReport.commit()

        finding_status_or_severity = (args.get("status"), args.get("severity"))
        _filter = and_(
            SecurityReport.report_id == test_id,
            SecurityReport.project_id == project_id
        )

        if finding_status_or_severity[0]:
            _available_values = {"false_positive", "ignored", "valid"}
            counted_statuses_or_severity = SecurityReport.query.with_entities(
                SecurityReport.status, func.count(SecurityReport.status)).filter(_filter).group_by(SecurityReport.status).all()
            counted_statuses_or_severity = list(map(lambda x: {x[0]: x[1]}, counted_statuses_or_severity))

        else:
            _available_values = {"critical", "high", "medium", "low", "info"}
            counted_statuses_or_severity = SecurityReport.query.with_entities(
                SecurityReport.severity, func.count(SecurityReport.severity)).filter(_filter).group_by(SecurityReport.severity).all()
            counted_statuses_or_severity = list(map(lambda x: {x[0]: x[1]}, counted_statuses_or_severity))

        for counted_stat_or_sevr in counted_statuses_or_severity:
            key, value = list(counted_stat_or_sevr.items())[0]

            if key.lower() not in _available_values:
                continue
            _available_values.remove(key.lower())

            SecurityResultsDAST.query.filter(
                and_(
                    SecurityResultsDAST.project_id == project_id,
                    SecurityResultsDAST.id == test_id
                )
            ).update(
                {
                    key.lower(): value
                }
            )
            SecurityResultsDAST.commit()

        for last_item in _available_values:
            SecurityResultsDAST.query.filter(
                and_(
                    SecurityResultsDAST.project_id == project_id,
                    SecurityResultsDAST.id == test_id
                )
            ).update(
                {
                    last_item: 0
                }
            )
            SecurityResultsDAST.commit()

        # Update all findings amount in Results table
        all_findings = SecurityReport.query.filter(
            and_(
                SecurityReport.project_id == project_id,
                SecurityReport.report_id == test_id
            )
        ).count()
        SecurityResultsDAST.query.filter(
            and_(
                SecurityResultsDAST.project_id == project_id,
                SecurityResultsDAST.id == test_id
            )
        ).update(
            {
                "findings": all_findings
            }
        )
        SecurityResultsDAST.commit()
        return accept_message
