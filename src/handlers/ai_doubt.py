"""
Purpose : Lambda handler — POST /ai/doubt
          Doubt solver: takes NCERT page text + student question
          → returns AI explanation grounded to the page content.

Author  : Questor Team
Date    : 2026-03-14

Request body (JSON):
  {
    "classLevel":        "Class 9",
    "subject":           "Science",
    "pageText":          "...current page text...",
    "previousPageText":  "...previous page text...",   (optional)
    "nextPageText":      "...next page text...",        (optional)
    "question":          "What is photosynthesis?"
  }

Lambda entry point : handler(event, context)
Local test         : python src/handlers/ai_doubt.py
"""

import json
import sys
import os
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import bedrock_client, BEDROCK_MODEL_ID

# Max tokens for student response — keep answers concise and class-appropriate
MAX_TOKENS = 300


def build_prompt(class_level: str, subject: str,
                 page_text: str, question: str,
                 prev_text: str = "", next_text: str = "") -> str:
    """
    Builds the grounded NCERT prompt. Includes prev/next pages if provided
    to handle topics that span multiple pages.
    """
    context_parts = []
    if prev_text:
        context_parts.append(f"[Previous page]\n{prev_text.strip()}")
    context_parts.append(f"[Current page]\n{page_text.strip()}")
    if next_text:
        context_parts.append(f"[Next page]\n{next_text.strip()}")

    context = "\n\n".join(context_parts)

    return f"""You are a helpful tutor for a {class_level} student studying {subject}.

Answer the student's question ONLY using the NCERT textbook content provided below.
- Use simple language appropriate for {class_level}.
- Keep the answer under 150 words.
- If the answer is not in the provided content, say exactly:
  "This topic is not covered on this page. Please check another chapter."

NCERT Textbook Content:
{context}

Student's Question:
{question}

Answer:"""


def handler(event, context):
    """
    AWS Lambda entry point.
    Supports Lambda Function URL and API Gateway event formats.
    """
    try:
        # ── Parse body ─────────────────────────────────────────────────────────
        body = json.loads(event.get("body") or "{}")

        class_level = body.get("classLevel", "").strip()
        subject     = body.get("subject", "").strip()
        page_text   = body.get("pageText", "").strip()
        question    = body.get("question", "").strip()
        prev_text   = body.get("previousPageText", "").strip()
        next_text   = body.get("nextPageText", "").strip()

        # ── Validate ───────────────────────────────────────────────────────────
        missing = [f for f, v in [
            ("classLevel", class_level),
            ("subject",    subject),
            ("pageText",   page_text),
            ("question",   question),
        ] if not v]

        if missing:
            return _response(400, {"error": f"Missing required fields: {', '.join(missing)}"})

        if len(question) > 500:
            return _response(400, {"error": "Question too long. Keep it under 500 characters."})

        # ── Build prompt & call Bedrock (Converse API — works with Nova) ──────
        prompt = build_prompt(class_level, subject, page_text, question, prev_text, next_text)

        bedrock_response = bedrock_client.converse(
            modelId=BEDROCK_MODEL_ID,
            messages=[
                {"role": "user", "content": [{"text": prompt}]}
            ],
            inferenceConfig={"maxTokens": MAX_TOKENS},
        )

        answer_text = bedrock_response["output"]["message"]["content"][0]["text"].strip()

        return _response(200, {
            "answer":     answer_text,
            "classLevel": class_level,
            "subject":    subject,
        })

    except ClientError as e:
        print(f"[ERROR] Bedrock call failed: {e}")
        return _response(502, {"error": "AI service unavailable. Please try again."})

    except Exception as e:
        print(f"[ERROR] ai_doubt: {e}")
        return _response(500, {"error": "Something went wrong. Please try again."})


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
    print("\n🧪 Testing ai_doubt locally...\n")

    test_event = {
        "body": json.dumps({
            "classLevel": "Class 9",
            "subject":    "Science",
            "pageText":   (
                "Photosynthesis is the process by which green plants and some other organisms "
                "use sunlight to synthesise nutrients from carbon dioxide and water. "
                "Photosynthesis in plants generally involves the green pigment chlorophyll "
                "and generates oxygen as a byproduct."
            ),
            "question": "What do plants need for photosynthesis?"
        })
    }

    result = handler(test_event, None)
    print(f"Status : {result['statusCode']}")
    print(f"Body   :\n")
    print(json.dumps(json.loads(result["body"]), indent=2))
