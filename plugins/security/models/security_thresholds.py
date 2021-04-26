from sqlalchemy import Column, Integer, String, Float

from plugins.base.db_manager import Base
from plugins.base.models.abstract_base import AbstractBaseMixin


class SecurityThresholds(AbstractBaseMixin, Base):
    __tablename__ = "sec_thresholds"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, unique=False, nullable=False)
    test_name = Column(String, unique=False, nullable=False)
    test_uid = Column(String, unique=False, nullable=False)
    critical = Column(Integer, unique=False, nullable=False)
    high = Column(Integer, unique=False, nullable=False)
    medium = Column(Integer, unique=False, nullable=False)
    low = Column(Integer, unique=False, nullable=False)
    info = Column(Integer, unique=False, nullable=False)
    critical_life = Column(Integer, unique=False, nullable=False)
    high_life = Column(Integer, unique=False, nullable=False)
    medium_life = Column(Integer, unique=False, nullable=False)
    low_life = Column(Integer, unique=False, nullable=False)
    info_life = Column(Integer, unique=False, nullable=False)
