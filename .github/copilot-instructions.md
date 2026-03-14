# Copilot Instructions — Questor Backend (AWS Lambda)

## Project Overview
**Questor** is an AI-powered school learning app for the AWS Nova Hackathon.
This repo is the **backend** — AWS Lambda functions behind API Gateway that handle:
- Auth validation & user logic
- Page context assembly for NCERT RAG
- Prompt building and AI invocation via Amazon Bedrock (Nova Lite)
- Student and teacher feature APIs

## Architecture
```
Flutter App
     │
 AWS Cognito (Auth)
     │
 API Gateway
     │
 AWS Lambda
  ├── User / Role Logic
  ├── Page Context Handler
  ├── Prompt Builder
  └── Bedrock Invocation
     │
 Amazon S3 (NCERT PDFs)     Amazon DynamoDB
     │                             │
 Amazon Bedrock (Nova Lite)
     │
 AI Response (page-grounded)
```

## Tech Stack
| Layer | Technology |
|---|---|
| Runtime | Node.js or Python |
| Hosting | AWS Lambda + API Gateway |
| Auth | AWS Cognito (JWT validation in Lambda) |
| AI | Amazon Bedrock — Nova Lite model |
| Storage | Amazon S3 (NCERT books) |
| Database | Amazon DynamoDB |

## Domain Concepts
| Term | Meaning |
|---|---|
| `pageContext` | Text from prev/current/next NCERT page sent as AI context |
| `doubt` | Student's question to the AI |
| `hotQuestion` | AI-generated challenging question from page content |
| `quiz` | AI-generated self-assessment for a student |
| `chapterSummary` | AI summary of a NCERT chapter (teacher feature) |
| `teachingGuidance` | AI suggestions on difficult topics and pacing |
| `questionBank` | AI-generated questions for tests/assignments |
| `learningGap` | AI-identified concept the student is struggling with |

## NCERT Page-Level RAG — Core Pattern

This is the central AI pattern. All student chatbot calls follow this flow:

1. Flutter sends: `studentQuestion` + `pageContext` (prev/current/next page text) + `classLevel` + `subject`.
2. Lambda assembles the grounded prompt (see template below).
3. Lambda calls Bedrock Nova Lite with the prompt.
4. Response is returned to Flutter.

### Standard Student Prompt Template
```
You are a tutor helping a {classLevel} student studying {subject}.

Answer ONLY using the provided NCERT page content below.
If the answer is not in the provided content, say:
"This topic is explained in another section of the book."

NCERT Page Context:
Page {pageNum - 1}: {previousPageText}
Page {pageNum}: {currentPageText}
Page {pageNum + 1}: {nextPageText}

Student Question:
{studentQuestion}

Explain in simple language appropriate for {classLevel}.
Maximum 150 words.
```

### Standard Teacher Prompt Template
```
You are a teaching assistant for a {classLevel} {subject} class.

Based on the following NCERT chapter content:
{chapterText}

Provide:
1. A brief chapter summary
2. Concepts students typically find difficult
3. 5 high-quality questions for a test or assignment

Keep the language and difficulty appropriate for {classLevel}.
```

## API Endpoints

### Student
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/student/doubt` | Solve a student doubt using page context |
| `POST` | `/api/student/hotquestions` | Generate hot questions from current page |
| `POST` | `/api/student/clarify` | Clarify a concept from current page |
| `POST` | `/api/student/quiz` | Generate a self-assessment quiz from page |

### Teacher
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/teacher/summarize` | Summarize a NCERT chapter |
| `POST` | `/api/teacher/guidance` | Get teaching guidance for a chapter |
| `POST` | `/api/teacher/questions` | Generate test questions for a chapter |
| `GET`  | `/api/teacher/insights/:studentId` | Get learning gap insights for a student |

### Shared
| Method | Path | Description |
|---|---|---|
| `GET`  | `/api/books` | List available NCERT books for a class/subject |
| `GET`  | `/api/books/:bookId/url` | Get pre-signed S3 URL for a PDF |

## Project Structure
```
src/
  handlers/       # Lambda entry points (thin — delegate to services)
  services/
    ai/           # All Bedrock Nova calls
    books/        # S3 URL generation, book metadata
    prompt/       # Prompt builders (student, teacher)
  middleware/     # JWT auth, role checks, input validation
  models/         # DynamoDB data models
  utils/
  config/         # Env var loading and validation
```

## RBAC — Role-Based Access Control
- Validate Cognito JWT on every Lambda invocation.
- Extract `role` from the token claims.
- `/api/student/*` endpoints must reject `teacher` role and vice versa.
- Log all unauthorized access attempts.

## S3 PDF Access
- Never return a permanent S3 URL. Always generate a **pre-signed URL** with a short expiry (e.g., 15 min).
- PDFs are organized: `s3://questor-ncert-books/class-{N}/{subject}.pdf`
- Lambda needs `s3:GetObject` on the books bucket only.

## Error Handling
- Use centralized error middleware.
- Return consistent shape: `{ "success": bool, "data": {}, "error": null }`.
- Never expose stack traces in responses.
- Log errors with: `requestId`, `userId`, `role`, `feature`.

## Anti-Hallucination Safeguards
- Always include the class level in the prompt (`classLevel` field is required).
- Prompt must explicitly instruct the model to stay within page context.
- Prompt must instruct the model to redirect off-topic questions.
- Set `max_tokens` to control response length (150–300 words for student, 400 for teacher).

## Demo Data
For the hackathon presentation:
- 3 schools × 3 classes × 5 students + 1 teacher each = seeded in DynamoDB.
- Provide a `/api/demo/seed` endpoint (disable in prod) that populates this data.

## Git Conventions
- Commit format: `type(scope): short description`
  - `feat(doubt): implement page-context prompt builder`
  - `feat(books): add pre-signed S3 URL generation`
  - `fix(auth): reject teacher JWT on student endpoints`

## Do's and Don'ts
| ✅ Do | ❌ Don't |
|---|---|
| Always include classLevel in every AI prompt | Let the LLM guess the class level |
| Use pre-signed S3 URLs | Expose permanent S3 URLs |
| Validate role from Cognito JWT | Trust role from the request body |
| Centralize all Bedrock calls in `src/services/ai/` | Scatter SDK calls in handlers |
| Set `max_tokens` on every Bedrock call | Allow unbounded AI responses |
