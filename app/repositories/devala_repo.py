import time
from typing import Any, Optional
from datetime import datetime

from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.devala import DevalaData
from app.models.devala_land import DevalaLand
from app.models.user import UserAccount
from app.models.roles import Role
from app.models.user_roles import UserRole
from app.schemas.devala import DevalaCreate, DevalaUpdate


class DevalaRepository:
    """Data access helpers for devala records."""

    DVL_PREFIX = "DVL"
    DVL_WIDTH = 7
    DV_ID_SEQUENCE = "devaladata_dv_id_seq"
    PRIMARY_KEY_CONSTRAINT = "devaladata_pkey"
    DVL_UNIQUE_CONSTRAINT = "devaladata_dv_trn_key"
    EMAIL_UNIQUE_CONSTRAINT = "devaladata_dv_email_key"

    def get(self, db: Session, dv_id: int) -> Optional[DevalaData]:
        return (
            db.query(DevalaData)
            .filter(DevalaData.dv_id == dv_id, DevalaData.dv_is_deleted.is_(False))
            .first()
        )

    def get_by_trn(self, db: Session, dv_trn: str) -> Optional[DevalaData]:
        return (
            db.query(DevalaData)
            .filter(DevalaData.dv_trn == dv_trn, DevalaData.dv_is_deleted.is_(False))
            .first()
        )

    def get_by_email(self, db: Session, dv_email: str) -> Optional[DevalaData]:
        return (
            db.query(DevalaData)
            .filter(
                DevalaData.dv_email == dv_email,
                DevalaData.dv_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_mobile(self, db: Session, dv_mobile: str) -> Optional[DevalaData]:
        return (
            db.query(DevalaData)
            .filter(
                DevalaData.dv_mobile == dv_mobile,
                DevalaData.dv_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_whtapp(self, db: Session, dv_whtapp: str) -> Optional[DevalaData]:
        return (
            db.query(DevalaData)
            .filter(
                DevalaData.dv_whtapp == dv_whtapp,
                DevalaData.dv_is_deleted.is_(False),
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
        dv_trn: Optional[str] = None,
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
        dv_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
        current_user: Optional[UserAccount] = None,
    ) -> list[DevalaData]:
        query = db.query(DevalaData).filter(DevalaData.dv_is_deleted.is_(False))

        # General search (existing functionality)
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    DevalaData.dv_trn.ilike(search_term),
                    DevalaData.dv_vname.ilike(search_term),
                    DevalaData.dv_addrs.ilike(search_term),
                    DevalaData.dv_email.ilike(search_term),
                    DevalaData.dv_typ.ilike(search_term),
                    DevalaData.dv_gndiv.ilike(search_term),
                    DevalaData.dv_parshawa.ilike(search_term),
                    DevalaData.dv_ownercd.ilike(search_term),
                )
            )

        # Specific field filters
        if dv_trn:
            query = query.filter(DevalaData.dv_trn == dv_trn)
        
        if gn_division:
            query = query.filter(DevalaData.dv_gndiv == gn_division)
        
        if temple:  # Maps to dv_ownercd
            query = query.filter(DevalaData.dv_ownercd == temple)
        
        if child_temple:  # Also maps to dv_ownercd for child temple filtering
            query = query.filter(DevalaData.dv_ownercd == child_temple)
        
        if parshawaya:  # Maps to dv_parshawa
            query = query.filter(DevalaData.dv_parshawa == parshawaya)
        
        if dv_typ:  # Devala type
            query = query.filter(DevalaData.dv_typ == dv_typ)
        
        if date_from:
            query = query.filter(DevalaData.dv_created_at >= date_from)
        
        if date_to:
            query = query.filter(DevalaData.dv_created_at <= date_to)
        
        # Note: province, district, divisional_secretariat, nikaya, category, status
        # are not currently in the DevalaData model. If they are in related tables,
        # you'll need to add joins here. For now, we skip them to avoid errors.

        # Data Entry users should see newest first
        order_desc = False
        if current_user:
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

        query = query.order_by(DevalaData.dv_id.desc() if order_desc else DevalaData.dv_id)

        return query.offset(max(skip, 0)).limit(limit).all()

    def count(
        self, 
        db: Session, 
        *, 
        search: Optional[str] = None,
        dv_trn: Optional[str] = None,
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
        dv_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
    ) -> int:
        query = db.query(func.count(DevalaData.dv_id)).filter(
            DevalaData.dv_is_deleted.is_(False)
        )

        # General search
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    DevalaData.dv_trn.ilike(search_term),
                    DevalaData.dv_vname.ilike(search_term),
                    DevalaData.dv_addrs.ilike(search_term),
                    DevalaData.dv_email.ilike(search_term),
                    DevalaData.dv_typ.ilike(search_term),
                    DevalaData.dv_gndiv.ilike(search_term),
                    DevalaData.dv_parshawa.ilike(search_term),
                    DevalaData.dv_ownercd.ilike(search_term),
                )
            )

        # Specific field filters (same as list method)
        if dv_trn:
            query = query.filter(DevalaData.dv_trn == dv_trn)
        
        if gn_division:
            query = query.filter(DevalaData.dv_gndiv == gn_division)
        
        if temple:
            query = query.filter(DevalaData.dv_ownercd == temple)
        
        if child_temple:
            query = query.filter(DevalaData.dv_ownercd == child_temple)
        
        if parshawaya:
            query = query.filter(DevalaData.dv_parshawa == parshawaya)
        
        if dv_typ:
            query = query.filter(DevalaData.dv_typ == dv_typ)
        
        if date_from:
            query = query.filter(DevalaData.dv_created_at >= date_from)
        
        if date_to:
            query = query.filter(DevalaData.dv_created_at <= date_to)

        return query.scalar() or 0

    def create(self, db: Session, *, data: DevalaCreate) -> DevalaData:
        base_payload = self._strip_strings(data.model_dump(exclude_unset=True))
        
        # Extract nested data before creating devala
        temple_lands_data = base_payload.pop("temple_owned_land", [])
        
        base_payload.setdefault("dv_is_deleted", False)
        base_payload.setdefault("dv_version_number", 1)

        attempts_remaining = 10  # Increased from 3 to 10 retries
        trn_floor: Optional[int] = None
        while attempts_remaining:
            attempts_remaining -= 1
            payload = dict(base_payload)

            self._ensure_unique_contact_fields(db, payload, current_id=None)
            self._sync_dv_id_sequence(db)
            payload["dv_trn"] = self.generate_next_trn(db, minimum=trn_floor)

            devala = DevalaData(**self._filter_known_columns(payload))
            db.add(devala)
            try:
                db.commit()
            except IntegrityError as exc:
                db.rollback()
                constraint = self._constraint_from_integrity_error(exc)

                if (
                    constraint == self.PRIMARY_KEY_CONSTRAINT
                    and attempts_remaining > 0
                ):
                    self._sync_dv_id_sequence(db, force=True)
                    time.sleep(0.1)  # Small delay before retry
                    continue

                if (
                    constraint == self.DVL_UNIQUE_CONSTRAINT
                    and attempts_remaining > 0
                ):
                    candidates = [
                        value
                        for value in (
                            trn_floor,
                            self._extract_trn_number(payload.get("dv_trn")),
                            self._get_latest_trn_number(db),
                        )
                        if value is not None
                    ]
                    trn_floor = max(candidates) if candidates else trn_floor
                    time.sleep(0.05)  # Small delay before retry
                    continue

                raise ValueError(self._translate_integrity_error(exc)) from exc

            db.refresh(devala)
            
            # Create related devala land records
            if temple_lands_data:
                for land_data in temple_lands_data:
                    if isinstance(land_data, dict):
                        land_data.pop("id", None)  # Remove id if present
                        devala_land = DevalaLand(dv_id=devala.dv_id, **land_data)
                        db.add(devala_land)
            
            # Commit the land records
            if temple_lands_data:
                db.commit()
                db.refresh(devala)
            
            return devala

        raise ValueError("Failed to create devala record after retries.")

    def update(
        self,
        db: Session,
        *,
        entity: DevalaData,
        data: DevalaUpdate,
    ) -> DevalaData:
        update_data = self._strip_strings(data.model_dump(exclude_unset=True))

        if "dv_trn" in update_data:
            update_data.pop("dv_trn", None)

        uniqueness_payload = {
            "dv_mobile": update_data.get("dv_mobile", entity.dv_mobile),
            "dv_whtapp": update_data.get("dv_whtapp", entity.dv_whtapp),
            "dv_email": update_data.get("dv_email", entity.dv_email),
        }
        self._ensure_unique_contact_fields(db, uniqueness_payload, current_id=entity.dv_id)

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.dv_version_number = (entity.dv_version_number or 1) + 1

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(self, db: Session, *, entity: DevalaData) -> DevalaData:
        entity.dv_is_deleted = True
        entity.dv_version_number = (entity.dv_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def generate_next_trn(self, db: Session, *, minimum: Optional[int] = None) -> str:
        prefix = self.DVL_PREFIX
        width = self.DVL_WIDTH

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
        valid_keys = {column.key for column in DevalaData.__table__.columns}
        return {key: value for key, value in payload.items() if key in valid_keys}

    def _ensure_unique_contact_fields(
        self,
        db: Session,
        payload: dict[str, Any],
        *,
        current_id: Optional[int],
    ) -> None:
        for field_name in ("dv_mobile", "dv_whtapp", "dv_email"):
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
        normalized = self._normalize_string(value, lower=field_name == "dv_email")
        if not normalized:
            return

        if not hasattr(DevalaData, field_name):
            return

        column = getattr(DevalaData, field_name)
        query = db.query(DevalaData).filter(DevalaData.dv_is_deleted.is_(False))

        if field_name == "dv_email":
            query = query.filter(func.lower(column) == normalized)
        else:
            query = query.filter(column == normalized)

        existing = query.first()

        if existing and existing.dv_id != current_id:
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
        stmt = select(func.max(DevalaData.dv_trn))
        latest = db.execute(stmt).scalar()
        return self._extract_trn_number(latest)

    def _extract_trn_number(self, value: Optional[str]) -> int:
        if not value:
            return 0
        prefix = self.DVL_PREFIX
        suffix = value[len(prefix):] if value.startswith(prefix) else value
        try:
            return int(suffix)
        except (TypeError, ValueError):
            return 0

    def _sync_dv_id_sequence(self, db: Session, *, force: bool = False) -> None:
        bind = db.get_bind()
        if bind is None or bind.dialect.name != "postgresql":
            return

        seq_name = self.DV_ID_SEQUENCE
        max_id = db.query(func.max(DevalaData.dv_id)).scalar()

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
        if "devaladata_pkey" in message:
            return "devaladata_pkey"
        if "devaladata_dv_trn_key" in message:
            return "devaladata_dv_trn_key"
        if "devaladata_dv_email_key" in message:
            return "devaladata_dv_email_key"
        return None

    def _translate_integrity_error(self, error: IntegrityError) -> str:
        constraint = self._constraint_from_integrity_error(error)
        if constraint == self.PRIMARY_KEY_CONSTRAINT:
            return "Unable to assign a new devala id. Please retry."
        if constraint == self.DVL_UNIQUE_CONSTRAINT:
            return "dv_trn already exists. Please retry."
        if constraint == self.EMAIL_UNIQUE_CONSTRAINT:
            return "dv_email already exists."
        return "Failed to persist devala record due to a database constraint violation."


devala_repo = DevalaRepository()
