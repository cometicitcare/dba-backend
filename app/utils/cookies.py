from fastapi import Response, Request
from app.core.config import settings

def set_auth_cookies(response: Response, *, access_token: str, refresh_token: str) -> Response:
    # Access token cookie (short-lived)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        domain=settings.COOKIE_DOMAIN,
        path=settings.COOKIE_PATH,
    )
    # Refresh token cookie (long-lived)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        domain=settings.COOKIE_DOMAIN,
        path=settings.COOKIE_PATH,
    )
    return response

def clear_auth_cookies(response: Response) -> Response:
    for k in ("access_token", "refresh_token"):
        response.delete_cookie(
            key=k,
            domain=settings.COOKIE_DOMAIN,
            path=settings.COOKIE_PATH,
        )
    return response
