from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.beneficiary import BeneficiaryData
from app.schemas.beneficiary import BeneficiaryCreate, BeneficiaryUpdate


class BeneficiaryRepository:
    """Data access helpers for beneficiary records."""

    def get(self, db: Session, bf_id: int) -> Optional[BeneficiaryData]:
        return (
            db.query(BeneficiaryData)
            .filter(
                BeneficiaryData.bf_id == bf_id,
                BeneficiaryData.bf_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_bnn(self, db: Session, bf_bnn: str) -> Optional[BeneficiaryData]:
        return (
            db.query(BeneficiaryData)
            .filter(
                BeneficiaryData.bf_bnn == bf_bnn,
                BeneficiaryData.bf_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_email(self, db: Session, bf_email: str) -> Optional[BeneficiaryData]:
        return (
            db.query(BeneficiaryData)
            .filter(
                BeneficiaryData.bf_email == bf_email,
                BeneficiaryData.bf_is_deleted.is_(False),
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
    ) -> list[BeneficiaryData]:
        query = db.query(BeneficiaryData).filter(
            BeneficiaryData.bf_is_deleted.is_(False)
        )

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BeneficiaryData.bf_bnn.ilike(search_term),
                    BeneficiaryData.bf_bfname.ilike(search_term),
                    BeneficiaryData.bf_bfaddrs.ilike(search_term),
                    BeneficiaryData.bf_mobile.ilike(search_term),
                    BeneficiaryData.bf_whatapp.ilike(search_term),
                    BeneficiaryData.bf_email.ilike(search_term),
                )
            )

        return (
            query.order_by(BeneficiaryData.bf_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def count(self, db: Session, *, search: Optional[str] = None) -> int:
        query = db.query(func.count(BeneficiaryData.bf_id)).filter(
            BeneficiaryData.bf_is_deleted.is_(False)
        )

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    BeneficiaryData.bf_bnn.ilike(search_term),
                    BeneficiaryData.bf_bfname.ilike(search_term),
                    BeneficiaryData.bf_bfaddrs.ilike(search_term),
                    BeneficiaryData.bf_mobile.ilike(search_term),
                    BeneficiaryData.bf_whatapp.ilike(search_term),
                    BeneficiaryData.bf_email.ilike(search_term),
                )
            )

        return query.scalar() or 0

    def create(self, db: Session, *, data: BeneficiaryCreate) -> BeneficiaryData:
        payload = data.model_dump()
        payload.setdefault("bf_is_deleted", False)
        payload.setdefault("bf_version_number", 1)

        beneficiary = BeneficiaryData(**payload)
        db.add(beneficiary)
        db.commit()
        db.refresh(beneficiary)
        return beneficiary

    def update(
        self,
        db: Session,
        *,
        entity: BeneficiaryData,
        data: BeneficiaryUpdate,
    ) -> BeneficiaryData:
        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.bf_version_number = (entity.bf_version_number or 1) + 1

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(self, db: Session, *, entity: BeneficiaryData) -> BeneficiaryData:
        entity.bf_is_deleted = True
        entity.bf_version_number = (entity.bf_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity


beneficiary_repo = BeneficiaryRepository()
