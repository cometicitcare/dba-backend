from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.beneficiary import BeneficiaryData
from app.repositories.beneficiary_repo import beneficiary_repo
from app.schemas.beneficiary import BeneficiaryCreate, BeneficiaryUpdate


class BeneficiaryService:
    """Business logic layer for beneficiary data."""

    def create_beneficiary(
        self, db: Session, *, payload: BeneficiaryCreate, actor_id: Optional[str]
    ) -> BeneficiaryData:
        existing = beneficiary_repo.get_by_bnn(db, payload.bf_bnn)
        if existing:
            raise ValueError(f"bf_bnn '{payload.bf_bnn}' already exists.")

        if payload.bf_email:
            email_conflict = beneficiary_repo.get_by_email(db, payload.bf_email)
            if email_conflict:
                raise ValueError(
                    f"bf_email '{payload.bf_email}' is already registered."
                )

        now = datetime.utcnow()
        payload_dict = payload.model_dump()
        payload_dict["bf_created_by"] = actor_id
        payload_dict["bf_updated_by"] = actor_id
        payload_dict.setdefault("bf_created_at", now)
        payload_dict.setdefault("bf_updated_at", now)

        enriched_payload = BeneficiaryCreate(**payload_dict)
        return beneficiary_repo.create(db, data=enriched_payload)

    def list_beneficiaries(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> list[BeneficiaryData]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return beneficiary_repo.list(db, skip=skip, limit=limit, search=search)

    def count_beneficiaries(self, db: Session, *, search: Optional[str] = None) -> int:
        return beneficiary_repo.count(db, search=search)

    def get_beneficiary(self, db: Session, bf_id: int) -> Optional[BeneficiaryData]:
        return beneficiary_repo.get(db, bf_id)

    def get_beneficiary_by_bnn(
        self, db: Session, bf_bnn: str
    ) -> Optional[BeneficiaryData]:
        return beneficiary_repo.get_by_bnn(db, bf_bnn)

    def update_beneficiary(
        self,
        db: Session,
        *,
        bf_id: int,
        payload: BeneficiaryUpdate,
        actor_id: Optional[str],
    ) -> BeneficiaryData:
        entity = beneficiary_repo.get(db, bf_id)
        if not entity:
            raise ValueError("Beneficiary record not found.")

        if payload.bf_bnn and payload.bf_bnn != entity.bf_bnn:
            duplicate = beneficiary_repo.get_by_bnn(db, payload.bf_bnn)
            if duplicate:
                raise ValueError(f"bf_bnn '{payload.bf_bnn}' already exists.")

        if payload.bf_email and payload.bf_email != entity.bf_email:
            email_conflict = beneficiary_repo.get_by_email(db, payload.bf_email)
            if email_conflict:
                raise ValueError(
                    f"bf_email '{payload.bf_email}' is already registered."
                )

        update_data = payload.model_dump(exclude_unset=True)
        update_data["bf_updated_by"] = actor_id
        update_data["bf_updated_at"] = datetime.utcnow()

        patched_payload = BeneficiaryUpdate(**update_data)
        return beneficiary_repo.update(db, entity=entity, data=patched_payload)

    def delete_beneficiary(
        self, db: Session, *, bf_id: int, actor_id: Optional[str]
    ) -> BeneficiaryData:
        entity = beneficiary_repo.get(db, bf_id)
        if not entity:
            raise ValueError("Beneficiary record not found.")

        entity.bf_updated_by = actor_id
        entity.bf_updated_at = datetime.utcnow()
        return beneficiary_repo.soft_delete(db, entity=entity)


beneficiary_service = BeneficiaryService()
