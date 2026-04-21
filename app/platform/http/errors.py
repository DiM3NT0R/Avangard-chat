from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class ValidationErrorItem(BaseModel):
    type: str
    loc: list[str | int]
    msg: str
    input: Any | None = None
    ctx: dict[str, Any] | None = None


class ValidationErrorResponse(BaseModel):
    detail: list[ValidationErrorItem]


_ERROR_RESPONSES: dict[int, dict[str, Any]] = {
    400: {
        "model": ErrorResponse,
        "description": "Bad Request",
    },
    401: {
        "model": ErrorResponse,
        "description": "Unauthorized",
    },
    403: {
        "model": ErrorResponse,
        "description": "Forbidden",
    },
    404: {
        "model": ErrorResponse,
        "description": "Not Found",
    },
    422: {
        "model": ValidationErrorResponse,
        "description": "Validation Error",
    },
}


def error_responses(*status_codes: int) -> dict[int, dict[str, Any]]:
    return {code: _ERROR_RESPONSES[code] for code in status_codes}
