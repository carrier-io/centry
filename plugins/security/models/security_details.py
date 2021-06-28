from sqlalchemy import String, Column, Integer, Text

from plugins.base.db_manager import Base
from plugins.base.models.abstract_base import AbstractBaseMixin


class SecurityDetails(AbstractBaseMixin, Base):
    __tablename__ = "security_details"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, unique=False, nullable=False)
    detail_hash = Column(String(128), unique=False)
    details = Column(Text, unique=False)
