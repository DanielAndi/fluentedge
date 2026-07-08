"""API error contract (FR-API-004)."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from api.app.metrics import ERROR_COUNT
from api.app.schemas import ErrorResponse


class APIError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "req_unknown")
    ERROR_COUNT.labels(code=exc.code).inc()
    body = ErrorResponse(
        request_id=request_id,
        error={"code": exc.code, "message": exc.message},
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())
