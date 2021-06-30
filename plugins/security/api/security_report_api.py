from datetime import datetime

from sqlalchemy import and_, or_

from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser
from plugins.project.models.project import Project
from plugins.project.models.statistics import Statistic
from plugins.project.models.quota import ProjectQuota

from ..models.security_reports import SecurityReport
from ..models.security_results import SecurityResultsDAST


class SecurityReportAPI(RestResource):
    get_rules = (
        dict(name="offset", type=int, default=0, location="args"),
        dict(name="limit", type=int, default=0, location="args"),
        dict(name="search", type=str, default="", location="args"),
        dict(name="sort", type=str, default="", location="args"),
        dict(name="order", type=str, default="", location="args"),
        dict(name="type", type=str, default="sast", location="args"),
    )
    delete_rules = (
        dict(name="id[]", type=int, action="append", location="args"),
    )
    post_rules = (
        dict(name="project_name", type=str, location="json"),
        dict(name="app_name", type=str, location="json"),
        dict(name="scan_time", type=float, location="json"),
        dict(name="dast_target", type=str, location="json"),
        dict(name="sast_code", type=str, location="json"),
        dict(name="scan_type", type=str, location="json"),
        dict(name="findings", type=int, location="json"),
        dict(name="false_positives", type=int, location="json"),
        dict(name="excluded", type=int, location="json"),
        dict(name="info_findings", type=int, location="json"),
        dict(name="environment", type=str, location="json")
    )

    def __init__(self):
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self._parser_get = build_req_parser(rules=self.get_rules)
        self._parser_post = build_req_parser(rules=self.post_rules)
        self._parser_delete = build_req_parser(rules=self.delete_rules)

    def get(self, project_id):
        reports = []
        args = self._parser_get.parse_args(strict=False)
        search_ = args.get("search")
        limit_ = args.get("limit")
        offset_ = args.get("offset")
        scan_type = args.get("type").upper()
        if args.get("sort"):
            sort_rule = getattr(getattr(SecurityResultsDAST, args["sort"]), args["order"])()
        else:
            sort_rule = SecurityResultsDAST.id.desc()
        if not args.get("search") and not args.get("sort"):
            total = SecurityResultsDAST.query.filter(and_(SecurityResultsDAST.project_id == project_id,
                                                      SecurityResultsDAST.scan_type == scan_type)
                                                 ).order_by(sort_rule).count()
            res = SecurityResultsDAST.query.filter(and_(SecurityResultsDAST.project_id == project_id,
                                                    SecurityResultsDAST.scan_type == scan_type)).\
                order_by(sort_rule).limit(limit_).offset(offset_).all()
        else:
            filter_ = and_(SecurityResultsDAST.project_id == project_id, SecurityResultsDAST.scan_type == scan_type,
                      or_(SecurityResultsDAST.project_name.like(f"%{search_}%"),
                          SecurityResultsDAST.app_name.like(f"%{search_}%"),
                          SecurityResultsDAST.scan_type.like(f"%{search_}%"),
                          SecurityResultsDAST.environment.like(f"%{search_}%")))
            res = SecurityResultsDAST.query.filter(filter_).order_by(sort_rule).limit(limit_).offset(offset_).all()
            total = SecurityResultsDAST.query.filter(filter_).order_by(sort_rule).count()
        for each in res:
            each_json = each.to_json()
            each_json["scan_time"] = each_json["scan_time"].replace("T", " ").split(".")[0]
            each_json["scan_duration"] = float(each_json["scan_duration"])
            reports.append(each_json)
        return {"total": total, "rows": reports}

    def delete(self, project_id: int):
        args = self._parser_delete.parse_args(strict=False)
        project = Project.get_or_404(project_id)
        for each in SecurityReport.query.filter(
            and_(SecurityReport.project_id == project.id, SecurityReport.report_id.in_(args["id[]"]))
        ).order_by(SecurityReport.id.asc()).all():
            each.delete()
        for each in SecurityResultsDAST.query.filter(
            SecurityResultsDAST.id.in_(args["id[]"])
        ).order_by(SecurityResultsDAST.id.asc()).all():
            each.delete()
        return {"message": "deleted"}

    def post(self, project_id: int):
        args = self._parser_post.parse_args(strict=False)
        project = Project.get_or_404(project_id)
        # TODO move sast/dast quota checks to a new endpoint, which will be triggered before the scan
        if args["scan_type"].lower() == 'sast':
            if not ProjectQuota.check_quota(project_id=project_id, quota='sast_scans'):
                return {"Forbidden": "The number of sast scans allowed in the project has been exceeded"}
        elif args["scan_type"].lower() == 'dast':
            if not ProjectQuota.check_quota(project_id=project_id, quota='dast_scans'):
                return {"Forbidden": "The number of dast scans allowed in the project has been exceeded"}
        report = SecurityResultsDAST(
            scan_time=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            project_id=project.id,
            scan_duration=args["scan_time"],
            project_name=args["project_name"],
            app_name=args["app_name"],
            dast_target=args["dast_target"],
            sast_code=args["sast_code"],
            scan_type=args["scan_type"],
            findings=args["findings"]-(args["false_positives"]+args["excluded"]),
            false_positives=args["false_positives"],
            excluded=args["excluded"],
            info_findings=args["info_findings"],
            environment=args["environment"]
        )
        report.insert()

        statistic = Statistic.query.filter_by(project_id=project_id).first()
        if args["scan_type"].lower() == 'sast':
            setattr(statistic, 'sast_scans', Statistic.sast_scans + 1)
        elif args["scan_type"].lower() == 'dast':
            setattr(statistic, 'dast_scans', Statistic.dast_scans + 1)
        statistic.commit()

        return {"id": report.id}