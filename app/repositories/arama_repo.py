import time
from typing import Any, Optional

from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.arama import AramaData
from app.models.arama_land import AramaLand
from app.models.arama_resident_silmatha import AramaResidentSilmatha
from app.schemas.arama import AramaCreate, AramaUpdate


class AramaRepository:
    """Data access helpers for arama records."""

    ARN_PREFIX = "ARN"
    ARN_WIDTH = 7
    AR_ID_SEQUENCE = "aramadata_ar_id_seq"
    PRIMARY_KEY_CONSTRAINT = "aramadata_pkey"
    ARN_UNIQUE_CONSTRAINT = "aramadata_ar_trn_key"
    EMAIL_UNIQUE_CONSTRAINT = "aramadata_ar_email_key"

    def get(self, db: Session, ar_id: int) -> Optional[AramaData]:
        return (
            db.query(AramaData)
            .filter(AramaData.ar_id == ar_id, AramaData.ar_is_deleted.is_(False))
            .first()
        )

    def get_by_trn(self, db: Session, ar_trn: str) -> Optional[AramaData]:
        return (
            db.query(AramaData)
            .filter(AramaData.ar_trn == ar_trn, AramaData.ar_is_deleted.is_(False))
            .first()
        )

    def get_by_email(self, db: Session, ar_email: str) -> Optional[AramaData]:
        return (
            db.query(AramaData)
            .filter(
                AramaData.ar_email == ar_email,
                AramaData.ar_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_mobile(self, db: Session, ar_mobile: str) -> Optional[AramaData]:
        return (
            db.query(AramaData)
            .filter(
                AramaData.ar_mobile == ar_mobile,
                AramaData.ar_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_whtapp(self, db: Session, ar_whtapp: str) -> Optional[AramaData]:
        return (
            db.query(AramaData)
            .filter(
                AramaData.ar_whtapp == ar_whtapp,
                AramaData.ar_is_deleted.is_(False),
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
        ar_trn: Optional[str] = None,
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
        ar_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
    ) -> list[AramaData]:
        query = db.query(AramaData).filter(AramaData.ar_is_deleted.is_(False))

        # General search (existing functionality)
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    AramaData.ar_trn.ilike(search_term),
                    AramaData.ar_vname.ilike(search_term),
                    AramaData.ar_addrs.ilike(search_term),
                    AramaData.ar_email.ilike(search_term),
                    AramaData.ar_typ.ilike(search_term),
                    AramaData.ar_gndiv.ilike(search_term),
                    AramaData.ar_parshawa.ilike(search_term),
                    AramaData.ar_ownercd.ilike(search_term),
                )
            )

        # Specific field filters
        if ar_trn:
            query = query.filter(AramaData.ar_trn == ar_trn)
        
        if gn_division:
            query = query.filter(AramaData.ar_gndiv == gn_division)
        
        if temple:  # Maps to ar_ownercd
            query = query.filter(AramaData.ar_ownercd == temple)
        
        if child_temple:  # Also maps to ar_ownercd for child temple filtering
            query = query.filter(AramaData.ar_ownercd == child_temple)
        
        if parshawaya:  # Maps to ar_parshawa
            query = query.filter(AramaData.ar_parshawa == parshawaya)
        
        if ar_typ:  # Arama type
            query = query.filter(AramaData.ar_typ == ar_typ)
        
        # Date range filtering (on creation date)
        if date_from:
            query = query.filter(AramaData.ar_created_at >= date_from)
        
        if date_to:
            query = query.filter(AramaData.ar_created_at <= date_to)
        
        # Note: province, district, divisional_secretariat, nikaya, category, status
        # are not currently in the AramaData model. If they are in related tables,
        # you'll need to add joins here. For now, we skip them to avoid errors.

        return (
            query.order_by(AramaData.ar_id).offset(max(skip, 0)).limit(limit).all()
        )

    def count(
        self, 
        db: Session, 
        *, 
        search: Optional[str] = None,
        ar_trn: Optional[str] = None,
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
        ar_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
    ) -> int:
        query = db.query(func.count(AramaData.ar_id)).filter(
            AramaData.ar_is_deleted.is_(False)
        )

        # General search
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    AramaData.ar_trn.ilike(search_term),
                    AramaData.ar_vname.ilike(search_term),
                    AramaData.ar_addrs.ilike(search_term),
                    AramaData.ar_email.ilike(search_term),
                    AramaData.ar_typ.ilike(search_term),
                    AramaData.ar_gndiv.ilike(search_term),
                    AramaData.ar_parshawa.ilike(search_term),
                    AramaData.ar_ownercd.ilike(search_term),
                )
            )

        # Specific field filters (same as list method)
        if ar_trn:
            query = query.filter(AramaData.ar_trn == ar_trn)
        
        if gn_division:
            query = query.filter(AramaData.ar_gndiv == gn_division)
        
        if temple:
            query = query.filter(AramaData.ar_ownercd == temple)
        
        if child_temple:
            query = query.filter(AramaData.ar_ownercd == child_temple)
        
        if parshawaya:
            query = query.filter(AramaData.ar_parshawa == parshawaya)
        
        if ar_typ:
            query = query.filter(AramaData.ar_typ == ar_typ)
        
        if date_from:
            query = query.filter(AramaData.ar_created_at >= date_from)
        
        if date_to:
            query = query.filter(AramaData.ar_created_at <= date_to)

        return query.scalar() or 0

    def create(self, db: Session, *, data: AramaCreate) -> AramaData:
        base_payload = self._strip_strings(data.model_dump(exclude_unset=True))
        
        # Extract nested data before creating arama
        temple_lands_data = base_payload.pop("temple_owned_land", [])
        resident_silmathas_data = base_payload.pop("resident_silmathas", [])
        
        base_payload.setdefault("ar_is_deleted", False)
        base_payload.setdefault("ar_version_number", 1)

        attempts_remaining = 10  # Increased from 3 to 10 retries
        trn_floor: Optional[int] = None
        while attempts_remaining:
            attempts_remaining -= 1
            payload = dict(base_payload)

            self._ensure_unique_contact_fields(db, payload, current_id=None)
            self._sync_ar_id_sequence(db)
            payload["ar_trn"] = self.generate_next_trn(db, minimum=trn_floor)

            arama = AramaData(**self._filter_known_columns(payload))
            db.add(arama)
            try:
                db.commit()
            except IntegrityError as exc:
                db.rollback()
                constraint = self._constraint_from_integrity_error(exc)

                if (
                    constraint == self.PRIMARY_KEY_CONSTRAINT
                    and attempts_remaining > 0
                ):
                    self._sync_ar_id_sequence(db, force=True)
                    time.sleep(0.1)  # Small delay before retry
                    continue

                if (
                    constraint == self.ARN_UNIQUE_CONSTRAINT
                    and attempts_remaining > 0
                ):
                    candidates = [
                        value
                        for value in (
                            trn_floor,
                            self._extract_trn_number(payload.get("ar_trn")),
                            self._get_latest_trn_number(db),
                        )
                        if value is not None
                    ]
                    trn_floor = max(candidates) if candidates else trn_floor
                    time.sleep(0.05)  # Small delay before retry
                    continue

                raise ValueError(self._translate_integrity_error(exc)) from exc

            db.refresh(arama)
            
            # Create related arama land records
            if temple_lands_data:
                for land_data in temple_lands_data:
                    if isinstance(land_data, dict):
                        land_data.pop("id", None)  # Remove id if present
                        arama_land = AramaLand(ar_id=arama.ar_id, **land_data)
                        db.add(arama_land)
            
            # Create related resident silmatha records
            if resident_silmathas_data:
                for silmatha_data in resident_silmathas_data:
                    if isinstance(silmatha_data, dict):
                        silmatha_data.pop("id", None)  # Remove id if present
                        resident_silmatha = AramaResidentSilmatha(ar_id=arama.ar_id, **silmatha_data)
                        db.add(resident_silmatha)
            
            # Commit the related records
            if temple_lands_data or resident_silmathas_data:
                db.commit()
                db.refresh(arama)
            
            return arama

        raise ValueError("Failed to create arama record after retries.")

    def update(
        self,
        db: Session,
        *,
        entity: AramaData,
        data: AramaUpdate,
    ) -> AramaData:
        update_data = self._strip_strings(data.model_dump(exclude_unset=True))

        if "ar_trn" in update_data:
            update_data.pop("ar_trn", None)

        uniqueness_payload = {
            "ar_mobile": update_data.get("ar_mobile", entity.ar_mobile),
            "ar_whtapp": update_data.get("ar_whtapp", entity.ar_whtapp),
            "ar_email": update_data.get("ar_email", entity.ar_email),
        }
        self._ensure_unique_contact_fields(db, uniqueness_payload, current_id=entity.ar_id)

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.ar_version_number = (entity.ar_version_number or 1) + 1

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(self, db: Session, *, entity: AramaData) -> AramaData:
        entity.ar_is_deleted = True
        entity.ar_version_number = (entity.ar_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def generate_next_trn(self, db: Session, *, minimum: Optional[int] = None) -> str:
        prefix = self.ARN_PREFIX
        width = self.ARN_WIDTH

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
        valid_keys = {column.key for column in AramaData.__table__.columns}
        return {key: value for key, value in payload.items() if key in valid_keys}

    def _ensure_unique_contact_fields(
        self,
        db: Session,
        payload: dict[str, Any],
        *,
        current_id: Optional[int],
    ) -> None:
        for field_name in ("ar_mobile", "ar_whtapp", "ar_email"):
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
        normalized = self._normalize_string(value, lower=field_name == "ar_email")
        if not normalized:
            return

        if not hasattr(AramaData, field_name):
            return

        column = getattr(AramaData, field_name)
        query = db.query(AramaData).filter(AramaData.ar_is_deleted.is_(False))

        if field_name == "ar_email":
            query = query.filter(func.lower(column) == normalized)
        else:
            query = query.filter(column == normalized)

        existing = query.first()

        if existing and existing.ar_id != current_id:
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
        # Filter by ARN prefix to avoid mixing with legacy prefixes
        stmt = select(func.max(AramaData.ar_trn)).where(
            AramaData.ar_trn.like(f"{self.ARN_PREFIX}%")
        )
        latest = db.execute(stmt).scalar()
        return self._extract_trn_number(latest)

    def _extract_trn_number(self, value: Optional[str]) -> int:
        if not value:
            return 0
        prefix = self.ARN_PREFIX
        suffix = value[len(prefix):] if value.startswith(prefix) else value
        try:
            return int(suffix)
        except (TypeError, ValueError):
            return 0

    def _sync_ar_id_sequence(self, db: Session, *, force: bool = False) -> None:
        bind = db.get_bind()
        if bind is None or bind.dialect.name != "postgresql":
            return

        seq_name = self.AR_ID_SEQUENCE
        max_id = db.query(func.max(AramaData.ar_id)).scalar()

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
        if "aramadata_pkey" in message:
            return "aramadata_pkey"
        if "aramadata_ar_trn_key" in message:
            return "aramadata_ar_trn_key"
        if "aramadata_ar_email_key" in message:
            return "aramadata_ar_email_key"
        return None

    def _translate_integrity_error(self, error: IntegrityError) -> str:
        constraint = self._constraint_from_integrity_error(error)
        if constraint == self.PRIMARY_KEY_CONSTRAINT:
            return "Unable to assign a new arama id. Please retry."
        if constraint == self.ARN_UNIQUE_CONSTRAINT:
            return "ar_trn already exists. Please retry."
        if constraint == self.EMAIL_UNIQUE_CONSTRAINT:
            return "ar_email already exists."
        return "Failed to persist arama record due to a database constraint violation."


arama_repo = AramaRepository()
