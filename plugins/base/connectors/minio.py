import logging
from typing import Optional

import boto3
from botocore.client import Config, ClientError
from plugins.base.constants import MINIO_ACCESS, MINIO_ENDPOINT, MINIO_SECRET, MINIO_REGION


class MinioClient:
    PROJECT_SECRET_KEY: str = "minio_aws_access"

    def __init__(self, project, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(self.__class__.__name__.lower())
        self.project = project
        aws_access_key_id, aws_secret_access_key = self.extract_access_data()
        self.s3_client = boto3.client(
            "s3", endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=Config(signature_version="s3v4"),
            region_name=MINIO_REGION
        )

    def extract_access_data(self) -> tuple:
        if self.project and self.PROJECT_SECRET_KEY in (self.project.secrets_json or {}):
            aws_access_json = self.project.secrets_json[self.PROJECT_SECRET_KEY]
            aws_access_key_id = aws_access_json.get("aws_access_key_id")
            aws_secret_access_key = aws_access_json.get("aws_secret_access_key")
            return aws_access_key_id, aws_secret_access_key
        return MINIO_ACCESS, MINIO_SECRET

    def format_bucket_name(self, bucket: str) -> str:
        prefix = f"p--{self.project.id}."
        if bucket == f"{prefix}{bucket}":
            return bucket.replace(prefix, "", 1)
        return f"{prefix}{bucket}"

    def list_bucket(self) -> list:
        prefix = f"p--{self.project.id}."
        return [
            each["Name"].replace(prefix, "", 1)
            for each in self.s3_client.list_buckets().get("Buckets", {})
            if each["Name"].startswith(prefix)
        ]

    def create_bucket(self, bucket: str) -> dict:
        try:
            return self.s3_client.create_bucket(
                ACL="public-read",
                Bucket=self.format_bucket_name(bucket),
                CreateBucketConfiguration={"LocationConstraint": MINIO_REGION}
            )
        except ClientError as client_error:
            self._logger.warning(str(client_error))
        except Exception as exc:
            self._logger.error(str(exc))
        return {}

    def list_files(self, bucket: str) -> list:
        response = self.s3_client.list_objects_v2(Bucket=self.format_bucket_name(bucket))
        files = [
            {"name": each["Key"], "size": each["Size"],
             "modified": each["LastModified"].strftime("%Y-%m-%d %H:%M:%S")}
            for each in response.get("Contents", {})
        ]
        continuation_token = response.get("NextContinuationToken")
        while continuation_token and response["Contents"]:
            response = self.s3_client.list_objects_v2(Bucket=self.format_bucket_name(bucket),
                                                      ContinuationToken=continuation_token)
            appendage = [
                {"name": each["Key"],
                    "size": each["Size"],
                    "modified": each["LastModified"].strftime("%Y-%m-%d %H:%M:%S")}
                for each in response.get("Contents", {})
            ]
            if not appendage:
                break
            files += appendage
            continuation_token = response.get("NextContinuationToken")
        return files

    def upload_file(self, bucket: str, file_obj, file_name: str):
        return self.s3_client.put_object(Key=file_name, Bucket=self.format_bucket_name(bucket), Body=file_obj)

    def download_file(self, bucket: str, file_name: str):
        return self.s3_client.get_object(Bucket=self.format_bucket_name(bucket), Key=file_name)["Body"].read()

    def remove_file(self, bucket: str, file_name: str):
        return self.s3_client.delete_object(Bucket=self.format_bucket_name(bucket), Key=file_name)

    def remove_bucket(self, bucket: str):
        for file_obj in self.list_files(bucket):
            self.remove_file(bucket, file_obj["name"])

        self.s3_client.delete_bucket(Bucket=self.format_bucket_name(bucket))

    def configure_bucket_lifecycle(self, bucket: str, days: int) -> None:
        self.s3_client.put_bucket_lifecycle_configuration(
            Bucket=self.format_bucket_name(bucket),
            LifecycleConfiguration={
                "Rules": [
                    {
                        "Expiration": {
                            "NoncurrentVersionExpiration": days,
                            "Days": days,
                            # "ExpiredObjectDeleteMarker": True
                        },
                        "ID": "bucket-retention-policy",
                        "Status": "Enabled"
                    }
                ]
            }
        )

    def get_bucket_lifecycle(self, bucket: str) -> dict:
        return self.s3_client.get_bucket_lifecycle(Bucket=self.format_bucket_name(bucket))

    def get_bucket_size(self, bucket: str) -> int:
        total_size = 0
        for each in self.s3_client.list_objects_v2(
                Bucket=self.format_bucket_name(bucket)
        ).get('Contents', {}):
            total_size += each["Size"]
        return total_size

