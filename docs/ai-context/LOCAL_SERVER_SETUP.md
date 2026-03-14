# Questor Backend — Local Server Setup

## What This Is
This is the backend for **Questor**, an AI-powered NCERT school learning app.
The local server simulates the AWS Lambda + API Gateway environment so the frontend can be built and tested without deploying to AWS.

## Prerequisites
- Python 3.10+
- Access to the team's AWS credentials (ask Milan/Jagadhesh)

## Setup Steps

```bash
# 1. Go to the backend folder
cd Questor-backend

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash
# source .venv/bin/activate         # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
```

Open `.env` and fill in:
```
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=<ask the team>
AWS_SECRET_ACCESS_KEY=<ask the team>
S3_BUCKET_NAME=questor-books
S3_NCERT_PREFIX=NCERT/
```

```bash
# 5. Start the local server
python local_server.py
```

Server runs at: `http://localhost:8000`

## Available Endpoints

See `docs/api/README.md` for the full, always up-to-date API reference.

## Notes
- This local server is for development only — not for production.
- Stop the server with `Ctrl+C`.
- If you add a new endpoint, also register it in `local_server.py` under `do_GET`.
