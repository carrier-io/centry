#     Copyright 2021 getcarrier.io
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
import string
from json import dumps
from sqlalchemy import Column, Integer, String, ARRAY, JSON

from plugins.base.db_manager import Base
from plugins.base.models.abstract_base import AbstractBaseMixin
from plugins.base.constants import CURRENT_RELEASE
from plugins.project.connectors.secrets import get_project_hidden_secrets, unsecret


class SecurityTestsDAST(AbstractBaseMixin, Base):
    __tablename__ = "security_tests_dast"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, unique=False, nullable=False)
    project_name = Column(String(64), nullable=False)
    test_uid = Column(String(128), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    test_environment = Column(String(128), nullable=False)
    urls_to_scan = Column(ARRAY(String(128)), nullable=False)
    urls_exclusions = Column(ARRAY(String(128)))
    reporting = Column(
        ARRAY(JSON),
        # nullable=False
    )
    scanners_cards = Column(JSON)  # {<scanner>: {<scanner_params>}, ...}
    processing = Column(JSON)  # {<processing_card>: <value>, }

    region = Column(String(128), nullable=False, default="default")
    # bucket = Column(String(128), nullable=False)
    # last_run = Column(Integer)
    # job_type = Column(String(20))

    def set_last_run(self, ts):
        self.last_run = ts
        self.commit()

    @staticmethod
    def sanitize(val):
        valid_chars = "_%s%s" % (string.ascii_letters, string.digits)
        return ''.join(c for c in val if c in valid_chars)

    def insert(self):
        super().insert()

    def configure_execution_json(
            self,
            output='cc',
            thresholds={}
    ):
        from json import loads

        if output == "dusty":
            from flask import current_app
            global_dast_settings = dict()
            global_dast_settings["max_concurrent_scanners"] = 1

            if "toolreports" in self.reporting:
                global_dast_settings["save_intermediates_to"] = "/tmp/intermediates"

            scanners_config = {}

            # scanners_data
            for scanner_name in self.scanners_cards:
                scanners_config[scanner_name] = {}
                scanners_data = (
                        current_app.config["CONTEXT"].rpc_manager.node.call(scanner_name)
                        or
                        {"target": "urls_to_scan"}
                )
                for setting in scanners_data:
                    scanners_config[scanner_name][setting] = self.__dict__.get(
                        scanners_data[setting],
                        scanners_data[setting]
                    )

            reporters_config = dict()
            reporters_config["galloper"] = {
                "url": unsecret(
                    "{{secret.galloper_url}}",
                    project_id=self.project_id
                ),
                "project_id": f"{self.project_id}",
                "token": unsecret(
                    "{{secret.auth_token}}",
                    project_id=self.project_id
                ),
            }
            # TODO: check valid reports names
            for report_type in self.reporting:
                if report_type == "toolreports":
                    reporters_config["galloper_tool_reports"] = {
                        "bucket": "dast",
                        "object": f"{self.test_uid}_tool_reports.zip",
                        "source": "/tmp/intermediates",
                    }

                elif report_type == "quaity":
                    reporters_config["galloper_junit_report"] = {
                        "bucket": "dast",
                        "object": f"{self.test_uid}_junit_report.xml",
                    }
                    reporters_config["galloper_quality_gate_report"] = {
                        "bucket": "dast",
                        "object": f"{self.test_uid}_quality_gate_report.json",
                    }
                    reporters_config["junit"] = {
                        "file": "/tmp/{project_name}_{testing_type}_{build_id}_report.xml",
                    }

                elif report_type == "jira":
                    project_secrets = get_project_hidden_secrets(self.project_id)
                    if "jira" in project_secrets:
                        jira_settings = loads(project_secrets["jira"])
                        reporters_config["jira"] = {
                            "url": jira_settings["jira_url"],
                            "username": jira_settings["jira_login"],
                            "password": jira_settings["jira_password"],
                            "project": jira_settings["jira_project"],
                            "fields": {
                                "Issue Type": jira_settings["issue_type"],
                            }
                        }

                elif report_type == "email":
                    project_secrets = get_project_hidden_secrets(self.project_id)
                    if "smtp" in project_secrets:
                        email_settings = loads(project_secrets["smtp"])
                        reporters_config["email"] = {
                            "server": email_settings["smtp_host"],
                            "port": email_settings["smtp_port"],
                            "login": email_settings["smtp_user"],
                            "password": email_settings["smtp_password"],
                            "mail_to": self.dast_settings.get("email_recipients", ""),
                        }
                        reporters_config["html"] = {
                            "file": "/tmp/{project_name}_{testing_type}_{build_id}_report.html",
                        }

                elif report_type == "ado":
                    project_secrets = get_project_hidden_secrets(self.project_id)
                    if "ado" in project_secrets:
                        reporters_config["azure_devops"] = loads(
                            project_secrets["ado"]
                        )

                elif report_type == "rp":
                    project_secrets = get_project_hidden_secrets(self.project_id)
                    if "rp" in project_secrets:
                        rp = loads(project_secrets.get("rp"))
                        reporters_config["reportportal"] = {
                            "rp_host": rp["rp_host"],
                            "rp_token": rp["rp_token"],
                            "rp_project_name": rp["rp_project"],
                            "rp_launch_name": "dast"
                        }
            # Thresholds
            tholds = {}
            if thresholds and any(int(thresholds[key]) > -1 for key in thresholds.keys()):

                for key, value in thresholds.items():
                    if int(value) > -1:
                        tholds[key.capitalize()] = int(value)

            dusty_config = {
                "config_version": 2,
                "suites": {
                    "dast": {
                        "settings": {
                            "project_name": self.project_name,
                            "project_description": self.name,
                            "environment_name": "target",
                            "testing_type": "DAST",
                            "scan_type": "full",
                            "build_id": self.test_uid,
                            "dast": global_dast_settings
                        },
                        "scanners": {
                            "dast": scanners_config
                        },
                        "processing": {
                            "min_severity_filter": {
                                "severity": "Info"
                            },
                            "quality_gate": {
                                "thresholds": tholds
                            },
                            "false_positive": {
                                "galloper": unsecret(
                                    "{{secret.galloper_url}}",
                                    project_id=self.project_id
                                ),
                                "project_id": f"{self.project_id}",
                                "token": unsecret(
                                    "{{secret.auth_token}}",
                                    project_id=self.project_id
                                )
                            },
                            "ignore_finding": {
                                "galloper": unsecret(
                                    "{{secret.galloper_url}}",
                                    project_id=self.project_id
                                ),
                                "project_id": f"{self.project_id}",
                                "token": unsecret(
                                    "{{secret.auth_token}}",
                                    project_id=self.project_id
                                )
                            }
                        },
                        "reporters": reporters_config
                    }
                }
            }
            from pprint import pprint
            print("DUSTY CONFIG")
            pprint(dusty_config)
            return dusty_config

        job_type = "dast"
        container = f"getcarrier/{job_type}:{CURRENT_RELEASE}"
        parameters = {
            "cmd": f"run -b galloper:{job_type}_{self.test_uid} -s {job_type}",
            "GALLOPER_URL": unsecret(
                "{{secret.galloper_url}}",
                project_id=self.project_id
            ),
            "GALLOPER_PROJECT_ID": f"{self.project_id}",
            "GALLOPER_AUTH_TOKEN": unsecret(
                "{{secret.auth_token}}",
                project_id=self.project_id
            ),
        }
        cc_env_vars = {
            "RABBIT_HOST": unsecret(
                "{{secret.rabbit_host}}",
                project_id=self.project_id
            ),
            "RABBIT_USER": unsecret(
                "{{secret.rabbit_user}}",
                project_id=self.project_id
            ),
            "RABBIT_PASSWORD": unsecret(
                "{{secret.rabbit_password}}",
                project_id=self.project_id
            )
        }
        concurrency = 1

        if output == "docker":
            return f"docker run --rm -i -t " \
                   f"-e project_id={self.project_id} " \
                   f"-e galloper_url={unsecret('{{secret.galloper_url}}', project_id=self.project_id)} " \
                   f"-e token=\"{unsecret('{{secret.auth_token}}', project_id=self.project_id)}\" " \
                   f"getcarrier/control_tower:{CURRENT_RELEASE} " \
                   f"-tid {self.test_uid}"
        if output == "cc":
            execution_json = {
                "job_name": self.name,
                "job_type": job_type,
                "concurrency": concurrency,
                "container": container,
                "execution_params": dumps(parameters),
                "cc_env_vars": cc_env_vars,
                "channel": self.region
            }
            if "quality" in self.scanners_cards:
                execution_json["quality_gate"] = "True"
            return execution_json

        return ""

    def to_json(self, exclude_fields: tuple = ()) -> dict:
        test_param = super().to_json(exclude_fields)
        test_param["tools"] = ",".join(test_param["scanners_cards"].keys())
        return test_param
