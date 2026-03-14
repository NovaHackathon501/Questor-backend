# AI Agent Instructions — Keeping Docs Up To Date

## Your Responsibility
Whenever you create, modify, or remove a backend endpoint, you **MUST** update `docs/api/README.md`.
Do not leave README.md out of sync with the actual code.

## When to Update

| Action | What to update |
|---|---|
| New endpoint added | Add it to the **Endpoints** table + add a full section with request/response |
| Endpoint modified (path, params, response shape) | Update the relevant section |
| Endpoint removed | Remove its section and table row |

## How to Update `docs/api/README.md`

1. Open `docs/api/README.md`
2. Add/update the endpoint row in the **Endpoints Summary** table
3. Add/update the full endpoint section below (method, path, params, example response)
4. Keep examples real — copy actual output from local testing, not invented JSON

## README Format to Follow

Each endpoint section must follow this format exactly:

```
### [METHOD] /path/to/endpoint

**Purpose**: One sentence describing what this responds with.

**Request**
- Method: GET / POST
- Path: /exact/path
- Query params (if any): `?param=value`

**Response**
\```json
{ "actual": "example output" }
\```
```

## What NOT to Do
- Do not leave placeholder text like "coming soon" or "TODO"
- Do not invent example responses — use real output
- Do not skip updating README when you add code changes
