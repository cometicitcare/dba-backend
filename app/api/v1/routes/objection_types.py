from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission
from app.api.deps import get_db
from app.models.user import UserAccount
from app.schemas.objection_type import ObjectionTypeOut
from app.repositories.objection_type_repo import objection_type_repo

router = APIRouter()


@router.get(
    "/types",
    response_model=List[ObjectionTypeOut],
)
def list_objection_types(
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Get list of objection types.
    
    By default, only returns active types.
    Use is_active=false to get all types including inactive ones.
    """
    objection_types = objection_type_repo.list(
        db,
        skip=0,
        limit=100,
        is_active=is_active
    )
    
    return [ObjectionTypeOut.model_validate(ot) for ot in objection_types]
