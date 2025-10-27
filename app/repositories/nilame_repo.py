# app/repositories/nilame_repo.py
from typing import Any, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.nilame import NilameRegist
from app.schemas.nilame import NilameCreate, NilameUpdate


class NilameRepository:
    """Data access helpers for nilame registrations."""

    REG_NUMBER_PREFIX = "KP"
    REG_NUMBER_WIDTH = 8

    def get(self, db: Session, kr_id: int) -> Optional[NilameRegist]:
        return (
            db.query(NilameRegist)
            .filter(
                NilameRegist.kr_id == kr_id,
                NilameRegist.kr_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_krn(self, db: Session, kr_krn: str) -> Optional[NilameRegist]:
        return (
            db.query(NilameRegist)
            .filter(
                NilameRegist.kr_krn == kr_krn,
                NilameRegist.kr_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_nic(self, db: Session, kr_nic: str) -> Optional[NilameRegist]:
        normalized = self._normalize_nic(kr_nic)
        if not normalized:
            return None
        return (
            db.query(NilameRegist)
            .filter(
                func.upper(NilameRegist.kr_nic) == normalized,
                NilameRegist.kr_is_deleted.is_(False),
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
    ) -> list[NilameRegist]:
        query = db.query(NilameRegist).filter(
            NilameRegist.kr_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    NilameRegist.kr_krn.ilike(term),
                    NilameRegist.kr_kname.ilike(term),
                    NilameRegist.kr_nic.ilike(term),
                    NilameRegist.kr_addrs.ilike(term),
                    NilameRegist.kr_grndiv.ilike(term),
                    NilameRegist.kr_trn.ilike(term),
                )
            )

        return (
            query.order_by(NilameRegist.kr_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(NilameRegist.kr_id)).filter(
            NilameRegist.kr_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    NilameRegist.kr_krn.ilike(term),
                    NilameRegist.kr_kname.ilike(term),
                    NilameRegist.kr_nic.ilike(term),
                    NilameRegist.kr_addrs.ilike(term),
                    NilameRegist.kr_grndiv.ilike(term),
                    NilameRegist.kr_trn.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: NilameCreate,
        actor_id: Optional[str],
    ) -> NilameRegist:
        payload = self._strip_strings(data.model_dump(exclude_unset=True))
        payload["kr_krn"] = self.generate_next_krn(db)
        payload.setdefault("kr_is_deleted", False)
        payload.setdefault("kr_version_number", 1)
        payload["kr_created_by"] = actor_id
        payload["kr_updated_by"] = actor_id

        self._ensure_unique_fields(db, payload, current_id=None)

        entity = NilameRegist(**self._filter_known_columns(payload))
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: NilameRegist,
        data: NilameUpdate,
        actor_id: Optional[str],
    ) -> NilameRegist:
        update_data = self._strip_strings(data.model_dump(exclude_unset=True))
        if "kr_krn" in update_data:
            update_data.pop("kr_krn", None)

        uniqueness_payload = {
            "kr_nic": update_data.get("kr_nic", entity.kr_nic),
            "kr_mobile": update_data.get(
                "kr_mobile", getattr(entity, "kr_mobile", None)
            ),
            "kr_email": update_data.get(
                "kr_email", getattr(entity, "kr_email", None)
            ),
        }
        self._ensure_unique_fields(db, uniqueness_payload, current_id=entity.kr_id)

        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        entity.kr_updated_by = actor_id
        entity.kr_version_number = (entity.kr_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: NilameRegist, actor_id: Optional[str]
    ) -> NilameRegist:
        entity.kr_is_deleted = True
        entity.kr_updated_by = actor_id
        entity.kr_version_number = (entity.kr_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def generate_next_krn(self, db: Session) -> str:
        prefix = self.REG_NUMBER_PREFIX
        width = self.REG_NUMBER_WIDTH

        stmt = (
            select(NilameRegist.kr_krn)
            .order_by(NilameRegist.kr_id.desc())
            .limit(1)
            .with_for_update()
        )

        try:
            latest = db.execute(stmt).scalars().first()
        except Exception:
            latest_entity = (
                db.query(NilameRegist)
                .order_by(NilameRegist.kr_id.desc())
                .first()
            )
            latest = latest_entity.kr_krn if latest_entity else None
        next_number = 1

        if latest:
            stripped = latest[len(prefix) :] if latest.startswith(prefix) else latest
            try:
                next_number = int(stripped) + 1
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
        valid_keys = {column.key for column in NilameRegist.__table__.columns}
        return {key: value for key, value in payload.items() if key in valid_keys}

    def _ensure_unique_fields(
        self,
        db: Session,
        payload: dict[str, Any],
        *,
        current_id: Optional[int],
    ) -> None:
        nic_value = self._normalize_nic(payload.get("kr_nic"))
        if nic_value:
            existing = (
                db.query(NilameRegist)
                .filter(
                    func.upper(NilameRegist.kr_nic) == nic_value,
                    NilameRegist.kr_is_deleted.is_(False),
                )
                .first()
            )
            if existing and existing.kr_id != current_id:
                raise ValueError(f"kr_nic '{nic_value}' already exists.")

        self._ensure_unique_contact_field(
            db,
            field_name="kr_mobile",
            value=payload.get("kr_mobile"),
            current_id=current_id,
        )
        self._ensure_unique_contact_field(
            db,
            field_name="kr_email",
            value=payload.get("kr_email"),
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
        normalized = self._normalize_string(value)
        if not normalized or not hasattr(NilameRegist, field_name):
            return

        column = getattr(NilameRegist, field_name)
        existing = (
            db.query(NilameRegist)
            .filter(column == normalized, NilameRegist.kr_is_deleted.is_(False))
            .first()
        )
        if existing and existing.kr_id != current_id:
            raise ValueError(f"{field_name} '{normalized}' already exists.")

    @staticmethod
    def _normalize_string(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    def _normalize_nic(self, value: Optional[str]) -> Optional[str]:
        normalized = self._normalize_string(value)
        return normalized.upper() if normalized else None


nilame_repo = NilameRepository()
