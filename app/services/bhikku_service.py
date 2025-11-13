from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, date
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import MetaData, Table, select, text
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.bhikku import Bhikku
from app.models.bhikku_high import BhikkuHighRegist
from app.models.nikaya import NikayaData
from app.models.parshawadata import ParshawaData
from app.models.user import UserAccount
from app.models.vihara import ViharaData
from app.repositories.bhikku_repo import bhikku_repo
from app.schemas.bhikku import BhikkuCreate, BhikkuUpdate


class BhikkuService:
    """Business logic and validation helpers for bhikku registrations."""

    FK_TABLE_MAP: Dict[str, Tuple[Optional[str], str, str]] = {
        "br_gndiv": ("public", "cmm_gndata", "gn_gnc"),
        "br_currstat": ("public", "statusdata", "st_statcd"),
        "br_parshawaya": ("public", "cmm_parshawadata", "pr_prn"),
        "br_cat": ("public", "cmm_cat", "cc_code"),
        "br_nikaya": ("public", "cmm_nikayadata", "nk_nkn"),
    }

    MOBILE_PATTERN = re.compile(r"^0\d{9}$")

    def __init__(self) -> None:
        self._table_cache: Dict[Tuple[Optional[str], str], Table] = {}
        self._mahanayaka_view_query = text(
            """
            SELECT regn, mahananame, currstat, vname, addrs
            FROM bikkudtls_mahanayakalist
            """
        )
        self._nikaya_view_query = text(
            """
            SELECT nkn, nname, prn, pname, regn
            FROM bikkudtls_nikaya_list
            """
        )
        self._acharya_view_query = text(
            """
            SELECT currstated, mobile, email, mahanadate, reqstdate, regn
            FROM bikkudtls_archarya_dtls
            """
        )
        self._details_view_query = text(
            """
            SELECT regn, birthpls, gihiname, dofb, fathrname, mahanadate,
                   mahananame, teacher, teachadrs, mhanavh, livetemple,
                   viharadipathi, pname, nname, nikayanayaka, effctdate,
                   curstatus, catogry, vadescrdtls
            FROM bikkudtls_bikkullist
            """
        )
        self._certification_view_query = text(
            """
            SELECT regno, mahananame, issuedate, reqstdate, adminautho,
                   prtoptn, paydate, payamount, usname, adminusr
            FROM bikkudtls_certification_data
            """
        )
        self._certification_print_view_query = text(
            """
            SELECT regno, mahananame, issuedate, reqstdate, adminautho,
                   prtoptn, paydate, payamount, usname, adminusr
            FROM bikkudtls_certification_printnow
            """
        )
        self._current_status_view_query = text(
            """
            SELECT statcd, descr, regn
            FROM bikkudtls_currstatus_list
            """
        )
        self._district_view_query = text(
            """
            SELECT dcode, dname, regn
            FROM bikkudtls_districtlist
            """
        )
        self._division_sec_view_query = text(
            """
            SELECT dvcode, dvname, regn
            FROM bikkudtls_divisionsec_dtls
            """
        )
        self._gn_view_query = text(
            """
            SELECT gnc, gnname, regn
            FROM bikkudtls_gn_dtls
            """
        )
        self._history_status_view_query = text(
            """
            SELECT descr, prvdate, chngdate, regno
            FROM bikkudtls_histtystatus_list
            """
        )
        self._id_all_view_query = text(
            """
            SELECT idn, stat, reqstdate, printdate, issuedate, mahanaacharyacd,
                   archadrs, achambl, achamhndate, acharegdt, mahananame, vname,
                   addrs, regn, dofb, mahanadate, gihiname, fathrdetails
            FROM bikkudtls_id_alllist
            """
        )
        self._id_district_view_query = text(
            """
            SELECT dcode, dname, idn
            FROM bikkudtls_iddistrict_list
            """
        )
        self._id_division_sec_view_query = text(
            """
            SELECT dvcode, dvname, idn
            FROM bikkudtls_iddvsec_list
            """
        )
        self._id_gn_view_query = text(
            """
            SELECT gnname, idn
            FROM bikkudtls_idgn_list
            """
        )
        self._nikayanayaka_view_query = text(
            """
            SELECT regn, mahananame, currstat, vname, addrs
            FROM bikkudtls_nikayanayaka_list
            """
        )
        self._parshawa_view_query = text(
            """
            SELECT prn, pname, regn
            FROM bikkudtls_parshawa_list
            """
        )
        self._status_history_composite_query = text(
            """
            SELECT regno, vadescrdtls
            FROM bikkudtls_statushystry_composit
            """
        )
        self._status_history_list_query = text(
            """
            SELECT regno, prvdate, chngdate, descr
            FROM bikkudtls_statushystry_list
            """
        )
        self._status_history_list2_query = text(
            """
            SELECT regno, statchgdescr
            FROM bikkudtls_statushystry_list2
            """
        )
        self._viharadipathi_view_query = text(
            """
            SELECT regn, mahananame
            FROM bikkudtls_viharadipathi_list
            """
        )
        self._current_status_summary_query = text(
            """
            SELECT statcd, descr, statcnt
            FROM bikkusumm_currstatus_list
            """
        )
        self._district_summary_query = text(
            """
            SELECT dcode, dname, totalbikku
            FROM bikkusumm_district_list
            """
        )
        self._gn_summary_query = text(
            """
            SELECT gnc, gnname, bikkucnt
            FROM bikkusumm_gn_list
            """
        )
        self._id_district_summary_query = text(
            """
            SELECT dcode, dname, idcnt
            FROM bikkusumm_iddistrict_list
            """
        )
        self._id_gn_summary_query = text(
            """
            SELECT gnname, idcnt
            FROM bikkusumm_idgn_list
            """
        )

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def create_bhikku(
        self, db: Session, *, payload: BhikkuCreate, actor_id: Optional[str]
    ) -> Bhikku:
        payload_dict = payload.model_dump()
        payload_dict["br_created_by"] = actor_id
        payload_dict["br_updated_by"] = actor_id
        payload_dict = self._strip_strings(payload_dict)
        payload_dict = self._normalize_contact_fields(payload_dict)
        self._validate_contact_formats(payload_dict)

        explicit_regn = payload_dict.get("br_regn")
        if explicit_regn:
            existing = bhikku_repo.get_raw_by_regn(db, explicit_regn)
            if existing and not existing.br_is_deleted:
                raise ValueError(f"br_regn '{explicit_regn}' already exists.")
            if existing and existing.br_is_deleted:
                raise ValueError(
                    f"br_regn '{explicit_regn}' belongs to a deleted record and cannot be reused."
                )

        self._validate_foreign_keys(db, payload_dict, current_regn=None)
        self._validate_unique_contact_fields(
            db,
            br_mobile=payload_dict.get("br_mobile"),
            br_email=payload_dict.get("br_email"),
            br_fathrsmobile=payload_dict.get("br_fathrsmobile"),
            current_regn=None,
        )

        enriched_payload = BhikkuCreate(**payload_dict)
        created = bhikku_repo.create(db, enriched_payload)
        return created

    def list_bhikkus(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        vh_trn: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[list[str]] = None,
        status: Optional[list[str]] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[Bhikku]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return bhikku_repo.get_all(
            db,
            skip=skip,
            limit=limit,
            search_key=search,
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

    def count_bhikkus(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        vh_trn: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[list[str]] = None,
        status: Optional[list[str]] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> int:
        total = bhikku_repo.get_total_count(
            db,
            search_key=search,
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
        return int(total or 0)

    def list_mahanayaka_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_mahanayakalist view."""
        result = db.execute(self._mahanayaka_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_nikaya_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_nikaya_list view."""
        result = db.execute(self._nikaya_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_acharya_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_archarya_dtls view."""
        result = db.execute(self._acharya_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_bhikku_details_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_bikkullist view."""
        result = db.execute(self._details_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_certification_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_certification_data view."""
        result = db.execute(self._certification_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_certification_print_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_certification_printnow view."""
        result = db.execute(self._certification_print_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_current_status_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_currstatus_list view."""
        result = db.execute(self._current_status_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_district_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_districtlist view."""
        result = db.execute(self._district_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_division_sec_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_divisionsec_dtls view."""
        result = db.execute(self._division_sec_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_gn_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_gn_dtls view."""
        result = db.execute(self._gn_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_history_status_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_histtystatus_list view."""
        result = db.execute(self._history_status_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_id_all_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_id_alllist view."""
        result = db.execute(self._id_all_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_id_district_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_iddistrict_list view."""
        result = db.execute(self._id_district_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_id_division_sec_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_iddvsec_list view."""
        result = db.execute(self._id_division_sec_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_id_gn_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_idgn_list view."""
        result = db.execute(self._id_gn_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_nikayanayaka_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_nikayanayaka_list view."""
        result = db.execute(self._nikayanayaka_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_nikaya_hierarchy(self, db: Session) -> list[dict[str, Any]]:
        """
        Return nikaya records enriched with their main bhikku and related parshawayas.
        """
        nikaya_rows = (
            db.query(NikayaData)
            .filter(NikayaData.nk_is_deleted.is_(False))
            .order_by(NikayaData.nk_nkn)
            .all()
        )

        if not nikaya_rows:
            return []

        parshawa_rows = (
            db.query(ParshawaData)
            .filter(ParshawaData.pr_is_deleted.is_(False))
            .all()
        )

        parshawa_by_nikaya: dict[str, list[ParshawaData]] = defaultdict(list)
        for parshawa in parshawa_rows:
            if parshawa.pr_nikayacd:
                parshawa_by_nikaya[parshawa.pr_nikayacd].append(parshawa)

        main_regns = {row.nk_nahimicd for row in nikaya_rows if row.nk_nahimicd}
        parshawa_regns = {row.pr_nayakahimi for row in parshawa_rows if row.pr_nayakahimi}
        wanted_regns = {regn for regn in main_regns.union(parshawa_regns) if regn}

        bhikku_map: dict[str, Bhikku] = {}
        vihara_map: dict[str, ViharaData] = {}
        if wanted_regns:
            bhikku_rows = (
                db.query(Bhikku)
                .filter(
                    Bhikku.br_regn.in_(wanted_regns),
                    Bhikku.br_is_deleted.is_(False),
                )
                .all()
            )
            bhikku_map = {row.br_regn: row for row in bhikku_rows}

            vihara_codes = {
                row.br_livtemple for row in bhikku_rows if row.br_livtemple
            }
            if vihara_codes:
                vihara_rows = (
                    db.query(ViharaData)
                    .filter(
                        ViharaData.vh_trn.in_(vihara_codes),
                        ViharaData.vh_is_deleted.is_(False),
                    )
                    .all()
                )
                vihara_map = {row.vh_trn: row for row in vihara_rows}

        def serialize_bhikku(entity: Optional[Bhikku]) -> Optional[dict[str, Any]]:
            if not entity:
                return None
            vihara = (
                vihara_map.get(entity.br_livtemple)
                if entity.br_livtemple
                else None
            )
            address = (
                (vihara.vh_addrs if vihara and vihara.vh_addrs else None)
                or entity.br_fathrsaddrs
                or self._build_address_string(
                    entity.br_vilage,
                    entity.br_division,
                    entity.br_district,
                    entity.br_province,
                )
            )
            return {
                "regn": entity.br_regn,
                "gihiname": entity.br_gihiname,
                "mahananame": entity.br_mahananame,
                "current_status": entity.br_currstat,
                "parshawaya": entity.br_parshawaya,
                "livtemple": entity.br_livtemple,
                "mahanatemple": entity.br_mahanatemple,
                "address": address,
            }

        hierarchy: list[dict[str, Any]] = []
        for nikaya in nikaya_rows:
            parshawa_items: list[dict[str, Any]] = []
            for parshawa in sorted(
                parshawa_by_nikaya.get(nikaya.nk_nkn, []),
                key=lambda item: ((item.pr_pname or "").lower(), item.pr_prn or ""),
            ):
                parshawa_items.append(
                    {
                        "code": parshawa.pr_prn,
                        "name": parshawa.pr_pname,
                        "remarks": parshawa.pr_rmrks,
                        "start_date": parshawa.pr_startdate,
                        "nayaka_regn": parshawa.pr_nayakahimi,
                        "nayaka": serialize_bhikku(
                            bhikku_map.get(parshawa.pr_nayakahimi)
                        ),
                    }
                )

            hierarchy.append(
                {
                    "nikaya": {
                        "code": nikaya.nk_nkn,
                        "name": nikaya.nk_nname,
                    },
                    "main_bhikku": serialize_bhikku(
                        bhikku_map.get(nikaya.nk_nahimicd)
                    ),
                    "parshawayas": parshawa_items,
                }
            )

        return hierarchy

    def list_parshawa_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_parshawa_list view."""
        result = db.execute(self._parshawa_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_status_history_composite(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_statushystry_composit view."""
        result = db.execute(self._status_history_composite_query).mappings().all()
        return [dict(row) for row in result]

    def list_status_history_list(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_statushystry_list view."""
        result = db.execute(self._status_history_list_query).mappings().all()
        return [dict(row) for row in result]

    def list_status_history_list2(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_statushystry_list2 view."""
        result = db.execute(self._status_history_list2_query).mappings().all()
        return [dict(row) for row in result]

    def list_viharadipathi_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the bikkudtls_viharadipathi_list view."""
        result = db.execute(self._viharadipathi_view_query).mappings().all()
        return [dict(row) for row in result]

    def list_current_status_summary(self, db: Session) -> list[dict[str, Any]]:
        """Return aggregated records from the bikkusumm_currstatus_list view."""
        result = db.execute(self._current_status_summary_query).mappings().all()
        return [dict(row) for row in result]

    def list_district_summary(self, db: Session) -> list[dict[str, Any]]:
        """Return aggregated records from the bikkusumm_district_list view."""
        result = db.execute(self._district_summary_query).mappings().all()
        return [dict(row) for row in result]

    def list_gn_summary(self, db: Session) -> list[dict[str, Any]]:
        """Return aggregated records from the bikkusumm_gn_list view."""
        result = db.execute(self._gn_summary_query).mappings().all()
        return [dict(row) for row in result]

    def list_id_district_summary(self, db: Session) -> list[dict[str, Any]]:
        """Return aggregated records from the bikkusumm_iddistrict_list view."""
        result = db.execute(self._id_district_summary_query).mappings().all()
        return [dict(row) for row in result]

    def list_id_gn_summary(self, db: Session) -> list[dict[str, Any]]:
        """Return aggregated records from the bikkusumm_idgn_list view."""
        result = db.execute(self._id_gn_summary_query).mappings().all()
        return [dict(row) for row in result]

    def get_bhikku(self, db: Session, *, br_regn: str) -> Optional[Bhikku]:
        return bhikku_repo.get_by_regn(db, br_regn)

    def get_bhikku_by_id(self, db: Session, *, br_id: int) -> Optional[Bhikku]:
        return bhikku_repo.get_by_id(db, br_id)

    def update_bhikku(
        self,
        db: Session,
        *,
        br_regn: str,
        payload: BhikkuUpdate,
        actor_id: Optional[str],
    ) -> Bhikku:
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")

        update_data = payload.model_dump(exclude_unset=True)
        update_data = self._strip_strings(update_data)
        update_data = self._normalize_contact_fields(update_data)
        self._validate_contact_formats(update_data)

        if "br_regn" in update_data and update_data["br_regn"]:
            new_regn = update_data["br_regn"]
            if new_regn != br_regn:
                raise ValueError("br_regn cannot be modified once created.")

        update_data["br_updated_by"] = actor_id
        self._validate_foreign_keys(db, update_data, current_regn=br_regn)
        self._validate_unique_contact_fields(
            db,
            br_mobile=update_data.get("br_mobile"),
            br_email=update_data.get("br_email"),
            br_fathrsmobile=update_data.get("br_fathrsmobile"),
            current_regn=br_regn,
        )

        update_payload = BhikkuUpdate(**update_data)
        updated = bhikku_repo.update(db, br_regn=br_regn, bhikku_update=update_payload)
        if not updated:
            raise ValueError("Bhikku record not found.")
        return updated

    def delete_bhikku(
        self,
        db: Session,
        *,
        br_regn: str,
        actor_id: Optional[str],
    ) -> Bhikku:
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")

        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        deleted = bhikku_repo.delete(db, br_regn=br_regn, updated_by=actor_id)
        if not deleted:
            raise ValueError("Bhikku record not found.")
        return deleted

    # --------------------------------------------------------------------- #
    # Helpers
    # --------------------------------------------------------------------- #
    def _validate_unique_contact_fields(
        self,
        db: Session,
        *,
        br_mobile: Optional[str],
        br_email: Optional[str],
        br_fathrsmobile: Optional[str],
        current_regn: Optional[str],
    ) -> None:
        # Duplicate contact details are permitted, so no uniqueness validation is required.
        return

    def _validate_contact_formats(self, payload: Dict[str, Any]) -> None:
        for field in ("br_mobile", "br_fathrsmobile"):
            value = payload.get(field)
            if not self._has_meaningful_value(value):
                continue
            if not isinstance(value, str) or not self.MOBILE_PATTERN.match(value):
                raise ValueError(
                    f"{field} '{value}' is not a valid mobile number. Expected 10 digits starting with 0."
                )

    @staticmethod
    def _normalize_contact_fields(data: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(data)
        if "br_email" in normalized and isinstance(normalized["br_email"], str):
            normalized["br_email"] = normalized["br_email"].lower()
        return normalized

    def _validate_foreign_keys(
        self,
        db: Session,
        payload: Dict[str, Any],
        *,
        current_regn: Optional[str],
    ) -> None:
        """Validate foreign key references for the provided payload."""
        # Direct table validations handled via ORM models for better readability.
        self._validate_user_reference(db, payload.get("br_created_by"), "br_created_by")
        self._validate_user_reference(db, payload.get("br_updated_by"), "br_updated_by")

        self._validate_vihara_reference(
            db, payload.get("br_livtemple"), "br_livtemple"
        )
        self._validate_vihara_reference(
            db, payload.get("br_mahanatemple"), "br_mahanatemple"
        )

        self._validate_bhikku_reference(
            db,
            payload.get("br_mahanaacharyacd"),
            "br_mahanaacharyacd",
            current_regn=current_regn,
        )

        self._validate_bhikku_reference(
            db,
            payload.get("br_viharadhipathi"),
            "br_viharadhipathi",
            current_regn=current_regn,
        )

        self._validate_bhikku_high_reference(
            db, payload.get("br_upasampada_serial_no"), "br_upasampada_serial_no"
        )

        self._validate_vihara_reference(
            db,
            payload.get("br_robing_tutor_residence"),
            "br_robing_tutor_residence",
        )
        self._validate_vihara_reference(
            db,
            payload.get("br_robing_after_residence_temple"),
            "br_robing_after_residence_temple",
        )

        for field, target in self.FK_TABLE_MAP.items():
            value = payload.get(field)
            if not self._has_meaningful_value(value):
                continue
            if not self._reference_exists(db, target, value):
                schema, table_name, column_name = target
                raise ValueError(
                    f"Invalid reference: {field} '{value}' not found in "
                    f"{schema or 'public'}.{table_name}."
                )

    def _validate_user_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(UserAccount.ua_user_id)
            .filter(
                UserAccount.ua_user_id == value,
                UserAccount.ua_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found.")

    def _validate_vihara_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(ViharaData.vh_trn)
            .filter(
                ViharaData.vh_trn == value,
                ViharaData.vh_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found.")

    def _validate_bhikku_reference(
        self,
        db: Session,
        value: Optional[str],
        field_name: str,
        *,
        current_regn: Optional[str],
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        # Allow referencing the current record when updating.
        if current_regn and value == current_regn:
            exists = bhikku_repo.get_raw_by_regn(db, value)
        else:
            exists = bhikku_repo.get_by_regn(db, value)

        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found.")

    def _validate_bhikku_high_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = (
            db.query(BhikkuHighRegist.bhr_regn)
            .filter(
                BhikkuHighRegist.bhr_regn == value,
                BhikkuHighRegist.bhr_is_deleted.is_(False),
            )
            .first()
        )
        if not exists:
            raise ValueError(f"Invalid reference: {field_name} '{value}' not found.")

    def _reference_exists(
        self,
        db: Session,
        target: Tuple[Optional[str], str, str],
        value: Any,
    ) -> bool:
        schema, table_name, column_name = target
        try:
            table = self._get_table(db, schema, table_name)
        except (NoSuchTableError, SQLAlchemyError) as exc:
            raise RuntimeError(
                f"Foreign key metadata for '{table_name}.{column_name}' is not available."
            ) from exc

        column = table.c.get(column_name)
        if column is None:
            raise RuntimeError(
                f"Column '{column_name}' not found on table '{table_name}'."
            )

        stmt = select(column).where(column == value).limit(1)
        result = db.execute(stmt).first()
        return result is not None

    def _get_table(
        self, db: Session, schema: Optional[str], table_name: str
    ) -> Table:
        cache_key = (schema, table_name)
        if cache_key not in self._table_cache:
            metadata = MetaData()
            table = Table(
                table_name,
                metadata,
                schema=schema,
                autoload_with=db.get_bind(),
            )
            self._table_cache[cache_key] = table
        return self._table_cache[cache_key]

    @staticmethod
    def _build_address_string(*parts: Optional[str]) -> Optional[str]:
        meaningful = [
            part.strip()
            for part in parts
            if isinstance(part, str) and part.strip()
        ]
        if not meaningful:
            return None
        return ", ".join(meaningful)

    @staticmethod
    def _strip_strings(data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
            else:
                cleaned[key] = value
        return cleaned

    @staticmethod
    def _has_meaningful_value(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        return True


bhikku_service = BhikkuService()
