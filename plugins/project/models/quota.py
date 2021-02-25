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
from .project import Project
from .statistics import Statistic
from plugins.base.models.abstract_base import AbstractBaseMixin
from plugins.base.db_manager import Base
from plugins.base.models.utils import utcnow


class ProjectQuota(AbstractBaseMixin, Base):
    __tablename__ = "project_quota"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, unique=False, nullable=False)
    name = Column(String, unique=False, nullable=False)
    performance_test_runs = Column(Integer, unique=False)  # per month
    ui_performance_test_runs = Column(Integer, unique=False)  # per month
    sast_scans = Column(Integer, unique=False)  # total active
    dast_scans = Column(Integer, unique=False)  # per month
    public_pool_workers = Column(Integer, unique=False)
    storage_space = Column(Integer, unique=False)
    data_retention_limit = Column(Integer, unique=False)
    tasks_count = Column(Integer, unique=False)
    tasks_executions = Column(Integer, unique=False)
    last_update_time = Column(DateTime, server_default=utcnow())

    def update(self, name, performance_test_runs, ui_performance_test_runs, sast_scans, dast_scans, public_pool_workers,
               storage_space, data_retention_limit, tasks_count, tasks_executions):
        self.name = name
        self.performance_test_runs = performance_test_runs
        self.ui_performance_test_runs = ui_performance_test_runs
        self.sast_scans = sast_scans
        self.dast_scans = dast_scans
        self.public_pool_workers = public_pool_workers
        self.storage_space = storage_space
        self.data_retention_limit = data_retention_limit
        self.tasks_count = tasks_count
        self.tasks_executions = tasks_executions
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
            statistic.tasks_executions = 0
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


def _update_quota(name, project_id, performance_test_runs, ui_performance_test_runs, sast_scans, dast_scans,
                  public_pool_workers, storage_space, data_retention_limit, tasks_count,
                  tasks_executions):
    quota = ProjectQuota.query.filter_by(project_id=project_id).first()
    if quota:
        quota.update(name=name, performance_test_runs=performance_test_runs, sast_scans=sast_scans,
                     ui_performance_test_runs=ui_performance_test_runs, dast_scans=dast_scans,
                     public_pool_workers=public_pool_workers, storage_space=storage_space,
                     data_retention_limit=data_retention_limit, tasks_count=tasks_count,
                     tasks_executions=tasks_executions)
    else:
        quota = ProjectQuota(name=name, project_id=project_id, performance_test_runs=performance_test_runs,
                             ui_performance_test_runs=ui_performance_test_runs, sast_scans=sast_scans,
                             dast_scans=dast_scans, public_pool_workers=public_pool_workers,
                             storage_space=storage_space, data_retention_limit=data_retention_limit,
                             tasks_count=tasks_count, tasks_executions=tasks_executions)
        quota.insert()
    return quota


def basic(project_id):
    return _update_quota(name="basic",
                         project_id=project_id,
                         performance_test_runs=10,
                         ui_performance_test_runs=10,
                         sast_scans=10,
                         dast_scans=1,
                         public_pool_workers=-1,
                         storage_space=100,
                         data_retention_limit=30,
                         tasks_count=3,
                         tasks_executions=250)


def startup(project_id):
    return _update_quota(name="startup",
                         project_id=project_id,
                         performance_test_runs=100,
                         ui_performance_test_runs=100,
                         sast_scans=100,
                         dast_scans=20,
                         public_pool_workers=-1,
                         storage_space=500,
                         data_retention_limit=90,
                         tasks_count=5,
                         tasks_executions=1000)


def professional(project_id):
    return _update_quota(name="professional",
                         project_id=project_id,
                         performance_test_runs=1000,
                         ui_performance_test_runs=1000,
                         sast_scans=1000,
                         dast_scans=100,
                         public_pool_workers=-1,
                         storage_space=1000,
                         data_retention_limit=180,
                         tasks_count=10,
                         tasks_executions=-1)


def enterprise(project_id):
    return _update_quota(name="enterprise",
                         project_id=project_id,
                         performance_test_runs=-1,
                         ui_performance_test_runs=-1,
                         sast_scans=-1,
                         dast_scans=-1,
                         public_pool_workers=-1,
                         storage_space=-1,
                         data_retention_limit=-1,
                         tasks_count=-1,
                         tasks_executions=-1)


def custom(project_id, performance_test_runs, ui_performance_test_runs,  sast_scans, dast_scans, public_pool_workers, storage_space,
           data_retention_limit, tasks_count, tasks_executions):
    return _update_quota(name="custom",
                         project_id=project_id,
                         performance_test_runs=performance_test_runs,
                         ui_performance_test_runs=ui_performance_test_runs,
                         sast_scans=sast_scans,
                         dast_scans=dast_scans,
                         public_pool_workers=public_pool_workers,
                         storage_space=storage_space,
                         data_retention_limit=data_retention_limit,
                         tasks_count=tasks_count,
                         tasks_executions=tasks_executions)
