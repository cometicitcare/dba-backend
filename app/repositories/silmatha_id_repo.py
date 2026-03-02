from __future__ import annotations

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.silmatha_id_card import SilmathaIDCard


class SilmathaIDRepository:
    """Access helpers for `silmatha_id_card` supplemental data."""

    def get_by_regn(self, db: Session, regn: str) -> Optional[SilmathaIDCard]:
        normalized = regn.strip() if isinstance(regn, str) else ""
        if not normalized:
            return None

        return (
            db.query(SilmathaIDCard)
            .filter(
                func.upper(SilmathaIDCard.sic_regn) == normalized.upper(),
                SilmathaIDCard.sic_is_deleted.is_(False),
            )
            .first()
        )


silmatha_id_repo = SilmathaIDRepository()
