from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.vihara import ViharaData
from app.repositories.vihara_repo import vihara_repo
from app.schemas.vihara import ViharaCreate, ViharaUpdate


class ViharaService:
    """Business logic layer for vihara data."""

    def create_vihara(
        self, db: Session, *, payload: ViharaCreate, actor_id: Optional[str]
    ) -> ViharaData:
        existing = vihara_repo.get_by_trn(db, payload.vh_trn)
        if existing:
            raise ValueError(f"vh_trn '{payload.vh_trn}' already exists.")

        email_conflict = vihara_repo.get_by_email(db, payload.vh_email)
        if email_conflict:
            raise ValueError(f"vh_email '{payload.vh_email}' is already registered.")

        now = datetime.utcnow()
        payload_dict = payload.model_dump()
        payload_dict["vh_created_by"] = actor_id
        payload_dict["vh_updated_by"] = actor_id
        payload_dict.setdefault("vh_created_at", now)
        payload_dict.setdefault("vh_updated_at", now)

        enriched_payload = ViharaCreate(**payload_dict)
        return vihara_repo.create(db, data=enriched_payload)

    def list_viharas(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[ViharaData]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return vihara_repo.list(db, skip=skip, limit=limit, search=search)

    def count_viharas(self, db: Session, *, search: Optional[str] = None) -> int:
        return vihara_repo.count(db, search=search)

    def get_vihara(self, db: Session, vh_id: int) -> Optional[ViharaData]:
        return vihara_repo.get(db, vh_id)

    def get_vihara_by_trn(self, db: Session, vh_trn: str) -> Optional[ViharaData]:
        return vihara_repo.get_by_trn(db, vh_trn)

    def update_vihara(
        self,
        db: Session,
        *,
        vh_id: int,
        payload: ViharaUpdate,
        actor_id: Optional[str],
    ) -> ViharaData:
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")

        if payload.vh_trn and payload.vh_trn != entity.vh_trn:
            duplicate = vihara_repo.get_by_trn(db, payload.vh_trn)
            if duplicate:
                raise ValueError(f"vh_trn '{payload.vh_trn}' already exists.")

        if payload.vh_email and payload.vh_email != entity.vh_email:
            email_conflict = vihara_repo.get_by_email(db, payload.vh_email)
            if email_conflict:
                raise ValueError(
                    f"vh_email '{payload.vh_email}' is already registered."
                )

        update_data = payload.model_dump(exclude_unset=True)
        update_data["vh_updated_by"] = actor_id
        update_data["vh_updated_at"] = datetime.utcnow()

        patched_payload = ViharaUpdate(**update_data)
        return vihara_repo.update(db, entity=entity, data=patched_payload)

    def delete_vihara(
        self, db: Session, *, vh_id: int, actor_id: Optional[str]
    ) -> ViharaData:
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")

        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        return vihara_repo.soft_delete(db, entity=entity)


vihara_service = ViharaService()
