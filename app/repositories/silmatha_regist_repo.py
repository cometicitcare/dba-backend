# app/repositories/silmatha_regist_repo.py
from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models.bhikku import Bhikku as BhikkuModel
from app.models.silmatha_regist import SilmathaRegist


class SilmathaRegistRepository:
    """Persist Silmatha-specific registrations for CAT01 bhikkus."""

    def create_from_bhikku(self, db: Session, bhikku: BhikkuModel) -> SilmathaRegist:
        payload = self._serialize_from_bhikku(bhikku)
        silmatha = SilmathaRegist(**payload)
        now = datetime.utcnow()
        silmatha.br_created_at = now
        silmatha.br_updated_at = now
        silmatha.br_version = now
        silmatha.br_is_deleted = False
        silmatha.br_version_number = 1

        db.add(silmatha)
        db.commit()
        db.refresh(silmatha)
        return silmatha

    def _serialize_from_bhikku(self, bhikku: BhikkuModel) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for column in SilmathaRegist.__table__.columns:
            name = column.name
            if name == "br_id":
                continue
            data[name] = getattr(bhikku, name)
        return data


silmatha_regist_repo = SilmathaRegistRepository()
