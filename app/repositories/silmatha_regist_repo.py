# app/repositories/silmatha_regist_repo.py
from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.silmatha_regist import SilmathaRegist
from app.models.user import UserAccount
from app.schemas import silmatha_regist as schemas


class SilmathaRegistRepository:
    """
    Data access helper for the `silmatha_regist` table.

    This repository keeps the legacy functional interface used elsewhere in the
    codebase while encapsulating repeated logic such as registration number
    generation and version updates.
    """

    def generate_next_regn(self, db: Session) -> str:
        """
        Generate the next registration number in format: SIL{YEAR}{SEQUENCE}.

        Example: SIL2025000001, SIL2025000002, etc.
        Total length: SIL(3) + YEAR(4) + SEQUENCE(6) = 13 characters.
        """
        current_year = datetime.utcnow().year
        prefix = f"SIL{current_year}"

        latest = (
            db.query(SilmathaRegist)
            .filter(SilmathaRegist.sil_regn.like(f"{prefix}%"))
            .order_by(SilmathaRegist.sil_regn.desc())
            .first()
        )

        if latest:
            try:
                sequence_part = latest.sil_regn[len(prefix) :]
                last_sequence = int(sequence_part)
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1

        return f"{prefix}{next_sequence:06d}"

    def generate_next_reprint_form_no(self, db: Session) -> str:
        """
        Generate the next reprint form number in format: SILR{YEAR}{SEQUENCE}.

        Example: SILR2025000001, SILR2025000002, etc.
        Total length: SILR(4) + YEAR(4) + SEQUENCE(6) = 14 characters.
        """
        current_year = datetime.utcnow().year
        prefix = f"SILR{current_year}"

        latest = (
            db.query(SilmathaRegist)
            .filter(SilmathaRegist.sil_reprint_form_no.like(f"{prefix}%"))
            .order_by(SilmathaRegist.sil_reprint_form_no.desc())
            .first()
        )

        if latest:
            try:
                sequence_part = latest.sil_reprint_form_no[len(prefix) :]
                last_sequence = int(sequence_part)
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1

        return f"{prefix}{next_sequence:06d}"

    def get_by_id(self, db: Session, sil_id: int):
        return (
            db.query(SilmathaRegist)
            .filter(
                SilmathaRegist.sil_id == sil_id,
                SilmathaRegist.sil_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_regn(self, db: Session, sil_regn: str):
        return (
            db.query(SilmathaRegist)
            .filter(
                SilmathaRegist.sil_regn == sil_regn,
                SilmathaRegist.sil_is_deleted.is_(False),
            )
            .first()
        )

    def get_raw_by_regn(self, db: Session, sil_regn: str):
        """Return a Silmatha record by registration number without filtering deleted rows."""
        return (
            db.query(SilmathaRegist)
            .filter(SilmathaRegist.sil_regn == sil_regn)
            .first()
        )

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search_key: Optional[str] = None,
        vh_trn: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        workflow_status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        current_user: Optional[UserAccount] = None,
    ):
        """Get paginated silmatha records with optional search functionality across all text fields."""
        query = db.query(SilmathaRegist).filter(SilmathaRegist.sil_is_deleted.is_(False))

        # Location-based access control removed - use RBAC permissions instead
        # Access control is now handled by FastAPI dependencies (has_permission, has_role, etc.)

        # Apply search filter
        if search_key and search_key.strip():
            search_pattern = f"%{search_key.strip()}%"
            query = query.filter(
                or_(
                    SilmathaRegist.sil_regn.ilike(search_pattern),
                    SilmathaRegist.sil_gihiname.ilike(search_pattern),
                    SilmathaRegist.sil_fathrname.ilike(search_pattern),
                    SilmathaRegist.sil_mahananame.ilike(search_pattern),
                    SilmathaRegist.sil_birthpls.ilike(search_pattern),
                    SilmathaRegist.sil_province.ilike(search_pattern),
                    SilmathaRegist.sil_district.ilike(search_pattern),
                    SilmathaRegist.sil_korale.ilike(search_pattern),
                    SilmathaRegist.sil_pattu.ilike(search_pattern),
                    SilmathaRegist.sil_division.ilike(search_pattern),
                    SilmathaRegist.sil_vilage.ilike(search_pattern),
                    SilmathaRegist.sil_gndiv.ilike(search_pattern),
                    SilmathaRegist.sil_mobile.ilike(search_pattern),
                    SilmathaRegist.sil_email.ilike(search_pattern),
                    SilmathaRegist.sil_fathrsaddrs.ilike(search_pattern),
                    SilmathaRegist.sil_fathrsmobile.ilike(search_pattern),
                )
            )

        # Apply advanced filters
        if vh_trn:
            query = query.filter(SilmathaRegist.sil_robing_tutor_residence == vh_trn)
        
        if province:
            query = query.filter(SilmathaRegist.sil_province == province)
        
        if district:
            query = query.filter(SilmathaRegist.sil_district == district)
        
        if divisional_secretariat:
            query = query.filter(SilmathaRegist.sil_division == divisional_secretariat)
        
        if gn_division:
            query = query.filter(SilmathaRegist.sil_gndiv == gn_division)
        
        if temple:
            query = query.filter(SilmathaRegist.sil_robing_after_residence_temple == temple)
        
        if child_temple:
            query = query.filter(SilmathaRegist.sil_mahanatemple == child_temple)
        
        # Note: parshawaya is not applicable to silmatha records, so we ignore this filter
        
        if category:
            query = query.filter(SilmathaRegist.sil_cat == category)
        
        if status:
            query = query.filter(SilmathaRegist.sil_currstat == status)
        
        # Workflow status filter with automatic inclusion of COMPLETED records
        if workflow_status:
            # If COMPLETED is not already in the list, add it
            if workflow_status != "COMPLETED":
                query = query.filter(
                    or_(
                        SilmathaRegist.sil_workflow_status == workflow_status,
                        SilmathaRegist.sil_workflow_status == "COMPLETED"
                    )
                )
            else:
                query = query.filter(SilmathaRegist.sil_workflow_status == workflow_status)
        
        if date_from:
            query = query.filter(SilmathaRegist.sil_reqstdate >= date_from)
        
        if date_to:
            query = query.filter(SilmathaRegist.sil_reqstdate <= date_to)

        return (
            query.order_by(SilmathaRegist.sil_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def get_total_count(
        self, 
        db: Session, 
        search_key: Optional[str] = None,
        vh_trn: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        workflow_status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        current_user: Optional[UserAccount] = None,
    ):
        """Get total count of non-deleted silmatha records for pagination with optional search."""
        
        # Location-based access control removed - use RBAC permissions instead
        # Access control is now handled by FastAPI dependencies (has_permission, has_role, etc.)
        
        # Base query for count
        base_query = db.query(SilmathaRegist).filter(SilmathaRegist.sil_is_deleted.is_(False))

        # Apply search filter
        if search_key and search_key.strip():
            search_pattern = f"%{search_key.strip()}%"
            base_query = base_query.filter(
                or_(
                    SilmathaRegist.sil_regn.ilike(search_pattern),
                    SilmathaRegist.sil_gihiname.ilike(search_pattern),
                    SilmathaRegist.sil_fathrname.ilike(search_pattern),
                    SilmathaRegist.sil_mahananame.ilike(search_pattern),
                    SilmathaRegist.sil_birthpls.ilike(search_pattern),
                    SilmathaRegist.sil_province.ilike(search_pattern),
                    SilmathaRegist.sil_district.ilike(search_pattern),
                    SilmathaRegist.sil_korale.ilike(search_pattern),
                    SilmathaRegist.sil_pattu.ilike(search_pattern),
                    SilmathaRegist.sil_division.ilike(search_pattern),
                    SilmathaRegist.sil_vilage.ilike(search_pattern),
                    SilmathaRegist.sil_gndiv.ilike(search_pattern),
                    SilmathaRegist.sil_mobile.ilike(search_pattern),
                    SilmathaRegist.sil_email.ilike(search_pattern),
                    SilmathaRegist.sil_fathrsaddrs.ilike(search_pattern),
                    SilmathaRegist.sil_fathrsmobile.ilike(search_pattern),
                )
            )

        # Apply advanced filters (same as get_all)
        if vh_trn:
            base_query = base_query.filter(SilmathaRegist.sil_robing_tutor_residence == vh_trn)
        
        if province:
            base_query = base_query.filter(SilmathaRegist.sil_province == province)
        
        if district:
            base_query = base_query.filter(SilmathaRegist.sil_district == district)
        
        if divisional_secretariat:
            base_query = base_query.filter(SilmathaRegist.sil_division == divisional_secretariat)
        
        if gn_division:
            base_query = base_query.filter(SilmathaRegist.sil_gndiv == gn_division)
        
        if temple:
            base_query = base_query.filter(SilmathaRegist.sil_robing_after_residence_temple == temple)
        
        if child_temple:
            base_query = base_query.filter(SilmathaRegist.sil_mahanatemple == child_temple)
        
        # Note: parshawaya is not applicable to silmatha records, so we ignore this filter
        
        if category:
            base_query = base_query.filter(SilmathaRegist.sil_cat == category)
        
        if status:
            base_query = base_query.filter(SilmathaRegist.sil_currstat == status)
        
        # Workflow status filter with automatic inclusion of COMPLETED records
        if workflow_status:
            if workflow_status != "COMPLETED":
                base_query = base_query.filter(
                    or_(
                        SilmathaRegist.sil_workflow_status == workflow_status,
                        SilmathaRegist.sil_workflow_status == "COMPLETED"
                    )
                )
            else:
                base_query = base_query.filter(SilmathaRegist.sil_workflow_status == workflow_status)
        
        if date_from:
            base_query = base_query.filter(SilmathaRegist.sil_reqstdate >= date_from)
        
        if date_to:
            base_query = base_query.filter(SilmathaRegist.sil_reqstdate <= date_to)

        # Return count
        return base_query.count()

    def get_by_mobile(self, db: Session, sil_mobile: str):
        return (
            db.query(SilmathaRegist)
            .filter(
                SilmathaRegist.sil_mobile == sil_mobile,
                SilmathaRegist.sil_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_email(self, db: Session, sil_email: str):
        return (
            db.query(SilmathaRegist)
            .filter(
                SilmathaRegist.sil_email == sil_email,
                SilmathaRegist.sil_is_deleted.is_(False),
            )
            .first()
        )

    def create(self, db: Session, silmatha: schemas.SilmathaRegistCreate):
        # Auto-generate sil_regn if not provided or empty.
        if not silmatha.sil_regn or silmatha.sil_regn.strip() == "":
            silmatha.sil_regn = self.generate_next_regn(db)

        db_silmatha = SilmathaRegist(**silmatha.model_dump())
        now = datetime.utcnow()
        db_silmatha.sil_is_deleted = False
        db_silmatha.sil_version_number = 1
        db_silmatha.sil_created_at = now
        db_silmatha.sil_updated_at = now
        db_silmatha.sil_version = now
        # Set workflow status to PENDING for new records
        db_silmatha.sil_workflow_status = "PENDING"

        db.add(db_silmatha)
        db.commit()
        db.refresh(db_silmatha)
        return db_silmatha

    def update(self, db: Session, sil_regn: str, silmatha_update: schemas.SilmathaRegistUpdate):
        db_silmatha = self.get_by_regn(db, sil_regn)
        if not db_silmatha:
            return None

        update_data = silmatha_update.model_dump(exclude_unset=True)
        update_data.pop("sil_regn", None)
        update_data.pop("sil_version_number", None)

        for key, value in update_data.items():
            setattr(db_silmatha, key, value)

        db_silmatha.sil_version_number = (db_silmatha.sil_version_number or 1) + 1
        now = datetime.utcnow()
        db_silmatha.sil_updated_at = now
        db_silmatha.sil_version = now

        db.commit()
        db.refresh(db_silmatha)
        return db_silmatha

    def delete(self, db: Session, sil_regn: str, updated_by: Optional[str] = None):
        db_silmatha = self.get_by_regn(db, sil_regn)
        if not db_silmatha:
            return None

        db_silmatha.sil_is_deleted = True
        if updated_by:
            db_silmatha.sil_updated_by = updated_by
        db_silmatha.sil_version_number = (db_silmatha.sil_version_number or 1) + 1
        now = datetime.utcnow()
        db_silmatha.sil_updated_at = now
        db_silmatha.sil_version = now

        db.commit()
        db.refresh(db_silmatha)
        return db_silmatha


silmatha_regist_repo = SilmathaRegistRepository()
