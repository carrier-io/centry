#!/usr/bin/python
# coding=utf-8

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

""" Vault DB model """

from sqlalchemy import Column, Integer, JSON  # pylint: disable=E0401

from .abstract_base import AbstractBaseMixin
from ..db_manager import Base


class Vault(AbstractBaseMixin, Base):  # pylint: disable=C0111
    __tablename__ = "vault"

    id = Column(Integer, primary_key=True)
    unseal_json = Column(JSON, unique=False, default={})
