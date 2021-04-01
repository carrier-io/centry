from flask import send_file
from plugins.base.utils.restApi import RestResource
from plugins.base.connectors.minio import MinioClient
from io import BytesIO


class Artifact(RestResource):
    def get(self, project_id: int, bucket: str, filename: str):
        project = self.rpc.project_get_or_404(project_id=project_id)
        fobj = MinioClient(project).download_file(bucket, filename)
        return send_file(BytesIO(fobj), attachment_filename=filename)
