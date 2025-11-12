from typing import Optional

from sqlalchemy.orm import Session

from app.models.bhikku_id_card import BhikkuIDCard


class BhikkuIDRepository:
    """Access helpers for `bhikku_id_card` supplemental data."""

    def get_by_regn(self, db: Session, regn: str) -> Optional[BhikkuIDCard]:
        normalized = regn.strip() if isinstance(regn, str) else ""
        if not normalized:
            return None
        return (
            db.query(BhikkuIDCard)
            .filter(
                BhikkuIDCard.bic_regn == normalized,
                BhikkuIDCard.bic_is_deleted.is_(False),
            )
            .first()
        )


bhikku_id_repo = BhikkuIDRepository()

