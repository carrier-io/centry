from abc import abstractmethod
from typing import Optional

from flask import current_app
from pylon.core.tools import log
from sqlalchemy import Column, JSON
from sqlalchemy.ext.mutable import MutableDict

from plugins.auth_manager.models.api_response_pd import ApiResponse
from plugins.auth_manager.models.group_pd import GroupRepresentation
from plugins.base.models.abstract_base import AbstractBaseMixin


def current_user_id():
    from flask import session
    return session.get('auth_attributes', {}).get('sub')


class KeycloakMixin:
    _rpc = None
    REALM = 'carrier'
    MAIN_GROUP_NAME = 'main'
    REDIS_DB = 7

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError

    @property
    def rpc(self):
        if not self._rpc:
            self._rpc = current_app.config["CONTEXT"].rpc_manager
        return self._rpc

    # _keycloak_group_id = Column('keycloak_group_id', String(64), unique=True, nullable=True,)
    keycloak_groups = Column('keycloak_groups', MutableDict.as_mutable(JSON), nullable=False, default={})

    @property
    def token(self):
        return self.rpc.call.auth_manager_get_token()

    def keycloak_search_main_group(self) -> Optional[str]:
        log.debug('Getting id using search method')
        print('Getting id using search method')
        response = self.rpc.call.auth_manager_get_groups(
            realm=self.REALM,
            token=self.token,
            search=self.id,
            with_members=False
        )
        if response.success:
            for found_group in response.data:
                if str(found_group.name) == str(self.id):
                    # self.keycloak_group_id = found_group.id
                    # return self._keycloak_group_id
                    self.update_from_response(found_group)
                    return self.keycloak_get_group_id(self.MAIN_GROUP_NAME)
        log.warning(f'Group for project {self.name} is not found in keycloak')
        return None

    def update_from_response(self, group_data: GroupRepresentation) -> None:
        print(group_data, type(group_data))
        self.keycloak_groups[self.MAIN_GROUP_NAME] = group_data.id
        for subgroup in group_data.subGroups:
            self.keycloak_groups[subgroup.name] = subgroup.id
        AbstractBaseMixin.insert(self)

    def keycloak_get_group_id(self, group_name: str, recursion_prevent: bool = False):
        print('keycloak_get_group_id', group_name)
        print(self.keycloak_groups)
        try:
            return self.keycloak_groups[group_name]
        except KeyError:
            if group_name == self.MAIN_GROUP_NAME:
                if not self.keycloak_search_main_group():
                    self.keycloak_create_main_group()
            else:
                self.keycloak_update_group_info()
                try:
                    self.keycloak_groups[group_name]
                except KeyError:
                    if recursion_prevent:
                        log.critical(f'Recursion on creating subgroup {group_name}')
                        return
                    return self.create_subgroup(group_name)

    def create_subgroup(self, name):
        response = self.rpc.call.auth_manager_add_subgroup(
            realm=self.REALM,
            token=self.token,
            parent=self.keycloak_group_representation_offline(),
            child=self.keycloak_group_representation_offline(name),
        )
        if response.success:
            if response.status == 201:
                self.set_group(name, response.data.id)
        else:
            log.critical(f'Error creating subgroup {response.error}')
            return None
        return self.keycloak_get_group_id(name, recursion_prevent=True)

    def keycloak_update_group_info(self):
        print(self.keycloak_group_representation_offline())
        response = self.rpc.call.auth_manager_get_groups(
            realm=self.REALM,
            token=self.token,
            with_members=False,
            group_or_id=self.keycloak_group_representation_offline(),
            response_debug_processor=lambda r: r.url
        )
        if response.success:
            print(response)
            self.update_from_response(response.data)
        else:
            log.critical(f'Error updating group info {response.error}')

    def keycloak_group_representation_offline(self, keycloak_group_name: str = None, **kwargs) -> GroupRepresentation:
        is_main_group = not keycloak_group_name or keycloak_group_name == self.MAIN_GROUP_NAME
        repr_name = id_key = keycloak_group_name
        if is_main_group:
            repr_name, id_key = self.id, self.MAIN_GROUP_NAME
        group = GroupRepresentation(
            name=str(repr_name),
            attributes={'project_name': [self.name], self.MAIN_GROUP_NAME: [is_main_group]},
            **kwargs
        )
        try:
            print('$$'*55)
            print(self.keycloak_groups)
            print(type(self.keycloak_groups))
            group.id = self.keycloak_groups[id_key]
        except KeyError:
            pass
        return group

    def set_group(self, name: str, group_keycloak_id: str):
        print('SETTING group', name, group_keycloak_id)
        self.keycloak_groups[name] = group_keycloak_id
        AbstractBaseMixin.insert(self)

    def keycloak_create_main_group(self) -> ApiResponse:
        print('CREATE CALLEDx')
        response = self.rpc.call.auth_manager_post_group(
            realm=self.REALM,
            token=self.token,
            group=self.keycloak_group_representation_offline(self.id),
        )
        if response.success:
            log.debug(f'Group {response.data.id} for project {self.name} successfully created')
            print(f'Group {response.data.id} for project {self.name} successfully created')
            self.set_group(self.MAIN_GROUP_NAME, response.data.id)
            self.keycloak_add_current_user_to_group(self.keycloak_get_group_id(self.MAIN_GROUP_NAME))
        return response

    def keycloak_add_current_user_to_group(self, group_id: str) -> None:
        self.rpc.call.auth_manager_add_users_to_groups(
            realm=self.REALM,
            token=self.token,
            users=[current_user_id()],
            groups=[group_id],
        )

    # def join_url(self):
    #     uid = uuid.uuid4()
    #     key = f'join_url:{uid}'
    #     with Redis(db=self.REDIS_DB) as redis_client:
    #         redis_client.set(key, self.id, 60 * 60)
    #     return url_for('customers:view', args=[uid])

    def invite_user(self, username: Optional[str] = None, email: Optional[str] = None):
        raise NotImplementedError
