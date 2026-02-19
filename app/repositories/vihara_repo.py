import time
from typing import Any, Optional
from datetime import datetime

from sqlalchemy import func, or_, select, text, case
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.vihara import ViharaData
from app.models.temple_land import TempleLand
from app.models.resident_bhikkhu import ResidentBhikkhu
from app.models.vihara_land import ViharaLand
from app.models.user import UserAccount
from app.models.roles import Role
from app.models.user_roles import UserRole
from app.schemas.vihara import ViharaCreate, ViharaUpdate


class ViharaRepository:
    """Data access helpers for vihara records."""

    TRN_PREFIX = "TRN"
    TRN_WIDTH = 7
    VH_ID_SEQUENCE = "vihaddata_vh_id_seq"
    PRIMARY_KEY_CONSTRAINT = "vihaddata_pkey"
    TRN_UNIQUE_CONSTRAINT = "vihaddata_vh_trn_key"
    EMAIL_UNIQUE_CONSTRAINT = "vihaddata_vh_email_key"

    def get(self, db: Session, vh_id: int) -> Optional[ViharaData]:
        return (
            db.query(ViharaData)
            .options(joinedload(ViharaData.temple_lands), joinedload(ViharaData.resident_bhikkhus))
            .filter(ViharaData.vh_id == vh_id, ViharaData.vh_is_deleted.is_(False))
            .first()
        )

    def get_by_trn(self, db: Session, vh_trn: str) -> Optional[ViharaData]:
        return (
            db.query(ViharaData)
            .options(joinedload(ViharaData.temple_lands), joinedload(ViharaData.resident_bhikkhus))
            .filter(ViharaData.vh_trn == vh_trn, ViharaData.vh_is_deleted.is_(False))
            .first()
        )

    def get_by_email(self, db: Session, vh_email: str) -> Optional[ViharaData]:
        return (
            db.query(ViharaData)
            .filter(
                ViharaData.vh_email == vh_email,
                ViharaData.vh_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_mobile(self, db: Session, vh_mobile: str) -> Optional[ViharaData]:
        return (
            db.query(ViharaData)
            .filter(
                ViharaData.vh_mobile == vh_mobile,
                ViharaData.vh_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_whtapp(self, db: Session, vh_whtapp: str) -> Optional[ViharaData]:
        return (
            db.query(ViharaData)
            .filter(
                ViharaData.vh_whtapp == vh_whtapp,
                ViharaData.vh_is_deleted.is_(False),
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
        vh_trn: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        vh_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
        current_user: Optional[UserAccount] = None,
    ) -> list[ViharaData]:
        query = db.query(ViharaData).filter(ViharaData.vh_is_deleted.is_(False))

        # General search (existing functionality)
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    ViharaData.vh_trn.ilike(search_term),
                    ViharaData.vh_vname.ilike(search_term),
                    ViharaData.vh_addrs.ilike(search_term),
                    ViharaData.vh_email.ilike(search_term),
                    ViharaData.vh_typ.ilike(search_term),
                    ViharaData.vh_gndiv.ilike(search_term),
                    ViharaData.vh_parshawa.ilike(search_term),
                    ViharaData.vh_ownercd.ilike(search_term),
                )
            )

        # Specific field filters
        if vh_trn:
            query = query.filter(ViharaData.vh_trn == vh_trn)
        
        if gn_division:
            query = query.filter(ViharaData.vh_gndiv == gn_division)
        
        if temple:  # Maps to vh_ownercd
            query = query.filter(ViharaData.vh_ownercd == temple)
        
        if child_temple:  # Also maps to vh_ownercd for child temple filtering
            query = query.filter(ViharaData.vh_ownercd == child_temple)
        
        if parshawaya:  # Maps to vh_parshawa
            query = query.filter(ViharaData.vh_parshawa == parshawaya)
        
        if vh_typ:  # Vihara type
            query = query.filter(ViharaData.vh_typ == vh_typ)
        # Date range filtering (on creation date)
        if date_from:
            query = query.filter(ViharaData.vh_created_at >= date_from)
        
        if date_to:
            query = query.filter(ViharaData.vh_created_at <= date_to)
        
        # Note: province, district, divisional_secretariat, nikaya, category, status
        # are not currently in the ViharaData model. If they are in related tables,
        # you'll need to add joins here. For now, we skip them to avoid errors.

        # Ordering logic:
        # - ADMIN users: See ALL records with pending approvals at top (ascending order),
        #                then other records (ascending order)
        # - DATA_ENTRY users: See newest first (descending order)
        # - Other users: See ascending order
        order_desc = False
        is_admin = False
        
        if current_user:
            now = datetime.utcnow()
            
            # Check for ADMIN role
            admin_role = (
                db.query(UserRole)
                .join(Role, Role.ro_role_id == UserRole.ur_role_id)
                .filter(
                    UserRole.ur_user_id == current_user.ua_user_id,
                    UserRole.ur_is_active.is_(True),
                    (UserRole.ur_expires_date.is_(None) | (UserRole.ur_expires_date > now)),
                    Role.ro_level == "ADMIN",
                )
                .first()
            )
            
            if admin_role:
                # Admin users see ALL records with pending approvals at the top
                is_admin = True
            else:
                # Check for DATA_ENTRY role
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
        
        # Apply ordering based on user role
        if is_admin:
            # Check if this is specifically a vihara_admin (VIHA_ADM role)
            vihara_admin_role = (
                db.query(UserRole)
                .join(Role, Role.ro_role_id == UserRole.ur_role_id)
                .filter(
                    UserRole.ur_user_id == current_user.ua_user_id,
                    UserRole.ur_is_active.is_(True),
                    (UserRole.ur_expires_date.is_(None) | (UserRole.ur_expires_date > now)),
                    Role.ro_role_id == "VIHA_ADM",  # Specifically check for vihara_admin role
                )
                .first()
            )
            
            if vihara_admin_role:
                # Vihara Admin: Special ordering as requested
                # 1. First: Stage 1 and 2 pending approval (ascending)
                # 2. Then: Completed stage records
                # 3. Then: Other stages (like pending, rejected, etc.)
                # Note: temp-vihara records are handled separately in the endpoint
                priority = case(
                    # Priority 0: Stage 1 and 2 pending approval
                    (ViharaData.vh_workflow_status.in_(["S1_PEND_APPROVAL", "S2_PEND_APPROVAL"]), 0),
                    # Priority 1: Completed stage
                    (ViharaData.vh_workflow_status == "COMPLETED", 1),
                    # Priority 2: Other stages (pending, rejected, etc.)
                    else_=2
                )
                query = query.order_by(priority, ViharaData.vh_id.asc())
            else:
                # Other admin users: original behavior
                # Admin: pending approval records first (ascending), then others (ascending)
                # Using CASE to prioritize pending approval statuses
                priority = case(
                    (ViharaData.vh_workflow_status.in_(["S1_PEND_APPROVAL", "S2_PEND_APPROVAL"]), 0),
                    else_=1
                )
                query = query.order_by(priority, ViharaData.vh_id.asc())
        else:
            # DATA_ENTRY or other users
            query = query.order_by(ViharaData.vh_id.desc() if order_desc else ViharaData.vh_id)

        return query.offset(max(skip, 0)).limit(limit).all()

    def count(
        self, 
        db: Session, 
        *, 
        search: Optional[str] = None,
        vh_trn: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        vh_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
        current_user: Optional[UserAccount] = None,
    ) -> int:
        query = db.query(func.count(ViharaData.vh_id)).filter(
            ViharaData.vh_is_deleted.is_(False)
        )

        # General search
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    ViharaData.vh_trn.ilike(search_term),
                    ViharaData.vh_vname.ilike(search_term),
                    ViharaData.vh_addrs.ilike(search_term),
                    ViharaData.vh_email.ilike(search_term),
                    ViharaData.vh_typ.ilike(search_term),
                    ViharaData.vh_gndiv.ilike(search_term),
                    ViharaData.vh_parshawa.ilike(search_term),
                    ViharaData.vh_ownercd.ilike(search_term),
                )
            )

        # Specific field filters (same as list method)
        if vh_trn:
            query = query.filter(ViharaData.vh_trn == vh_trn)
        
        if gn_division:
            query = query.filter(ViharaData.vh_gndiv == gn_division)
        
        if temple:
            query = query.filter(ViharaData.vh_ownercd == temple)
        
        if child_temple:
            query = query.filter(ViharaData.vh_ownercd == child_temple)
        
        if parshawaya:
            query = query.filter(ViharaData.vh_parshawa == parshawaya)
        
        if vh_typ:
            query = query.filter(ViharaData.vh_typ == vh_typ)
        
        if date_from:
            query = query.filter(ViharaData.vh_created_at >= date_from)
        
        if date_to:
            query = query.filter(ViharaData.vh_created_at <= date_to)
        
        # Note: Admin users now see ALL records (not filtered by status)
        # The count should reflect all matching records regardless of user role
        # Ordering/prioritization is handled in the list method

        return query.scalar() or 0

    def create(self, db: Session, *, data: ViharaCreate) -> ViharaData:
        base_payload = self._strip_strings(data.model_dump(exclude_unset=True))
        
        # Extract nested data before creating vihara
        temple_lands_data = base_payload.pop("temple_owned_land", [])
        resident_bhikkhus_data = base_payload.pop("resident_bhikkhus", [])
        
        base_payload.setdefault("vh_is_deleted", False)
        base_payload.setdefault("vh_version_number", 1)

        attempts_remaining = 10  # Increased from 3 to 10 retries
        trn_floor: Optional[int] = None
        while attempts_remaining:
            attempts_remaining -= 1
            payload = dict(base_payload)

            self._ensure_unique_contact_fields(db, payload, current_id=None)
            self._sync_vh_id_sequence(db)
            payload["vh_trn"] = self.generate_next_trn(db, minimum=trn_floor)

            vihara = ViharaData(**self._filter_known_columns(payload))
            db.add(vihara)
            try:
                db.commit()
            except IntegrityError as exc:
                db.rollback()
                constraint = self._constraint_from_integrity_error(exc)

                if (
                    constraint == self.PRIMARY_KEY_CONSTRAINT
                    and attempts_remaining > 0
                ):
                    self._sync_vh_id_sequence(db, force=True)
                    time.sleep(0.1)  # Small delay before retry
                    continue

                if (
                    constraint == self.TRN_UNIQUE_CONSTRAINT
                    and attempts_remaining > 0
                ):
                    candidates = [
                        value
                        for value in (
                            trn_floor,
                            self._extract_trn_number(payload.get("vh_trn")),
                            self._get_latest_trn_number(db),
                        )
                        if value is not None
                    ]
                    trn_floor = max(candidates) if candidates else trn_floor
                    time.sleep(0.05)  # Small delay before retry
                    continue

                raise ValueError(self._translate_integrity_error(exc)) from exc

            db.refresh(vihara)
            
            # Create related temple land records (from new payload format)
            if temple_lands_data:
                for land_data in temple_lands_data:
                    if isinstance(land_data, dict):
                        land_data.pop("id", None)  # Remove id if present
                        # Create TempleLand record (not ViharaLand)
                        temple_land = TempleLand(vh_id=vihara.vh_id, **land_data)
                        db.add(temple_land)
            
            # Create related resident bhikkhu records
            if resident_bhikkhus_data:
                for bhikkhu_data in resident_bhikkhus_data:
                    if isinstance(bhikkhu_data, dict):
                        bhikkhu_data.pop("id", None)  # Remove id if present
                        resident_bhikkhu = ResidentBhikkhu(vh_id=vihara.vh_id, **bhikkhu_data)
                        db.add(resident_bhikkhu)
            
            # Commit all related records
            if temple_lands_data or resident_bhikkhus_data:
                db.commit()
                db.refresh(vihara)
            
            return vihara

        raise ValueError("Failed to create vihara record after retries.")

    def update(
        self,
        db: Session,
        *,
        entity: ViharaData,
        data: ViharaUpdate,
    ) -> ViharaData:
        update_data = self._strip_strings(data.model_dump(exclude_unset=True))

        if "vh_trn" in update_data:
            update_data.pop("vh_trn", None)

        uniqueness_payload = {
            "vh_mobile": update_data.get("vh_mobile", entity.vh_mobile),
            "vh_whtapp": update_data.get("vh_whtapp", entity.vh_whtapp),
            "vh_email": update_data.get("vh_email", entity.vh_email),
        }
        self._ensure_unique_contact_fields(db, uniqueness_payload, current_id=entity.vh_id)

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.vh_version_number = (entity.vh_version_number or 1) + 1

        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ValueError(self._translate_integrity_error(exc)) from exc
        db.refresh(entity)
        return entity

    def soft_delete(self, db: Session, *, entity: ViharaData) -> ViharaData:
        entity.vh_is_deleted = True
        entity.vh_version_number = (entity.vh_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def generate_next_trn(self, db: Session, *, minimum: Optional[int] = None) -> str:
        prefix = self.TRN_PREFIX
        width = self.TRN_WIDTH

        current_max = self._get_latest_trn_number(db)
        if minimum is not None:
            current_max = max(current_max, minimum)
        next_number = current_max + 1
        return f"{prefix}{next_number:0{width}d}"

    @staticmethod
    def _strip_strings(payload: dict[str, Any]) -> dict[str, Any]:
        for key, value in payload.items():
            if isinstance(value, str):
                payload[key] = value.strip()
        return payload

    @staticmethod
    def _filter_known_columns(payload: dict[str, Any]) -> dict[str, Any]:
        valid_keys = {column.key for column in ViharaData.__table__.columns}
        return {key: value for key, value in payload.items() if key in valid_keys}

    def _ensure_unique_contact_fields(
        self,
        db: Session,
        payload: dict[str, Any],
        *,
        current_id: Optional[int],
    ) -> None:
        for field_name in ("vh_mobile", "vh_whtapp", "vh_email"):
            value = payload.get(field_name)
            self._ensure_unique_contact_field(
                db,
                field_name=field_name,
                value=value,
                current_id=current_id,
            )

    def _ensure_unique_contact_field(
        self,
        db: Session,
        *,
        field_name: str,
        value: Optional[str],
        current_id: Optional[int],
    ) -> None:
        display_value = value
        normalized = self._normalize_string(value, lower=field_name == "vh_email")
        if not normalized:
            return

        if not hasattr(ViharaData, field_name):
            return

        column = getattr(ViharaData, field_name)
        query = db.query(ViharaData).filter(ViharaData.vh_is_deleted.is_(False))

        if field_name == "vh_email":
            query = query.filter(func.lower(column) == normalized)
        else:
            query = query.filter(column == normalized)

        existing = query.first()

        if existing and existing.vh_id != current_id:
            raise ValueError(f"{field_name} '{display_value}' already exists.")

    @staticmethod
    def _normalize_string(value: Optional[str], *, lower: bool = False) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            return None
        return trimmed.lower() if lower else trimmed

    def _get_latest_trn_number(self, db: Session) -> int:
        # Filter by TRN prefix to avoid mixing with legacy VH prefixes
        stmt = select(func.max(ViharaData.vh_trn)).where(
            ViharaData.vh_trn.like(f"{self.TRN_PREFIX}%")
        )
        latest = db.execute(stmt).scalar()
        return self._extract_trn_number(latest)

    def _extract_trn_number(self, value: Optional[str]) -> int:
        if not value:
            return 0
        prefix = self.TRN_PREFIX
        suffix = value[len(prefix):] if value.startswith(prefix) else value
        try:
            return int(suffix)
        except (TypeError, ValueError):
            return 0

    def _sync_vh_id_sequence(self, db: Session, *, force: bool = False) -> None:
        bind = db.get_bind()
        if bind is None or bind.dialect.name != "postgresql":
            return

        seq_name = self.VH_ID_SEQUENCE
        max_id = db.query(func.max(ViharaData.vh_id)).scalar()

        if not force:
            seq_state = db.execute(
                text(
                    f"SELECT last_value, is_called FROM {seq_name}"
                )
            ).first()
            mapping = seq_state._mapping if seq_state else None

            if max_id is None:
                if (
                    mapping
                    and mapping.get("last_value") == 1
                    and mapping.get("is_called") is False
                ):
                    return
                db.execute(text(f"SELECT setval('{seq_name}', 1, false)"))
                return

            if mapping:
                last_value = mapping.get("last_value")
                is_called = mapping.get("is_called")
                if last_value is not None:
                    if last_value > max_id:
                        return
                    if last_value == max_id and is_called:
                        return

        if max_id is None:
            db.execute(text(f"SELECT setval('{seq_name}', 1, false)"))
        else:
            db.execute(text(f"SELECT setval('{seq_name}', :value)"), {"value": max_id})

    @staticmethod
    def _constraint_from_integrity_error(error: IntegrityError) -> Optional[str]:
        origin = getattr(error, "orig", None)
        diag = getattr(origin, "diag", None) if origin else None
        constraint = getattr(diag, "constraint_name", None) if diag else None
        if constraint:
            return constraint

        message = str(origin or error).lower()
        if "vihaddata_pkey" in message:
            return "vihaddata_pkey"
        if "vihaddata_vh_trn_key" in message:
            return "vihaddata_vh_trn_key"
        if "vihaddata_vh_email_key" in message:
            return "vihaddata_vh_email_key"
        return None

    def _translate_integrity_error(self, error: IntegrityError) -> str:
        constraint = self._constraint_from_integrity_error(error)
        if constraint == self.PRIMARY_KEY_CONSTRAINT:
            return "Unable to assign a new vihara id. Please retry."
        if constraint == self.TRN_UNIQUE_CONSTRAINT:
            return "vh_trn already exists. Please retry."
        if constraint == self.EMAIL_UNIQUE_CONSTRAINT:
            return "vh_email already exists."
        return "Failed to persist vihara record due to a database constraint violation."


vihara_repo = ViharaRepository()
