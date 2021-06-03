from sqlalchemy import String, Column, Integer, Text

from plugins.base.db_manager import Base
from plugins.base.models.abstract_base import AbstractBaseMixin


class SecurityReport(AbstractBaseMixin, Base):
    __tablename__ = "security_report"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, unique=False, nullable=False)
    report_id = Column(Integer, nullable=False)
    issue_hash = Column(String(128), unique=False)
    tool_name = Column(String(128), unique=False)
    description = Column(Text, unique=False)
    severity = Column(String(16), unique=False)
    details = Column(Integer, unique=False)
    endpoints = Column(Text, unique=False)
    # false_positive = Column(Integer, unique=False)
    # info_finding = Column(Integer, unique=False)
    # excluded_finding = Column(Integer, unique=False)
    status = Column(String(16), unique=False)
