"""
Purpose : Lambda handler — POST /ai/guidance  (Teacher feature)
          Gives teaching guidance: which topics need more time, what students find difficult.

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

MAX_TOKENS = 400


def handler(event, context):
    try:
        body         = json.loads(event.get("body") or "{}")
        class_level  = body.get("classLevel", "").strip()
        subject      = body.get("subject", "").strip()
        chapter_text = body.get("chapterText", "").strip()

        missing = [f for f, v in [("classLevel", class_level), ("subject", subject), ("chapterText", chapter_text)] if not v]
        if missing:
            return _response(400, {"error": f"Missing required fields: {', '.join(missing)}"})

        prompt = f"""You are an experienced {class_level} {subject} teacher mentor.

Analyze the NCERT chapter content below and give teaching guidance:
1. Topics that need extra teaching time (2-3 bullet points)
2. Concepts students commonly find difficult (2-3 bullet points)
3. Suggested teaching approach (1-2 sentences)

Keep advice practical and specific to {class_level} students.

NCERT Chapter Content:
{chapter_text}

Teaching Guidance:"""

        response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": MAX_TOKENS},
        )
        guidance = response["output"]["message"]["content"][0]["text"].strip()

        return _response(200, {
            "guidance":   guidance,
            "classLevel": class_level,
            "subject":    subject,
        })

    except ClientError as e:
        print(f"[ERROR] Bedrock: {e}")
        return _response(502, {"error": "AI service unavailable. Please try again."})
    except Exception as e:
        print(f"[ERROR] ai_guidance: {e}")
        return _response(500, {"error": "Something went wrong."})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body),
    }


if __name__ == "__main__":
    print("\n🧪 Testing ai_guidance locally...\n")
    result = handler({"body": json.dumps({
        "classLevel":  "Class 9",
        "subject":     "Science",
        "chapterText": "Photosynthesis is the process by which green plants use sunlight to synthesise nutrients from carbon dioxide and water. Chlorophyll absorbs sunlight. The process occurs in chloroplasts. Oxygen is released as a byproduct. The light reaction and dark reaction are two stages.",
    })}, None)
    print(f"Status : {result['statusCode']}")
    print(json.dumps(json.loads(result["body"]), indent=2))
