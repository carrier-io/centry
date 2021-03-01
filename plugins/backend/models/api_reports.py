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

from sqlalchemy import String, Column, Integer, Float, Text

from plugins.base.db_manager import Base
from plugins.base.models.abstract_base import AbstractBaseMixin


class APIReport(AbstractBaseMixin, Base):
    __tablename__ = "api_report"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, unique=False, nullable=False)
    test_uid = Column(String(128), unique=False, nullable=False)
    name = Column(String(128), unique=False)
    status = Column(String(128), unique=False)
    environment = Column(String(128), unique=False)
    type = Column(String(128), unique=False)
    end_time = Column(String(128), unique=False)
    start_time = Column(String(128), unique=False)
    failures = Column(Integer, unique=False)
    total = Column(Integer, unique=False)
    thresholds_missed = Column(Integer, unique=False, nullable=True)
    throughput = Column(Float, unique=False)
    vusers = Column(Integer, unique=False)
    pct50 = Column(Float, unique=False)
    pct75 = Column(Float, unique=False)
    pct90 = Column(Float, unique=False)
    pct95 = Column(Float, unique=False)
    pct99 = Column(Float, unique=False)
    _max = Column(Float, unique=False)
    _min = Column(Float, unique=False)
    mean = Column(Float, unique=False)
    duration = Column(Integer, unique=False)
    build_id = Column(String(128), unique=True)
    lg_type = Column(String(16), unique=False)
    onexx = Column(Integer, unique=False)
    twoxx = Column(Integer, unique=False)
    threexx = Column(Integer, unique=False)
    fourxx = Column(Integer, unique=False)
    fivexx = Column(Integer, unique=False)
    requests = Column(Text, unique=False)
    release_id = Column(Integer, nullable=True)

    def to_json(self, exclude_fields: tuple = ()) -> dict:
        json_dict = super().to_json(exclude_fields=("requests",))
        json_dict["requests"] = self.requests.split(";")
        return json_dict
