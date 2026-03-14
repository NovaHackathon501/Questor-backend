"""
Purpose : Lambda handler — POST /ai/hotquestions
          Generates 5 challenging questions from a given NCERT page.
          Great for students who want to test their understanding.

Request body:
  { "classLevel": "Class 9", "subject": "Science", "pageText": "..." }

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
        body        = json.loads(event.get("body") or "{}")
        class_level = body.get("classLevel", "").strip()
        subject     = body.get("subject", "").strip()
        page_text   = body.get("pageText", "").strip()

        missing = [f for f, v in [("classLevel", class_level), ("subject", subject), ("pageText", page_text)] if not v]
        if missing:
            return _response(400, {"error": f"Missing required fields: {', '.join(missing)}"})

        prompt = f"""You are a teacher creating questions for {class_level} {subject} students.

Based ONLY on the NCERT content below, generate 5 challenging but fair questions.
- Make them thought-provoking, not just fact recall
- Questions must be answerable from the content provided
- Keep language appropriate for {class_level}
- Format: numbered list, one question per line, no answers

NCERT Content:
{page_text}

5 Questions:"""

        response    = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": MAX_TOKENS},
        )
        output = response["output"]["message"]["content"][0]["text"].strip()

        # Parse numbered questions into a list
        lines     = [l.strip() for l in output.split("\n") if l.strip()]
        questions = [l for l in lines if l[0].isdigit()]

        return _response(200, {
            "questions":  questions,
            "classLevel": class_level,
            "subject":    subject,
        })

    except ClientError as e:
        print(f"[ERROR] Bedrock: {e}")
        return _response(502, {"error": "AI service unavailable. Please try again."})
    except Exception as e:
        print(f"[ERROR] ai_hotquestions: {e}")
        return _response(500, {"error": "Something went wrong."})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body),
    }


if __name__ == "__main__":
    print("\n🧪 Testing ai_hotquestions locally...\n")
    result = handler({"body": json.dumps({
        "classLevel": "Class 9",
        "subject":    "Science",
        "pageText":   "Photosynthesis is the process by which green plants use sunlight to synthesise nutrients from carbon dioxide and water, producing oxygen as a byproduct. Chlorophyll in leaves absorbs sunlight.",
    })}, None)
    print(f"Status : {result['statusCode']}")
    print(json.dumps(json.loads(result["body"]), indent=2))
