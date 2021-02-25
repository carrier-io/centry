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

import logging
from typing import Optional
from flask import abort
from sqlalchemy import String, Column, Integer, JSON, Boolean, and_

from plugins.base.models.abstract_base import AbstractBaseMixin
from plugins.base.db_manager import Base, db_session
from plugins.base.connectors.auth import SessionProject, is_user_part_of_the_project, only_users_projects


class Project(AbstractBaseMixin, Base):
    __tablename__ = "project"

    API_EXCLUDE_FIELDS = ("secrets_json", "worker_pool_config_json")

    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=False)
    project_owner = Column(String(256), unique=False)
    secrets_json = Column(JSON, unique=False, default={})
    worker_pool_config_json = Column(JSON, unique=False, default={})
    package = Column(String, nullable=False, default="basic")
    dast_enabled = Column(Boolean, nullable=False, default=False)
    sast_enabled = Column(Boolean, nullable=False, default=False)
    performance_enabled = Column(Boolean, nullable=False, default=False)

    def insert(self) -> None:
        super().insert()
        from plugins.base.connectors.minio import MinioClient
        MinioClient(project=self).create_bucket(bucket="reports")
        MinioClient(project=self).create_bucket(bucket="tasks")

    def used_in_session(self):
        selected_id = SessionProject.get()
        return self.id == selected_id

    def to_json(self, exclude_fields: tuple = ()) -> dict:
        json_data = super().to_json(exclude_fields=exclude_fields)
        json_data["used_in_session"] = self.used_in_session()
        return json_data

    def get_data_retention_limit(self) -> Optional[int]:
        from .quota import ProjectQuota
        project_quota = ProjectQuota.query.filter_by(project_id=self.id).first()
        if project_quota and project_quota.data_retention_limit:
            return project_quota.data_retention_limit

    @staticmethod
    def get_storage_space_quota(project_id):
        from .quota import ProjectQuota
        project_quota = ProjectQuota.query.filter_by(project_id=project_id).first()
        if project_quota and project_quota.storage_space:
            return project_quota.storage_space

    @staticmethod
    def get_or_404(project_id):
        project = Project.query.get_or_404(project_id)
        if not is_user_part_of_the_project(project.id):
            abort(404, description="User not a part of project")
        return project.to_json()

    @staticmethod
    def list_projects(project_id=None, search_=None, limit_=None, offset_=None):
        allowed_project_ids = only_users_projects()
        _filter = None
        if "all" not in allowed_project_ids:
            _filter = Project.id.in_(allowed_project_ids)
        if project_id:
            project = Project.get_or_404(project_id)
            return project.to_json(exclude_fields=Project.API_EXCLUDE_FIELDS), 200
        elif search_:
            filter_ = Project.name.ilike(f"%{search_}%")
            if _filter is not None:
                filter_ = and_(_filter, filter_)
            projects = Project.query.filter(filter_).limit(limit_).offset(offset_).all()
        else:
            if _filter is not None:
                projects = Project.query.filter(_filter).limit(limit_).offset(offset_).all()
            else:
                projects = Project.query.limit(limit_).offset(offset_).all()
        return [project.to_json(exclude_fields=Project.API_EXCLUDE_FIELDS) for project in projects]

    # TODO: think on how to get that back
    # @classmethod
    # def apply_full_delete_by_pk(cls, pk: int) -> None:
    #     import docker
    #     import psycopg2
    #
    #     from galloper.processors.minio import MinioClient
    #
    #     from galloper.database.models.task_results import Results
    #     from galloper.database.models.task import Task
    #     from galloper.database.models.security_results import SecurityResults
    #     from galloper.database.models.security_reports import SecurityReport
    #     from galloper.database.models.security_details import SecurityDetails
    #     from galloper.database.models.api_reports import APIReport
    #     from galloper.database.models.api_release import APIRelease
    #     from galloper.database.models.performance_tests import PerformanceTests
    #     from galloper.database.models.ui_report import UIReport
    #     from galloper.database.models.ui_result import UIResult
    #     from galloper.database.models.statistic import Statistic
    #     from galloper.database.models.project_quota import ProjectQuota
    #
    #
    #     _logger = logging.getLogger(cls.__name__.lower())
    #     _logger.info("Start deleting entire project within transaction")
    #
    #     project = cls.query.get_or_404(pk)
    #     minio_client = MinioClient(project=project)
    #     docker_client = docker.from_env()
    #     buckets_for_removal = minio_client.list_bucket()
    #
    #     db_session.query(Project).filter_by(id=pk).delete()
    #     for model_class in (
    #         Results, SecurityResults, SecurityReport, SecurityDetails, APIRelease
    #     ):
    #         db_session.query(model_class).filter_by(project_id=pk).delete()
    #
    #
    #     for api_report in APIReport.query.filter_by(project_id=pk).all():
    #         api_report.delete(commit=False)
    #
    #     task_ids = []
    #     for task in Task.query.filter_by(project_id=pk).all():
    #         task_ids.append(task.task_id)
    #         task.delete(commit=False)
    #
    #     for test in PerformanceTests.query.filter_by(project_id=pk).all():
    #         test.delete(commit=False)
    #
    #     for result in UIResult.query.filter_by(project_id=pk).all():
    #         result.delete(commit=False)
    #
    #     for result in UIReport.query.filter_by(project_id=pk).all():
    #         result.delete(commit=False)
    #
    #     for stats in Statistic.query.filter_by(project_id=pk).all():
    #         stats.delete(commit=False)
    #
    #     for quota in ProjectQuota.query.filter_by(project_id=pk).all():
    #         quota.delete(commit=False)
    #
    #     try:
    #         db_session.flush()
    #     except (psycopg2.DatabaseError,
    #             psycopg2.DataError,
    #             psycopg2.ProgrammingError,
    #             psycopg2.OperationalError,
    #             psycopg2.IntegrityError,
    #             psycopg2.InterfaceError,
    #             psycopg2.InternalError,
    #             psycopg2.Error) as exc:
    #         db_session.rollback()
    #         _logger.error(str(exc))
    #     else:
    #         db_session.commit()
    #         for bucket in buckets_for_removal:
    #             minio_client.remove_bucket(bucket=bucket)
    #         for task_id in task_ids:
    #             try:
    #                 volume = docker_client.volumes.get(task_id)
    #             except docker.errors.NotFound as docker_exc:
    #                 _logger.info(str(docker_exc))
    #             else:
    #                 volume.remove(force=True)
    #         _logger.info("Project successfully deleted!")
    #
    #     selected_project_id = SessionProject.get()
    #     if pk == selected_project_id:
    #         SessionProject.pop()
