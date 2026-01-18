from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, date
from typing import Any, Dict, Optional, Tuple

from fastapi import UploadFile
from sqlalchemy import MetaData, Table, select, text
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError
from sqlalchemy.orm import Session, noload

from app.models.bhikku import Bhikku
from app.models.bhikku_high import BhikkuHighRegist
from app.models.nikaya import NikayaData
from app.models.parshawadata import ParshawaData
from app.models.user import UserAccount
from app.models.vihara import ViharaData
from app.repositories.bhikku_repo import bhikku_repo
from app.schemas.bhikku import BhikkuCreate, BhikkuUpdate
from app.utils.file_storage import file_storage_service


class BhikkuService:
    """Business logic and validation helpers for bhikku registrations."""

    FK_TABLE_MAP: Dict[str, Tuple[Optional[str], str, str]] = {
        "br_gndiv": ("public", "cmm_gndata", "gn_gnc"),
        "br_currstat": ("public", "statusdata", "st_statcd"),
        "br_parshawaya": ("public", "cmm_parshawadata", "pr_prn"),
        "br_cat": ("public", "cmm_cat", "cc_code"),
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
        self._province_view_query = text(
            """
            SELECT cp_code, cp_name
            FROM cmm_province
            WHERE cp_is_deleted = false
            ORDER BY cp_name
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
        self, db: Session, *, payload: BhikkuCreate, actor_id: Optional[str], current_user: Optional[UserAccount] = None
    ) -> Bhikku:
        payload_dict = payload.model_dump()
        payload_dict["br_created_by"] = actor_id
        payload_dict["br_updated_by"] = actor_id
        payload_dict = self._strip_strings(payload_dict)
        payload_dict = self._normalize_contact_fields(payload_dict)
        self._validate_contact_formats(payload_dict)

        # Handle temporary bhikku references - these can't be stored as FK references
        # because br_viharadhipathi and br_mahanaacharyacd have foreign key constraints
        # to bhikku_regist.br_regn. Temporary bhikku records are stored in temporary_bhikku
        # table with numeric tb_id that don't exist in bhikku_regist.
        # 
        # Supported formats:
        # - TEMP-* format (e.g., "TEMP-17" from READ_ALL response)
        # - Pure numeric strings (e.g., "17" - tb_id from temporary_bhikku table)
        # - TB* format (e.g., "TB000001" - alternative temp bhikku identifier)
        # 
        # Store the temp bhikku reference in remarks for later retrieval and set field to NULL
        temp_refs = []
        for field in ["br_viharadhipathi", "br_mahanaacharyacd"]:
            value = payload_dict.get(field)
            if value and isinstance(value, str):
                value = value.strip()
                # Extract temp bhikku ID from various formats
                temp_id = None
                if value.startswith("TEMP-"):
                    # Format: "TEMP-17"
                    temp_id = value[5:]
                elif value.startswith("TB"):
                    # Format: "TB000001" or "TB17" - treat as temp bhikku reference
                    temp_id = value
                elif value.isdigit():
                    # Format: "17" - pure numeric tb_id
                    temp_id = value
                
                if temp_id:
                    temp_refs.append(f"[TEMP_{field.upper()}:{temp_id}]")
                    payload_dict[field] = None
        
        # Handle temporary vihara references - these can't be stored as FK references
        # Clear fields that reference temporary viharas (TEMP-* format from READ_ALL response)
        # All these fields have FK to vihaddata table
        for field in ["br_livtemple", "br_mahanatemple", "br_robing_tutor_residence", "br_robing_after_residence_temple"]:
            value = payload_dict.get(field)
            if value and isinstance(value, str):
                # Extract temp vihara ID from "TEMP-11" format
                if value.startswith("TEMP-"):
                    temp_id = value[5:]  # Remove "TEMP-" prefix
                    temp_refs.append(f"[TEMP_{field.upper()}:{temp_id}]")
                    payload_dict[field] = None
        
        # Append temp references to remarks if any
        if temp_refs:
            existing_remarks = payload_dict.get("br_remarks") or ""
            # Remove any existing temp references from remarks first
            import re
            existing_remarks = re.sub(r'\[TEMP_BR_[A-Z_]+:\d+\]', '', existing_remarks).strip()
            temp_refs_str = " ".join(temp_refs)
            payload_dict["br_remarks"] = f"{existing_remarks} {temp_refs_str}".strip() if existing_remarks else temp_refs_str

        # Auto-populate location from current user (location-based access control)
        if current_user and current_user.ua_location_type == "DISTRICT_BRANCH" and current_user.ua_district_branch_id:
            from app.models.district_branch import DistrictBranch
            district_branch = db.query(DistrictBranch).filter(
                DistrictBranch.db_id == current_user.ua_district_branch_id
            ).first()
            if district_branch and district_branch.db_district_code:
                payload_dict["br_created_by_district"] = district_branch.db_district_code

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
        
        # Validate no duplicate gihiname + date of birth combination
        self._validate_no_duplicate_gihiname_dob(
            db,
            br_gihiname=payload_dict.get("br_gihiname"),
            br_dofb=payload_dict.get("br_dofb"),
            current_regn=None,
        )

        # Create the enriched payload WITHOUT workflow_status (it will be set by the repository/model default to PENDING)
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
        province: Optional[str] = None,
        vh_trn: Optional[str] = None,
        district: Optional[str] = None,
        current_user: Optional[UserAccount] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[list[str]] = None,
        status: Optional[list[str]] = None,
        workflow_status: Optional[list[str]] = None,
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
            workflow_status=workflow_status,
            date_from=date_from,
            date_to=date_to,
            current_user=current_user,
        )

    def count_bhikkus(
        self, 
        db: Session, 
        *, 
        search: Optional[str] = None,
        province: Optional[str] = None,
        vh_trn: Optional[str] = None,
        district: Optional[str] = None,
        current_user: Optional[UserAccount] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        category: Optional[list[str]] = None,
        status: Optional[list[str]] = None,
        workflow_status: Optional[list[str]] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> int:
        total = bhikku_repo.get_total_count(
            db, 
            search_key=search,
            province=province,
            vh_trn=vh_trn,
            district=district,
            current_user=current_user,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            temple=temple,
            child_temple=child_temple,
            nikaya=nikaya,
            parshawaya=parshawaya,
            category=category,
            status=status,
            workflow_status=workflow_status,
            date_from=date_from,
            date_to=date_to
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

    def list_province_view(self, db: Session) -> list[dict[str, Any]]:
        """Return records from the cmm_province table."""
        result = db.execute(self._province_view_query).mappings().all()
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
        Return nikaya records with their parshawayas and nayaka bhikku info from database.
        Uses nikaya -> bhikku (nk_nahimicd) and parshawa -> bhikku (pr_nayakahimi) relationships.
        """
        # Get nikayas with their main bhikku
        nikaya_rows = (
            db.query(NikayaData)
            .filter(NikayaData.nk_is_deleted.is_(False))
            .order_by(NikayaData.nk_nkn)
            .all()
        )

        if not nikaya_rows:
            return []

        # Get parshawayas
        parshawa_rows = (
            db.query(ParshawaData)
            .filter(ParshawaData.pr_is_deleted.is_(False))
            .all()
        )

        # Group parshawayas by nikaya
        parshawa_by_nikaya: dict[str, list[ParshawaData]] = defaultdict(list)
        for parshawa in parshawa_rows:
            if parshawa.pr_nikayacd:
                parshawa_by_nikaya[parshawa.pr_nikayacd].append(parshawa)

        # Collect all bhikku registration numbers we need
        main_regns = {row.nk_nahimicd for row in nikaya_rows if row.nk_nahimicd}
        parshawa_regns = {row.pr_nayakahimi for row in parshawa_rows if row.pr_nayakahimi and row.pr_nayakahimi != 'PENDING'}
        wanted_regns = {regn for regn in main_regns.union(parshawa_regns) if regn}

        # Get bhikku data
        bhikku_map: dict[str, Bhikku] = {}
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

        def serialize_bhikku(entity: Optional[Bhikku]) -> Optional[dict[str, Any]]:
            if not entity:
                return None
            return {
                "regn": entity.br_regn,
                "gihiname": entity.br_gihiname,
                "mahananame": entity.br_mahanayaka_name or entity.br_mahananame,
                "current_status": entity.br_currstat,
                "parshawaya": entity.br_parshawaya,
                "livtemple": entity.br_livtemple,
                "mahanatemple": entity.br_mahanatemple,
                "address": entity.br_fathrsaddrs,
            }

        hierarchy: list[dict[str, Any]] = []
        for nikaya in nikaya_rows:
            parshawa_items: list[dict[str, Any]] = []
            for parshawa in sorted(
                parshawa_by_nikaya.get(nikaya.nk_nkn, []),
                key=lambda item: ((item.pr_pname or "").lower(), item.pr_prn or ""),
            ):
                nayaka_regn = parshawa.pr_nayakahimi if parshawa.pr_nayakahimi and parshawa.pr_nayakahimi != 'PENDING' else None
                parshawa_items.append(
                    {
                        "code": parshawa.pr_prn,
                        "name": parshawa.pr_pname,
                        "remarks": parshawa.pr_rmrks,
                        "start_date": parshawa.pr_startdate,
                        "nayaka_regn": nayaka_regn,
                        "nayaka": serialize_bhikku(
                            bhikku_map.get(nayaka_regn) if nayaka_regn else None
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
                        bhikku_map.get(nikaya.nk_nahimicd) if nikaya.nk_nahimicd else None
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

    def list_bhikkus_by_vihara(self, db: Session, vh_trn: str) -> list[dict[str, Optional[str]]]:
        """Return bhikku regn and name for a given vihara code."""
        if not vh_trn:
            return []

        rows = (
            db.query(Bhikku.br_regn, Bhikku.br_mahananame)
            .filter(
                Bhikku.br_livtemple == vh_trn,
                Bhikku.br_is_deleted.is_(False),
            )
            .order_by(Bhikku.br_mahananame.asc())
            .all()
        )
        return [{"regn": regn, "br_mahananame": name} for regn, name in rows]

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
    
    def enrich_bhikku_dict(self, bhikku: Bhikku, db: Session = None) -> dict:
        """Transform Bhikku model to dictionary with resolved foreign key names as nested objects"""
        
        # Parse temporary bhikku references from remarks
        import re
        temp_viharadhipathi_id = None
        temp_mahanaacharyacd_id = None
        temp_livtemple_id = None
        temp_mahanatemple_id = None
        temp_robing_tutor_residence_id = None
        temp_robing_after_residence_temple_id = None
        remarks_display = bhikku.br_remarks or ""
        
        if remarks_display:
            # Extract temp viharadhipathi reference
            viharadhipathi_match = re.search(r'\[TEMP_BR_VIHARADHIPATHI:(\d+)\]', remarks_display)
            if viharadhipathi_match:
                temp_viharadhipathi_id = int(viharadhipathi_match.group(1))
            
            # Extract temp mahanaacharyacd reference
            mahanaacharyacd_match = re.search(r'\[TEMP_BR_MAHANAACHARYACD:(\d+)\]', remarks_display)
            if mahanaacharyacd_match:
                temp_mahanaacharyacd_id = int(mahanaacharyacd_match.group(1))
            
            # Extract temp livtemple reference (temporary vihara)
            livtemple_match = re.search(r'\[TEMP_BR_LIVTEMPLE:(\d+)\]', remarks_display)
            if livtemple_match:
                temp_livtemple_id = int(livtemple_match.group(1))
            
            # Extract temp mahanatemple reference (temporary vihara)
            mahanatemple_match = re.search(r'\[TEMP_BR_MAHANATEMPLE:(\d+)\]', remarks_display)
            if mahanatemple_match:
                temp_mahanatemple_id = int(mahanatemple_match.group(1))
            
            # Extract temp robing_tutor_residence reference (temporary vihara)
            robing_tutor_match = re.search(r'\[TEMP_BR_ROBING_TUTOR_RESIDENCE:(\d+)\]', remarks_display)
            if robing_tutor_match:
                temp_robing_tutor_residence_id = int(robing_tutor_match.group(1))
            
            # Extract temp robing_after_residence_temple reference (temporary vihara)
            robing_after_match = re.search(r'\[TEMP_BR_ROBING_AFTER_RESIDENCE_TEMPLE:(\d+)\]', remarks_display)
            if robing_after_match:
                temp_robing_after_residence_temple_id = int(robing_after_match.group(1))
            
            # Remove temp references from display remarks
            remarks_display = re.sub(r'\[TEMP_BR_[A-Z_]+:\d+\]', '', remarks_display).strip()
        
        # Fetch temporary bhikku details if needed
        temp_viharadhipathi_data = None
        temp_mahanaacharyacd_data = None
        
        if db and (temp_viharadhipathi_id or temp_mahanaacharyacd_id):
            from app.models.temporary_bhikku import TemporaryBhikku
            
            if temp_viharadhipathi_id:
                temp_bhikku = db.query(TemporaryBhikku).filter(
                    TemporaryBhikku.tb_id == temp_viharadhipathi_id
                ).first()
                if temp_bhikku:
                    temp_viharadhipathi_data = {
                        "br_regn": f"TEMP-{temp_bhikku.tb_id}",
                        "br_mahananame": temp_bhikku.tb_name or "",
                        "br_upasampadaname": ""
                    }
            
            if temp_mahanaacharyacd_id:
                temp_bhikku = db.query(TemporaryBhikku).filter(
                    TemporaryBhikku.tb_id == temp_mahanaacharyacd_id
                ).first()
                if temp_bhikku:
                    temp_mahanaacharyacd_data = {
                        "br_regn": f"TEMP-{temp_bhikku.tb_id}",
                        "br_mahananame": temp_bhikku.tb_name or "",
                        "br_upasampadaname": ""
                    }
        
        # Fetch temporary vihara details if needed
        temp_livtemple_data = None
        temp_mahanatemple_data = None
        temp_robing_tutor_residence_data = None
        temp_robing_after_residence_temple_data = None
        
        if db and (temp_livtemple_id or temp_mahanatemple_id or temp_robing_tutor_residence_id or temp_robing_after_residence_temple_id):
            from app.models.temporary_vihara import TemporaryVihara
            
            if temp_livtemple_id:
                temp_vihara = db.query(TemporaryVihara).filter(
                    TemporaryVihara.tv_id == temp_livtemple_id
                ).first()
                if temp_vihara:
                    temp_livtemple_data = {
                        "vh_trn": f"TEMP-{temp_vihara.tv_id}",
                        "vh_vname": temp_vihara.tv_name or ""
                    }
            
            if temp_mahanatemple_id:
                temp_vihara = db.query(TemporaryVihara).filter(
                    TemporaryVihara.tv_id == temp_mahanatemple_id
                ).first()
                if temp_vihara:
                    temp_mahanatemple_data = {
                        "vh_trn": f"TEMP-{temp_vihara.tv_id}",
                        "vh_vname": temp_vihara.tv_name or ""
                    }
            
            if temp_robing_tutor_residence_id:
                temp_vihara = db.query(TemporaryVihara).filter(
                    TemporaryVihara.tv_id == temp_robing_tutor_residence_id
                ).first()
                if temp_vihara:
                    temp_robing_tutor_residence_data = {
                        "vh_trn": f"TEMP-{temp_vihara.tv_id}",
                        "vh_vname": temp_vihara.tv_name or ""
                    }
            
            if temp_robing_after_residence_temple_id:
                temp_vihara = db.query(TemporaryVihara).filter(
                    TemporaryVihara.tv_id == temp_robing_after_residence_temple_id
                ).first()
                if temp_vihara:
                    temp_robing_after_residence_temple_data = {
                        "vh_trn": f"TEMP-{temp_vihara.tv_id}",
                        "vh_vname": temp_vihara.tv_name or ""
                    }
        
        # Handle multi_mahanaacharyacd - split and resolve names
        multi_mahanaacharyacd_value = bhikku.br_multi_mahanaacharyacd
        if bhikku.br_multi_mahanaacharyacd and db:
            # Assuming comma-separated registration numbers
            regns = [r.strip() for r in bhikku.br_multi_mahanaacharyacd.split(',') if r.strip()]
            if regns:
                # Query all at once for efficiency
                bhikku_names = db.query(Bhikku.br_regn, Bhikku.br_mahananame).filter(
                    Bhikku.br_regn.in_(regns),
                    Bhikku.br_is_deleted.is_(False)
                ).all()
                name_map = {b.br_regn: b.br_mahananame for b in bhikku_names}
                resolved_names = [name_map.get(regn) for regn in regns if name_map.get(regn)]
                if resolved_names:
                    multi_mahanaacharyacd_value = ', '.join(resolved_names)
        
        bhikku_dict = {
            "br_id": bhikku.br_id,
            "br_regn": bhikku.br_regn,
            "br_reqstdate": bhikku.br_reqstdate,
            "br_birthpls": bhikku.br_birthpls,
            # Replace codes with nested objects containing code and name
            "br_province": {
                "cp_code": bhikku.province_rel.cp_code,
                "cp_name": bhikku.province_rel.cp_name
            } if bhikku.province_rel else bhikku.br_province,
            "br_district": {
                "dd_dcode": bhikku.district_rel.dd_dcode,
                "dd_dname": bhikku.district_rel.dd_dname
            } if bhikku.district_rel else bhikku.br_district,
            "br_korale": bhikku.br_korale,
            "br_pattu": bhikku.br_pattu,
            "br_division": {
                "dv_dvcode": bhikku.division_rel.dv_dvcode,
                "dv_dvname": bhikku.division_rel.dv_dvname
            } if bhikku.division_rel else bhikku.br_division,
            "br_vilage": bhikku.br_vilage,
            "br_gndiv": {
                "gn_gnc": bhikku.gndiv_rel.gn_gnc,
                "gn_gnname": bhikku.gndiv_rel.gn_gnname
            } if bhikku.gndiv_rel else bhikku.br_gndiv,
            "br_gihiname": bhikku.br_gihiname,
            "br_dofb": bhikku.br_dofb,
            "br_fathrname": bhikku.br_fathrname,
            "br_remarks": remarks_display or None,  # Use cleaned remarks without temp references
            "br_currstat": {
                "st_statcd": bhikku.status_rel.st_statcd,
                "st_descr": bhikku.status_rel.st_descr
            } if bhikku.status_rel else bhikku.br_currstat,
            "br_effctdate": bhikku.br_effctdate,
            "br_parshawaya": {
                "code": bhikku.parshawaya_rel.pr_prn,
                "name": bhikku.parshawaya_rel.pr_pname
            } if bhikku.parshawaya_rel else bhikku.br_parshawaya,
            "br_livtemple": temp_livtemple_data if temp_livtemple_data else ({
                "vh_trn": bhikku.livtemple_rel.vh_trn,
                "vh_vname": bhikku.livtemple_rel.vh_vname
            } if bhikku.livtemple_rel else bhikku.br_livtemple),
            "br_mahanatemple": temp_mahanatemple_data if temp_mahanatemple_data else ({
                "vh_trn": bhikku.mahanatemple_rel.vh_trn,
                "vh_vname": bhikku.mahanatemple_rel.vh_vname
            } if bhikku.mahanatemple_rel else bhikku.br_mahanatemple),
            "br_mahanaacharyacd": temp_mahanaacharyacd_data if temp_mahanaacharyacd_data else ({
                "br_regn": bhikku.mahanaacharyacd_rel.br_regn,
                "br_mahananame": bhikku.mahanaacharyacd_rel.br_mahananame or "",
                "br_upasampadaname": ""
            } if bhikku.mahanaacharyacd_rel else bhikku.br_mahanaacharyacd),
            "br_multi_mahanaacharyacd": multi_mahanaacharyacd_value,
            "br_mahananame": bhikku.br_mahananame,
            "br_mahanadate": bhikku.br_mahanadate,
            "br_cat": {
                "cc_code": bhikku.category_rel.cc_code,
                "cc_catogry": bhikku.category_rel.cc_catogry
            } if bhikku.category_rel else bhikku.br_cat,
            "br_viharadhipathi": temp_viharadhipathi_data if temp_viharadhipathi_data else ({
                "br_regn": bhikku.viharadhipathi_rel.br_regn,
                "br_mahananame": bhikku.viharadhipathi_rel.br_mahananame or "",
                "br_upasampadaname": ""
            } if bhikku.viharadhipathi_rel else bhikku.br_viharadhipathi),
            "br_nikaya": {
                "code": bhikku.nikaya_rel.nk_nkn,
                "name": bhikku.nikaya_rel.nk_nname
            } if bhikku.nikaya_rel else bhikku.br_nikaya,
            "br_mahanayaka_name": bhikku.mahanayaka_rel.br_mahananame if bhikku.mahanayaka_rel else bhikku.br_mahanayaka_name,
            "br_mahanayaka_address": bhikku.br_mahanayaka_address,
            "br_residence_at_declaration": bhikku.br_residence_at_declaration,
            "br_declaration_date": bhikku.br_declaration_date,
            "br_robing_tutor_residence": temp_robing_tutor_residence_data if temp_robing_tutor_residence_data else ({
                "vh_trn": bhikku.robing_tutor_residence_rel.vh_trn,
                "vh_vname": bhikku.robing_tutor_residence_rel.vh_vname
            } if bhikku.robing_tutor_residence_rel else bhikku.br_robing_tutor_residence),
            "br_robing_after_residence_temple": temp_robing_after_residence_temple_data if temp_robing_after_residence_temple_data else ({
                "vh_trn": bhikku.robing_after_residence_temple_rel.vh_trn,
                "vh_vname": bhikku.robing_after_residence_temple_rel.vh_vname
            } if bhikku.robing_after_residence_temple_rel else bhikku.br_robing_after_residence_temple),
            "br_mobile": bhikku.br_mobile,
            "br_email": bhikku.br_email,
            "br_fathrsaddrs": bhikku.br_fathrsaddrs,
            "br_fathrsmobile": bhikku.br_fathrsmobile,
            "br_upasampada_serial_no": bhikku.br_upasampada_serial_no,
            "br_form_id": bhikku.br_form_id,
            "br_workflow_status": bhikku.br_workflow_status,
            "br_approval_status": bhikku.br_approval_status,
            "br_approved_by": bhikku.br_approved_by,
            "br_approved_at": bhikku.br_approved_at,
            "br_rejected_by": bhikku.br_rejected_by,
            "br_rejected_at": bhikku.br_rejected_at,
            "br_rejection_reason": bhikku.br_rejection_reason,
            "br_printed_at": bhikku.br_printed_at,
            "br_printed_by": bhikku.br_printed_by,
            "br_scanned_at": bhikku.br_scanned_at,
            "br_scanned_by": bhikku.br_scanned_by,
            "br_reprint_status": bhikku.br_reprint_status,
            "br_reprint_requested_by": bhikku.br_reprint_requested_by,
            "br_reprint_requested_at": bhikku.br_reprint_requested_at,
            "br_reprint_request_reason": bhikku.br_reprint_request_reason,
            "br_reprint_approved_by": bhikku.br_reprint_approved_by,
            "br_reprint_approved_at": bhikku.br_reprint_approved_at,
            "br_reprint_rejected_by": bhikku.br_reprint_rejected_by,
            "br_reprint_rejected_at": bhikku.br_reprint_rejected_at,
            "br_reprint_rejection_reason": bhikku.br_reprint_rejection_reason,
            "br_reprint_completed_by": bhikku.br_reprint_completed_by,
            "br_reprint_completed_at": bhikku.br_reprint_completed_at,
            "br_scanned_document_path": bhikku.br_scanned_document_path,
            "br_is_deleted": bhikku.br_is_deleted,
            "br_version_number": bhikku.br_version_number,
            "br_created_by": bhikku.br_created_by,
            "br_updated_by": bhikku.br_updated_by,
            "br_created_by_district": bhikku.br_created_by_district,  # Location-based access control
        }
        
        return bhikku_dict

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

        # Handle temporary bhikku references - these can't be stored as FK references
        # because br_viharadhipathi and br_mahanaacharyacd have foreign key constraints
        # to bhikku_regist.br_regn. Temporary bhikku records are stored in temporary_bhikku
        # table with numeric tb_id that don't exist in bhikku_regist.
        # 
        # Supported formats:
        # - TEMP-* format (e.g., "TEMP-17" from READ_ALL response)
        # - Pure numeric strings (e.g., "17" - tb_id from temporary_bhikku table)
        # - TB* format (e.g., "TB000001" - alternative temp bhikku identifier)
        # 
        # Store the temp bhikku reference in remarks for later retrieval and set field to NULL
        temp_refs = []
        for field in ["br_viharadhipathi", "br_mahanaacharyacd"]:
            # Only process fields that were explicitly included in the update
            if field not in update_data:
                continue
            value = update_data.get(field)
            if value and isinstance(value, str):
                value = value.strip()
                # Extract temp bhikku ID from various formats
                temp_id = None
                if value.startswith("TEMP-"):
                    # Format: "TEMP-17"
                    temp_id = value[5:]
                elif value.startswith("TB"):
                    # Format: "TB000001" or "TB17" - treat as temp bhikku reference
                    temp_id = value
                elif value.isdigit():
                    # Format: "17" - pure numeric tb_id
                    temp_id = value
                
                if temp_id:
                    temp_refs.append(f"[TEMP_{field.upper()}:{temp_id}]")
                    update_data[field] = None
        
        # Handle temporary vihara references - these can't be stored as FK references
        # Clear fields that reference temporary viharas (TEMP-* format from READ_ALL response)
        # All these fields have FK to vihaddata table
        for field in ["br_livtemple", "br_mahanatemple", "br_robing_tutor_residence", "br_robing_after_residence_temple"]:
            # Only process fields that were explicitly included in the update
            if field not in update_data:
                continue
            value = update_data.get(field)
            if value and isinstance(value, str):
                # Extract temp vihara ID from "TEMP-11" format
                if value.startswith("TEMP-"):
                    temp_id = value[5:]  # Remove "TEMP-" prefix
                    temp_refs.append(f"[TEMP_{field.upper()}:{temp_id}]")
                    update_data[field] = None
        
        # Append temp references to remarks if any
        if temp_refs:
            existing_remarks = update_data.get("br_remarks") or entity.br_remarks or ""
            # Remove any existing temp references from remarks first
            import re
            existing_remarks = re.sub(r'\[TEMP_BR_[A-Z_]+:\d+\]', '', existing_remarks).strip()
            temp_refs_str = " ".join(temp_refs)
            update_data["br_remarks"] = f"{existing_remarks} {temp_refs_str}".strip() if existing_remarks else temp_refs_str

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

        # Check if this is a data edit (not just workflow fields)
        # Data fields exclude workflow and audit fields
        workflow_fields = {
            "br_workflow_status", "br_approval_status", "br_approved_by", "br_approved_at",
            "br_rejected_by", "br_rejected_at", "br_rejection_reason",
            "br_printed_by", "br_printed_at", "br_scanned_by", "br_scanned_at",
            "br_reprint_status", "br_reprint_requested_by", "br_reprint_requested_at",
            "br_reprint_request_reason", "br_reprint_amount", "br_reprint_remarks",
            "br_reprint_approved_by", "br_reprint_approved_at", "br_reprint_rejected_by",
            "br_reprint_rejected_at", "br_reprint_rejection_reason",
            "br_reprint_completed_by", "br_reprint_completed_at",
            "br_created_by", "br_updated_by", "br_created_at", "br_updated_at",
            "br_version", "br_version_number", "br_is_deleted"
        }
        
        # Check if any non-workflow fields are being updated
        data_fields_updated = any(key not in workflow_fields for key in update_data.keys())
        
        if data_fields_updated:
            # Reset workflow status to PENDING when actual data is edited
            # This ensures the record goes through the complete workflow again:
            # PENDING -> PRINTED -> PEND-APPROVAL -> APPROVED/REJECTED -> COMPLETED
            update_data["br_workflow_status"] = "PENDING"
        
        # Increment version number for the edit (done in repository)
        # entity.br_version_number will be incremented by repository

        update_payload = BhikkuUpdate(**update_data)
        updated = bhikku_repo.update(db, br_regn=br_regn, bhikku_update=update_payload)
        if not updated:
            raise ValueError("Bhikku record not found.")
        
        # After successful update, clear workflow-related fields if data was edited
        # This is done after the repository update to ensure workflow is properly reset
        if data_fields_updated:
            updated.br_approval_status = None
            updated.br_approved_by = None
            updated.br_approved_at = None
            updated.br_rejected_by = None
            updated.br_rejected_at = None
            updated.br_rejection_reason = None
            updated.br_printed_by = None
            updated.br_printed_at = None
            updated.br_scanned_by = None
            updated.br_scanned_at = None
            db.commit()
            db.refresh(updated)
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
    # Workflow Methods
    # --------------------------------------------------------------------- #
    def approve_bhikku(
        self,
        db: Session,
        *,
        br_regn: str,
        actor_id: Optional[str],
    ) -> Bhikku:
        """Approve a bhikku registration - transitions workflow from PEND-APPROVAL to APPROVED and then to COMPLETED status"""
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")
        
        if entity.br_workflow_status != "PEND-APPROVAL":
            raise ValueError(f"Cannot approve bhikku with workflow status: {entity.br_workflow_status}. Must be PEND-APPROVAL.")
        
        # Update workflow fields - goes to APPROVED then COMPLETED
        entity.br_workflow_status = "COMPLETED"
        entity.br_approval_status = "APPROVED"
        entity.br_approved_by = actor_id
        entity.br_approved_at = datetime.utcnow()
        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        entity.br_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def reject_bhikku(
        self,
        db: Session,
        *,
        br_regn: str,
        actor_id: Optional[str],
        rejection_reason: Optional[str] = None,
    ) -> Bhikku:
        """Reject a bhikku registration - transitions workflow from PEND-APPROVAL to REJECTED status"""
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")
        
        if entity.br_workflow_status != "PEND-APPROVAL":
            raise ValueError(f"Cannot reject bhikku with workflow status: {entity.br_workflow_status}. Must be PEND-APPROVAL.")
        
        # Update workflow fields
        entity.br_workflow_status = "REJECTED"
        entity.br_approval_status = "REJECTED"
        entity.br_rejected_by = actor_id
        entity.br_rejected_at = datetime.utcnow()
        entity.br_rejection_reason = rejection_reason
        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        entity.br_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_printed(
        self,
        db: Session,
        *,
        br_regn: str,
        actor_id: Optional[str],
    ) -> Bhikku:
        """Mark bhikku certificate as printed - transitions workflow from PENDING to PRINTED status"""
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")
        
        if entity.br_workflow_status != "PENDING":
            raise ValueError(f"Cannot mark as printed bhikku with workflow status: {entity.br_workflow_status}. Must be PENDING.")
        
        # Update workflow fields
        entity.br_workflow_status = "PRINTED"
        entity.br_printed_by = actor_id
        entity.br_printed_at = datetime.utcnow()
        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        entity.br_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_scanned(
        self,
        db: Session,
        *,
        br_regn: str,
        actor_id: Optional[str],
    ) -> Bhikku:
        """Mark bhikku certificate as scanned - transitions workflow from PRINTED to PEND-APPROVAL status"""
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")
        
        if entity.br_workflow_status != "PRINTED":
            raise ValueError(f"Cannot mark as scanned bhikku with workflow status: {entity.br_workflow_status}. Must be PRINTED.")
        
        # Update workflow fields
        entity.br_workflow_status = "PEND-APPROVAL"
        entity.br_scanned_by = actor_id
        entity.br_scanned_at = datetime.utcnow()
        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        entity.br_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_printing(
        self,
        db: Session,
        *,
        br_regn: str,
        actor_id: Optional[str],
    ) -> Bhikku:
        """Mark bhikku certificate as in printing process - transitions workflow from PENDING to PRINTING status"""
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")
        
        if entity.br_workflow_status != "PENDING":
            raise ValueError(f"Cannot mark as printing bhikku with workflow status: {entity.br_workflow_status}. Must be PENDING.")
        
        # Update workflow fields
        entity.br_workflow_status = "PRINTING"
        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        entity.br_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def reset_to_pending(
        self,
        db: Session,
        *,
        br_regn: str,
        actor_id: Optional[str],
    ) -> Bhikku:
        """Reset bhikku workflow status to PENDING - for corrections or resubmissions"""
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")
        
        # Clear workflow fields
        entity.br_workflow_status = "PENDING"
        entity.br_approval_status = None
        entity.br_approved_by = None
        entity.br_approved_at = None
        entity.br_rejected_by = None
        entity.br_rejected_at = None
        entity.br_rejection_reason = None
        entity.br_printed_by = None
        entity.br_printed_at = None
        entity.br_scanned_by = None
        entity.br_scanned_at = None
        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        entity.br_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    # --------------------------------------------------------------------- #
    # Reprint Workflow Methods
    # --------------------------------------------------------------------- #
    def request_reprint(
        self,
        db: Session,
        *,
        br_regn: str,
        actor_id: Optional[str],
        reprint_reason: str,
        reprint_amount: Optional[float] = None,
        reprint_remarks: Optional[str] = None,
    ) -> Bhikku:
        """Request a reprint for a bhikku certificate - initiates reprint workflow"""
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")
        
        # Can only request reprint for completed records
        if entity.br_workflow_status not in ["COMPLETED", "PRINTED"]:
            raise ValueError(f"Cannot request reprint for bhikku with workflow status: {entity.br_workflow_status}. Must be COMPLETED or PRINTED.")
        
        # Check if there's already a pending reprint request
        if entity.br_reprint_status == "REPRINT_PENDING":
            raise ValueError("There is already a pending reprint request for this bhikku.")
        
        # Set reprint workflow fields
        entity.br_reprint_status = "REPRINT_PENDING"
        entity.br_reprint_requested_by = actor_id
        entity.br_reprint_requested_at = datetime.utcnow()
        entity.br_reprint_request_reason = reprint_reason
        entity.br_reprint_amount = reprint_amount
        entity.br_reprint_remarks = reprint_remarks
        # Clear previous reprint approval/rejection data
        entity.br_reprint_approved_by = None
        entity.br_reprint_approved_at = None
        entity.br_reprint_rejected_by = None
        entity.br_reprint_rejected_at = None
        entity.br_reprint_rejection_reason = None
        entity.br_reprint_completed_by = None
        entity.br_reprint_completed_at = None
        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        entity.br_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def accept_reprint(
        self,
        db: Session,
        *,
        br_regn: str,
        actor_id: Optional[str],
    ) -> Bhikku:
        """Accept a reprint request - transitions to REPRINT_ACCEPTED status"""
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")
        
        if entity.br_reprint_status != "REPRINT_PENDING":
            raise ValueError(f"Cannot accept reprint with status: {entity.br_reprint_status}. Must be REPRINT_PENDING.")
        
        # Update reprint workflow fields
        entity.br_reprint_status = "REPRINT_ACCEPTED"
        entity.br_reprint_approved_by = actor_id
        entity.br_reprint_approved_at = datetime.utcnow()
        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        entity.br_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def reject_reprint(
        self,
        db: Session,
        *,
        br_regn: str,
        actor_id: Optional[str],
        rejection_reason: Optional[str] = None,
    ) -> Bhikku:
        """Reject a reprint request - transitions to REPRINT_REJECTED status"""
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")
        
        if entity.br_reprint_status != "REPRINT_PENDING":
            raise ValueError(f"Cannot reject reprint with status: {entity.br_reprint_status}. Must be REPRINT_PENDING.")
        
        # Update reprint workflow fields
        entity.br_reprint_status = "REPRINT_REJECTED"
        entity.br_reprint_rejected_by = actor_id
        entity.br_reprint_rejected_at = datetime.utcnow()
        entity.br_reprint_rejection_reason = rejection_reason
        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        entity.br_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def complete_reprint(
        self,
        db: Session,
        *,
        br_regn: str,
        actor_id: Optional[str],
    ) -> Bhikku:
        """Complete a reprint - transitions to REPRINT_COMPLETED status"""
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError("Bhikku record not found.")
        
        if entity.br_reprint_status != "REPRINT_ACCEPTED":
            raise ValueError(f"Cannot complete reprint with status: {entity.br_reprint_status}. Must be REPRINT_ACCEPTED.")
        
        # Update reprint workflow fields
        entity.br_reprint_status = "REPRINT_COMPLETED"
        entity.br_reprint_completed_by = actor_id
        entity.br_reprint_completed_at = datetime.utcnow()
        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        entity.br_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    # --------------------------------------------------------------------- #
    # Helpers
    # --------------------------------------------------------------------- #
    def _validate_no_duplicate_gihiname_dob(
        self,
        db: Session,
        *,
        br_gihiname: Optional[str],
        br_dofb,
        current_regn: Optional[str],
    ) -> None:
        """
        Check for duplicate records with same gihiname AND date of birth combination.
        Only validates if both gihiname and date of birth are provided.
        """
        if not self._has_meaningful_value(br_gihiname) or not br_dofb:
            return
        
        # Convert br_dofb to date object if it's a string
        from datetime import date as date_type
        if isinstance(br_dofb, str):
            try:
                br_dofb = date_type.fromisoformat(br_dofb)
            except ValueError:
                return  # Invalid date format, skip validation
        
        # Check in bhikku_regist table
        existing = db.query(Bhikku).filter(
            Bhikku.br_gihiname == br_gihiname,
            Bhikku.br_dofb == br_dofb,
            Bhikku.br_is_deleted.is_(False),
        ).first()
        
        if existing and existing.br_regn != current_regn:
            raise ValueError(
                f"A record with the same gihiname '{br_gihiname}' and date of birth '{br_dofb}' already exists (Regn: {existing.br_regn})."
            )
        
        # Also check in direct_bhikku_high table
        from app.models.direct_bhikku_high import DirectBhikkuHigh
        existing_dbh = db.query(DirectBhikkuHigh).filter(
            DirectBhikkuHigh.dbh_gihiname == br_gihiname,
            DirectBhikkuHigh.dbh_dofb == br_dofb,
            DirectBhikkuHigh.dbh_is_deleted.is_(False),
        ).first()
        
        if existing_dbh:
            raise ValueError(
                f"A record with the same gihiname '{br_gihiname}' and date of birth '{br_dofb}' already exists (Direct High Bhikku Regn: {existing_dbh.dbh_regn})."
            )

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
        
        self._validate_vihara_reference(
            db, payload.get("br_robing_tutor_residence"), "br_robing_tutor_residence"
        )
        
        self._validate_vihara_reference(
            db, payload.get("br_robing_after_residence_temple"), "br_robing_after_residence_temple"
        )

        self._validate_bhikku_reference(
            db,
            payload.get("br_viharadhipathi"),
            "br_viharadhipathi",
            current_regn=current_regn,
        )

        self._validate_bhikku_reference(
            db,
            payload.get("br_mahanaacharyacd"),
            "br_mahanaacharyacd",
            current_regn=current_regn,
        )
        
        self._validate_bhikku_reference(
            db,
            payload.get("br_mahanayaka_name"),
            "br_mahanayaka_name",
            current_regn=current_regn,
        )

        self._validate_bhikku_high_reference(
            db, payload.get("br_upasampada_serial_no"), "br_upasampada_serial_no"
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
        """
        Strip whitespace from string values and convert empty strings to None.
        This is crucial for foreign key fields that should be NULL when empty.
        """
        cleaned: Dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, str):
                stripped = value.strip()
                # Convert empty strings to None to avoid FK violations
                cleaned[key] = None if stripped == "" else stripped
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

    # --------------------------------------------------------------------- #
    # File Upload Methods
    # --------------------------------------------------------------------- #
    async def upload_scanned_document(
        self,
        db: Session,
        *,
        br_regn: str,
        file: UploadFile,
        actor_id: Optional[str],
    ) -> Bhikku:
        """
        Upload a scanned document for a Bhikku record.
        
        When uploading a new document, the old file is renamed with a version suffix (v1, v2, etc.)
        instead of being deleted, preserving the file history.
        
        Args:
            db: Database session
            br_regn: Bhikku registration number
            file: Uploaded file (PDF, JPG, PNG - max 5MB)
            actor_id: User ID performing the upload
            
        Returns:
            Updated Bhikku instance with file path stored
            
        Raises:
            ValueError: If bhikku not found or file upload fails
        """
        import os
        from pathlib import Path
        
        # Get the bhikku record
        entity = bhikku_repo.get_by_regn(db, br_regn)
        if not entity:
            raise ValueError(f"Bhikku with registration number '{br_regn}' not found.")
        
        # Archive old file with version suffix instead of deleting it
        if entity.br_scanned_document_path:
            old_file_path = entity.br_scanned_document_path
            
            # Remove leading /storage/ if present for path parsing
            clean_path = old_file_path
            if clean_path.startswith("/storage/"):
                clean_path = clean_path[9:]  # Remove "/storage/"
            
            # Parse the old file path to add version suffix
            path_obj = Path(clean_path)
            file_dir = path_obj.parent
            file_name = path_obj.name  # full filename with extension
            file_stem = path_obj.stem  # filename without extension
            file_ext = path_obj.suffix  # extension with dot
            
            # Determine the next version number by scanning the directory for ALL versioned files
            # Find the highest version number that exists
            storage_dir = Path("app/storage") / file_dir
            max_version = 0
            
            if storage_dir.exists():
                for existing_file in storage_dir.glob("*_v*" + file_ext):
                    # Extract version number from filename like "filename_v2.png"
                    version_match = existing_file.stem.rsplit("_v", 1)
                    if len(version_match) == 2 and version_match[1].isdigit():
                        version_num = int(version_match[1])
                        max_version = max(max_version, version_num)
            
            # Use next version number
            next_version = max_version + 1
            versioned_name = f"{file_stem}_v{next_version}{file_ext}"
            versioned_relative_path = str(file_dir / versioned_name)
            
            # Rename the old file to versioned name
            try:
                file_storage_service.rename_file(
                    old_file_path, 
                    versioned_relative_path
                )
            except Exception as e:
                # If renaming fails, log it but continue with upload
                print(f"Warning: Could not rename old file {old_file_path}: {e}")
        
        # Save new file using the file storage service
        # File will be stored at: app/storage/bhikku_regist/<year>/<month>/<day>/<br_regn>/scanned_document_*.*
        relative_path, _ = await file_storage_service.save_file(
            file,
            br_regn,
            "scanned_document",
            subdirectory="bhikku_regist"
        )
        
        # Update the bhikku record with the file path
        entity.br_scanned_document_path = relative_path
        entity.br_updated_by = actor_id
        entity.br_updated_at = datetime.utcnow()
        # Increment version number when new document is uploaded
        entity.br_version_number = (entity.br_version_number or 0) + 1
        
        # Auto-transition workflow status to PEND-APPROVAL when document is uploaded
        # Only transition if currently in PRINTED status
        if entity.br_workflow_status == "PRINTED":
            entity.br_workflow_status = "PEND-APPROVAL"
            entity.br_scanned_by = actor_id
            entity.br_scanned_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        
        return entity

    def get_qr_search_details(
        self, db: Session, record_id: str, record_type: Optional[str] = None
    ) -> Optional[list]:
        """
        Get limited details for QR search verification.
        Automatically detects record type if not provided.
        
        Args:
            db: Database session
            record_id: Registration number (br_regn, sil_regn, or bhr_regn)
            record_type: Optional record type ("bhikku", "silmatha", or "bhikku_high")
            
        Returns:
            List with limited details or None if not found
        """
        from app.models.silmatha_regist import SilmathaRegist
        
        # If record type is specified, search only that type
        if record_type == "bhikku":
            entity = db.query(Bhikku).filter(Bhikku.br_regn == record_id).first()
            if entity:
                return self._format_bhikku_qr_response(db, entity)
                
        elif record_type == "silmatha":
            entity = db.query(SilmathaRegist).filter(SilmathaRegist.sil_regn == record_id).first()
            if entity:
                return self._format_silmatha_qr_response(db, entity)
                
        elif record_type == "bhikku_high":
            entity = db.query(BhikkuHighRegist).options(noload('*')).filter(BhikkuHighRegist.bhr_regn == record_id).first()
            if entity:
                return self._format_bhikku_high_qr_response(db, entity)
        
        else:
            # Auto-detect: Try all types
            # Try Bhikku first
            entity = db.query(Bhikku).filter(Bhikku.br_regn == record_id).first()
            if entity:
                return self._format_bhikku_qr_response(db, entity)
            
            # Try Silmatha
            entity = db.query(SilmathaRegist).filter(SilmathaRegist.sil_regn == record_id).first()
            if entity:
                return self._format_silmatha_qr_response(db, entity)
            
            # Try Bhikku High
            entity = db.query(BhikkuHighRegist).options(noload('*')).filter(BhikkuHighRegist.bhr_regn == record_id).first()
            if entity:
                return self._format_bhikku_high_qr_response(db, entity)
        
        return None

    def _format_bhikku_qr_response(self, db: Session, entity: Bhikku) -> list:
        """Format Bhikku record for QR search response"""
        # Get temple details if available
        live_location = None
        if entity.br_livtemple:
            temple = db.query(ViharaData).filter(
                ViharaData.vh_trn == entity.br_livtemple
            ).first()
            if temple:
                live_location = f"{temple.vh_vname}, {temple.vh_addrs}" if temple.vh_addrs else temple.vh_vname
        
        # Get status description
        from app.models.status import StatusData
        from app.models.bhikku_category import BhikkuCategory
        
        status_text = entity.br_currstat
        if entity.br_currstat:
            status = db.query(StatusData).filter(StatusData.st_statcd == entity.br_currstat).first()
            if status and status.st_descr:
                status_text = status.st_descr
        
        # Get category description
        category_text = entity.br_cat
        if entity.br_cat:
            category = db.query(BhikkuCategory).filter(BhikkuCategory.cc_code == entity.br_cat).first()
            if category and category.cc_catogry:
                category_text = category.cc_catogry
        
        return [
            {"titel": "Registration Number", "text": entity.br_regn},
            {"titel": "Name", "text": entity.br_mahananame},
            {"titel": "Birth Name", "text": entity.br_gihiname},
            {"titel": "Date of Birth", "text": str(entity.br_dofb) if entity.br_dofb else None},
            {"titel": "Contact Number", "text": entity.br_mobile},
            {"titel": "Email", "text": entity.br_email},
            {"titel": "Live Location", "text": live_location},
            {"titel": "Current Status", "text": status_text},
            {"titel": "Category", "text": category_text},
            {"titel": "Ordination Date", "text": str(entity.br_mahanadate) if entity.br_mahanadate else None},
        ]

    def _format_silmatha_qr_response(self, db: Session, entity) -> list:
        """Format Silmatha record for QR search response"""
        from app.models.silmatha_regist import SilmathaRegist
        from app.models.status import StatusData
        from app.models.bhikku_category import BhikkuCategory
        
        # Get temple details if available
        live_location = None
        if hasattr(entity, 'sil_mahanatemple') and entity.sil_mahanatemple:
            temple = db.query(ViharaData).filter(
                ViharaData.vh_trn == entity.sil_mahanatemple
            ).first()
            if temple:
                live_location = f"{temple.vh_vname}, {temple.vh_addrs}" if temple.vh_addrs else temple.vh_vname
        
        # Get status description
        status_text = entity.sil_currstat
        if entity.sil_currstat:
            status = db.query(StatusData).filter(StatusData.st_statcd == entity.sil_currstat).first()
            if status and status.st_descr:
                status_text = status.st_descr
        
        # Get category description
        category_text = entity.sil_cat
        if entity.sil_cat:
            category = db.query(BhikkuCategory).filter(BhikkuCategory.cc_code == entity.sil_cat).first()
            if category and category.cc_catogry:
                category_text = category.cc_catogry
        
        return [
            {"titel": "Registration Number", "text": entity.sil_regn},
            {"titel": "Name", "text": entity.sil_mahananame},
            {"titel": "Birth Name", "text": entity.sil_gihiname},
            {"titel": "Date of Birth", "text": str(entity.sil_dofb) if entity.sil_dofb else None},
            {"titel": "Contact Number", "text": entity.sil_mobile},
            {"titel": "Email", "text": entity.sil_email},
            {"titel": "Live Location", "text": live_location},
            {"titel": "Current Status", "text": status_text},
            {"titel": "Category", "text": category_text},
            {"titel": "Ordination Date", "text": str(entity.sil_mahanadate) if entity.sil_mahanadate else None},
        ]

    def _format_bhikku_high_qr_response(self, db: Session, entity: BhikkuHighRegist) -> list:
        """Format Bhikku High record for QR search response"""
        from app.models.status import StatusData
        from app.models.bhikku_category import BhikkuCategory
        
        # Get temple details if available
        live_location = None
        if entity.bhr_livtemple:
            temple = db.query(ViharaData).filter(
                ViharaData.vh_trn == entity.bhr_livtemple
            ).first()
            if temple:
                live_location = f"{temple.vh_vname}, {temple.vh_addrs}" if temple.vh_addrs else temple.vh_vname
        
        # Get candidate details for birth name and DOB
        birth_name = None
        date_of_birth = None
        contact_number = None
        email = None
        
        if entity.bhr_candidate_regn:
            candidate = db.query(Bhikku).filter(
                Bhikku.br_regn == entity.bhr_candidate_regn
            ).first()
            if candidate:
                birth_name = candidate.br_gihiname
                date_of_birth = candidate.br_dofb
                contact_number = candidate.br_mobile
                email = candidate.br_email
        
        # Get status description
        status_text = entity.bhr_currstat
        if entity.bhr_currstat:
            status = db.query(StatusData).filter(StatusData.st_statcd == entity.bhr_currstat).first()
            if status and status.st_descr:
                status_text = status.st_descr
        
        # Get category description
        category_text = entity.bhr_cc_code
        if entity.bhr_cc_code:
            category = db.query(BhikkuCategory).filter(BhikkuCategory.cc_code == entity.bhr_cc_code).first()
            if category and category.cc_catogry:
                category_text = category.cc_catogry
        
        return [
            {"titel": "Registration Number", "text": entity.bhr_regn},
            {"titel": "Name", "text": entity.bhr_assumed_name},
            {"titel": "Birth Name", "text": birth_name},
            {"titel": "Date of Birth", "text": str(date_of_birth) if date_of_birth else None},
            {"titel": "Contact Number", "text": contact_number},
            {"titel": "Email", "text": email},
            {"titel": "Live Location", "text": live_location},
            {"titel": "Current Status", "text": status_text},
            {"titel": "Category", "text": category_text},
            {"titel": "Ordination Date", "text": str(entity.bhr_higher_ordination_date) if entity.bhr_higher_ordination_date else None},
        ]


bhikku_service = BhikkuService()
