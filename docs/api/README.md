# Questor Backend — API Reference

> **AI Agents**: Per `docs/ai-context/AI_UPDATE_INSTRUCTIONS.md`, update this file every time an endpoint is added, changed, or removed.

**Base URL (local)**: `http://localhost:8000`
**Base URL (production)**: _To be added after API Gateway deployment_

---

## Endpoints Summary

| Method | Path | Who | Description |
|---|---|---|---|
| GET | `/books/structure` | Both | Full NCERT folder tree |
| GET | `/books/chapter` | Both | Pre-signed S3 URL for a chapter PDF |
| POST | `/ai/doubt` | Student | AI explanation for a doubt |
| POST | `/ai/hotquestions` | Student | 5 challenging questions from a page |
| POST | `/ai/quiz` | Student | 5-question MCQ quiz (structured JSON) |
| POST | `/ai/summarize` | Teacher | Chapter key points summary |
| POST | `/ai/guidance` | Teacher | Teaching tips and difficult concepts |
| POST | `/ai/questions` | Teacher | Exam questions from chapter content |

---

## GET /books/chapter

**Purpose**: Returns a 15-minute pre-signed S3 URL for a specific chapter PDF. Flutter app uses this URL to open the PDF in the viewer.

**Request**
- Method: `GET`
- Path: `/books/chapter`
- Query params:
  - `class` — e.g. `class-9` *(required)*
  - `subject` — e.g. `Science` *(required)*
  - `chapter` — e.g. `1` → maps to `Chapter 1.pdf` *(required unless `file` is given)*
  - `file` — e.g. `Answers.pdf` or `Prelims.pdf` → use exact filename *(required unless `chapter` is given)*

**Examples**
```
GET /books/chapter?class=class-9&subject=Science&chapter=3
GET /books/chapter?class=class-9&subject=Science&file=Answers.pdf
GET /books/chapter?class=class-9&subject=English&file=Prelims.pdf
```

**Response (200)**
```json
{
  "url": "https://questor-books.s3.ap-south-1.amazonaws.com/NCERT/class-9/Science/Chapter%201.pdf?X-Amz-...",
  "key": "NCERT/class-9/Science/Chapter 1.pdf",
  "expiresIn": 900
}
```

**Handler**: `src/handlers/get_chapter_url.py`

---

## GET /books/structure

**Purpose**: Returns the complete NCERT folder hierarchy from S3 so the frontend can build subject and chapter navigation menus.

**Request**: `GET /books/structure` — no params

**Response**
```json
{
  "NCERT": {
    "class-7": {},
    "class-8": {},
    "class-9": {
      "English": ["Chapter 1.pdf", "...", "Prelims.pdf"],
      "Science": ["Chapter 1.pdf", "...", "Chapter 12.pdf", "Answers.pdf", "Prelims.pdf"]
    }
  }
}
```

**Handler**: `src/handlers/get_structure.py`

---

## POST /ai/doubt *(Student)*

**Purpose**: Answers a student's doubt grounded to the NCERT page they are reading.

**Request body**
```json
{
  "classLevel": "Class 9",
  "subject": "Science",
  "pageText": "...current page text...",
  "previousPageText": "...(optional)...",
  "nextPageText": "...(optional)...",
  "question": "What do plants need for photosynthesis?"
}
```

**Response (200)**
```json
{
  "answer": "Plants need sunlight, carbon dioxide, and water...",
  "classLevel": "Class 9",
  "subject": "Science"
}
```

**Handler**: `src/handlers/ai_doubt.py`

---

## POST /ai/hotquestions *(Student)*

**Purpose**: Generates 5 challenging questions from a page to test student understanding.

**Request body**
```json
{
  "classLevel": "Class 9",
  "subject": "Science",
  "pageText": "...page text..."
}
```

**Response (200)**
```json
{
  "questions": [
    "1. What is the role of chlorophyll in photosynthesis?",
    "2. Why do plants release oxygen during photosynthesis?",
    "..."
  ],
  "classLevel": "Class 9",
  "subject": "Science"
}
```

**Handler**: `src/handlers/ai_hotquestions.py`

---

## POST /ai/quiz *(Student — structured JSON for Flutter rendering)*

**Purpose**: Generates a 5-question MCQ quiz from page content. Returns structured JSON — Flutter renders this directly as interactive Q&A cards.

**Request body**
```json
{
  "classLevel": "Class 9",
  "subject": "Science",
  "pageText": "...page text..."
}
```

**Response (200)**
```json
{
  "questions": [
    {
      "number": 1,
      "question": "What pigment absorbs sunlight in plants?",
      "options": {"A": "Melanin", "B": "Chlorophyll", "C": "Haemoglobin", "D": "Carotene"},
      "answer": "B",
      "explanation": "Chlorophyll is the green pigment that absorbs sunlight for photosynthesis."
    }
  ],
  "totalQuestions": 5,
  "classLevel": "Class 9",
  "subject": "Science"
}
```

**Handler**: `src/handlers/ai_quiz.py`

---

## POST /ai/summarize *(Teacher)*

**Purpose**: Summarizes a chapter into key points for quick teacher preparation.

**Request body**
```json
{
  "classLevel": "Class 9",
  "subject": "Science",
  "chapterText": "...chapter text..."
}
```

**Response (200)**
```json
{
  "summary": "Overview: ...\n\nKey Concepts:\n- ...\n\nImportant Terms: ...",
  "classLevel": "Class 9",
  "subject": "Science"
}
```

**Handler**: `src/handlers/ai_summarize.py`

---

## POST /ai/guidance *(Teacher)*

**Purpose**: Provides teaching guidance — topics needing extra time, concepts students find difficult, suggested approach.

**Request body**
```json
{
  "classLevel": "Class 9",
  "subject": "Science",
  "chapterText": "...chapter text..."
}
```

**Response (200)**
```json
{
  "guidance": "Topics needing extra time:\n- ...\n\nCommon difficulties:\n- ...\n\nSuggested approach: ...",
  "classLevel": "Class 9",
  "subject": "Science"
}
```

**Handler**: `src/handlers/ai_guidance.py`

---

## POST /ai/questions *(Teacher)*

**Purpose**: Generates mixed-type exam questions (short answer, long answer, application-based).

**Request body**
```json
{
  "classLevel": "Class 9",
  "subject": "Science",
  "chapterText": "...chapter text...",
  "count": 5
}
```

**Response (200)**
```json
{
  "questions": [
    "1. [Short Answer] What is photosynthesis?",
    "2. [Long Answer] Explain the two stages of photosynthesis.",
    "..."
  ],
  "count": 5,
  "classLevel": "Class 9",
  "subject": "Science"
}
```

**Handler**: `src/handlers/ai_questions.py`


---

## GET /books/chapter

**Purpose**: Returns a 15-minute pre-signed S3 URL for a specific chapter PDF. Flutter app uses this URL to open the PDF in the viewer.

**Request**
- Method: `GET`
- Path: `/books/chapter`
- Query params:
  - `class` — e.g. `class-9` *(required)*
  - `subject` — e.g. `Science` *(required)*
  - `chapter` — e.g. `1` → maps to `Chapter 1.pdf` *(required unless `file` is given)*
  - `file` — e.g. `Answers.pdf` or `Prelims.pdf` → use exact filename *(required unless `chapter` is given)*

**Examples**
```
# Regular chapter
GET /books/chapter?class=class-9&subject=Science&chapter=3

# Answer key
GET /books/chapter?class=class-9&subject=Science&file=Answers.pdf

# Prelims
GET /books/chapter?class=class-9&subject=English&file=Prelims.pdf
```

**Response (200)**
```json
{
  "url": "https://questor-books.s3.ap-south-1.amazonaws.com/NCERT/class-9/Science/Chapter%201.pdf?X-Amz-...",
  "key": "NCERT/class-9/Science/Chapter 1.pdf",
  "expiresIn": 900
}
```

**Response (400)** — missing params
```json
{ "error": "Missing required query params: chapter" }
```

**Response (404)** — chapter not found in S3
```json
{ "error": "Chapter not found: NCERT/class-9/Science/Chapter 99.pdf", "hint": "Check class, subject, and chapter values." }
```

**Handler**: `src/handlers/get_chapter_url.py`

---

## GET /books/structure

**Purpose**: Returns the complete NCERT folder hierarchy from S3 so the frontend can build subject and chapter navigation menus.

**Request**
- Method: `GET`
- Path: `/books/structure`
- Params: none

**Response**
```json
{
  "NCERT": {
    "class-7": {},
    "class-8": {},
    "class-9": {
      "English": [
        "Chapter 1.pdf",
        "Chapter 2.pdf",
        "Chapter 3.pdf",
        "Chapter 4.pdf",
        "Chapter 5.pdf",
        "Chapter 6.pdf",
        "Chapter 7.pdf",
        "Chapter 8.pdf",
        "Chapter 9.pdf",
        "Prelims.pdf"
      ],
      "Science": [
        "Answers.pdf",
        "Chapter 1.pdf",
        "Chapter 2.pdf",
        "Chapter 3.pdf",
        "Chapter 4.pdf",
        "Chapter 5.pdf",
        "Chapter 6.pdf",
        "Chapter 7.pdf",
        "Chapter 8.pdf",
        "Chapter 9.pdf",
        "Chapter 10.pdf",
        "Chapter 11.pdf",
        "Chapter 12.pdf",
        "Prelims.pdf"
      ]
    }
  }
}
```

**Handler**: `src/handlers/get_structure.py`
**S3 source**: `questor-books` → prefix `NCERT/`

---

_More endpoints will be added here as they are implemented._
