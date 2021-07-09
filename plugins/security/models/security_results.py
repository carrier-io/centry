import string
from datetime import datetime as dt

from sqlalchemy import String, Column, Integer, JSON, DateTime, ARRAY

from plugins.base.db_manager import Base
from plugins.base.models.abstract_base import AbstractBaseMixin


class SecurityResultsDAST(AbstractBaseMixin, Base):
    __tablename__ = "security_results_dast"

    # TODO: excluded = ignored
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, unique=False, nullable=False)
    test_id = Column(Integer, unique=False)
    test_uid = Column(String(128), unique=False)
    test_name = Column(String(128), unique=False)
    start_date = Column(DateTime, default=dt.utcnow)
    duration = Column(String(128), unique=False)
    #
    scan_time = Column(String(128), unique=False)
    scan_duration = Column(String(128), unique=False)
    project_name = Column(String(128), unique=False)
    app_name = Column(String(128), unique=False)
    dast_target = Column(String(128), unique=False)
    sast_code = Column(String(128), unique=False)
    scan_type = Column(String(4), unique=False)
    findings = Column(Integer, unique=False)
    false_positives = Column(Integer, unique=False)
    excluded = Column(Integer, unique=False)
    info_findings = Column(Integer, unique=False)
    environment = Column(String(32), unique=False)
    #
    # findings counts
    # findings = Column(Integer, unique=False, default=0)
    valid = Column(Integer, unique=False, default=0)
    false_positive = Column(Integer, unique=False, default=0)
    ignored = Column(Integer, unique=False, default=0)
    critical = Column(Integer, unique=False, default=0)
    high = Column(Integer, unique=False, default=0)
    medium = Column(Integer, unique=False, default=0)
    low = Column(Integer, unique=False, default=0)
    info = Column(Integer, unique=False, default=0)
    # other
    # excluded = Column(Integer, unique=False)
    tags = Column(ARRAY(String))
    test_status = Column(
        JSON,
        default={
            "status": "Pending...",
            "percentage": 0,
            "description": "Process details description"
        }
    )

    # TODO: write this method
    def set_test_status(self, ts):
        self.test_status = ts
        self.commit()

    @staticmethod
    def sanitize(val):
        valid_chars = "_%s%s" % (string.ascii_letters, string.digits)
        return ''.join(c for c in val if c in valid_chars)

    def insert(self):
        super().insert()

    def to_json(self, exclude_fields: tuple = ()) -> dict:
        test_param = super().to_json(exclude_fields)

        from datetime import timedelta
        test_param["name"] = test_param.pop("test_name")
        if test_param["duration"]:
            test_param["ended_date"] = str(test_param["start_date"] + timedelta(seconds=float(test_param["duration"])))
        test_param["start_date"] = str(test_param["start_date"])
        return test_param
