from enum import Enum
from typing import Union

from sqlalchemy.orm import Session

from app.services.auth_service import auth_service


# Mapping CRUD-like semantic labels to permission action keywords.
_CRUD_ACTION_TO_PERMISSION = {
    "CREATE": "create",
    "READ": "read",
    "READ_ONE": "read",
    "READ_ALL": "read",
    "UPDATE": "update",
    "DELETE": "delete",
}


def ensure_permission(
    db: Session,
    user_id: str,
    resource: str,
    action: str,
) -> None:
    """
    Ensure the user has the requested permission; raise HTTP 403 otherwise.
    """
    auth_service.require_permission(db=db, user_id=user_id, resource=resource, action=action)


def ensure_crud_permission(
    db: Session,
    user_id: str,
    resource: str,
    action: Union[str, Enum],
) -> None:
    """
    Map conventional CRUD actions to permission keywords and ensure access.
    """
    if isinstance(action, Enum):
        action_key = action.value
    else:
        action_key = str(action)

    action_key = action_key.upper()
    permission = _CRUD_ACTION_TO_PERMISSION.get(action_key)
    if not permission:
        # Fall back to using the action value directly.
        permission = action_key.lower()

    ensure_permission(db=db, user_id=user_id, resource=resource, action=permission)
