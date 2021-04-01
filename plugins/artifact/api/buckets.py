from datetime import datetime
from dateutil.relativedelta import relativedelta
from werkzeug.exceptions import Forbidden
from hurry.filesize import size

from plugins.base.utils.api_utils import build_req_parser
from plugins.base.utils.restApi import RestResource
from plugins.base.connectors.minio import MinioClient


class Buckets(RestResource):
    post_rules = (
        dict(name="name", type=str, location="json", required=True),
        dict(name="expiration_measure", type=str, location="json",
             choices=("days", "weeks", "months", "years"),
             help="Bad choice: {error_msg}"),
        dict(name="expiration_value", type=int, location="json", required=False),
    )

    def __init__(self):
        super().__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self._parser_post = build_req_parser(rules=self.post_rules)

    def get(self, project_id: int):
        project = self.rpc.project_get_or_404(project_id=project_id)
        c = MinioClient(project)
        buckets = c.list_bucket()
        rows = []
        for bucket in buckets:
            rows.append(dict(name=bucket, size=size(c.get_bucket_size(bucket))))
        return {"total": len(buckets), "rows": rows}

    def post(self, project_id: int):
        args = self._parser_post.parse_args()
        bucket = args["name"]
        expiration_measure = args["expiration_measure"]
        expiration_value = args["expiration_value"]

        project = self.rpc.project_get_or_404(project_id)
        data_retention_limit = project.get_data_retention_limit()
        minio_client = MinioClient(project=project)
        days = data_retention_limit or None

        if expiration_value and expiration_measure:
            today_date = datetime.today().date()
            expiration_date = today_date + relativedelta(**{expiration_measure: expiration_value})
            time_delta = expiration_date - today_date
            days = time_delta.days
            if data_retention_limit != -1 and days > data_retention_limit:
                raise Forbidden(description="The data retention limit allowed in the project has been exceeded")

        created = minio_client.create_bucket(bucket)
        if created and days:
            minio_client.configure_bucket_lifecycle(bucket=bucket, days=days)
        return {"message": "Created", "code": 200}