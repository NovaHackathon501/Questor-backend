"""
Purpose : Shared S3 client and config setup for Questor backend
"""

import os
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION     = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "questor-books")
S3_NCERT_PREFIX = os.getenv("S3_NCERT_PREFIX", "NCERT/")

_session = boto3.session.Session(
    aws_access_key_id     = os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name           = AWS_REGION,
)

s3_client = _session.client("s3")
