from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.vihara import ViharaData
from app.schemas.vihara import ViharaCreate, ViharaUpdate


class ViharaRepository:
    """Data access helpers for vihara records."""

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

    def allocate_identifiers(self, db: Session) -> tuple[int, str]:
        next_id = (db.query(func.max(ViharaData.vh_id)).scalar() or 0) + 1
        next_trn = self._format_vh_trn(next_id)

        while (
            db.query(ViharaData)
            .filter(or_(ViharaData.vh_id == next_id, ViharaData.vh_trn == next_trn))
            .first()
        ):
            next_id += 1
            next_trn = self._format_vh_trn(next_id)

        return next_id, next_trn

    @staticmethod
    def _format_vh_trn(sequence: int) -> str:
        return f"TRN{sequence:07d}"

    def create(self, db: Session, *, data: ViharaCreate) -> ViharaData:
        payload = data.model_dump()
        payload.setdefault("vh_is_deleted", False)
        payload["vh_version_number"] = 1
        next_id, next_trn = self.allocate_identifiers(db)
        payload["vh_id"] = next_id
        payload["vh_trn"] = next_trn

        vihara = ViharaData(**payload)
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
        update_data = data.model_dump(exclude_unset=True)

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


vihara_repo = ViharaRepository()
