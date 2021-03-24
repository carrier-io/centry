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
from sqlalchemy import String, Column, Integer, JSON, ARRAY, Text, and_

from plugins.base.models.abstract_base import AbstractBaseMixin
from plugins.base.db_manager import Base, db_session
from plugins.base.connectors.auth import SessionProject, is_user_part_of_the_project, only_users_projects

def user_is_project_admin():
    # this one need to be implemented in user permissions
    return True

def user_is_project_contributor():
    # this one need to be implemented in user permissions
    return True

def user_is_project_viewer():
    # this one need to be implemented in user permissions
    return True

def whomai():
    # Get user name from session
    return "User"

def get_project_integrations():
    # Get user name from project_intergations_config
    return ["rp", "ado", "email"]

def get_user_projects():
    # List of groups/projects user is part of
    return [{"name": "PMI", "id": 1}, {"name": "Alfresco", "id": 2}, {"name": "Verifone 2Checkout", "id": 3}]

def last_visited_chapter():
    return "Performance"

def get_active_project():
    return SessionProject.get()


class Project(AbstractBaseMixin, Base):
    __tablename__ = "project"

    API_EXCLUDE_FIELDS = ("secrets_json", "worker_pool_config_json")

    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=False)
    project_owner = Column(String(256), unique=False)
    secrets_json = Column(JSON, unique=False, default={})
    worker_pool_config_json = Column(JSON, unique=False, default={})
    plugins = Column(ARRAY(Text), unique=False, default={})

    def insert(self) -> None:
        super().insert()
        from plugins.base.connectors.minio import MinioClient
        MinioClient(project=self).create_bucket(bucket="reports")
        MinioClient(project=self).create_bucket(bucket="tasks")
        SessionProject.set(self.id)

    def used_in_session(self):
        selected_id = SessionProject.get()
        return self.id == selected_id

    def to_json(self, exclude_fields: tuple = ()) -> dict:
        json_data = super().to_json(exclude_fields=exclude_fields)
        # json_data["used_in_session"] = self.used_in_session()
        json_data["chapters"] = self.compile_chapters()
        json_data["username"] = whomai()
        json_data["projects"] = get_user_projects()
        json_data["integrations"] = get_project_integrations()
        json_data["regions"] = self.worker_pool_config_json.get("regions", ["default"])
        json_data["default_chapter"] = last_visited_chapter()
        return json_data

    def compile_chapters(self):
        chapters = []
        if user_is_project_admin():
            chapters.append({
                "title": "Configuration", "link": "?chapter=Configuration&module=Tasks&page=list",
                "nav": [
                    {"title": "Users", "link": "?chapter=Configuration&module=Users&page=all"},
                    {"title": "Quotas", "link": "?chapter=Configuration&module=Quotas&page=all"},
                    {"title": "Tasks", "link": "?chapter=Configuration&module=Tasks&page=list", "active": True},
                    {"title": "Secrets", "link": "?chapter=Configuration&module=Secrets&page=list"},
                    {"title": "Artifacts", "link": "?chapter=Configuration&module=Artifacts&page=list"},
                    {"title": "Integrations", "link": "?chapter=Configuration&module=Integrations&page=all"},
                    {"title": "Plugins", "link": "?chapter=Configuration&module=Plugins&page=all"}
                ]
            })
        if 'dashboards' in self.plugins:
            chapters.append({
                "title": "Portfolio", "link": "?chapter=Portfolio",
                "nav": [
                    {"title": "Dashboards", "link": "?chapter=Portfolio&module=Dashboards&page=all", "active": True},
                    {"title": "Data Explorer", "link": "?chapter=Portfolio&module=Data%20Explorer&page=all"},
                    {"title": "Create Portfolio", "link": "?chapter=Portfolio&module=Create%20Portfolio&page=all"},
                ]
            })
        if any( plugin in ["backend", "visual"] for plugin in self.plugins):
            nav = [{"title": "Overview", "link": "?chapter=Performance&module=Overview&page=overview", "active": True}]
            if "backend" in self.plugins:
                nav.append({"title": "Backend", "link": "?chapter=Performance&module=Backend&page=list"})
            if "visual" in self.plugins:
                nav.append({"title": "Visual", "link": "?chapter=Performance&module=Visual&page=visual"})
            nav.append({"title": "Results", "link": "?chapter=Performance&module=Results&page=reports"})
            nav.append({"title": "Thresholds", "link": "?chapter=Performance&module=Thresholds&page=thresholds"})
            chapters.append({"title": "Performance", "link": "?chapter=Performance", "nav": nav})
        if any (plugin in ["cloud", "infra", "code", "application"] for plugin in self.plugins):
            nav = [{"title": "Overview", "link": "?chapter=Security&module=Overview&page=overview", "active": True}]
            if "code" in self.plugins:
                nav.append({"title": "Code", "link": "?chapter=Security&module=Code&page=list"})
            if "application" in self.plugins:
                nav.append({"title": "App", "link": "?chapter=Security&module=App&page=list"})
            if "cloud" in self.plugins:
                nav.append({"title": "Cloud", "link": "?chapter=Security&module=Cloud&page=list"})
            if "infra" in self.plugins:
                nav.append({"title": "Infra", "link": "?chapter=Security&module=Infra&page=list"})
            nav.append({"title": "Results", "link": "?chapter=Security&module=Results&page=all"})
            nav.append({"title": "Thresholds", "link": "?chapter=Security&module=Thresholds&page=all"})
            nav.append({"title": "Bug Bar", "link": "?chapter=Security&module=Bugbar&page=all"})
            chapters.append({"title": "Security", "link": "?chapter=Security", "nav": nav})
        return chapters

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
    def get_or_404(project_id, exclude_fields=()):
        project = Project.query.get_or_404(project_id)
        if not is_user_part_of_the_project(project.id):
            abort(404, description="User not a part of project")
        return project

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
