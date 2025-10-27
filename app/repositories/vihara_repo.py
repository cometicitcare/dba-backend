from typing import Any, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.vihara import ViharaData
from app.schemas.vihara import ViharaCreate, ViharaUpdate


class ViharaRepository:
    """Data access helpers for vihara records."""

    TRN_PREFIX = "TRN"
    TRN_WIDTH = 7

    def get(self, db: Session, vh_id: int) -> Optional[ViharaData]:
        return (
            db.query(ViharaData)
            .filter(ViharaData.vh_id == vh_id, ViharaData.vh_is_deleted.is_(False))
            .first()
        )

    def get_by_trn(self, db: Session, vh_trn: str) -> Optional[ViharaData]:
        return (
            db.query(ViharaData)
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
    ) -> list[ViharaData]:
        query = db.query(ViharaData).filter(ViharaData.vh_is_deleted.is_(False))

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

        return (
            query.order_by(ViharaData.vh_id).offset(max(skip, 0)).limit(limit).all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(ViharaData.vh_id)).filter(
            ViharaData.vh_is_deleted.is_(False)
        )

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

        return query.scalar() or 0

    def create(self, db: Session, *, data: ViharaCreate) -> ViharaData:
        payload = self._strip_strings(data.model_dump(exclude_unset=True))
        payload["vh_trn"] = self.generate_next_trn(db)
        payload.setdefault("vh_is_deleted", False)
        payload.setdefault("vh_version_number", 1)

        self._ensure_unique_contact_fields(db, payload, current_id=None)

        vihara = ViharaData(**self._filter_known_columns(payload))
        db.add(vihara)
        db.commit()
        db.refresh(vihara)
        return vihara

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

        db.commit()
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
    def generate_next_trn(self, db: Session) -> str:
        prefix = self.TRN_PREFIX
        width = self.TRN_WIDTH

        stmt = (
            select(ViharaData.vh_trn)
            .order_by(ViharaData.vh_id.desc())
            .limit(1)
            .with_for_update()
        )

        try:
            latest = db.execute(stmt).scalars().first()
        except Exception:
            latest_entity = (
                db.query(ViharaData)
                .order_by(ViharaData.vh_id.desc())
                .first()
            )
            latest = latest_entity.vh_trn if latest_entity else None

        next_number = 1
        if latest:
            suffix = latest[len(prefix) :] if latest.startswith(prefix) else latest
            try:
                next_number = int(suffix) + 1
            except ValueError:
                next_number = 1

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


vihara_repo = ViharaRepository()
