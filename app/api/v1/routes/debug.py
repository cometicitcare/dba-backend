"""
Test endpoint to debug RBAC context
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.user import UserAccount
from app.api.auth_dependencies import get_user_access_context

router = APIRouter()


@router.get("/debug/user/{username}")
def debug_user_context(username: str, db: Session = Depends(get_db)):
    """Debug endpoint to test RBAC context retrieval"""
    try:
        user = db.query(UserAccount).filter(UserAccount.ua_username == username).first()
        if not user:
            return {"error": f"User {username} not found"}
        
        context = get_user_access_context(db, user)
        
        return {
            "success": True,
            "user": {
                "ua_user_id": user.ua_user_id,
                "ua_username": user.ua_username,
                "ua_email": user.ua_email
            },
            "context": context
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
