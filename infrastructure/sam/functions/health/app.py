"""SAM Lambda health handler (FR-INF-004).

Optional adapter for API Gateway-compatible local testing.
Primary demo uses the FastAPI container directly.
"""

from __future__ import annotations

import json
import os
import uuid


def lambda_handler(event, context):
  request_id = f"req_{uuid.uuid4().hex[:12]}"
  path = (event.get("path") or event.get("rawPath") or "/").rstrip("/") or "/"

  if path.endswith("/health"):
    body = {
      "status": "ok",
      "service": "fluentedge-sam-adapter",
      "request_id": request_id,
      "dependencies": {
        "api_proxy": {
          "status": "not_configured",
          "message": (
            "SAM adapter is optional; use FastAPI at "
            f"{os.environ.get('API_URL', 'http://localhost:8000')} for full stack"
          ),
        }
      },
      "model_ready": False,
    }
    return _response(200, body)

  if path.endswith("/predict"):
    body = {
      "request_id": request_id,
      "error": {
        "code": "NOT_IMPLEMENTED",
        "message": "Use the FastAPI /predict endpoint in the primary local demo.",
      },
    }
    return _response(501, body)

  body = {
    "request_id": request_id,
    "error": {"code": "NOT_FOUND", "message": f"Unknown path: {path}"},
  }
  return _response(404, body)


def _response(status_code: int, body: dict) -> dict:
  return {
    "statusCode": status_code,
    "headers": {"Content-Type": "application/json"},
    "body": json.dumps(body),
  }
