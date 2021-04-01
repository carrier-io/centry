from plugins.base.utils.restApi import RestResource
from plugins.base.connectors.minio import MinioClient
from hurry.filesize import size


class Buckets(RestResource):
    def get(self, project_id: int):
        project = self.rpc.project_get_or_404(project_id=project_id)
        c = MinioClient(project)
        buckets = c.list_bucket()
        rows = []
        for bucket in buckets:
            rows.append(dict(name=bucket, size=size(c.get_bucket_size(bucket))))
        return {"total": len(buckets), "rows": rows}
