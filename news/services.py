from .minio_serivce import MinioService


class FileService:
    @staticmethod
    def upload_to_minio(file, title):
        minio_service = MinioService()
        unique_name = f"posts/{title}/{file.name}"
        minio_service.upload_file(file, unique_name)
        return f"{minio_service.s3.meta.endpoint_url}/{minio_service.bucket_name}/{unique_name}"

