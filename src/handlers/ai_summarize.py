"""
Purpose : Lambda handler — POST /ai/summarize  (Teacher feature)
          Summarizes an NCERT chapter into key points for quick teacher prep.

Request body:
  { "classLevel": "Class 9", "subject": "Science", "chapterText": "..." }

Lambda entry point : handler(event, context)
"""

import json
import sys
import os
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import bedrock_client, BEDROCK_MODEL_ID

MAX_TOKENS = 500


def handler(event, context):
    try:
        body         = json.loads(event.get("body") or "{}")
        class_level  = body.get("classLevel", "").strip()
        subject      = body.get("subject", "").strip()
        chapter_text = body.get("chapterText", "").strip()

        missing = [f for f, v in [("classLevel", class_level), ("subject", subject), ("chapterText", chapter_text)] if not v]
        if missing:
            return _response(400, {"error": f"Missing required fields: {', '.join(missing)}"})

        prompt = f"""You are helping a {class_level} {subject} teacher prepare for class.

Summarize the NCERT chapter content below into:
1. A 2-3 sentence overview
2. Key concepts (bullet points, max 6)
3. Important terms to highlight in class (comma-separated list)

NCERT Chapter Content:
{chapter_text}

Summary:"""

        response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": MAX_TOKENS},
        )
        summary = response["output"]["message"]["content"][0]["text"].strip()

        return _response(200, {
            "summary":    summary,
            "classLevel": class_level,
            "subject":    subject,
        })

    except ClientError as e:
        print(f"[ERROR] Bedrock: {e}")
        return _response(502, {"error": "AI service unavailable. Please try again."})
    except Exception as e:
        print(f"[ERROR] ai_summarize: {e}")
        return _response(500, {"error": "Something went wrong."})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body),
    }


if __name__ == "__main__":
    print("\n🧪 Testing ai_summarize locally...\n")
    result = handler({"body": json.dumps({
        "classLevel":  "Class 9",
        "subject":     "Science",
        "chapterText": "Photosynthesis is the process by which green plants use sunlight to synthesise nutrients from carbon dioxide and water. Chlorophyll absorbs sunlight. The process occurs in chloroplasts. Oxygen is released as a byproduct.",
    })}, None)
    print(f"Status : {result['statusCode']}")
    print(json.dumps(json.loads(result["body"]), indent=2))
