from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.beneficiary import BeneficiaryData
from app.models.user import UserAccount
from app.schemas.beneficiary import BeneficiaryCreate, BeneficiaryUpdate


class BeneficiaryRepository:
    """Data access helpers for beneficiary records."""

    BNN_PREFIX = "BF"
    BNN_PADDING = 8

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
        payload["bf_is_deleted"] = False
        payload["bf_version_number"] = 1

        if payload.get("bf_id") is None:
            payload["bf_id"] = self._get_next_id(db)

        if not payload.get("bf_bnn"):
            payload["bf_bnn"] = self._format_bnn(payload["bf_id"])
        else:
            # Ensure bf_bnn follows the expected format before persisting.
            payload["bf_bnn"] = payload["bf_bnn"].upper()

        duplicate = (
            db.query(BeneficiaryData)
            .filter(BeneficiaryData.bf_bnn == payload["bf_bnn"])
            .first()
        )
        if duplicate:
            raise ValueError(f"bf_bnn '{payload['bf_bnn']}' already exists.")

        creator_id = payload.get("bf_created_by")
        if creator_id:
            self._assert_user_exists(db, creator_id)

        updater_id = payload.get("bf_updated_by")
        if updater_id:
            self._assert_user_exists(db, updater_id)

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
        update_data.pop("bf_version_number", None)
        update_data.pop("bf_id", None)

        updater_id = update_data.get("bf_updated_by")
        if updater_id:
            self._assert_user_exists(db, updater_id)

        for key, value in update_data.items():
            setattr(entity, key, value)

        entity.bf_version_number = (entity.bf_version_number or 1) + 1

        db.commit()
        db.refresh(entity)
        return entity

    def soft_delete(self, db: Session, *, entity: BeneficiaryData) -> BeneficiaryData:
        if entity.bf_updated_by:
            self._assert_user_exists(db, entity.bf_updated_by)

        entity.bf_is_deleted = True
        entity.bf_version_number = (entity.bf_version_number or 1) + 1
        db.commit()
        db.refresh(entity)
        return entity

    def _get_next_id(self, db: Session) -> int:
        max_id = db.query(func.max(BeneficiaryData.bf_id)).scalar()
        return (max_id or 0) + 1

    def _format_bnn(self, sequence: int) -> str:
        return f"{self.BNN_PREFIX}{sequence:0{self.BNN_PADDING}d}"

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


beneficiary_repo = BeneficiaryRepository()
