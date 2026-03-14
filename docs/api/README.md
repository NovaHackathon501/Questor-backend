# Questor Backend — API Reference

> **AI Agents**: Per `docs/ai-context/AI_UPDATE_INSTRUCTIONS.md`, update this file every time an endpoint is added, changed, or removed.

**Base URL (local)**: `http://localhost:8000`
**Base URL (production)**: _To be added after API Gateway deployment_

---

## Endpoints Summary

| Method | Path | Description |
|---|---|---|
| GET | `/books/structure` | Returns full NCERT folder tree (all classes, subjects, chapters) |
| GET | `/books/chapter` | Returns a pre-signed S3 URL for a specific chapter PDF |

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
