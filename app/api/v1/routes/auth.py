from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from app.api.deps import get_db
from app.schemas.auth import LoginIn, Token
from app.services.auth_service import auth_service
from app.utils.cookies import set_auth_cookies, clear_auth_cookies
from app.core.config import settings
from fastapi import HTTPException, status

router = APIRouter()

@router.post("/login")
async def login(data: LoginIn, response: Response, db: AsyncSession = Depends(get_db)):
    access, refresh = await auth_service.authenticate(db, data.username, data.password)
    set_auth_cookies(response, access_token=access, refresh_token=refresh)
    # We can return a minimal body; FE won't need tokens in JSON
    return {"ok": True}

@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    # Read refresh token from cookie
    refresh = request.cookies.get("refresh_token")
    if not refresh:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    # Validate refresh token & subject
    try:
        payload = jwt.decode(refresh, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("typ") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        user_id = str(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # Issue a new access token (optionally rotate refresh as well)
    new_access = jwt.encode(
        {"sub": user_id, "typ": "access"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    # keep max-age via cookie options; you can also rotate refresh if you prefer
    set_auth_cookies(response, access_token=new_access, refresh_token=refresh)
    return {"ok": True}

@router.post("/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"ok": True}
