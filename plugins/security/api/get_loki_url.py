import json
import gzip

import flask
from sqlalchemy import and_

from pylon.core.tools import log
from pylon.core.seeds.minio import MinIOHelper
from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser
from ..models.security_results import SecurityResultsDAST


class GetLokiUrl(RestResource):
    _get_rules = (
        dict(name="type", type=str, location="args"),
    )

    def __init__(self, settings):
        super().__init__()
        self.__init_req_parsers()
        from flask import current_app
        self.settings = settings
        # self.app_setting = current_app.config["SETTINGS"]

    def __init_req_parsers(self):
        self.get_parser = build_req_parser(rules=self._get_rules)

    def get(self, project_id: int):

        # state = self._get_task_state()
        key = flask.request.args.get("task_id", None)
        # if key is None or key not in state:
        #     return {"message": ""}, 404

        # websocket_base_url = self.settings["logs"]["url"]
        websocket_base_url = "https://127.0.0.1:3100/api/v1/push"
        websocket_base_url = websocket_base_url.replace("https://", "wss://")
        websocket_base_url = websocket_base_url.replace("api/v1/push", "api/v1/tail")
        #
        logs_query = "{" + f'task_key="{key}"' + "}"
        # logs_start = state[key].get("ts_start", 0)
        logs_limit = 10000000000

        # return {"websocket_url": f"{websocket_base_url}?query={logs_query}&start={logs_start}&limit={logs_limit}" }

        return {"websocket_url": f"{websocket_base_url}?query={logs_query}&start=0&limit=1000000" }

    def _get_minio(self):  # pylint: disable=R0201
        return MinIOHelper.get_client(self.app_setting["storage"])

    def _load_state_object(self, bucket, key):
        minio = self._get_minio()
        try:
            return json.loads(gzip.decompress(minio.get_object(bucket, key).read()))
        except:  # pylint: disable=W0702
            log.exception("Failed to load state object")
            return None

    def _get_task_state(self):
        state = self._load_state_object(
            self.settings["storage"]["buckets"]["state"],
            self.settings["storage"]["objects"]["task_state"]
        )
        return state if state is not None else dict()
