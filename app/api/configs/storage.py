import os
import boto3
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

S3_ENDPOINT = os.environ["SUPABASE_STORAGE_URL"]       # e.g. https://<project_ref>.storage.supabase.co/storage/v1/s3
S3_ACCESS_KEY = os.environ["SUPABASE_ACCESS_KEY"]
S3_SECRET_KEY = os.environ["SUPABASE_SECRET_KEY"]
S3_REGION = os.environ["SUPABASE_REGION"]           # your actual project region, not "local"

BUCKET = "Rag_project"

s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
    config=Config(s3={"addressing_style": "path"}),   # <-- this is the forcePathStyle equivalent
)


def upload_bytes(key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    s3_client.put_object(Bucket=BUCKET, Key=key, Body=data, ContentType=content_type)
    return key


def download_bytes(key: str) -> bytes:
    response = s3_client.get_object(Bucket=BUCKET, Key=key)
    return response["Body"].read()


def get_presigned_url(key: str, expires_in: int = 3600) -> str:
    return s3_client.generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=expires_in
    )


def delete_object(key: str) -> None:
    s3_client.delete_object(Bucket=BUCKET, Key=key)