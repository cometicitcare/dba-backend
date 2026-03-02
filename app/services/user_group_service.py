from sqlalchemy.orm import Session
from app.models.user_group import UserGroup
from app.schemas.user_group import UserGroupCreate, UserGroupUpdate
from app.utils.http_exceptions import validation_error
from datetime import datetime

class UserGroupService:

    def add_user_to_group(self, db: Session, user_group: UserGroupCreate):
        # Check if the user is already in the group
        existing_user_group = db.query(UserGroup).filter(
            UserGroup.user_id == user_group.user_id,
            UserGroup.group_id == user_group.group_id
        ).first()
        if existing_user_group:
            raise validation_error([("user_id", "User is already in this group.")])

        # Add the user to the group
        new_user_group = UserGroup(
            user_id=user_group.user_id,
            group_id=user_group.group_id,
            created_by=user_group.created_by,
            updated_by=user_group.created_by,  # Initially the same as created_by
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        db.add(new_user_group)
        db.commit()
        db.refresh(new_user_group)
        return new_user_group

    def update_user_group(self, db: Session, user_id: str, group_id: int, user_group: UserGroupUpdate):
        # Find the user-group relationship
        existing_user_group = db.query(UserGroup).filter(
            UserGroup.user_id == user_id,
            UserGroup.group_id == group_id
        ).first()
        if not existing_user_group:
            raise validation_error([("user_group", "User is not in this group.")])
        
        # Update the user-group relationship
        existing_user_group.updated_by = user_group.updated_by
        existing_user_group.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(existing_user_group)
        return existing_user_group

    def remove_user_from_group(self, db: Session, user_id: str, group_id: int):
        # Find the user-group relationship
        user_group = db.query(UserGroup).filter(
            UserGroup.user_id == user_id,
            UserGroup.group_id == group_id
        ).first()
        if not user_group:
            raise validation_error([("user_group", "User is not in this group.")])
        
        # Remove the user from the group
        db.delete(user_group)
        db.commit()
        return user_group

# Initialize the service
user_group_service = UserGroupService()