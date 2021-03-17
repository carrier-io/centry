from flask_restful import Resource
from plugins.base.connectors.minio import MinioClient
from plugins.base.utils.api_utils import build_req_parser, str2bool
from hurry.filesize import size


class Buckets(Resource):
    def get(self, project_id: int):
        from flask import current_app
        project = current_app.config["CONTEXT"].rpc_manager.call.project_get_or_404(project_id=project_id)
        c = MinioClient(project)
        buckets = c.list_bucket()
        rows = []
        for bucket in buckets:
            rows.append(dict(name=bucket, size=size(c.get_bucket_size(bucket))))
        return { "total": len(buckets), "rows": rows }