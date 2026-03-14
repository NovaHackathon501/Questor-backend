"""
Purpose : Shared AWS client and config setup for Questor backend
"""

import os
import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION       = os.getenv("AWS_REGION", "ap-south-1")      # S3, DynamoDB → Mumbai
BEDROCK_REGION   = os.getenv("BEDROCK_REGION", "us-east-1")   # Bedrock Nova → US
S3_BUCKET_NAME   = os.getenv("S3_BUCKET_NAME", "questor-books")
S3_NCERT_PREFIX  = os.getenv("S3_NCERT_PREFIX", "NCERT/")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-2-lite-v1:0")

_session = boto3.session.Session(
    aws_access_key_id     = os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name           = AWS_REGION,
)

from botocore.config import Config

s3_client      = _session.client("s3")
bedrock_client = _session.client(
    "bedrock-runtime",
    region_name=BEDROCK_REGION,
    config=Config(retries={"max_attempts": 1, "mode": "standard"})  # no auto-retries on quota errors
)

