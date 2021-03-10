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
import operator
from json import loads
from sqlalchemy import and_
from flask_restful import Api, Resource, reqparse
from plugins.base.connectors.minio import MinioClient
from werkzeug.exceptions import Forbidden


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    return False


def build_req_parser(rules: tuple, location=("json", "values")) -> reqparse.RequestParser:
    request_parser = reqparse.RequestParser()
    for rule in rules:
        if isinstance(rule, dict):
            kwargs = rule.copy()
            name = kwargs["name"]
            del kwargs["name"]
            if "location" not in kwargs:
                # Use global location unless it"s specified by the rule.
                kwargs["location"] = location
            request_parser.add_argument(name, **kwargs)

        elif isinstance(rule, (list, tuple)):
            name, _type, required, default = rule
            kwargs = {
                "type": _type,
                "location": location,
                "required": required
            }
            if default is not None:
                kwargs["default"] = default
            request_parser.add_argument(name, **kwargs)

    return request_parser


def add_resource_to_api(api: Api, resource: Resource, *urls, **kwargs) -> None:
    # This /api/v1 thing is made here to be able to register auth endpoints for local development
    urls = (*(f"/api/v2{url}" for url in urls), *(f"/api/v2{url}/" for url in urls))
    api.add_resource(resource, *urls, **kwargs)


def _calcualte_limit(limit, total):
    return len(total) if limit == 'All' else limit


def get(project_id, args, data_model, additional_filter=None):
    from flask import current_app
    project = current_app.context.rpc_manager.call_function('project_get_ot_404', project_id=project_id)
    limit_ = args.get("limit")
    offset_ = args.get("offset")
    if args.get("sort"):
        sort_rule = getattr(getattr(data_model, args["sort"]), args["order"])()
    else:
        sort_rule = data_model.id.desc()
    filter_ = list()
    filter_.append(operator.eq(data_model.project_id, project["id"]))
    if additional_filter:
        for key, value in additional_filter.items():
            filter_.append(operator.eq(getattr(data_model, key), value))
    if args.get('filter'):
        for key, value in loads(args.get("filter")).items():
            filter_.append(operator.eq(getattr(data_model, key), value))
    filter_ = and_(*tuple(filter_))
    total = data_model.query.order_by(sort_rule).filter(filter_).count()
    res = data_model.query.filter(filter_).order_by(sort_rule).limit(
        _calcualte_limit(limit_, total)).offset(offset_).all()
    return total, res


def upload_file(bucket, f, project, create_if_not_exists=True):
    name = f.filename
    content = f.read()
    f.seek(0, 2)
    file_size = f.tell()
    try:
        f.remove()
    except:
        pass
    from flask import current_app
    storage_space_quota = current_app.context.rpc_manager.call_function(
        'project_get_storage_space_quota',
        project_id=project['id']
    )
    statistic = current_app.context.rpc_manager.call_function('project_statistics', project_id=project['id'])

    if storage_space_quota != -1 and statistic['storage_space'] + file_size > storage_space_quota * 1000000:
        raise Forbidden(description="The storage space limit allowed in the project has been exceeded")
    if create_if_not_exists:
        if bucket not in MinioClient(project=project).list_bucket():
            MinioClient(project=project).create_bucket(bucket)
    MinioClient(project=project).upload_file(bucket, content, name)
