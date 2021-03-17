from flask_restful import Resource
from plugins.base.connectors.minio import MinioClient
from plugins.base.utils.api_utils import build_req_parser, str2bool
from hurry.filesize import size


class Artifacts(Resource):
    def get(self, project_id: int, bucket: str):
        from flask import current_app
        project = current_app.config["CONTEXT"].rpc_manager.call.project_get_or_404(project_id=project_id)
        c = MinioClient(project)
        files = c.list_files(bucket)
        for each in files:
            each["size"] = size(each["size"])
        return { "total": len(files), "rows": files }