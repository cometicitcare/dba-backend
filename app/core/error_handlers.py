from typing import Any, Iterable

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

def register_exception_handlers(app: FastAPI) -> None:
    """Attach application-wide exception handlers with consistent error payloads."""

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [_normalize_pydantic_error(err) for err in exc.errors()]
        return _build_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation failed",
            errors=errors,
        )

    @app.exception_handler(ValidationError)
    async def handle_validation_error(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        errors = [_normalize_pydantic_error(err) for err in exc.errors()]
        return _build_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation failed",
            errors=errors,
        )

    @app.exception_handler(ValueError)
    async def handle_value_error(request: Request, exc: ValueError) -> JSONResponse:
        return _build_response(
            status.HTTP_400_BAD_REQUEST,
            "Validation failed",
            [_make_error(None, str(exc))],
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        message, errors = _extract_from_detail(exc.detail)
        if not errors and message:
            errors = [_make_error(None, message)]
        return _build_response(exc.status_code, message or "Request failed", errors)

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # TODO: add structured logging once logging stack is in place.
        import traceback
        print(f"❌ UNHANDLED EXCEPTION: {type(exc).__name__}: {str(exc)}")
        traceback.print_exc()
        return _build_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Internal server error",
            [_make_error(None, f"{type(exc).__name__}: {str(exc)}")],
        )


def _build_response(
    status_code: int,
    message: str,
    errors: Iterable[dict[str | None, str]],
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "errors": list(errors),
        },
    )


def _extract_from_detail(
    detail: Any,
) -> tuple[str | None, list[dict[str | None, str]]]:
    if detail is None:
        return None, []

    if isinstance(detail, dict):
        message = detail.get("message") or detail.get("detail")
        errors = detail.get("errors")
        if isinstance(errors, list):
            return message, [_normalize_error(item) for item in errors]
        return message, []

    if isinstance(detail, list):
        return (
            "Validation failed",
            [_normalize_error(item) for item in detail],
        )

    return str(detail), []


def _normalize_pydantic_error(error: dict[str, Any]) -> dict[str | None, str]:
    loc = error.get("loc") or []
    field = _format_location(loc)
    message = error.get("msg") or "Invalid input."
    return _make_error(field, message)


def _normalize_error(data: Any) -> dict[str | None, str]:
    if isinstance(data, dict):
        field = data.get("field")
        message = data.get("message") or data.get("msg") or "Invalid input."
        if not field and "loc" in data:
            field = _format_location(data["loc"])
        return _make_error(field, message)

    if isinstance(data, str):
        return _make_error(None, data)

    return _make_error(None, str(data))


def _format_location(location: Any) -> str | None:
    if isinstance(location, (list, tuple)):
        filtered = [str(part) for part in location if part not in {"body", "query", "path"}]
        if filtered:
            return ".".join(filtered)
        if location:
            return str(location[-1])
        return None
    if location is None:
        return None
    return str(location)


def _make_error(field: str | None, message: str) -> dict[str | None, str]:
    return {"field": field, "message": message}
