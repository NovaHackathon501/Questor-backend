"""
Purpose : Lambda handler — POST /ai/quiz
          Generates a 5-question MCQ quiz from NCERT page text.
          Returns STRUCTURED JSON so Flutter can render Q&A properly.

Request body:
  { "classLevel": "Class 9", "subject": "Science", "pageText": "..." }

Response:
  {
    "questions": [
      {
        "number": 1,
        "question": "What pigment absorbs sunlight in plants?",
        "options": {"A": "Melanin", "B": "Chlorophyll", "C": "Haemoglobin", "D": "Carotene"},
        "answer": "B",
        "explanation": "Chlorophyll is the green pigment that absorbs sunlight."
      }
    ]
  }

Lambda entry point : handler(event, context)
"""

import json
import sys
import os
import re
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import bedrock_client, BEDROCK_MODEL_ID

MAX_TOKENS = 1000


def handler(event, context):
    try:
        body        = json.loads(event.get("body") or "{}")
        class_level = body.get("classLevel", "").strip()
        subject     = body.get("subject", "").strip()
        page_text   = body.get("pageText", "").strip()

        missing = [f for f, v in [("classLevel", class_level), ("subject", subject), ("pageText", page_text)] if not v]
        if missing:
            return _response(400, {"error": f"Missing required fields: {', '.join(missing)}"})

        prompt = f"""You are a teacher creating a quiz for {class_level} {subject} students.

Based ONLY on the NCERT content below, create 5 multiple choice questions.

Return ONLY a valid JSON array (no markdown, no explanation, just raw JSON):
[
  {{
    "number": 1,
    "question": "Question text here?",
    "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
    "answer": "A",
    "explanation": "Brief explanation why A is correct."
  }}
]

NCERT Content:
{page_text}

JSON:"""

        response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": MAX_TOKENS},
        )
        raw = response["output"]["message"]["content"][0]["text"].strip()

        # Extract JSON array from response (handle markdown code blocks if present)
        json_match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not json_match:
            return _response(500, {"error": "AI returned unexpected format. Please try again."})

        questions = json.loads(json_match.group())

        return _response(200, {
            "questions":  questions,
            "classLevel": class_level,
            "subject":    subject,
            "totalQuestions": len(questions),
        })

    except json.JSONDecodeError:
        print(f"[ERROR] ai_quiz: Failed to parse AI JSON response: {raw}")
        return _response(500, {"error": "AI returned invalid quiz format. Please try again."})
    except ClientError as e:
        print(f"[ERROR] Bedrock: {e}")
        return _response(502, {"error": "AI service unavailable. Please try again."})
    except Exception as e:
        print(f"[ERROR] ai_quiz: {e}")
        return _response(500, {"error": "Something went wrong."})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body),
    }


if __name__ == "__main__":
    print("\n🧪 Testing ai_quiz locally...\n")
    result = handler({"body": json.dumps({
        "classLevel": "Class 9",
        "subject":    "Science",
        "pageText":   "Photosynthesis is the process by which green plants use sunlight to synthesise nutrients from carbon dioxide and water, producing oxygen as a byproduct. Chlorophyll in leaves absorbs sunlight. The process takes place in chloroplasts.",
    })}, None)
    print(f"Status : {result['statusCode']}")
    print(json.dumps(json.loads(result["body"]), indent=2))
