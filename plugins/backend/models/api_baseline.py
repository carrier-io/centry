from sqlalchemy import Column, Integer, String, JSON, ARRAY

from plugins.base.db_manager import Base
from plugins.base.models.abstract_base import AbstractBaseMixin


class APIBaseline(AbstractBaseMixin, Base):
    __tablename__ = "api_baseline"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, unique=False, nullable=False)
    report_id = Column(Integer, unique=False, nullable=False)
    test = Column(String, unique=False, nullable=False)
    environment = Column(String, unique=False, nullable=False)
    summary = Column(ARRAY(JSON), unique=False, nullable=False)
