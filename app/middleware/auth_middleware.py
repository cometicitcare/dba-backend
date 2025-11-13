from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer 
import jwt
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        group: str = payload.get("group")
        
        if user_id is None or role is None or group is None:
            raise HTTPException(status_code=403, detail="Invalid token")

        return {"user_id": user_id, "role": role, "group": group}

    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")