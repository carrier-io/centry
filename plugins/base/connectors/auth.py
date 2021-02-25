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

from functools import wraps
from typing import Optional

from flask import session, redirect, url_for, request
from werkzeug.exceptions import NotFound
from requests import get
from plugins.base.constants import APP_HOST, LOCAL_DEV

from plugins.base.config import Config


class SessionProject:
    PROJECT_CACHE_KEY = Config().PROJECT_CACHE_KEY

    @staticmethod
    def set(project_id: int) -> None:
        session[SessionProject.PROJECT_CACHE_KEY] = project_id

    @staticmethod
    def pop() -> Optional[int]:
        return session.pop(SessionProject.PROJECT_CACHE_KEY, default=None)

    @staticmethod
    def get() -> Optional[int]:
        return session.get(SessionProject.PROJECT_CACHE_KEY)


class SessionUser:
    USER_CACHE_KEY = Config().USER_CACHE_KEY

    @staticmethod
    def set(user_session: dict) -> None:
        session[SessionUser.USER_CACHE_KEY] = user_session

    @staticmethod
    def pop() -> Optional[int]:
        return session.pop(SessionUser.USER_CACHE_KEY, default=None)

    @staticmethod
    def get() -> Optional[int]:
        return session.get(SessionUser.USER_CACHE_KEY)


def superadmin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if is_superadmin():
            try:
                return func(*args, **kwargs)
            except NotFound:
                ...
        return redirect(url_for("projects.list"))

    return decorated_function


def project_required(func):
    from plugins.project.models.project import Project

    @wraps(func)
    def decorated_function(*args, **kwargs):
        project_id = SessionProject.get()
        if is_user_part_of_the_project(project_id):
            try:
                project = Project.query.get_or_404(project_id)
                return func(project, *args, **kwargs)
            except NotFound:
                ...

        return redirect(url_for("projects.list"))

    return decorated_function


def filter_projects(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if is_superadmin():
            try:
                return func(only_users_projects(), *args, **kwargs)
            except NotFound:
                ...
        return redirect(url_for("projects.list"))
    return decorated_function


def _get_user_data():
    if LOCAL_DEV:
        return {"groups": ["/superadmin"]}
    user_data = SessionUser.get()
    if not user_data:
        headers = {}
        for header in request.headers:
            if header[0].lower() in ["cookie", "authorization"]:
                headers[header[0]] = header[1]
        headers["Content-Type"] = "application/json"
        user_data = get(f"{APP_HOST}/forward-auth/me", headers=headers).json()
    return user_data


def only_users_projects():
    user_data = _get_user_data()
    project = []
    for group in user_data["groups"]:
        group = group.split("/")[1]
        try:
            group = int(group)
        except:
            group = group.replace("superadmin", "all")
        project.append(group)
    return project


def is_superadmin():
    if LOCAL_DEV:
        return True
    user_data = _get_user_data()
    if Config().SUPERADMIN_GROUP in user_data["groups"]:
        return True
    return False


def is_user_part_of_the_project(project_id):
    user_data = _get_user_data()
    if Config().SUPERADMIN_GROUP in user_data["groups"]:
        return True
    else:
        # check permission
        if f"/{project_id}" in user_data["groups"]:
            return True
    return False
