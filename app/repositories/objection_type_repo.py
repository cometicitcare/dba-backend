from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.objection_type import ObjectionType
from app.schemas.objection_type import ObjectionTypeCreate, ObjectionTypeUpdate


class ObjectionTypeRepository:
    """Data access helpers for objection type records."""

    def get(self, db: Session, ot_id: int) -> Optional[ObjectionType]:
        """Get objection type by ID"""
        return (
            db.query(ObjectionType)
            .filter(ObjectionType.ot_id == ot_id, ObjectionType.ot_is_deleted.is_(False))
            .first()
        )

    def get_by_code(self, db: Session, ot_code: str) -> Optional[ObjectionType]:
        """Get objection type by code"""
        return (
            db.query(ObjectionType)
            .filter(
                ObjectionType.ot_code == ot_code,
                ObjectionType.ot_is_deleted.is_(False)
            )
            .first()
        )

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[ObjectionType]:
        """List objection types with filters"""
        query = db.query(ObjectionType).filter(ObjectionType.ot_is_deleted.is_(False))

        if is_active is not None:
            query = query.filter(ObjectionType.ot_is_active == is_active)

        return (
            query.order_by(ObjectionType.ot_code)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(
        self,
        db: Session,
        *,
        is_active: Optional[bool] = None
    ) -> int:
        """Count objection types with filters"""
        query = db.query(ObjectionType).filter(ObjectionType.ot_is_deleted.is_(False))

        if is_active is not None:
            query = query.filter(ObjectionType.ot_is_active == is_active)

        return query.count()

    def create(
        self, 
        db: Session, 
        *, 
        data: ObjectionTypeCreate,
        created_by: Optional[str] = None
    ) -> ObjectionType:
        """Create new objection type"""
        objection_type = ObjectionType(
            ot_code=data.ot_code,
            ot_name_en=data.ot_name_en,
            ot_name_si=data.ot_name_si,
            ot_name_ta=data.ot_name_ta,
            ot_description=data.ot_description,
            ot_is_active=data.ot_is_active,
            ot_created_by=created_by
        )
        
        db.add(objection_type)
        db.commit()
        db.refresh(objection_type)
        return objection_type

    def update(
        self, 
        db: Session, 
        *, 
        objection_type: ObjectionType,
        data: ObjectionTypeUpdate,
        updated_by: Optional[str] = None
    ) -> ObjectionType:
        """Update objection type"""
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(objection_type, field, value)
        
        objection_type.ot_updated_by = updated_by
        
        db.commit()
        db.refresh(objection_type)
        return objection_type

    def delete(
        self, 
        db: Session, 
        *, 
        objection_type: ObjectionType,
        deleted_by: Optional[str] = None
    ) -> ObjectionType:
        """Soft delete objection type"""
        objection_type.ot_is_deleted = True
        objection_type.ot_updated_by = deleted_by
        
        db.commit()
        db.refresh(objection_type)
        return objection_type


objection_type_repo = ObjectionTypeRepository()
