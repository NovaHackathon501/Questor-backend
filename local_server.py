"""
Purpose : Lightweight local HTTP server for testing Lambda handlers with Postman.
          NOT for production — only for local development.
Usage   : python local_server.py
Endpoints:
  GET  http://localhost:8000/books/structure
  GET  http://localhost:8000/books/chapter?class=class-9&subject=Science&chapter=1
  POST http://localhost:8000/ai/doubt
"""

import sys
import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Allow imports from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from handlers.get_structure   import handler as get_structure_handler
from handlers.get_chapter_url import handler as get_chapter_url_handler
from handlers.ai_doubt        import handler as ai_doubt_handler

PORT = 8000


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path

        # Flatten parse_qs values (returns lists by default)
        raw_params = parse_qs(parsed.query)
        params = {k: v[0] for k, v in raw_params.items()}

        # ── Route: GET /books/structure ───────────────────────────────────────
        if path == "/books/structure":
            result = get_structure_handler({}, None)
            self._send(result["statusCode"], result["body"])

        # ── Route: GET /books/chapter?class=&subject=&chapter= ────────────────
        elif path == "/books/chapter":
            event  = {"queryStringParameters": params}
            result = get_chapter_url_handler(event, None)
            self._send(result["statusCode"], result["body"])

        else:
            self._send(404, json.dumps({"error": f"Route not found: {path}"}))

    def do_POST(self):
        parsed = urlparse(self.path)
        path   = parsed.path

        # Read request body
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length).decode("utf-8") if length else "{}"

        # ── Route: POST /ai/doubt ─────────────────────────────────────────────────
        if path == "/ai/doubt":
            event  = {"body": body}
            result = ai_doubt_handler(event, None)
            self._send(result["statusCode"], result["body"])

        else:
            self._send(404, json.dumps({"error": f"Route not found: {path}"}))

    def _send(self, status: int, body: str):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format, *args):
        print(f"  [{self.command}] {self.path} → {args[1]}")


if __name__ == "__main__":
    print(f"\n🚀 Local server running at http://localhost:{PORT}")
    print(f"   GET  http://localhost:{PORT}/books/structure")
    print(f"   GET  http://localhost:{PORT}/books/chapter?class=class-9&subject=Science&chapter=1")
    print(f"   POST http://localhost:{PORT}/ai/doubt")
    print(f"\n   Press Ctrl+C to stop.\n")

    server = HTTPServer(("localhost", PORT), RequestHandler)
    server.serve_forever()
