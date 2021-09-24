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


from typing import Optional, List

from flask_restful import Resource

from flask import request, make_response, jsonify
from pydantic import ValidationError, parse_obj_as
from requests import Response
from ..models.integration import Integration
from ..models.integration_pd import IntegrationPD

from ...shared.utils.rpc import RpcMixin


# class CheckConnectionApi(Resource, RpcMixin):
#     def post(self, integration_name: str, **kwargs) -> Response:
#         print('POST', integration_name)
#         integration = self.rpc.call.integrations_get_integration(integration_name)
#         if not integration:
#             return make_response({'error': 'integration not found'}, 404)
#         try:
#             settings = integration.settings_model.parse_obj(request.json)
#         except ValidationError as e:
#             return make_response(e.json(), 400)
#         print('settings', settings)
#         print(integration)
#         print(request.json)
#         if not settings.check_connection():
#             return make_response({'check_connection': False}, 400)


class IntegrationsApi(Resource, RpcMixin):
    def get(self, project_id: int, **kwargs) -> Response:
        results = Integration.query.filter(Integration.project_id == project_id).all()
        results = parse_obj_as(List[IntegrationPD], results)
        return make_response(jsonify([i.dict() for i in results]), 200)

    # @BaseResource.check_token
    # def put(self, realm: str, user_id: str, **kwargs) -> Response:
    #     user = UserRepresentation.parse_obj(request.json)
    #     user.id = user_id
    #
    #     # todo: if not debug remove response_debug_processor
    #     if 'response_debug_processor' not in kwargs:
    #         kwargs['response_debug_processor'] = lambda r: {
    #             'status_code': r.status_code,
    #             'updating_fields': user.dict(exclude_unset=True)
    #         }
    #     response = put_entity(
    #         base_url=self.settings['keycloak_urls']['user'],
    #         realm=realm,
    #         token=self.token,
    #         entity=user,
    #         **kwargs
    #     )
    #     return make_response(response.dict(), response.status)

    def post(self, integration_name: str, **kwargs) -> Response:
        print('POST', integration_name)
        integration = self.rpc.call.integrations_get_integration(integration_name)
        if not integration:
            return make_response({'error': 'integration not found'}, 404)
        try:
            settings = integration.settings_model.parse_obj(request.json)
        except ValidationError as e:
            return make_response(e.json(), 400)


        print('settings', settings)
        print(integration)

        print('KSA', request.json.get('save_action'))
        print('request.json', request.json)
        check_connection_response = settings.check_connection()
        if not request.json.get('save_action'):
            return make_response(
                jsonify([{'loc': ['check_connection'], 'msg': 'Connection failed'}]),
                200 if check_connection_response else 400
            )

        db_integration = Integration(
            name=integration_name,
            project_id=request.json.get('project_id'),
            settings=settings.dict(),
            section=integration.section

        )
        print('%'*55)
        print(db_integration)
        db_integration.insert()
        return IntegrationPD.from_orm(db_integration).dict()
        # return db_integration.to_json(exclude_fields=('password', ))


        # user = UserRepresentation.parse_obj(request.json)
        # response = post_entity(
        #     base_url=self.settings['keycloak_urls']['user'],
        #     realm=realm,
        #     token=self.token,
        #     entity=user,
        #     **kwargs
        # )
        # return make_response(response.dict(), response.status)



    # @BaseResource.check_token
    # def delete(self, realm: str, user_id: str, **kwargs) -> Response:
    #     response = delete_entity(
    #         base_url=self.settings['keycloak_urls']['user'],
    #         realm=realm,
    #         token=self.token,
    #         entity_or_id=user_id,
    #         **kwargs
    #     )
    #     return make_response(response.dict(), response.status)
