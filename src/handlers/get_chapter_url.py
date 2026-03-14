"""
Purpose : Lambda handler — GET /books/chapter
          Takes class, subject, and either chapter number or file name
          → returns a 15-min pre-signed S3 URL for the PDF.

Author  : Questor Team
Date    : 2026-03-14

Query params (all case-sensitive except subject, which is auto title-cased):
  - class   : e.g. "class-9"
  - subject : e.g. "Science" or "science" (auto-corrected)
  - chapter : e.g. "1"  → maps to "Chapter 1.pdf"  (use this OR file)
  - file    : e.g. "Answers.pdf" or "Prelims.pdf"   (use this OR chapter)

Lambda entry point : handler(event, context)
Local test         : python src/handlers/get_chapter_url.py
"""

import json
import sys
import os
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import s3_client, S3_BUCKET_NAME, S3_NCERT_PREFIX

# Pre-signed URL valid for 15 minutes
PRESIGN_EXPIRY_SECONDS = 900


def handler(event, context):
    """
    AWS Lambda entry point.
    Supports both Lambda Function URL and API Gateway event formats.
    """
    try:
        # ── Parse query params ─────────────────────────────────────────────────
        params = event.get("queryStringParameters") or {}

        class_level = params.get("class", "").strip().lower()
        subject      = params.get("subject", "").strip().title()  # auto title-case: "science" → "Science"
        chapter      = params.get("chapter", "").strip()
        file_param   = params.get("file", "").strip()

        # Must provide either chapter number or file name
        if not class_level or not subject:
            return _response(400, {"error": "Missing required query params: class, subject"})
        if not chapter and not file_param:
            return _response(400, {"error": "Provide either 'chapter' (number) or 'file' (filename)"})

        # Validate chapter is a valid integer
        if chapter:
            if not chapter.isdigit():
                return _response(400, {"error": "'chapter' must be a number, e.g. chapter=1"})

        # ── Build S3 key ───────────────────────────────────────────────────────
        filename = file_param if file_param else f"Chapter {chapter}.pdf"
        s3_key   = f"{S3_NCERT_PREFIX}{class_level}/{subject}/{filename}"

        # ── Verify the object exists before signing ────────────────────────────
        try:
            s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ("404", "NoSuchKey"):
                return _response(404, {
                    "error": f"File not found: {s3_key}",
                    "hint": f"Available subjects use title-case e.g. 'Science', 'English'. Check chapter number too."
                })
            raise

        # ── Generate pre-signed URL ────────────────────────────────────────────
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=PRESIGN_EXPIRY_SECONDS,
        )

        return _response(200, {
            "url":       url,
            "key":       s3_key,
            "expiresIn": PRESIGN_EXPIRY_SECONDS,
        })

    except Exception as e:
        print(f"[ERROR] get_chapter_url: {e}")
        return _response(500, {"error": "Failed to generate chapter URL."})


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }


# ── Local test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🧪 Testing get_chapter_url locally...\n")

    # Simulate: GET /books/chapter?class=class-9&subject=Science&chapter=1
    test_event = {
        "queryStringParameters": {
            "class":   "class-9",
            "subject": "Science",
            "chapter": "1",
        }
    }

    result = handler(test_event, None)
    print(f"Status : {result['statusCode']}")
    print(f"Body   :\n")
    print(json.dumps(json.loads(result["body"]), indent=2))
