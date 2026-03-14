"""
Purpose : Lambda handler — GET /books/structure
          Returns the full NCERT folder tree from S3.
Author  : Questor Team
Date    : 2026-03-14

Lambda entry point : handler(event, context)
Local test         : python src/handlers/get_structure.py
"""

import json
import sys
import os

# Allow imports from src/ when running locally
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import S3_NCERT_PREFIX
from s3_helper import list_all_objects, build_tree, flatten_tree


def handler(event, context):
    """
    AWS Lambda entry point.
    Called by API Gateway for GET /books/structure
    """
    try:
        prefix = S3_NCERT_PREFIX  # "NCERT/"

        # 1. List all S3 objects under NCERT/
        keys = list_all_objects(prefix)

        if not keys:
            return _response(200, {"NCERT": {}})

        # 2. Build nested tree from flat S3 keys
        raw_tree = build_tree(keys, prefix)

        # 3. Clean up internal _files markers
        clean_tree = flatten_tree(raw_tree)

        return _response(200, {"NCERT": clean_tree})

    except Exception as e:
        print(f"[ERROR] get_structure: {e}")
        return _response(500, {"error": "Failed to retrieve book structure."})


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",   # Allow Flutter app to call
        },
        "body": json.dumps(body),
    }


# ── Local test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🧪 Testing get_structure locally...\n")

    result = handler({}, None)

    print(f"Status : {result['statusCode']}")
    print(f"Body   :\n")

    body = json.loads(result["body"])
    print(json.dumps(body, indent=2))
