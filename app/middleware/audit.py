# app/middleware/audit.py
from __future__ import annotations

from typing import Optional

from fastapi import Request
from fastapi.responses import Response
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.session import SessionLocal
from app.services.audit_service import audit_service
from app.services.auth_service import auth_service


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user_id = self._resolve_user_id(request)
        session_id = self._resolve_session_id(request)
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        token, _ = audit_service.begin_request(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            route=request.url.path,
            method=request.method,
        )

        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            status_code = response.status_code if response else 500
            try:
                await run_in_threadpool(self._log_api_call, status_code)
            finally:
                audit_service.end_request(token)

    def _resolve_user_id(self, request: Request) -> Optional[str]:
        token = request.cookies.get("access_token")
        if not token:
            return None
        try:
            return auth_service.decode_token(token)
        except Exception:
            return None

    def _resolve_session_id(self, request: Request) -> Optional[str]:
        if session_cookie := request.cookies.get("session_id"):
            return session_cookie
        if header_value := request.headers.get("X-Session-Id"):
            return header_value
        if auth_header := request.headers.get("Authorization"):
            return auth_header.split(" ", 1)[-1]
        return None

    def _log_api_call(self, status_code: int) -> None:
        db = SessionLocal()
        try:
            db.info["skip_audit"] = True
            audit_service.log_api_call(db, status_code=status_code)
        except Exception:
            db.rollback()
        finally:
            db.close()
