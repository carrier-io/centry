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

from sqlalchemy import String, Column, Integer, Text

from plugins.base.db_manager import Base
from plugins.base.models.abstract_base import AbstractBaseMixin


class Results(AbstractBaseMixin, Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, unique=False, nullable=False)
    task_id = Column(String(128), unique=False, nullable=False)
    ts = Column(Integer, unique=False, nullable=False)
    results = Column(Text, unique=False, nullable=False)
    log = Column(Text, unique=False, nullable=False)
