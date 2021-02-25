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

import json

from plugins.base.config import Config
from plugins.base.db_manager import db_session

config = Config()

class AbstractBaseMixin:
    __table__ = None
    __table_args__ = {"schema": config.DATABASE_SCHEMA} if config.DATABASE_SCHEMA else None

    def __repr__(self) -> str:
        return json.dumps(self.to_json(), indent=2)

    def to_json(self, exclude_fields: tuple = ()) -> dict:
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns if column.name not in exclude_fields
        }

    @staticmethod
    def commit() -> None:
        db_session.commit()

    def add(self) -> None:
        db_session.add(self)

    def insert(self) -> None:
        self.add()
        self.commit()

    def delete(self, commit: bool = True) -> None:
        db_session.delete(self)
        if commit:
            self.commit()
