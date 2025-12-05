# app/repositories/direct_bhikku_high_repo.py
"""
Repository for Direct High Bhikku Registration
Handles data access operations for combined bhikku and high bhikku records
"""
import time
from typing import Any, Optional

from sqlalchemy import func, or_, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.direct_bhikku_high import DirectBhikkuHigh
from app.schemas.direct_bhikku_high import DirectBhikkuHighCreate, DirectBhikkuHighUpdate


class DirectBhikkuHighRepository:
    """Data access helpers for direct high bhikku records."""

    REGN_PREFIX = "DBH"
    REGN_WIDTH = 9  # e.g., DBH2025001
    SEQUENCE_NAME = "direct_bhikku_high_dbh_id_seq"
    PRIMARY_KEY_CONSTRAINT = "direct_bhikku_high_pkey"
    REGN_UNIQUE_CONSTRAINT = "direct_bhikku_high_dbh_regn_key"

    def get(self, db: Session, dbh_id: int) -> Optional[DirectBhikkuHigh]:
        """Get direct high bhikku by ID"""
        return (
            db.query(DirectBhikkuHigh)
            .filter(
                DirectBhikkuHigh.dbh_id == dbh_id,
                DirectBhikkuHigh.dbh_is_deleted.is_(False)
            )
            .first()
        )

    def get_by_regn(self, db: Session, dbh_regn: str) -> Optional[DirectBhikkuHigh]:
        """Get direct high bhikku by registration number"""
        return (
            db.query(DirectBhikkuHigh)
            .filter(
                DirectBhikkuHigh.dbh_regn == dbh_regn,
                DirectBhikkuHigh.dbh_is_deleted.is_(False)
            )
            .first()
        )

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        parshawaya: Optional[str] = None,
        status: Optional[str] = None,
        workflow_status: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
        current_user = None,
    ) -> list[DirectBhikkuHigh]:
        """List direct high bhikku records with filters"""
        query = db.query(DirectBhikkuHigh).filter(
            DirectBhikkuHigh.dbh_is_deleted.is_(False)
        )

        # Location-based access control
        if current_user and hasattr(current_user, 'ua_district'):
            user_district = current_user.ua_district
            if user_district:
                # Filter by created_by_district for district users
                query = query.filter(
                    DirectBhikkuHigh.dbh_created_by_district == user_district
                )

        # General search
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    DirectBhikkuHigh.dbh_regn.ilike(search_term),
                    DirectBhikkuHigh.dbh_gihiname.ilike(search_term),
                    DirectBhikkuHigh.dbh_mahananame.ilike(search_term),
                    DirectBhikkuHigh.dbh_assumed_name.ilike(search_term),
                    DirectBhikkuHigh.dbh_mobile.ilike(search_term),
                    DirectBhikkuHigh.dbh_email.ilike(search_term),
                )
            )

        # Field filters
        if province:
            query = query.filter(DirectBhikkuHigh.dbh_province == province)
        
        if district:
            query = query.filter(DirectBhikkuHigh.dbh_district == district)
        
        if divisional_secretariat:
            query = query.filter(DirectBhikkuHigh.dbh_division == divisional_secretariat)
        
        if gn_division:
            query = query.filter(DirectBhikkuHigh.dbh_gndiv == gn_division)
        
        if parshawaya:
            query = query.filter(DirectBhikkuHigh.dbh_parshawaya == parshawaya)
        
        if status:
            query = query.filter(DirectBhikkuHigh.dbh_currstat == status)
        
        if workflow_status:
            query = query.filter(DirectBhikkuHigh.dbh_workflow_status == workflow_status)
        
        # Date range filtering
        if date_from:
            query = query.filter(DirectBhikkuHigh.dbh_created_at >= date_from)
        
        if date_to:
            query = query.filter(DirectBhikkuHigh.dbh_created_at <= date_to)

        return (
            query.order_by(DirectBhikkuHigh.dbh_id.desc())
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(
        self, 
        db: Session, 
        *, 
        search: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        parshawaya: Optional[str] = None,
        status: Optional[str] = None,
        workflow_status: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
        current_user = None,
    ) -> int:
        """Count direct high bhikku records with filters"""
        query = db.query(func.count(DirectBhikkuHigh.dbh_id)).filter(
            DirectBhikkuHigh.dbh_is_deleted.is_(False)
        )

        # Location-based access control
        if current_user and hasattr(current_user, 'ua_district'):
            user_district = current_user.ua_district
            if user_district:
                query = query.filter(
                    DirectBhikkuHigh.dbh_created_by_district == user_district
                )

        # Apply same filters as list
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    DirectBhikkuHigh.dbh_regn.ilike(search_term),
                    DirectBhikkuHigh.dbh_gihiname.ilike(search_term),
                    DirectBhikkuHigh.dbh_mahananame.ilike(search_term),
                    DirectBhikkuHigh.dbh_assumed_name.ilike(search_term),
                    DirectBhikkuHigh.dbh_mobile.ilike(search_term),
                    DirectBhikkuHigh.dbh_email.ilike(search_term),
                )
            )

        if province:
            query = query.filter(DirectBhikkuHigh.dbh_province == province)
        if district:
            query = query.filter(DirectBhikkuHigh.dbh_district == district)
        if divisional_secretariat:
            query = query.filter(DirectBhikkuHigh.dbh_division == divisional_secretariat)
        if gn_division:
            query = query.filter(DirectBhikkuHigh.dbh_gndiv == gn_division)
        if parshawaya:
            query = query.filter(DirectBhikkuHigh.dbh_parshawaya == parshawaya)
        if status:
            query = query.filter(DirectBhikkuHigh.dbh_currstat == status)
        if workflow_status:
            query = query.filter(DirectBhikkuHigh.dbh_workflow_status == workflow_status)
        if date_from:
            query = query.filter(DirectBhikkuHigh.dbh_created_at >= date_from)
        if date_to:
            query = query.filter(DirectBhikkuHigh.dbh_created_at <= date_to)

        return query.scalar() or 0

    def create(
        self, db: Session, *, payload: DirectBhikkuHighCreate, actor_id: str
    ) -> DirectBhikkuHigh:
        """Create a new direct high bhikku record"""
        # Generate registration number if not provided
        regn = payload.dbh_regn
        if not regn:
            regn = self._generate_regn(db)

        # Convert payload to dict
        data = payload.model_dump(exclude_unset=True, exclude_none=False)
        data["dbh_regn"] = regn
        data["dbh_created_by"] = actor_id
        data["dbh_updated_by"] = actor_id
        data["dbh_workflow_status"] = "PENDING"
        data.setdefault("dbh_version_number", 1)

        entity = DirectBhikkuHigh(**data)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                db.add(entity)
                db.commit()
                db.refresh(entity)
                return entity
            except IntegrityError as exc:
                db.rollback()
                error_msg = str(exc.orig).lower() if exc.orig else ""
                
                if self.REGN_UNIQUE_CONSTRAINT in error_msg and attempt < max_retries - 1:
                    # Retry with new registration number
                    time.sleep(0.1)
                    entity.dbh_regn = self._generate_regn(db)
                    continue
                
                # Re-raise on final attempt or other errors
                if self.REGN_UNIQUE_CONSTRAINT in error_msg:
                    raise ValueError("Failed to generate unique registration number") from exc
                raise RuntimeError("Database error during creation") from exc

        raise RuntimeError("Failed to create record after maximum retries")

    def update(
        self,
        db: Session,
        *,
        entity: DirectBhikkuHigh,
        payload: DirectBhikkuHighUpdate,
        actor_id: str,
    ) -> DirectBhikkuHigh:
        """Update an existing direct high bhikku record"""
        update_data = payload.model_dump(exclude_unset=True, exclude_none=False)
        
        # Remove fields that shouldn't be updated directly
        update_data.pop("dbh_id", None)
        update_data.pop("dbh_regn", None)
        update_data.pop("dbh_created_by", None)
        update_data.pop("dbh_created_at", None)
        
        # Set audit fields
        update_data["dbh_updated_by"] = actor_id

        for field, value in update_data.items():
            setattr(entity, field, value)

        # Increment version number
        entity.dbh_version_number = (entity.dbh_version_number or 1) + 1

        try:
            db.commit()
            db.refresh(entity)
            return entity
        except IntegrityError as exc:
            db.rollback()
            raise RuntimeError("Database error during update") from exc

    def delete(self, db: Session, *, entity: DirectBhikkuHigh, actor_id: str) -> None:
        """Soft delete a direct high bhikku record"""
        entity.dbh_is_deleted = True
        entity.dbh_updated_by = actor_id
        # Increment version number on delete
        entity.dbh_version_number = (entity.dbh_version_number or 1) + 1
        
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise RuntimeError("Database error during deletion") from exc

    def _generate_regn(self, db: Session) -> str:
        """
        Generate a unique registration number in format: DBH{YEAR}{SEQUENCE}.
        
        Example: DBH2025000001, DBH2025000002, ..., DBH2026000001 (resets each year)
        Total length: DBH(3) + YEAR(4) + SEQUENCE(5) = 12 characters.
        """
        from datetime import datetime
        
        current_year = datetime.utcnow().year
        prefix = f"{self.REGN_PREFIX}{current_year}"
        
        # Find the latest registration number for this year
        latest = (
            db.query(DirectBhikkuHigh)
            .filter(DirectBhikkuHigh.dbh_regn.like(f"{prefix}%"))
            .order_by(DirectBhikkuHigh.dbh_regn.desc())
            .first()
        )
        
        if latest:
            try:
                # Extract sequence part after prefix (e.g., "00001" from "DBH202500001")
                sequence_part = latest.dbh_regn[len(prefix):]
                last_sequence = int(sequence_part)
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            # First record for this year
            next_sequence = 1
        
        # Format: DBH2025 + 00001 (5 digits)
        return f"{prefix}{next_sequence:05d}"


# Singleton instance
direct_bhikku_high_repo = DirectBhikkuHighRepository()
