from typing import Optional

from sqlalchemy.orm import Session

from app.models.parshawadata import ParshawaData
from app.repositories.parshawadata_repo import parshawa_repo
from app.schemas.parshawadata import ParshawaCreate, ParshawaUpdate


class ParshawaService:
    """Business logic for Bhikku Parshawa data records."""

    def create(
        self,
        db: Session,
        *,
        payload: ParshawaCreate,
        actor_id: Optional[str],
    ) -> ParshawaData:
        return parshawa_repo.create(db, data=payload, actor_id=actor_id)

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[ParshawaData]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return parshawa_repo.list(db, skip=skip, limit=limit, search=search)

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        return parshawa_repo.count(db, search=search)

    def get(self, db: Session, pr_id: int) -> Optional[ParshawaData]:
        return parshawa_repo.get(db, pr_id)

    def get_by_prn(self, db: Session, pr_prn: str) -> Optional[ParshawaData]:
        return parshawa_repo.get_by_prn(db, pr_prn)

    def update(
        self,
        db: Session,
        *,
        entity: ParshawaData,
        payload: ParshawaUpdate,
        actor_id: Optional[str],
    ) -> ParshawaData:
        return parshawa_repo.update(
            db, entity=entity, data=payload, actor_id=actor_id
        )

    def soft_delete(
        self,
        db: Session,
        *,
        entity: ParshawaData,
        actor_id: Optional[str],
    ) -> ParshawaData:
        return parshawa_repo.soft_delete(db, entity=entity, actor_id=actor_id)


parshawa_service = ParshawaService()
