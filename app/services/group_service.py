from sqlalchemy.orm import Session
from app.models.group import Group
from app.schemas.group import GroupCreate, GroupUpdate
from app.utils.http_exceptions import validation_error
from datetime import datetime

class GroupService:
    
    def create_group(self, db: Session, group: GroupCreate):
        # Check if group name already exists
        existing_group = db.query(Group).filter(Group.group_name == group.group_name).first()
        if existing_group:
            raise validation_error([("group_name", "Group name already exists.")])
        
        # Create a new group
        new_group = Group(
            group_name=group.group_name,
            group_description=group.group_description,
            created_by=group.created_by,
            updated_by=group.created_by,  # Initially the same as created_by
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        return new_group

    def update_group(self, db: Session, group_id: int, group: GroupUpdate):
        # Find the group by ID
        existing_group = db.query(Group).filter(Group.group_id == group_id).first()
        if not existing_group:
            raise validation_error([("group_id", "Group not found.")])
        
        # Update the group details
        existing_group.group_name = group.group_name
        existing_group.group_description = group.group_description
        existing_group.updated_by = group.updated_by
        existing_group.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(existing_group)
        return existing_group

    def get_group_by_id(self, db: Session, group_id: int):
        # Retrieve a group by its ID
        return db.query(Group).filter(Group.group_id == group_id).first()

    def get_groups(self, db: Session, page: int = 1, limit: int = 20):
        # Retrieve a list of groups with pagination
        skip = (page - 1) * limit
        return db.query(Group).offset(skip).limit(limit).all()

    def count_groups(self, db: Session):
        # Count the total number of groups
        return db.query(Group).count()

    def delete_group(self, db: Session, group_id: int):
        # Delete a group
        group_to_delete = db.query(Group).filter(Group.group_id == group_id).first()
        if not group_to_delete:
            raise validation_error([("group_id", "Group not found.")])
        
        db.delete(group_to_delete)
        db.commit()
        return group_to_delete

# Initialize the service
group_service = GroupService()