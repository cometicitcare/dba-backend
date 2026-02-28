# app/repositories/gov_officers_repo.py
from typing import List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.gov_officers import GovOfficer
from app.schemas.gov_officers import GovOfficerCreate, GovOfficerUpdate


class GovOfficerRepository:
    """Data-access layer for the ``cmm_gov_officers`` table."""

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_by_id(self, db: Session, go_id: int) -> Optional[GovOfficer]:
        return (
            db.query(GovOfficer)
            .filter(
                GovOfficer.go_id == go_id,
                GovOfficer.go_is_deleted.is_(False),
            )
            .first()
        )

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search_key: Optional[str] = None,
    ) -> Tuple[List[GovOfficer], int]:
        query = db.query(GovOfficer).filter(GovOfficer.go_is_deleted.is_(False))

        if search_key and search_key.strip():
            pattern = f"%{search_key.strip()}%"
            query = query.filter(
                or_(
                    GovOfficer.go_first_name.ilike(pattern),
                    GovOfficer.go_last_name.ilike(pattern),
                    GovOfficer.go_title.ilike(pattern),
                    GovOfficer.go_contact_number.ilike(pattern),
                    GovOfficer.go_email.ilike(pattern),
                    GovOfficer.go_address.ilike(pattern),
                    GovOfficer.go_id_number.ilike(pattern),
                )
            )

        total = query.count()
        records = (
            query.order_by(GovOfficer.go_id.desc()).offset(skip).limit(limit).all()
        )
        return records, total

    # ── Mutations ─────────────────────────────────────────────────────────────

    def create(
        self,
        db: Session,
        *,
        obj_in: GovOfficerCreate,
        created_by: Optional[str] = None,
    ) -> GovOfficer:
        db_obj = GovOfficer(
            go_title=obj_in.go_title,
            go_first_name=obj_in.go_first_name,
            go_last_name=obj_in.go_last_name,
            go_contact_number=obj_in.go_contact_number,
            go_email=obj_in.go_email,
            go_address=obj_in.go_address,
            go_id_number=obj_in.go_id_number,
            go_created_by=created_by,
            go_updated_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: GovOfficer,
        obj_in: GovOfficerUpdate,
        updated_by: Optional[str] = None,
    ) -> GovOfficer:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db_obj.go_updated_by = updated_by
        db_obj.go_version_number = (db_obj.go_version_number or 1) + 1
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(
        self,
        db: Session,
        *,
        go_id: int,
        deleted_by: Optional[str] = None,
    ) -> Optional[GovOfficer]:
        db_obj = self.get_by_id(db, go_id)
        if not db_obj:
            return None
        db_obj.go_is_deleted = True
        db_obj.go_updated_by = deleted_by
        db.commit()
        db.refresh(db_obj)
        return db_obj


gov_officers_repo = GovOfficerRepository()
