# app/repositories/bhikku_repo.py
from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models import bhikku as models
from app.schemas import bhikku as schemas


class BhikkuRepository:
    """
    Data access helper for the `bhikku_regist` table.

    This repository keeps the legacy functional interface used elsewhere in the
    codebase while encapsulating repeated logic such as registration number
    generation and version updates.
    """

    def generate_next_regn(self, db: Session) -> str:
        """
        Generate the next registration number in format: BH{YEAR}{SEQUENCE}.

        Example: BH2025000001, BH2025000002, etc.
        Total length: BH(2) + YEAR(4) + SEQUENCE(6) = 12 characters.
        """
        current_year = datetime.utcnow().year
        prefix = f"BH{current_year}"

        latest = (
            db.query(models.Bhikku)
            .filter(models.Bhikku.br_regn.like(f"{prefix}%"))
            .order_by(models.Bhikku.br_regn.desc())
            .first()
        )

        if latest:
            try:
                sequence_part = latest.br_regn[len(prefix) :]
                last_sequence = int(sequence_part)
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1

        return f"{prefix}{next_sequence:06d}"

    def get_by_id(self, db: Session, br_id: int):
        return (
            db.query(models.Bhikku)
            .filter(
                models.Bhikku.br_id == br_id,
                models.Bhikku.br_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_regn(self, db: Session, br_regn: str):
        return (
            db.query(models.Bhikku)
            .filter(
                models.Bhikku.br_regn == br_regn,
                models.Bhikku.br_is_deleted.is_(False),
            )
            .first()
        )

    def get_raw_by_regn(self, db: Session, br_regn: str):
        """Return a Bhikku record by registration number without filtering deleted rows."""
        return (
            db.query(models.Bhikku)
            .filter(models.Bhikku.br_regn == br_regn)
            .first()
        )

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search_key: Optional[str] = None,
    ):
        """Get paginated bhikkus with optional search functionality across all text fields."""
        query = db.query(models.Bhikku).filter(models.Bhikku.br_is_deleted.is_(False))

        if search_key and search_key.strip():
            search_pattern = f"%{search_key.strip()}%"
            query = query.filter(
                or_(
                    models.Bhikku.br_regn.ilike(search_pattern),
                    models.Bhikku.br_upasampada_serial_no.ilike(search_pattern),
                    models.Bhikku.br_gihiname.ilike(search_pattern),
                    models.Bhikku.br_fathrname.ilike(search_pattern),
                    models.Bhikku.br_mahananame.ilike(search_pattern),
                    models.Bhikku.br_birthpls.ilike(search_pattern),
                    models.Bhikku.br_province.ilike(search_pattern),
                    models.Bhikku.br_district.ilike(search_pattern),
                    models.Bhikku.br_korale.ilike(search_pattern),
                    models.Bhikku.br_pattu.ilike(search_pattern),
                    models.Bhikku.br_division.ilike(search_pattern),
                    models.Bhikku.br_vilage.ilike(search_pattern),
                    models.Bhikku.br_gndiv.ilike(search_pattern),
                    models.Bhikku.br_mobile.ilike(search_pattern),
                    models.Bhikku.br_email.ilike(search_pattern),
                    models.Bhikku.br_fathrsaddrs.ilike(search_pattern),
                    models.Bhikku.br_fathrsmobile.ilike(search_pattern),
                    models.Bhikku.br_parshawaya.ilike(search_pattern),
                    models.Bhikku.br_nikaya.ilike(search_pattern),
                    models.Bhikku.br_livtemple.ilike(search_pattern),
                    models.Bhikku.br_mahanatemple.ilike(search_pattern),
                    models.Bhikku.br_mahanaacharyacd.ilike(search_pattern),
                    models.Bhikku.br_currstat.ilike(search_pattern),
                    models.Bhikku.br_cat.ilike(search_pattern),
                    models.Bhikku.br_mahanayaka_name.ilike(search_pattern),
                    models.Bhikku.br_mahanayaka_address.ilike(search_pattern),
                    models.Bhikku.br_viharadhipathi.ilike(search_pattern),
                    models.Bhikku.br_residence_at_declaration.ilike(search_pattern),
                    models.Bhikku.br_robing_tutor_residence.ilike(search_pattern),
                    models.Bhikku.br_robing_after_residence_temple.ilike(search_pattern),
                )
            )

        return (
            query.order_by(models.Bhikku.br_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def get_total_count(self, db: Session, search_key: Optional[str] = None):
        """Get total count of non-deleted bhikkus for pagination with optional search."""
        query = db.query(func.count(models.Bhikku.br_id)).filter(
            models.Bhikku.br_is_deleted.is_(False)
        )

        if search_key and search_key.strip():
            search_pattern = f"%{search_key.strip()}%"
            query = query.filter(
                or_(
                    models.Bhikku.br_regn.ilike(search_pattern),
                    models.Bhikku.br_upasampada_serial_no.ilike(search_pattern),
                    models.Bhikku.br_gihiname.ilike(search_pattern),
                    models.Bhikku.br_fathrname.ilike(search_pattern),
                    models.Bhikku.br_mahananame.ilike(search_pattern),
                    models.Bhikku.br_birthpls.ilike(search_pattern),
                    models.Bhikku.br_province.ilike(search_pattern),
                    models.Bhikku.br_district.ilike(search_pattern),
                    models.Bhikku.br_korale.ilike(search_pattern),
                    models.Bhikku.br_pattu.ilike(search_pattern),
                    models.Bhikku.br_division.ilike(search_pattern),
                    models.Bhikku.br_vilage.ilike(search_pattern),
                    models.Bhikku.br_gndiv.ilike(search_pattern),
                    models.Bhikku.br_mobile.ilike(search_pattern),
                    models.Bhikku.br_email.ilike(search_pattern),
                    models.Bhikku.br_fathrsaddrs.ilike(search_pattern),
                    models.Bhikku.br_fathrsmobile.ilike(search_pattern),
                    models.Bhikku.br_parshawaya.ilike(search_pattern),
                    models.Bhikku.br_nikaya.ilike(search_pattern),
                    models.Bhikku.br_livtemple.ilike(search_pattern),
                    models.Bhikku.br_mahanatemple.ilike(search_pattern),
                    models.Bhikku.br_mahanaacharyacd.ilike(search_pattern),
                    models.Bhikku.br_currstat.ilike(search_pattern),
                    models.Bhikku.br_cat.ilike(search_pattern),
                    models.Bhikku.br_mahanayaka_name.ilike(search_pattern),
                    models.Bhikku.br_mahanayaka_address.ilike(search_pattern),
                    models.Bhikku.br_viharadhipathi.ilike(search_pattern),
                    models.Bhikku.br_residence_at_declaration.ilike(search_pattern),
                    models.Bhikku.br_robing_tutor_residence.ilike(search_pattern),
                    models.Bhikku.br_robing_after_residence_temple.ilike(search_pattern),
                )
            )

        return query.scalar()

    def get_by_mobile(self, db: Session, br_mobile: str):
        return (
            db.query(models.Bhikku)
            .filter(
                models.Bhikku.br_mobile == br_mobile,
                models.Bhikku.br_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_email(self, db: Session, br_email: str):
        return (
            db.query(models.Bhikku)
            .filter(
                models.Bhikku.br_email == br_email,
                models.Bhikku.br_is_deleted.is_(False),
            )
            .first()
        )

    def get_by_fathrsmobile(self, db: Session, br_fathrsmobile: str):
        return (
            db.query(models.Bhikku)
            .filter(
                models.Bhikku.br_fathrsmobile == br_fathrsmobile,
                models.Bhikku.br_is_deleted.is_(False),
            )
            .first()
        )

    def create(self, db: Session, bhikku: schemas.BhikkuCreate):
        # Auto-generate br_regn if not provided or empty.
        if not bhikku.br_regn or bhikku.br_regn.strip() == "":
            bhikku.br_regn = self.generate_next_regn(db)

        db_bhikku = models.Bhikku(**bhikku.model_dump())
        now = datetime.utcnow()
        db_bhikku.br_is_deleted = False
        db_bhikku.br_version_number = 1
        db_bhikku.br_created_at = now
        db_bhikku.br_updated_at = now
        db_bhikku.br_version = now

        db.add(db_bhikku)
        db.commit()
        db.refresh(db_bhikku)
        return db_bhikku

    def update(self, db: Session, br_regn: str, bhikku_update: schemas.BhikkuUpdate):
        db_bhikku = self.get_by_regn(db, br_regn)
        if not db_bhikku:
            return None

        update_data = bhikku_update.model_dump(exclude_unset=True)
        update_data.pop("br_regn", None)
        update_data.pop("br_version_number", None)

        for key, value in update_data.items():
            setattr(db_bhikku, key, value)

        db_bhikku.br_version_number = (db_bhikku.br_version_number or 1) + 1
        now = datetime.utcnow()
        db_bhikku.br_updated_at = now
        db_bhikku.br_version = now

        db.commit()
        db.refresh(db_bhikku)
        return db_bhikku

    def delete(self, db: Session, br_regn: str, updated_by: Optional[str] = None):
        db_bhikku = self.get_by_regn(db, br_regn)
        if not db_bhikku:
            return None

        db_bhikku.br_is_deleted = True
        if updated_by:
            db_bhikku.br_updated_by = updated_by
        db_bhikku.br_version_number = (db_bhikku.br_version_number or 1) + 1
        now = datetime.utcnow()
        db_bhikku.br_updated_at = now
        db_bhikku.br_version = now

        db.commit()
        db.refresh(db_bhikku)
        return db_bhikku


bhikku_repo = BhikkuRepository()


def generate_next_regn(db: Session) -> str:
    return bhikku_repo.generate_next_regn(db)


def get_by_id(db: Session, br_id: int):
    return bhikku_repo.get_by_id(db, br_id)


def get_by_regn(db: Session, br_regn: str):
    return bhikku_repo.get_by_regn(db, br_regn)


def get_all(
    db: Session, skip: int = 0, limit: int = 100, search_key: Optional[str] = None
):
    return bhikku_repo.get_all(db, skip=skip, limit=limit, search_key=search_key)


def get_total_count(db: Session, search_key: Optional[str] = None):
    return bhikku_repo.get_total_count(db, search_key=search_key)


def create(db: Session, bhikku: schemas.BhikkuCreate):
    return bhikku_repo.create(db, bhikku)


def update(db: Session, br_regn: str, bhikku_update: schemas.BhikkuUpdate):
    return bhikku_repo.update(db, br_regn=br_regn, bhikku_update=bhikku_update)


def delete(db: Session, br_regn: str):
    return bhikku_repo.delete(db, br_regn=br_regn)


def get_by_mobile(db: Session, br_mobile: str):
    return bhikku_repo.get_by_mobile(db, br_mobile)


def get_by_email(db: Session, br_email: str):
    return bhikku_repo.get_by_email(db, br_email)


def get_by_fathrsmobile(db: Session, br_fathrsmobile: str):
    return bhikku_repo.get_by_fathrsmobile(db, br_fathrsmobile)
