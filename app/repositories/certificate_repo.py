# app/repositories/certificate_repo.py
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.certificate import CertificateData
from app.models.user import UserAccount
from app.schemas.certificate import CertificateCreate, CertificateUpdate


class CertificateRepository:
    """Data access helpers for certificate records."""

    CODE_PREFIX = "CERT"
    CODE_PADDING = 7

    def get(self, db: Session, cd_id: int) -> Optional[CertificateData]:
        return (
            db.query(CertificateData)
            .filter(
                CertificateData.cd_id == cd_id,
                CertificateData.cd_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_code(self, db: Session, cd_code: str) -> Optional[CertificateData]:
        return (
            db.query(CertificateData)
            .filter(
                CertificateData.cd_code == cd_code,
                CertificateData.cd_is_deleted.is_(False),
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
    ) -> list[CertificateData]:
        query = db.query(CertificateData).filter(
            CertificateData.cd_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    CertificateData.cd_code.ilike(term),
                    CertificateData.cd_stat.ilike(term),
                    CertificateData.cd_remarks.ilike(term),
                    CertificateData.cd_url.ilike(term),
                    CertificateData.cd_cat.ilike(term),
                )
            )

        return (
            query.order_by(CertificateData.cd_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(CertificateData.cd_id)).filter(
            CertificateData.cd_is_deleted.is_(False)
        )

        if search:
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    CertificateData.cd_code.ilike(term),
                    CertificateData.cd_stat.ilike(term),
                    CertificateData.cd_remarks.ilike(term),
                    CertificateData.cd_url.ilike(term),
                    CertificateData.cd_cat.ilike(term),
                )
            )

        return query.scalar() or 0

    def create(
        self,
        db: Session,
        *,
        data: CertificateCreate,
        actor_id: Optional[str],
    ) -> CertificateData:
        payload = data.model_dump()
        payload.pop("cd_code", None)
        payload["cd_code"] = self.generate_next_code(db)
        payload.setdefault("cd_is_deleted", False)
        payload.setdefault("cd_version_number", 1)
        payload["cd_created_by"] = actor_id
        payload["cd_updated_by"] = actor_id

        if actor_id:
            self._assert_user_exists(db, actor_id)

        entity = CertificateData(**payload)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    def update(
        self,
        db: Session,
        *,
        entity: CertificateData,
        data: CertificateUpdate,
        actor_id: Optional[str],
    ) -> CertificateData:
        update_data = data.model_dump(exclude_unset=True)
        update_data.pop("cd_code", None)
        for key, value in update_data.items():
            setattr(entity, key, value)

        if actor_id:
            self._assert_user_exists(db, actor_id)

        entity.cd_updated_by = actor_id
        entity.cd_version_number = (entity.cd_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(
        self, db: Session, *, entity: CertificateData, actor_id: Optional[str]
    ) -> CertificateData:
        entity.cd_is_deleted = True
        entity.cd_updated_by = actor_id
        entity.cd_version_number = (entity.cd_version_number or 1) + 1
        if actor_id:
            self._assert_user_exists(db, actor_id)
        db.commit()
        db.refresh(entity)
        return entity

    def generate_next_code(self, db: Session) -> str:
        latest_row = (
            db.query(CertificateData.cd_code)
            .filter(CertificateData.cd_code.like(f"{self.CODE_PREFIX}%"))
            .order_by(CertificateData.cd_code.desc())
            .first()
        )
        latest_code = latest_row[0] if latest_row else None
        next_sequence = self._extract_sequence(latest_code) + 1
        return f"{self.CODE_PREFIX}{next_sequence:0{self.CODE_PADDING}d}"

    def _extract_sequence(self, code: Optional[str]) -> int:
        if not code:
            return 0
        try:
            numeric_part = code[len(self.CODE_PREFIX) :]
            return int(numeric_part)
        except (ValueError, TypeError):
            return 0

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


certificate_repo = CertificateRepository()
