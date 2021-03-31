from flask import send_file
from flask_restful import Resource
from plugins.base.connectors.minio import MinioClient
from io import BytesIO


class Artifact(Resource):
    def __init__(self):
        from flask import current_app
        self.app = current_app

    def get(self, project_id: int, bucket: str, filename: str):
        project = self.app.config["CONTEXT"].rpc_manager.call.project_get_or_404(project_id=project_id)
        fobj = MinioClient(project).download_file(bucket, filename)
        return send_file(BytesIO(fobj), attachment_filename=filename)