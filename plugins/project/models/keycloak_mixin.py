from abc import abstractmethod
from typing import Optional

from flask import current_app
from pydantic import BaseModel
from pylon.core.tools import log
from sqlalchemy import Column, JSON
from sqlalchemy.ext.mutable import MutableDict

from plugins.auth_manager.models.api_response_pd import ApiResponse
from plugins.auth_manager.models.group_pd import GroupRepresentation
from plugins.base.models.abstract_base import AbstractBaseMixin


def current_user_id() -> str:
    from flask import session
    return session['auth_attributes']['sub']


def current_user_email() -> str:
    from flask import session
    return session['auth_attributes']['email']


class KeycloakMixin:
    _rpc = None
    REALM = 'carrier'


    MAIN_GROUP_NAME = 'owner'
    SUBGROUP_NAMES = ['maintainer', 'analyst']

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

    keycloak_groups = Column('keycloak_groups', MutableDict.as_mutable(JSON), nullable=False, default={})

    @property
    def token(self):
        return self.rpc.call.auth_manager_get_token()

    def _search_main_group(self) -> Optional[str]:
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
                    self._refresh_main_group_from_keycloak(found_group)
                    return self.get_group_id(self.MAIN_GROUP_NAME)
        log.warning(f'Group for project {self.name} is not found in keycloak')
        return None

    def _refresh_main_group_from_keycloak(self, group_data: GroupRepresentation) -> None:
        print(group_data, type(group_data))
        self.keycloak_groups[self.MAIN_GROUP_NAME] = group_data.id
        for subgroup in group_data.subGroups:
            self.keycloak_groups[subgroup.name] = subgroup.id
        AbstractBaseMixin.insert(self)

    def get_group_id(self, group_name: str, recursion_prevent: bool = False):
        print('keycloak_get_group_id', group_name)
        print(self.keycloak_groups)
        try:
            return self.keycloak_groups[group_name]
        except KeyError:
            if group_name == self.MAIN_GROUP_NAME:
                if not self._search_main_group():
                    self.create_main_group()
            else:
                self.update_group_info()
                try:
                    self.keycloak_groups[group_name]
                except KeyError:
                    if recursion_prevent:
                        log.critical(f'Recursion on creating subgroup {group_name}')
                        return
                    return self.create_subgroup(group_name)

    def create_subgroup(self, name: str) -> Optional[str]:
        response = self.rpc.call.auth_manager_add_subgroup(
            realm=self.REALM,
            token=self.token,
            parent=self.get_group_representation_offline(),
            child=self.get_group_representation_offline(name),
        )
        print('RDRDRDR', self.get_group_id(self.MAIN_GROUP_NAME))
        if response.success:
            if response.status == 201:
                print('RDRDRDR', response.data,)
                print('RDRDRDR', type(response.data))
                self.map_group_by_id(name, response.data.id)
        else:
            print(response)
            log.critical(f'Error creating subgroup {response.error}')
            return None
        return self.get_group_id(name, recursion_prevent=True)

    def update_group_info(self):
        print(self.get_group_representation_offline())
        response = self.rpc.call.auth_manager_get_groups(
            realm=self.REALM,
            token=self.token,
            with_members=False,
            group_or_id=self.get_group_representation_offline(),
            # response_debug_processor=lambda r: r.url
        )
        if response.success:
            print(response)
            self._refresh_main_group_from_keycloak(response.data)
        else:
            log.critical(f'Error updating group info {response.error}')

    def get_group_representation_offline(self, keycloak_group_name: str = None, **kwargs) -> GroupRepresentation:
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

    def map_group_by_id(self, name: str, group_keycloak_id: str):
        print('SETTING group', name, group_keycloak_id)
        self.keycloak_groups[name] = group_keycloak_id
        AbstractBaseMixin.insert(self)

    def create_main_group(self) -> ApiResponse:
        print('CREATE CALLEDx')
        response = self.rpc.call.auth_manager_post_group(
            realm=self.REALM,
            token=self.token,
            group=self.get_group_representation_offline(self.id),
        )
        if response.success:
            log.debug(f'Group {response.data.id} for project {self.name} successfully created')
            print(f'Group {response.data.id} for project {self.name} successfully created')
            self.map_group_by_id(self.MAIN_GROUP_NAME, response.data.id)
            self.add_current_user_to_group(self.get_group_id(self.MAIN_GROUP_NAME))
        return response

    def add_current_user_to_group(self, group_id: str) -> None:
        self.rpc.call.auth_manager_add_users_to_groups(
            realm=self.REALM,
            token=self.token,
            users=[current_user_id()],
            groups=[group_id],
        )


    def create_subgroups(self):
        for g in self.SUBGROUP_NAMES:
            subgroup_id = self.create_subgroup(g)
            print('SUBGROUP created', subgroup_id)

    def send_invitations(self, invitations):
        for i in invitations:
            print(i)
            Invitation.__tmp_invite(i)
            # self.get_group_id()



class InvitationModel(BaseModel):
    project_id: int
    group_name: str
    group_id: str
    email: str


import json
import uuid
from redis import Redis
from flask import url_for
from plugins.base.constants import REDIS_PASSWORD, REDIS_USER, REDIS_HOST, REDIS_PORT


class Invitation:
    REDIS_DB = 7
    MODEL = InvitationModel
    PREFIX = 'join_url'
    DELIMITER = ':'
    EXPIRE = 60 * 60

    def redis_encoder(self, data):
        return json.dumps(data)

    # def __init__(self, project_id):
    #     super().__init__()




    def __tmp_invite(self, subgroup_id):
        url = self.make_join_url(subgroup_id)
        from pathlib import Path
        folder_path = Path(f'/home/aspect/PycharmProjects/centry/tmp/emails/{self.project_id}')
        folder_path.mkdir(parents=True, exist_ok=True)
        with open(f'{folder_path}/{g}.txt', 'w') as out:
            out.write(f'This is an invitational email for project:\n{self.project_id}\nfor group:\n{g}\n{url}')

    def make_join_url(self, group_id: str, email: str = None):
        uid = uuid.uuid4()
        key = f'{self.PREFIX}{self.DELIMITER}{uid}'
        with Redis(
                host=REDIS_HOST, port=REDIS_PORT,
                db=self.REDIS_DB,
                username=REDIS_USER,
                password=REDIS_PASSWORD,
        ) as redis_client:
            redis_client.set(key, json.dumps([group_id, email]), self.EXPIRE)
        return url_for('project.project_join', url_id=uid)
