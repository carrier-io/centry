#   Copyright 2019 getcarrier.io
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from influxdb import InfluxDBClient
from .secrets import get_project_hidden_secrets, get_project_secrets


def get_client(project_id, db_name=None):
    secrets = get_project_secrets(project_id)
    hidden_secrets = get_project_hidden_secrets(project_id)
    influx_host = secrets.get("influx_ip") if "influx_ip" in secrets else hidden_secrets.get("influx_ip", "")
    influx_user = secrets.get("influx_user") if "influx_user" in secrets else hidden_secrets.get("influx_user", "")
    influx_password = secrets.get("influx_password") if "influx_password" in secrets else \
        hidden_secrets.get("influx_password", "")

    return InfluxDBClient(influx_host, 8086, influx_user, influx_password, db_name)


def create_project_databases(project_id):
    hidden_secrets = get_project_hidden_secrets(project_id)
    db_list = [hidden_secrets.get("jmeter_db"), hidden_secrets.get("gatling_db"), hidden_secrets.get("comparison_db"),
               hidden_secrets.get("telegraf_db")]
    client = get_client(project_id)
    for each in db_list:
        client.query(f"create database {each} with duration 180d replication 1 shard duration 7d name autogen")


def drop_project_databases(project_id):
    hidden_secrets = get_project_hidden_secrets(project_id)
    db_list = [hidden_secrets.get("jmeter_db"), hidden_secrets.get("gatling_db"), hidden_secrets.get("comparison_db"),
               hidden_secrets.get("telegraf_db")]
    client = get_client(project_id)
    for each in db_list:
        client.query(f"drop database {each}")