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
from app.models.user import UserAccount
from app.models.roles import Role
from app.models.user_roles import UserRole
from app.schemas.direct_bhikku_high import DirectBhikkuHighCreate, DirectBhikkuHighUpdate


class DirectBhikkuHighRepository:
    """Data access helpers for direct high bhikku records."""

    REGN_PREFIX = "DBH"
    REGN_WIDTH = 3  # Sequence width: 001, 002, 003 (3 digits)
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

        # Data Entry users should see newest first
        order_desc = False
        if current_user:
            from datetime import datetime
            now = datetime.utcnow()
            data_entry_role = (
                db.query(UserRole)
                .join(Role, Role.ro_role_id == UserRole.ur_role_id)
                .filter(
                    UserRole.ur_user_id == current_user.ua_user_id,
                    UserRole.ur_is_active.is_(True),
                    (UserRole.ur_expires_date.is_(None) | (UserRole.ur_expires_date > now)),
                    Role.ro_level == "DATA_ENTRY",
                )
                .first()
            )
            order_desc = data_entry_role is not None

        query = query.order_by(DirectBhikkuHigh.dbh_id.desc() if order_desc else DirectBhikkuHigh.dbh_id)

        return query.offset(max(skip, 0)).limit(limit).all()

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
        self, db: Session, *, payload: DirectBhikkuHighCreate, actor_id: str, current_user=None
    ) -> DirectBhikkuHigh:
        """Create a new direct high bhikku record"""
        import re
        
        # Convert payload to dict
        data = payload.model_dump(exclude_unset=True, exclude_none=False)
        
        # Always generate registration number (ignore any provided value)
        data.pop("dbh_regn", None)
        regn = self._generate_regn(db)
        
        data["dbh_regn"] = regn
        data["dbh_created_by"] = actor_id
        data["dbh_updated_by"] = actor_id
        data["dbh_workflow_status"] = "PENDING"
        data.setdefault("dbh_version_number", 1)
        
        # Set location-based access control field
        if current_user and hasattr(current_user, 'ua_district'):
            user_district = current_user.ua_district
            if user_district:
                data["dbh_created_by_district"] = user_district

        # Handle temporary bhikku references (TEMP-*)
        temp_remarks = []
        bhikku_fk_fields = [
            "dbh_karmacharya_name",
            "dbh_upaddhyaya_name", 
            "dbh_tutors_tutor_regn",
            "dbh_presiding_bhikshu_regn",
            "dbh_samanera_serial_no",
        ]
        for field in bhikku_fk_fields:
            if field in data and data[field]:
                value = str(data[field])
                if value.startswith("TEMP-"):
                    temp_id = value.replace("TEMP-", "")
                    temp_remarks.append(f"[TEMP_DBH_{field.upper().replace('DBH_', '')}:{temp_id}]")
                    data[field] = None
        
        # Handle temporary vihara references (TEMP-*)
        vihara_fk_fields = [
            "dbh_livtemple",
            "dbh_residence_higher_ordination_trn",
            "dbh_residence_permanent_trn",
            "dbh_higher_ordination_place",
        ]
        for field in vihara_fk_fields:
            if field in data and data[field]:
                value = str(data[field])
                if value.startswith("TEMP-"):
                    temp_id = value.replace("TEMP-", "")
                    temp_remarks.append(f"[TEMP_DBH_{field.upper().replace('DBH_', '')}:{temp_id}]")
                    data[field] = None
        
        # Append temp references to remarks
        if temp_remarks:
            existing_remarks = data.get("dbh_remarks") or ""
            data["dbh_remarks"] = (existing_remarks + " " + " ".join(temp_remarks)).strip()

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
        import re
        
        update_data = payload.model_dump(exclude_unset=True, exclude_none=False)
        
        # Remove fields that shouldn't be updated directly
        update_data.pop("dbh_id", None)
        update_data.pop("dbh_regn", None)
        update_data.pop("dbh_created_by", None)
        update_data.pop("dbh_created_at", None)
        
        # Set audit fields
        update_data["dbh_updated_by"] = actor_id

        # Handle temporary bhikku references (TEMP-*)
        temp_remarks = []
        current_remarks = entity.dbh_remarks or ""
        
        # Remove old temp references from remarks before adding new ones
        current_remarks = re.sub(r'\[TEMP_DBH_[A-Z_]+:\d+\]', '', current_remarks).strip()
        
        bhikku_fk_fields = [
            "dbh_karmacharya_name",
            "dbh_upaddhyaya_name",
            "dbh_tutors_tutor_regn",
            "dbh_presiding_bhikshu_regn",
            "dbh_samanera_serial_no",
        ]
        for field in bhikku_fk_fields:
            if field in update_data and update_data[field] is not None:
                value = str(update_data[field])
                if value.startswith("TEMP-"):
                    temp_id = value.replace("TEMP-", "")
                    temp_remarks.append(f"[TEMP_DBH_{field.upper().replace('DBH_', '')}:{temp_id}]")
                    update_data[field] = None
        
        # Handle temporary vihara references (TEMP-*)
        vihara_fk_fields = [
            "dbh_livtemple",
            "dbh_residence_higher_ordination_trn",
            "dbh_residence_permanent_trn",
            "dbh_higher_ordination_place",
        ]
        for field in vihara_fk_fields:
            if field in update_data and update_data[field] is not None:
                value = str(update_data[field])
                if value.startswith("TEMP-"):
                    temp_id = value.replace("TEMP-", "")
                    temp_remarks.append(f"[TEMP_DBH_{field.upper().replace('DBH_', '')}:{temp_id}]")
                    update_data[field] = None
        
        # Update remarks with temp references
        if temp_remarks:
            # If remarks are being updated in payload, use that as base
            if "dbh_remarks" in update_data and update_data["dbh_remarks"]:
                base_remarks = update_data["dbh_remarks"]
                # Clean temp refs from new remarks too
                base_remarks = re.sub(r'\[TEMP_DBH_[A-Z_]+:\d+\]', '', base_remarks).strip()
            else:
                base_remarks = current_remarks
            update_data["dbh_remarks"] = (base_remarks + " " + " ".join(temp_remarks)).strip()


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
        
        Example: DBH2025001, DBH2025002, ..., DBH2026001 (resets each year)
        Total length: DBH(3) + YEAR(4) + SEQUENCE(3) = 10 characters.
        """
        from datetime import datetime
        
        current_year = datetime.utcnow().year
        prefix = f"{self.REGN_PREFIX}{current_year}"
        expected_length = len(prefix) + self.REGN_WIDTH  # e.g., 7 + 3 = 10
        
        # Find the latest VALID registration number for this year
        # Filter by exact length to avoid malformed records
        all_records = (
            db.query(DirectBhikkuHigh.dbh_regn)
            .filter(
                DirectBhikkuHigh.dbh_regn.like(f"{prefix}%"),
                func.length(DirectBhikkuHigh.dbh_regn) == expected_length
            )
            .all()
        )
        
        # Extract sequences and find the maximum
        max_sequence = 0
        for (regn,) in all_records:
            try:
                sequence_part = regn[len(prefix):]
                sequence = int(sequence_part)
                max_sequence = max(max_sequence, sequence)
            except (ValueError, IndexError):
                continue
        
        next_sequence = max_sequence + 1
        
        # Format: DBH2025 + 004 (3 digits using REGN_WIDTH)
        return f"{prefix}{next_sequence:0{self.REGN_WIDTH}d}"
        return f"{prefix}{next_sequence:05d}"


# Singleton instance
direct_bhikku_high_repo = DirectBhikkuHighRepository()
