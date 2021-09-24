from plugins.shared.db_manager import Base
from plugins.shared.models.abstract_base import AbstractBaseMixin
from plugins.shared.utils.rpc import RpcMixin
from sqlalchemy import Integer, Column, String, Boolean, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSON


class Integration(AbstractBaseMixin, RpcMixin, Base):
    __tablename__ = "integration"
    # __table_args__ = (UniqueConstraint('project_id', 'is_default', 'name', name='_project_default_uc'),)
    __table_args__ = (
        Index(
            'ix_project_default_uc',  # Index name
            'project_id', 'name',  # Columns which are part of the index
            unique=True,
            postgresql_where=Column('is_default')),  # The condition
    )
    # API_EXCLUDE_FIELDS = ("secrets_json", "worker_pool_config_json")

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=False)
    project_id = Column(Integer, unique=False)
    settings = Column(JSON, unique=False, default={})
    is_default = Column(Boolean, default=False, nullable=False)
    section = Column(String(64), unique=False, nullable=False)

    # @property
    # def section(self):
    #     return self.rpc.call.integrations_get_integration(self.name).section

