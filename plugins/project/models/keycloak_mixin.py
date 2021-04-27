from abc import abstractmethod, abstractclassmethod
from typing import Optional

from flask import current_app
from pylon.core.tools import log
from sqlalchemy import Column, String

from plugins.auth_manager.models.api_response_pd import ApiResponse
from plugins.auth_manager.models.group_pd import GroupRepresentation
from plugins.base.models.abstract_base import AbstractBaseMixin


def mock_user_session_id():
    from flask import session
    return session.get('auth_attributes', {}).get('sub')


class KeycloakMixin:
    _rpc = None
    REALM = 'carrier'

    @property
    def rpc(self):
        if not self._rpc:
            self._rpc = current_app.config["CONTEXT"].rpc_manager
        return self._rpc

    _keycloak_group_id = Column('keycloak_group_id', String(64), unique=True, nullable=True,)

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError

    @property
    def token(self):
        return self.rpc.call.auth_manager_get_token()

    def keycloak_search_group(self) -> Optional[str]:
        log.debug('Getting id using search method')
        response = self.rpc.call.auth_manager_get_groups(
            realm=self.REALM,
            token=self.token,
            search=self.id
        )
        if response.success:
            for found_group in response.data:
                if str(found_group.name) == str(self.id):
                    self.keycloak_group_id = found_group.id
                    return self._keycloak_group_id
        log.warning(f'Group for project {self.name} is not found in keycloak')
        return None

    @property
    def keycloak_group_id(self) -> str:
        if self._keycloak_group_id:
            return self._keycloak_group_id
        if not self.keycloak_search_group():
            self.keycloak_create_group()
        return self._keycloak_group_id

    @keycloak_group_id.setter
    def keycloak_group_id(self, value: str):
        self._keycloak_group_id = value
        AbstractBaseMixin.insert(self)

    @property
    def keycloak_group_representation_offline(self) -> GroupRepresentation:
        group = GroupRepresentation(
            name=str(self.id),
            attributes={'project_name': [self.name]}
        )
        if self._keycloak_group_id:
            group.id = self._keycloak_group_id
        return group

    def keycloak_create_group(self) -> ApiResponse:
        response = self.rpc.call.auth_manager_post_group(
            realm=self.REALM,
            token=self.token,
            group=self.keycloak_group_representation_offline,
        )
        if response.success:
            log.debug(f'Group {response.data.id} for project {self.name} successfully created')
            self.keycloak_group_id = response.data.id
            self.keycloak_add_current_user_to_group()
        return response

    def keycloak_add_current_user_to_group(self) -> None:
        self.rpc.call.auth_manager_add_users_to_groups(
            realm=self.REALM,
            token=self.token,
            users=[mock_user_session_id()],
            groups=[self.keycloak_group_id],
        )

    def invite_user(self, username: Optional[str] = None, email: Optional[str] = None):
        raise NotImplementedError
