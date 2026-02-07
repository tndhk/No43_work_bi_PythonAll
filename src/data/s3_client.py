import boto3
from src.data.config import settings


def get_s3_client():
    """S3クライアントを取得"""
    endpoint_url = settings.s3_endpoint or None

    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )
