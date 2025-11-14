# app/repositories/bhikku_repo.py
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, aliased

from app.models import bhikku as models
from app.models.bhikku_category import BhikkuCategory
from app.models.district import District
from app.models.divisional_secretariat import DivisionalSecretariat
from app.models.gramasewaka import Gramasewaka
from app.models.nikaya import NikayaData
from app.models.parshawadata import ParshawaData
from app.models.province import Province
from app.models.status import StatusData
from app.models.vihara import ViharaData
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

    def get_with_master_by_regn(self, db: Session, br_regn: str):
        query = self._query_with_master_data(db)
        return (
            query.filter(
                models.Bhikku.br_regn == br_regn,
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
        province: Optional[str] = None,
        vh_trn: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ):
        """Get paginated bhikkus with optional search functionality and filters."""
        query = db.query(models.Bhikku).filter(models.Bhikku.br_is_deleted.is_(False))

        query = self._apply_filters(
            query,
            search_key=search_key,
            province=province,
            vh_trn=vh_trn,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            temple=temple,
            child_temple=child_temple,
            nikaya=nikaya,
            parshawaya=parshawaya,
            category=category,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

        return (
            query.order_by(models.Bhikku.br_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def get_all_with_master(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search_key: Optional[str] = None,
        province: Optional[str] = None,
        vh_trn: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ):
        query = self._query_with_master_data(db).filter(
            models.Bhikku.br_is_deleted.is_(False)
        )
        query = self._apply_filters(
            query,
            search_key=search_key,
            province=province,
            vh_trn=vh_trn,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            temple=temple,
            child_temple=child_temple,
            nikaya=nikaya,
            parshawaya=parshawaya,
            category=category,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )
        return (
            query.order_by(models.Bhikku.br_id)
            .offset(max(skip, 0))
            .limit(limit)
            .all()
        )

    def get_total_count(
        self,
        db: Session,
        search_key: Optional[str] = None,
        province: Optional[str] = None,
        vh_trn: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ):
        """Get total count of non-deleted bhikkus for pagination with optional search and filters."""
        query = db.query(func.count(models.Bhikku.br_id)).filter(
            models.Bhikku.br_is_deleted.is_(False)
        )

        query = self._apply_filters(
            query,
            search_key=search_key,
            province=province,
            vh_trn=vh_trn,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            temple=temple,
            child_temple=child_temple,
            nikaya=nikaya,
            parshawaya=parshawaya,
            category=category,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

        return query.scalar()

    def _normalize_text_filter(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed if trimmed else None

    def _normalize_list_filter(self, values: Optional[List[str]]) -> List[str]:
        if not values:
            return []
        return [item.strip() for item in values if item and item.strip()]

    def _apply_filters(
        self,
        query,
        *,
        search_key: Optional[str] = None,
        province: Optional[str] = None,
        vh_trn: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ):
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

        province = self._normalize_text_filter(province)
        if province:
            query = query.filter(models.Bhikku.br_province == province)

        vh_trn = self._normalize_text_filter(vh_trn)
        if vh_trn:
            query = query.filter(models.Bhikku.br_viharadhipathi == vh_trn)

        district = self._normalize_text_filter(district)
        if district:
            query = query.filter(models.Bhikku.br_district == district)

        divisional_secretariat = self._normalize_text_filter(divisional_secretariat)
        if divisional_secretariat:
            query = query.filter(models.Bhikku.br_division == divisional_secretariat)

        gn_division = self._normalize_text_filter(gn_division)
        if gn_division:
            query = query.filter(models.Bhikku.br_gndiv == gn_division)

        temple = self._normalize_text_filter(temple)
        if temple:
            query = query.filter(models.Bhikku.br_mahanatemple == temple)

        child_temple = self._normalize_text_filter(child_temple)
        if child_temple:
            query = query.filter(models.Bhikku.br_livtemple == child_temple)

        nikaya = self._normalize_text_filter(nikaya)
        if nikaya:
            query = query.filter(models.Bhikku.br_nikaya == nikaya)

        parshawaya = self._normalize_text_filter(parshawaya)
        if parshawaya:
            query = query.filter(models.Bhikku.br_parshawaya == parshawaya)

        category_items = self._normalize_list_filter(category)
        if category_items:
            query = query.filter(models.Bhikku.br_cat.in_(category_items))

        status_items = self._normalize_list_filter(status)
        if status_items:
            query = query.filter(models.Bhikku.br_currstat.in_(status_items))

        if date_from:
            query = query.filter(models.Bhikku.br_reqstdate >= date_from)
        if date_to:
            query = query.filter(models.Bhikku.br_reqstdate <= date_to)

        return query

    def _query_with_master_data(self, db: Session):
        province_alias = aliased(Province)
        district_alias = aliased(District)
        division_alias = aliased(DivisionalSecretariat)
        gn_alias = aliased(Gramasewaka)
        status_alias = aliased(StatusData)
        parshawaya_alias = aliased(ParshawaData)
        nikaya_alias = aliased(NikayaData)
        category_alias = aliased(BhikkuCategory)
        liv_temple_alias = aliased(ViharaData)
        mahanatemple_alias = aliased(ViharaData)
        robing_tutor_alias = aliased(ViharaData)
        robing_after_alias = aliased(ViharaData)
        acharya_alias = aliased(models.Bhikku)
        viharadhipathi_alias = aliased(models.Bhikku)

        return (
            db.query(
                models.Bhikku,
                province_alias.cp_name.label("br_province_name"),
                district_alias.dd_dname.label("br_district_name"),
                division_alias.dv_dvname.label("br_division_name"),
                gn_alias.gn_gnname.label("br_gndiv_name"),
                status_alias.st_descr.label("br_currstat_name"),
                parshawaya_alias.pr_pname.label("br_parshawaya_name"),
                nikaya_alias.nk_nname.label("br_nikaya_name"),
                category_alias.cc_catogry.label("br_cat_name"),
                liv_temple_alias.vh_vname.label("br_livtemple_name"),
                mahanatemple_alias.vh_vname.label("br_mahanatemple_name"),
                robing_tutor_alias.vh_vname.label(
                    "br_robing_tutor_residence_name"
                ),
                robing_after_alias.vh_vname.label(
                    "br_robing_after_residence_temple_name"
                ),
                func.coalesce(
                    acharya_alias.br_mahananame, acharya_alias.br_gihiname
                ).label("br_mahanaacharyacd_name"),
                func.coalesce(
                    viharadhipathi_alias.br_mahananame,
                    viharadhipathi_alias.br_gihiname,
                ).label("br_viharadhipathi_name"),
            )
            .outerjoin(
                province_alias,
                and_(
                    province_alias.cp_code == models.Bhikku.br_province,
                    province_alias.cp_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                district_alias,
                and_(
                    district_alias.dd_dcode == models.Bhikku.br_district,
                    district_alias.dd_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                division_alias,
                and_(
                    division_alias.dv_dvcode == models.Bhikku.br_division,
                    division_alias.dv_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                gn_alias,
                and_(
                    gn_alias.gn_gnc == models.Bhikku.br_gndiv,
                    gn_alias.gn_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                status_alias,
                and_(
                    status_alias.st_statcd == models.Bhikku.br_currstat,
                    status_alias.st_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                parshawaya_alias,
                and_(
                    parshawaya_alias.pr_prn == models.Bhikku.br_parshawaya,
                    parshawaya_alias.pr_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                nikaya_alias,
                and_(
                    nikaya_alias.nk_nkn == models.Bhikku.br_nikaya,
                    nikaya_alias.nk_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                category_alias,
                and_(
                    category_alias.cc_code == models.Bhikku.br_cat,
                    category_alias.cc_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                liv_temple_alias,
                and_(
                    liv_temple_alias.vh_trn == models.Bhikku.br_livtemple,
                    liv_temple_alias.vh_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                mahanatemple_alias,
                and_(
                    mahanatemple_alias.vh_trn == models.Bhikku.br_mahanatemple,
                    mahanatemple_alias.vh_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                robing_tutor_alias,
                and_(
                    robing_tutor_alias.vh_trn
                    == models.Bhikku.br_robing_tutor_residence,
                    robing_tutor_alias.vh_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                robing_after_alias,
                and_(
                    robing_after_alias.vh_trn
                    == models.Bhikku.br_robing_after_residence_temple,
                    robing_after_alias.vh_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                acharya_alias,
                and_(
                    acharya_alias.br_regn == models.Bhikku.br_mahanaacharyacd,
                    acharya_alias.br_is_deleted.is_(False),
                ),
            )
            .outerjoin(
                viharadhipathi_alias,
                and_(
                    viharadhipathi_alias.br_regn
                    == models.Bhikku.br_viharadhipathi,
                    viharadhipathi_alias.br_is_deleted.is_(False),
                ),
            )
        )

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
