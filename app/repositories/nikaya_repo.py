from __future__ import annotations

from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.nikaya import NikayaData
from app.models.user import UserAccount
from app.repositories.bhikku_repo import bhikku_repo
from app.schemas.nikaya import NikayaCreate, NikayaUpdate


class NikayaRepository:
    """Data access helpers for `cmm_nikayadata` records."""

    def get(self, db: Session, nk_id: int) -> Optional[NikayaData]:
        return (
            db.query(NikayaData)
            .filter(
                NikayaData.nk_id == nk_id,
                NikayaData.nk_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_nkn(self, db: Session, nk_nkn: str) -> Optional[NikayaData]:
        normalized = self._normalize_string(nk_nkn)
        if not normalized:
            return None
        return (
            db.query(NikayaData)
            .filter(
                func.upper(NikayaData.nk_nkn) == normalized,
                NikayaData.nk_is_deleted.is_(False),
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
    ) -> list[NikayaData]:
        query = db.query(NikayaData).filter(
            NikayaData.nk_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    NikayaData.nk_nkn.ilike(term),
                    NikayaData.nk_nname.ilike(term),
                    NikayaData.nk_nahimicd.ilike(term),
                    NikayaData.nk_rmakrs.ilike(term),
                )
            )

        sanitized_limit = max(1, min(limit, 200))
        sanitized_skip = max(0, skip)
        return (
            query.order_by(NikayaData.nk_id)
            .offset(sanitized_skip)
            .limit(sanitized_limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(NikayaData.nk_id)).filter(
            NikayaData.nk_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    NikayaData.nk_nkn.ilike(term),
                    NikayaData.nk_nname.ilike(term),
                    NikayaData.nk_nahimicd.ilike(term),
                    NikayaData.nk_rmakrs.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: NikayaCreate,
        actor_id: Optional[str],
    ) -> NikayaData:
        payload = self._strip_strings(data.model_dump(exclude_unset=True))
        nk_nkn = payload.get("nk_nkn")
        if not nk_nkn or not nk_nkn.strip():
            raise ValueError("nk_nkn is required.")
        payload["nk_nkn"] = nk_nkn.strip().upper()
        payload["nk_created_by"] = actor_id
        payload["nk_updated_by"] = actor_id
        payload["nk_is_deleted"] = False
        payload["nk_version_number"] = 1
        if payload.get("nk_nahimicd"):
            payload["nk_nahimicd"] = payload["nk_nahimicd"].strip().upper()

        self._ensure_unique_nkn(db, payload.get("nk_nkn"), current_id=None)
        self._validate_foreign_keys(
            db,
            nahimi_cd=payload.get("nk_nahimicd"),
            created_by=payload.get("nk_created_by"),
            updated_by=payload.get("nk_updated_by"),
        )

        entity = NikayaData(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: NikayaData,
        data: NikayaUpdate,
        actor_id: Optional[str],
    ) -> NikayaData:
        update_data = self._strip_strings(data.model_dump(exclude_unset=True))
        update_data.pop("nk_id", None)
        update_data.pop("nk_version_number", None)
        update_data.pop("nk_created_by", None)
        update_data.pop("nk_created_at", None)
        update_data.pop("nk_is_deleted", None)
        update_data.pop("nk_version", None)
        update_data.pop("nk_updated_by", None)

        new_nkn = update_data.get("nk_nkn")
        if new_nkn is not None:
            normalized_nkn = new_nkn.strip()
            if not normalized_nkn:
                raise ValueError("nk_nkn cannot be blank.")
            update_data["nk_nkn"] = normalized_nkn.upper()
            self._ensure_unique_nkn(db, update_data["nk_nkn"], current_id=entity.nk_id)
        if "nk_nahimicd" in update_data and update_data["nk_nahimicd"]:
            update_data["nk_nahimicd"] = update_data["nk_nahimicd"].strip().upper()

        self._validate_foreign_keys(
            db,
            nahimi_cd=update_data.get("nk_nahimicd", entity.nk_nahimicd),
            created_by=entity.nk_created_by,
            updated_by=actor_id or entity.nk_updated_by,
        )

        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        entity.nk_updated_by = actor_id
        entity.nk_version_number = (entity.nk_version_number or 1) + 1

        db.commit()
        db.refresh(entity)
        return entity

    def set_mahanayaka(
        self,
        db: Session,
        *,
        entity: NikayaData,
        br_regn: str,
        nk_startdate=None,
        nk_rmakrs: Optional[str] = None,
        actor_id: Optional[str],
    ) -> NikayaData:
        normalized_regn = br_regn.strip().upper() if br_regn else None
        if not normalized_regn:
            raise ValueError("br_regn is required.")

        bhikku = bhikku_repo.get_by_regn(db, normalized_regn)
        if not bhikku:
            raise ValueError(f"Bhikku with br_regn '{br_regn}' does not exist.")

        entity.nk_nahimicd = normalized_regn
        if nk_startdate is not None:
            entity.nk_startdate = nk_startdate
        if nk_rmakrs is not None:
            stripped = nk_rmakrs.strip()
            entity.nk_rmakrs = stripped or None
        entity.nk_updated_by = actor_id
        entity.nk_version_number = (entity.nk_version_number or 1) + 1

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: NikayaData, actor_id: Optional[str]
    ) -> NikayaData:
        if actor_id:
            self._assert_user_exists(db, actor_id)
        entity.nk_is_deleted = True
        entity.nk_updated_by = actor_id
        entity.nk_version_number = (entity.nk_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _strip_strings(self, payload: dict) -> dict:
        for key, value in list(payload.items()):
            if isinstance(value, str):
                stripped = value.strip()
                payload[key] = stripped or None
        return payload

    def _normalize_string(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        stripped = value.strip()
        return stripped.upper() if stripped else None

    def _ensure_unique_nkn(
        self,
        db: Session,
        nk_nkn: Optional[str],
        *,
        current_id: Optional[int],
    ) -> None:
        normalized = self._normalize_string(nk_nkn)
        if not normalized:
            return
        existing = (
            db.query(NikayaData)
            .filter(
                func.upper(NikayaData.nk_nkn) == normalized,
                NikayaData.nk_is_deleted.is_(False),
            )
            .first()
        )
        if existing and existing.nk_id != current_id:
            raise ValueError(f"nk_nkn '{nk_nkn}' is already in use.")

    def _validate_foreign_keys(
        self,
        db: Session,
        *,
        nahimi_cd: Optional[str],
        created_by: Optional[str],
        updated_by: Optional[str],
    ) -> None:
        if nahimi_cd:
            bhikku = bhikku_repo.get_by_regn(db, nahimi_cd)
            if not bhikku:
                raise ValueError(f"nk_nahimicd '{nahimi_cd}' does not reference a valid bhikku.")

        if created_by:
            self._assert_user_exists(db, created_by)
        if updated_by:
            self._assert_user_exists(db, updated_by)

    def _assert_user_exists(self, db: Session, user_id: str) -> None:
        exists = (
            db.query(UserAccount.ua_user_id)
            .filter(
                UserAccount.ua_user_id == user_id,
                UserAccount.ua_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"user '{user_id}' does not exist.")


nikaya_repo = NikayaRepository()
