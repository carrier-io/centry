#     Copyright 2020 getcarrier.io
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timedelta
from .statistics import Statistic
from plugins.base.models.abstract_base import AbstractBaseMixin
from plugins.base.db_manager import Base
from plugins.base.models.utils import utcnow


class ProjectQuota(AbstractBaseMixin, Base):
    __tablename__ = "project_quota"

    id = Column(Integer, primary_key=True)
    vuh_limit = Column(Integer, unique=False, nullable=False)
    project_id = Column(Integer, unique=False, nullable=False)
    storage_space = Column(Integer, unique=False)
    data_retention_limit = Column(Integer, unique=False)
    last_update_time = Column(DateTime, server_default=utcnow())

    def update(self, vuh_limit, storage_space, data_retention_limit):
        self.vuh_limit = vuh_limit
        self.storage_space = storage_space
        self.data_retention_limit = data_retention_limit
        self.commit()

    @classmethod
    def update_time(cls, project_quota) -> bool:
        if not project_quota.last_update_time:
            project_quota.last_update_time = datetime.utcnow()
            project_quota.commit()
            return True
        if (datetime.utcnow() - project_quota.last_update_time).total_seconds() > 2592000:
            project_quota.last_update_time = project_quota.last_update_time + timedelta(seconds=2592000)
            statistic = Statistic.query.filter_by(project_id=project_quota.project_id).first()
            statistic.vuh_used = 0
            statistic.dast_scans = 0
            statistic.sast_scans = 0
            statistic.performance_test_runs = 0
            statistic.ui_performance_test_runs = 0
            statistic.commit()
            return True
        return False

    @classmethod
    def check_quota(cls, project_id: int, quota: str) -> bool:
        project_quota = ProjectQuota.query.filter_by(project_id=project_id).first()
        ProjectQuota.update_time(project_quota)
        project_quota = project_quota.to_json()
        if project_quota:
            if project_quota[quota] == -1:
                return True
            statistic = Statistic.query.filter_by(project_id=project_id).first().to_json()
            if statistic[quota] >= project_quota[quota]:
                return False
        return True

    @staticmethod
    def check_quota_json(project_id: int, quota: str):
        if quota:
            return ProjectQuota.check_quota(project_id, quota)
        return ProjectQuota.query.filter(ProjectQuota.project_id == project_id).first().to_json()


def _update_quota(project_id, vuh_limit, storage_space, data_retention_limit):
    quota = ProjectQuota.query.filter_by(project_id=project_id).first()
    if quota:
        quota.update(vuh_limit=vuh_limit, storage_space=storage_space, data_retention_limit=data_retention_limit)
    else:
        quota = ProjectQuota(project_id=project_id, vuh_limit=vuh_limit,
                             storage_space=storage_space, data_retention_limit=data_retention_limit)
        quota.insert()
    return quota


def create(project_id, vuh_limit, storage_space, data_retention_limit):
    return _update_quota(project_id=project_id,
                         vuh_limit=vuh_limit,
                         storage_space=storage_space,
                         data_retention_limit=data_retention_limit)
