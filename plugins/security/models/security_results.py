import string
from datetime import datetime as dt

from sqlalchemy import String, Column, Integer, JSON, DateTime

from plugins.base.db_manager import Base
from plugins.base.models.abstract_base import AbstractBaseMixin


class SecurityResultsDAST(AbstractBaseMixin, Base):
    __tablename__ = "security_results_dast"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, unique=False, nullable=False)
    test_id = Column(Integer, unique=False)
    test_uid = Column(String(128), unique=False)
    test_name = Column(String(128), unique=False)
    start_date = Column(DateTime, default=dt.utcnow)
    # duration = Column(String(128), unique=False)
    # findings = Column(Integer, unique=False)
    # false_positive = Column(Integer, unique=False)
    # excluded = Column(Integer, unique=False)
    # info = Column(Integer, unique=False)
    # tag = Column()
    test_status = Column(String(128), default="Pending")
    execution_json = Column(JSON)

    # TODO: write this method
    def set_task_status(self, ts):
        self.status = ts
        self.commit()

    @staticmethod
    def sanitize(val):
        valid_chars = "_%s%s" % (string.ascii_letters, string.digits)
        return ''.join(c for c in val if c in valid_chars)

    def insert(self):
        super().insert()

    def to_json(self, exclude_fields: tuple = ()) -> dict:
        test_param = super().to_json(exclude_fields)
        test_param["name"] = test_param.pop("test_name")
        test_param["start_date"] = str(test_param["start_date"])
        return test_param
