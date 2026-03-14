"""
Purpose : Lambda handler — POST /ai/questions  (Teacher feature)
          Generates test/assignment questions from NCERT chapter content.

Request body:
  {
    "classLevel":  "Class 9",
    "subject":     "Science",
    "chapterText": "...",
    "count":       5        (optional, default 5, max 10)
  }

Lambda entry point : handler(event, context)
"""

import json
import sys
import os
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import bedrock_client, BEDROCK_MODEL_ID

MAX_TOKENS = 600


def handler(event, context):
    try:
        body         = json.loads(event.get("body") or "{}")
        class_level  = body.get("classLevel", "").strip()
        subject      = body.get("subject", "").strip()
        chapter_text = body.get("chapterText", "").strip()
        count        = min(int(body.get("count", 5)), 10)  # cap at 10

        missing = [f for f, v in [("classLevel", class_level), ("subject", subject), ("chapterText", chapter_text)] if not v]
        if missing:
            return _response(400, {"error": f"Missing required fields: {', '.join(missing)}"})

        prompt = f"""You are a {class_level} {subject} teacher creating exam questions.

Based ONLY on the NCERT content below, generate {count} high-quality exam questions.
Mix question types: include short answer, long answer, and application-based questions.
All questions must be answerable from the content provided.
Format: numbered list with question type in brackets.
Example: "1. [Short Answer] What is..."

NCERT Chapter Content:
{chapter_text}

{count} Exam Questions:"""

        response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": MAX_TOKENS},
        )
        output = response["output"]["message"]["content"][0]["text"].strip()

        lines     = [l.strip() for l in output.split("\n") if l.strip()]
        questions = [l for l in lines if l and l[0].isdigit()]

        return _response(200, {
            "questions":  questions,
            "count":      len(questions),
            "classLevel": class_level,
            "subject":    subject,
        })

    except ClientError as e:
        print(f"[ERROR] Bedrock: {e}")
        return _response(502, {"error": "AI service unavailable. Please try again."})
    except Exception as e:
        print(f"[ERROR] ai_questions: {e}")
        return _response(500, {"error": "Something went wrong."})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body),
    }


if __name__ == "__main__":
    print("\n🧪 Testing ai_questions locally...\n")
    result = handler({"body": json.dumps({
        "classLevel":  "Class 9",
        "subject":     "Science",
        "chapterText": "Photosynthesis is the process by which green plants use sunlight to synthesise nutrients from carbon dioxide and water. Chlorophyll absorbs sunlight. The process occurs in chloroplasts. Oxygen is released as a byproduct.",
        "count":       5,
    })}, None)
    print(f"Status : {result['statusCode']}")
    print(json.dumps(json.loads(result["body"]), indent=2))
