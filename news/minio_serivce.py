import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from django.conf import settings


class MinioService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=f"http://{settings.MINIO_STORAGE_ENDPOINT}",
            aws_access_key_id=settings.MINIO_STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_STORAGE_SECRET_KEY,
            config=boto3.session.Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        self.bucket_name = settings.MINIO_STORAGE_BUCKET_NAME

    def upload_file(self, file, unique_name):
        try:
            self.s3.upload_fileobj(file, self.bucket_name, unique_name)
            return f"{settings.MINIO_STORAGE_ENDPOINT}/{self.bucket_name}/{unique_name}"
        except (NoCredentialsError, PartialCredentialsError):
            raise Exception("Invalid credentials for MinIO")
        except ClientError as e:
            raise Exception(f"Failed to upload file: {e}")

    def download_file(self, unique_name):
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=unique_name)  # Используем self.bucket_name
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"Failed to download file: {e}")
