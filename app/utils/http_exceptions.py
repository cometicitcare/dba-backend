from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from fastapi import HTTPException, status
from pydantic import ValidationError


def format_pydantic_errors(exc: ValidationError) -> list[tuple[str | None, str]]:
    """Convert a Pydantic ValidationError into a list of (field, message) tuples."""
    results: list[tuple[str | None, str]] = []
    for error in exc.errors():
        loc = ".".join(str(item) for item in error.get("loc", []))
        msg = error.get("msg", "")
        results.append((loc or None, msg))
    return results or [(None, "Invalid payload data")]


def validation_error(
    errors: Iterable[Any],
    message: str = "Validation failed",
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> HTTPException:
    """Create an HTTPException with a consistent validation error payload."""
    # A bare string is iterable but should be treated as a single error message,
    # not iterated character-by-character.
    if isinstance(errors, str):
        errors = [errors]
    formatted = [_format_error(item) for item in errors]
    return HTTPException(
        status_code=status_code,
        detail={"message": message, "errors": formatted},
    )


def _format_error(data: Any) -> dict[str | None, str]:
    if isinstance(data, dict):
        field = data.get("field")
        message = data.get("message") or ""
        return {"field": field, "message": message}

    if isinstance(data, (list, tuple)) and len(data) == 2:
        field, message = data
        return {"field": str(field) if field is not None else None, "message": str(message)}

    return {"field": None, "message": str(data)}

