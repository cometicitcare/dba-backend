from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.main_bhikku import MainBhikku
from app.repositories.main_bhikku_repo import main_bhikku_repo
from app.schemas.main_bhikku import MainBhikkuCreate, MainBhikkuUpdate


class MainBhikkuService:
    """Business logic for managing Nikaya / Parshawaya Mahanayaka records."""

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create_entry(
        self, db: Session, *, payload: MainBhikkuCreate, actor_id: Optional[str]
    ) -> MainBhikku:
        # Deactivate any existing active record for the same slot
        main_bhikku_repo.deactivate_existing(
            db,
            mb_nikaya_cd=payload.mb_nikaya_cd,
            mb_type=payload.mb_type.value,
            mb_parshawa_cd=payload.mb_parshawa_cd,
            actor_id=actor_id,
        )
        return main_bhikku_repo.create(db, data=payload, actor_id=actor_id)

    def get_by_id(self, db: Session, mb_id: int) -> Optional[MainBhikku]:
        return main_bhikku_repo.get(db, mb_id)

    def list_entries(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        mb_type: Optional[str] = None,
        mb_nikaya_cd: Optional[str] = None,
        mb_parshawa_cd: Optional[str] = None,
    ) -> list[MainBhikku]:
        return main_bhikku_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
            mb_type=mb_type,
            mb_nikaya_cd=mb_nikaya_cd,
            mb_parshawa_cd=mb_parshawa_cd,
        )

    def count_entries(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        mb_type: Optional[str] = None,
        mb_nikaya_cd: Optional[str] = None,
        mb_parshawa_cd: Optional[str] = None,
    ) -> int:
        return main_bhikku_repo.count(
            db,
            search=search,
            mb_type=mb_type,
            mb_nikaya_cd=mb_nikaya_cd,
            mb_parshawa_cd=mb_parshawa_cd,
        )

    def update_entry(
        self,
        db: Session,
        *,
        mb_id: int,
        payload: MainBhikkuUpdate,
        actor_id: Optional[str],
    ) -> MainBhikku:
        entity = main_bhikku_repo.get(db, mb_id)
        if not entity:
            raise ValueError("Main bhikku record not found.")
        return main_bhikku_repo.update(db, entity=entity, data=payload, actor_id=actor_id)

    def delete_entry(
        self,
        db: Session,
        *,
        mb_id: int,
        actor_id: Optional[str],
    ) -> MainBhikku:
        entity = main_bhikku_repo.get(db, mb_id)
        if not entity:
            raise ValueError("Main bhikku record not found.")
        return main_bhikku_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    # ------------------------------------------------------------------
    # Helper used by set-mahanayaka endpoints
    # ------------------------------------------------------------------

    def upsert_from_appointment(
        self,
        db: Session,
        *,
        mb_type: str,
        mb_nikaya_cd: str,
        mb_parshawa_cd: Optional[str],
        mb_bhikku_regn: str,
        mb_start_date=None,
        mb_remarks: Optional[str] = None,
        actor_id: Optional[str],
    ) -> MainBhikku:
        """Called when set-nikaya-mahanayaka or set-parshawa-mahanayaka fires.

        Deactivates the old active record (if any) and creates a fresh one.
        """
        create_payload = MainBhikkuCreate(
            mb_type=mb_type,
            mb_nikaya_cd=mb_nikaya_cd,
            mb_parshawa_cd=mb_parshawa_cd,
            mb_bhikku_regn=mb_bhikku_regn,
            mb_start_date=mb_start_date,
            mb_remarks=mb_remarks,
            mb_is_active=True,
        )
        return self.create_entry(db, payload=create_payload, actor_id=actor_id)


main_bhikku_service = MainBhikkuService()
