from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import MetaData, Table, select
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.bhikku_high import BhikkuHighRegist
from app.models.user import UserAccount
from app.models.vihara import ViharaData
from app.repositories import bhikku_repo
from app.repositories.bhikku_high_repo import bhikku_high_repo
from app.schemas.bhikku_high import BhikkuHighCreate, BhikkuHighUpdate


class BhikkuHighService:
    """Business logic layer for higher bhikku registrations."""

    FK_TABLE_MAP: Dict[str, Tuple[Optional[str], str, str]] = {
        "bhr_gndiv": ("public", "cmm_gndata", "gn_gnc"),
    }

    def __init__(self) -> None:
        self._table_cache: Dict[Tuple[Optional[str], str], Table] = {}

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def create_bhikku_high(
        self, db: Session, *, payload: BhikkuHighCreate, actor_id: Optional[str], current_user: Optional[UserAccount] = None
    ) -> BhikkuHighRegist:
        payload_dict = self._strip_strings(payload.model_dump())
        # Optional references that can be blank/null
        if not self._has_meaningful_value(payload_dict.get("bhr_samanera_serial_no")):
            payload_dict["bhr_samanera_serial_no"] = None

        # Handle temporary bhikku references - these can't be stored as FK references
        # Store the temp references in remarks for later retrieval
        import re
        temp_refs = []
        for field in ["bhr_candidate_regn", "bhr_karmacharya_name", "bhr_upaddhyaya_name", 
                      "bhr_tutors_tutor_regn", "bhr_presiding_bhikshu_regn", "bhr_samanera_serial_no"]:
            value = payload_dict.get(field)
            if value and isinstance(value, str):
                if value.startswith("TEMP-"):
                    temp_id = value[5:]  # Remove "TEMP-" prefix
                    temp_refs.append(f"[TEMP_{field.upper()}:{temp_id}]")
                    payload_dict[field] = None
        
        # Handle temporary vihara references
        for field in ["bhr_livtemple", "bhr_residence_higher_ordination_trn", 
                      "bhr_residence_permanent_trn", "bhr_higher_ordination_place"]:
            value = payload_dict.get(field)
            if value and isinstance(value, str):
                if value.startswith("TEMP-"):
                    temp_id = value[5:]  # Remove "TEMP-" prefix
                    temp_refs.append(f"[TEMP_{field.upper()}:{temp_id}]")
                    payload_dict[field] = None
        
        # Append temp references to remarks if any
        if temp_refs:
            existing_remarks = payload_dict.get("bhr_remarks") or ""
            existing_remarks = re.sub(r'\[TEMP_BHR_[A-Z_]+:\d+\]', '', existing_remarks).strip()
            temp_refs_str = " ".join(temp_refs)
            payload_dict["bhr_remarks"] = f"{existing_remarks} {temp_refs_str}".strip() if existing_remarks else temp_refs_str

        # Auto-populate location from current user (location-based access control)
        if current_user and current_user.ua_location_type == "DISTRICT_BRANCH" and current_user.ua_district_branch_id:
            from app.models.district_branch import DistrictBranch
            district_branch = db.query(DistrictBranch).filter(
                DistrictBranch.db_id == current_user.ua_district_branch_id
            ).first()
            if district_branch and district_branch.db_district_code:
                payload_dict["bhr_created_by_district"] = district_branch.db_district_code

        explicit_regn = payload_dict.get("bhr_regn")
        if explicit_regn:
            existing = bhikku_high_repo.get_raw_by_regn(db, explicit_regn)
            if existing and not existing.bhr_is_deleted:
                raise ValueError(f"bhr_regn '{explicit_regn}' already exists.")
            if existing and existing.bhr_is_deleted:
                raise ValueError(
                    f"bhr_regn '{explicit_regn}' belongs to a deleted record and cannot be reused."
                )

        self._validate_foreign_keys(db, payload_dict)
        self._validate_user_reference(db, actor_id, "bhr_created_by")
        self._validate_user_reference(db, actor_id, "bhr_updated_by")
        self._validate_unique_contact_fields(
            db,
            bhr_mobile=payload_dict.get("bhr_mobile"),
            bhr_email=payload_dict.get("bhr_email"),
            current_regn=None,
        )

        enriched_payload = BhikkuHighCreate(**payload_dict)
        return bhikku_high_repo.create(db, data=enriched_payload, actor_id=actor_id)

    def list_bhikku_highs(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        current_user: Optional[UserAccount] = None,
        vh_trn: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        status: Optional[list] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> list[BhikkuHighRegist]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return bhikku_high_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
            current_user=current_user,
            vh_trn=vh_trn,
            province=province,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            temple=temple,
            child_temple=child_temple,
            nikaya=nikaya,
            parshawaya=parshawaya,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

    def count_bhikku_highs(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        vh_trn: Optional[str] = None,
        province: Optional[str] = None,
        district: Optional[str] = None,
        divisional_secretariat: Optional[str] = None,
        gn_division: Optional[str] = None,
        temple: Optional[str] = None,
        child_temple: Optional[str] = None,
        nikaya: Optional[str] = None,
        parshawaya: Optional[str] = None,
        status: Optional[list] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> int:
        total = bhikku_high_repo.count(
            db,
            search=search,
            vh_trn=vh_trn,
            province=province,
            district=district,
            divisional_secretariat=divisional_secretariat,
            gn_division=gn_division,
            temple=temple,
            child_temple=child_temple,
            nikaya=nikaya,
            parshawaya=parshawaya,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )
        return int(total or 0)

    def get_bhikku_high(self, db: Session, *, bhr_id: int) -> Optional[BhikkuHighRegist]:
        return bhikku_high_repo.get(db, bhr_id)

    def get_bhikku_high_by_regn(
        self, db: Session, *, bhr_regn: str
    ) -> Optional[BhikkuHighRegist]:
        return bhikku_high_repo.get_by_regn(db, bhr_regn)

    def enrich_bhikku_high_dict(self, bhikku_high: BhikkuHighRegist) -> dict:
        """Transform BhikkuHighRegist model to dictionary with resolved nested objects"""
        import re
        from sqlalchemy.orm import joinedload
        
        # Parse temporary references from remarks
        temp_candidate_regn_id = None
        temp_karmacharya_id = None
        temp_upaddhyaya_id = None
        temp_tutors_tutor_id = None
        temp_presiding_bhikshu_id = None
        temp_samanera_serial_id = None
        temp_livtemple_id = None
        temp_residence_higher_id = None
        temp_residence_permanent_id = None
        temp_higher_ordination_place_id = None
        remarks_display = bhikku_high.bhr_remarks or ""
        
        if remarks_display:
            # Extract temp bhikku references
            match = re.search(r'\[TEMP_BHR_CANDIDATE_REGN:(\d+)\]', remarks_display)
            if match:
                temp_candidate_regn_id = int(match.group(1))
            match = re.search(r'\[TEMP_BHR_KARMACHARYA_NAME:(\d+)\]', remarks_display)
            if match:
                temp_karmacharya_id = int(match.group(1))
            match = re.search(r'\[TEMP_BHR_UPADDHYAYA_NAME:(\d+)\]', remarks_display)
            if match:
                temp_upaddhyaya_id = int(match.group(1))
            match = re.search(r'\[TEMP_BHR_TUTORS_TUTOR_REGN:(\d+)\]', remarks_display)
            if match:
                temp_tutors_tutor_id = int(match.group(1))
            match = re.search(r'\[TEMP_BHR_PRESIDING_BHIKSHU_REGN:(\d+)\]', remarks_display)
            if match:
                temp_presiding_bhikshu_id = int(match.group(1))
            match = re.search(r'\[TEMP_BHR_SAMANERA_SERIAL_NO:(\d+)\]', remarks_display)
            if match:
                temp_samanera_serial_id = int(match.group(1))
            
            # Extract temp vihara references
            match = re.search(r'\[TEMP_BHR_LIVTEMPLE:(\d+)\]', remarks_display)
            if match:
                temp_livtemple_id = int(match.group(1))
            match = re.search(r'\[TEMP_BHR_RESIDENCE_HIGHER_ORDINATION_TRN:(\d+)\]', remarks_display)
            if match:
                temp_residence_higher_id = int(match.group(1))
            match = re.search(r'\[TEMP_BHR_RESIDENCE_PERMANENT_TRN:(\d+)\]', remarks_display)
            if match:
                temp_residence_permanent_id = int(match.group(1))
            match = re.search(r'\[TEMP_BHR_HIGHER_ORDINATION_PLACE:(\d+)\]', remarks_display)
            if match:
                temp_higher_ordination_place_id = int(match.group(1))
            
            # Remove temp references from display remarks
            remarks_display = re.sub(r'\[TEMP_BHR_[A-Z_]+:\d+\]', '', remarks_display).strip()
        
        # Manually fetch related data with explicit queries to avoid N+1
        candidate = None
        status_obj = None
        parshawaya_obj = None
        livtemple_obj = None
        residence_higher_obj = None
        residence_permanent_obj = None
        tutor_obj = None
        presiding_obj = None
        karmacharya_obj = None
        upaddhyaya_obj = None
        samanera_obj = None
        higher_ordination_place_obj = None
        
        # Temp data objects
        temp_candidate_data = None
        temp_karmacharya_data = None
        temp_upaddhyaya_data = None
        temp_tutors_tutor_data = None
        temp_presiding_bhikshu_data = None
        temp_samanera_data = None
        temp_livtemple_data = None
        temp_residence_higher_data = None
        temp_residence_permanent_data = None
        temp_higher_ordination_place_data = None
        
        db = bhikku_high._sa_instance_state.session
        if db:
            # Fetch temp bhikku data
            if temp_candidate_regn_id or temp_karmacharya_id or temp_upaddhyaya_id or temp_tutors_tutor_id or temp_presiding_bhikshu_id or temp_samanera_serial_id:
                from app.models.temporary_bhikku import TemporaryBhikku
                
                if temp_candidate_regn_id:
                    temp_bhikku = db.query(TemporaryBhikku).filter(TemporaryBhikku.tb_id == temp_candidate_regn_id).first()
                    if temp_bhikku:
                        temp_candidate_data = {"br_regn": f"TEMP-{temp_bhikku.tb_id}", "br_mahananame": temp_bhikku.tb_name or "", "br_upasampadaname": ""}
                
                if temp_karmacharya_id:
                    temp_bhikku = db.query(TemporaryBhikku).filter(TemporaryBhikku.tb_id == temp_karmacharya_id).first()
                    if temp_bhikku:
                        temp_karmacharya_data = {"br_regn": f"TEMP-{temp_bhikku.tb_id}", "br_mahananame": temp_bhikku.tb_name or "", "br_upasampadaname": ""}
                
                if temp_upaddhyaya_id:
                    temp_bhikku = db.query(TemporaryBhikku).filter(TemporaryBhikku.tb_id == temp_upaddhyaya_id).first()
                    if temp_bhikku:
                        temp_upaddhyaya_data = {"br_regn": f"TEMP-{temp_bhikku.tb_id}", "br_mahananame": temp_bhikku.tb_name or "", "br_upasampadaname": ""}
                
                if temp_tutors_tutor_id:
                    temp_bhikku = db.query(TemporaryBhikku).filter(TemporaryBhikku.tb_id == temp_tutors_tutor_id).first()
                    if temp_bhikku:
                        temp_tutors_tutor_data = {"br_regn": f"TEMP-{temp_bhikku.tb_id}", "br_mahananame": temp_bhikku.tb_name or "", "br_upasampadaname": ""}
                
                if temp_presiding_bhikshu_id:
                    temp_bhikku = db.query(TemporaryBhikku).filter(TemporaryBhikku.tb_id == temp_presiding_bhikshu_id).first()
                    if temp_bhikku:
                        temp_presiding_bhikshu_data = {"br_regn": f"TEMP-{temp_bhikku.tb_id}", "br_mahananame": temp_bhikku.tb_name or "", "br_upasampadaname": ""}
                
                if temp_samanera_serial_id:
                    temp_bhikku = db.query(TemporaryBhikku).filter(TemporaryBhikku.tb_id == temp_samanera_serial_id).first()
                    if temp_bhikku:
                        temp_samanera_data = {"br_regn": f"TEMP-{temp_bhikku.tb_id}", "br_mahananame": temp_bhikku.tb_name or "", "br_upasampadaname": ""}
            
            # Fetch temp vihara data
            if temp_livtemple_id or temp_residence_higher_id or temp_residence_permanent_id or temp_higher_ordination_place_id:
                from app.models.temporary_vihara import TemporaryVihara
                
                if temp_livtemple_id:
                    temp_vihara = db.query(TemporaryVihara).filter(TemporaryVihara.tv_id == temp_livtemple_id).first()
                    if temp_vihara:
                        temp_livtemple_data = {"vh_trn": f"TEMP-{temp_vihara.tv_id}", "vh_vname": temp_vihara.tv_name or ""}
                
                if temp_residence_higher_id:
                    temp_vihara = db.query(TemporaryVihara).filter(TemporaryVihara.tv_id == temp_residence_higher_id).first()
                    if temp_vihara:
                        temp_residence_higher_data = {"vh_trn": f"TEMP-{temp_vihara.tv_id}", "vh_vname": temp_vihara.tv_name or ""}
                
                if temp_residence_permanent_id:
                    temp_vihara = db.query(TemporaryVihara).filter(TemporaryVihara.tv_id == temp_residence_permanent_id).first()
                    if temp_vihara:
                        temp_residence_permanent_data = {"vh_trn": f"TEMP-{temp_vihara.tv_id}", "vh_vname": temp_vihara.tv_name or ""}
                
                if temp_higher_ordination_place_id:
                    temp_vihara = db.query(TemporaryVihara).filter(TemporaryVihara.tv_id == temp_higher_ordination_place_id).first()
                    if temp_vihara:
                        temp_higher_ordination_place_data = {"vh_trn": f"TEMP-{temp_vihara.tv_id}", "vh_vname": temp_vihara.tv_name or ""}
            
            # Fetch regular related data
            if bhikku_high.bhr_candidate_regn:
                from app.models.bhikku import Bhikku
                candidate = db.query(Bhikku).filter(Bhikku.br_regn == bhikku_high.bhr_candidate_regn).first()
            
            if bhikku_high.bhr_currstat:
                from app.models.status import StatusData
                status_obj = db.query(StatusData).filter(StatusData.st_statcd == bhikku_high.bhr_currstat).first()
            
            if bhikku_high.bhr_parshawaya:
                from app.models.parshawadata import ParshawaData
                parshawaya_obj = db.query(ParshawaData).filter(ParshawaData.pr_prn == bhikku_high.bhr_parshawaya).first()
            
            if bhikku_high.bhr_livtemple:
                from app.models.vihara import ViharaData
                livtemple_obj = db.query(ViharaData).filter(ViharaData.vh_trn == bhikku_high.bhr_livtemple).first()
            
            if bhikku_high.bhr_residence_higher_ordination_trn:
                from app.models.vihara import ViharaData
                residence_higher_obj = db.query(ViharaData).filter(ViharaData.vh_trn == bhikku_high.bhr_residence_higher_ordination_trn).first()
            
            if bhikku_high.bhr_residence_permanent_trn:
                from app.models.vihara import ViharaData
                residence_permanent_obj = db.query(ViharaData).filter(ViharaData.vh_trn == bhikku_high.bhr_residence_permanent_trn).first()
            
            if bhikku_high.bhr_tutors_tutor_regn:
                from app.models.bhikku import Bhikku
                tutor_obj = db.query(Bhikku).filter(Bhikku.br_regn == bhikku_high.bhr_tutors_tutor_regn).first()
            
            if bhikku_high.bhr_presiding_bhikshu_regn:
                from app.models.bhikku import Bhikku
                presiding_obj = db.query(Bhikku).filter(Bhikku.br_regn == bhikku_high.bhr_presiding_bhikshu_regn).first()
            
            if bhikku_high.bhr_karmacharya_name:
                from app.models.bhikku import Bhikku
                karmacharya_obj = db.query(Bhikku).filter(Bhikku.br_regn == bhikku_high.bhr_karmacharya_name).first()
            
            if bhikku_high.bhr_upaddhyaya_name:
                from app.models.bhikku import Bhikku
                upaddhyaya_obj = db.query(Bhikku).filter(Bhikku.br_regn == bhikku_high.bhr_upaddhyaya_name).first()
            
            if bhikku_high.bhr_samanera_serial_no:
                from app.models.bhikku import Bhikku
                samanera_obj = db.query(Bhikku).filter(Bhikku.br_regn == bhikku_high.bhr_samanera_serial_no).first()
            
            if bhikku_high.bhr_higher_ordination_place:
                from app.models.vihara import ViharaData
                higher_ordination_place_obj = db.query(ViharaData).filter(ViharaData.vh_trn == bhikku_high.bhr_higher_ordination_place).first()
        
        bhikku_high_dict = {
            "bhr_id": bhikku_high.bhr_id,
            "bhr_regn": bhikku_high.bhr_regn,
            "bhr_reqstdate": bhikku_high.bhr_reqstdate,
            "bhr_samanera_serial_no": temp_samanera_data if temp_samanera_data else (
                {"br_regn": samanera_obj.br_regn, "br_mahananame": samanera_obj.br_mahananame or "", "br_upasampadaname": ""} if samanera_obj else bhikku_high.bhr_samanera_serial_no
            ),
            "bhr_remarks": remarks_display or None,
            
            "bhr_currstat": {
                "st_statcd": status_obj.st_statcd,
                "st_descr": status_obj.st_descr
            } if status_obj else bhikku_high.bhr_currstat,
            
            "bhr_parshawaya": {
                "code": parshawaya_obj.pr_prn,
                "name": parshawaya_obj.pr_pname
            } if parshawaya_obj else bhikku_high.bhr_parshawaya,
            
            "bhr_livtemple": temp_livtemple_data if temp_livtemple_data else (
                {"vh_trn": livtemple_obj.vh_trn, "vh_vname": livtemple_obj.vh_vname} if livtemple_obj else bhikku_high.bhr_livtemple
            ),
            
            "bhr_cc_code": bhikku_high.bhr_cc_code,
            "bhr_candidate_regn": temp_candidate_data if temp_candidate_data else (
                {"br_regn": candidate.br_regn, "br_mahananame": candidate.br_mahananame or "", "br_upasampadaname": ""} if candidate else bhikku_high.bhr_candidate_regn
            ),
            "bhr_higher_ordination_place": temp_higher_ordination_place_data if temp_higher_ordination_place_data else (
                {"vh_trn": higher_ordination_place_obj.vh_trn, "vh_vname": higher_ordination_place_obj.vh_vname} if higher_ordination_place_obj else bhikku_high.bhr_higher_ordination_place
            ),
            "bhr_higher_ordination_date": bhikku_high.bhr_higher_ordination_date,
            "bhr_karmacharya_name": temp_karmacharya_data if temp_karmacharya_data else (
                {"br_regn": karmacharya_obj.br_regn, "br_mahananame": karmacharya_obj.br_mahananame or "", "br_upasampadaname": ""} if karmacharya_obj else bhikku_high.bhr_karmacharya_name
            ),
            "bhr_upaddhyaya_name": temp_upaddhyaya_data if temp_upaddhyaya_data else (
                {"br_regn": upaddhyaya_obj.br_regn, "br_mahananame": upaddhyaya_obj.br_mahananame or "", "br_upasampadaname": ""} if upaddhyaya_obj else bhikku_high.bhr_upaddhyaya_name
            ),
            "bhr_assumed_name": bhikku_high.bhr_assumed_name,
            
            "bhr_residence_higher_ordination_trn": temp_residence_higher_data if temp_residence_higher_data else (
                {"vh_trn": residence_higher_obj.vh_trn, "vh_vname": residence_higher_obj.vh_vname} if residence_higher_obj else bhikku_high.bhr_residence_higher_ordination_trn
            ),
            
            "bhr_residence_permanent_trn": temp_residence_permanent_data if temp_residence_permanent_data else (
                {"vh_trn": residence_permanent_obj.vh_trn, "vh_vname": residence_permanent_obj.vh_vname} if residence_permanent_obj else bhikku_high.bhr_residence_permanent_trn
            ),
            
            "bhr_declaration_residence_address": bhikku_high.bhr_declaration_residence_address,
            
            "bhr_tutors_tutor_regn": temp_tutors_tutor_data if temp_tutors_tutor_data else (
                {"br_regn": tutor_obj.br_regn, "br_mahananame": tutor_obj.br_mahananame or "", "br_upasampadaname": ""} if tutor_obj else bhikku_high.bhr_tutors_tutor_regn
            ),
            
            "bhr_presiding_bhikshu_regn": temp_presiding_bhikshu_data if temp_presiding_bhikshu_data else (
                {"br_regn": presiding_obj.br_regn, "br_mahananame": presiding_obj.br_mahananame or "", "br_upasampadaname": ""} if presiding_obj else bhikku_high.bhr_presiding_bhikshu_regn
            ),
            
            "bhr_declaration_date": bhikku_high.bhr_declaration_date,
            "bhr_form_id": bhikku_high.bhr_form_id,
            "bhr_workflow_status": bhikku_high.bhr_workflow_status,
            "bhr_approval_status": bhikku_high.bhr_approval_status,
            "bhr_approved_by": bhikku_high.bhr_approved_by,
            "bhr_approved_at": bhikku_high.bhr_approved_at,
            "bhr_rejected_by": bhikku_high.bhr_rejected_by,
            "bhr_rejected_at": bhikku_high.bhr_rejected_at,
            "bhr_rejection_reason": bhikku_high.bhr_rejection_reason,
            "bhr_printed_by": bhikku_high.bhr_printed_by,
            "bhr_printed_at": bhikku_high.bhr_printed_at,
            "bhr_scanned_by": bhikku_high.bhr_scanned_by,
            "bhr_scanned_at": bhikku_high.bhr_scanned_at,
            "bhr_scanned_document_path": bhikku_high.bhr_scanned_document_path,
            "bhr_created_by_district": bhikku_high.bhr_created_by_district,
            "bhr_version": bhikku_high.bhr_version,
            "bhr_is_deleted": bhikku_high.bhr_is_deleted,
            "bhr_created_at": bhikku_high.bhr_created_at,
            "bhr_updated_at": bhikku_high.bhr_updated_at,
            "bhr_created_by": bhikku_high.bhr_created_by,
            "bhr_updated_by": bhikku_high.bhr_updated_by,
            "bhr_version_number": bhikku_high.bhr_version_number,
            
            # Flag to indicate this is from bhikku_high_regist table
            "form_type": "not_direct"
        }
        
        return bhikku_high_dict

    def convert_direct_to_bhikku_high_dict(self, direct_bhikku_high, db: Session) -> dict:
        """
        Convert DirectBhikkuHigh model to bhikku_high format dictionary.
        Maps direct_bhikku_high fields to bhikku_high equivalent fields.
        """
        import re
        from app.models.status import StatusData
        from app.models.parshawadata import ParshawaData
        from app.models.vihara import ViharaData
        from app.models.bhikku import Bhikku
        
        # Parse temporary references from remarks
        temp_karmacharya_id = None
        temp_upaddhyaya_id = None
        temp_tutors_tutor_id = None
        temp_presiding_bhikshu_id = None
        temp_samanera_serial_id = None
        temp_livtemple_id = None
        temp_residence_higher_id = None
        temp_residence_permanent_id = None
        temp_higher_ordination_place_id = None
        remarks_display = direct_bhikku_high.dbh_remarks or ""
        
        if remarks_display:
            # Extract temp bhikku references (using DBH prefix for direct bhikku high)
            match = re.search(r'\[TEMP_DBH_KARMACHARYA_NAME:(\d+)\]', remarks_display)
            if match:
                temp_karmacharya_id = int(match.group(1))
            match = re.search(r'\[TEMP_DBH_UPADDHYAYA_NAME:(\d+)\]', remarks_display)
            if match:
                temp_upaddhyaya_id = int(match.group(1))
            match = re.search(r'\[TEMP_DBH_TUTORS_TUTOR_REGN:(\d+)\]', remarks_display)
            if match:
                temp_tutors_tutor_id = int(match.group(1))
            match = re.search(r'\[TEMP_DBH_PRESIDING_BHIKSHU_REGN:(\d+)\]', remarks_display)
            if match:
                temp_presiding_bhikshu_id = int(match.group(1))
            match = re.search(r'\[TEMP_DBH_SAMANERA_SERIAL_NO:(\d+)\]', remarks_display)
            if match:
                temp_samanera_serial_id = int(match.group(1))
            
            # Extract temp vihara references
            match = re.search(r'\[TEMP_DBH_LIVTEMPLE:(\d+)\]', remarks_display)
            if match:
                temp_livtemple_id = int(match.group(1))
            match = re.search(r'\[TEMP_DBH_RESIDENCE_HIGHER_ORDINATION_TRN:(\d+)\]', remarks_display)
            if match:
                temp_residence_higher_id = int(match.group(1))
            match = re.search(r'\[TEMP_DBH_RESIDENCE_PERMANENT_TRN:(\d+)\]', remarks_display)
            if match:
                temp_residence_permanent_id = int(match.group(1))
            match = re.search(r'\[TEMP_DBH_HIGHER_ORDINATION_PLACE:(\d+)\]', remarks_display)
            if match:
                temp_higher_ordination_place_id = int(match.group(1))
            
            # Remove temp references from display remarks
            remarks_display = re.sub(r'\[TEMP_DBH_[A-Z_]+:\d+\]', '', remarks_display).strip()
        
        # Temp data objects
        temp_karmacharya_data = None
        temp_upaddhyaya_data = None
        temp_tutors_tutor_data = None
        temp_presiding_bhikshu_data = None
        temp_samanera_data = None
        temp_livtemple_data = None
        temp_residence_higher_data = None
        temp_residence_permanent_data = None
        temp_higher_ordination_place_data = None
        
        # Fetch temp bhikku data
        if temp_karmacharya_id or temp_upaddhyaya_id or temp_tutors_tutor_id or temp_presiding_bhikshu_id or temp_samanera_serial_id:
            from app.models.temporary_bhikku import TemporaryBhikku
            
            if temp_karmacharya_id:
                temp_bhikku = db.query(TemporaryBhikku).filter(TemporaryBhikku.tb_id == temp_karmacharya_id).first()
                if temp_bhikku:
                    temp_karmacharya_data = {"br_regn": f"TEMP-{temp_bhikku.tb_id}", "br_mahananame": temp_bhikku.tb_name or "", "br_upasampadaname": ""}
            
            if temp_upaddhyaya_id:
                temp_bhikku = db.query(TemporaryBhikku).filter(TemporaryBhikku.tb_id == temp_upaddhyaya_id).first()
                if temp_bhikku:
                    temp_upaddhyaya_data = {"br_regn": f"TEMP-{temp_bhikku.tb_id}", "br_mahananame": temp_bhikku.tb_name or "", "br_upasampadaname": ""}
            
            if temp_tutors_tutor_id:
                temp_bhikku = db.query(TemporaryBhikku).filter(TemporaryBhikku.tb_id == temp_tutors_tutor_id).first()
                if temp_bhikku:
                    temp_tutors_tutor_data = {"br_regn": f"TEMP-{temp_bhikku.tb_id}", "br_mahananame": temp_bhikku.tb_name or "", "br_upasampadaname": ""}
            
            if temp_presiding_bhikshu_id:
                temp_bhikku = db.query(TemporaryBhikku).filter(TemporaryBhikku.tb_id == temp_presiding_bhikshu_id).first()
                if temp_bhikku:
                    temp_presiding_bhikshu_data = {"br_regn": f"TEMP-{temp_bhikku.tb_id}", "br_mahananame": temp_bhikku.tb_name or "", "br_upasampadaname": ""}
            
            if temp_samanera_serial_id:
                temp_bhikku = db.query(TemporaryBhikku).filter(TemporaryBhikku.tb_id == temp_samanera_serial_id).first()
                if temp_bhikku:
                    temp_samanera_data = {"br_regn": f"TEMP-{temp_bhikku.tb_id}", "br_mahananame": temp_bhikku.tb_name or "", "br_upasampadaname": ""}
        
        # Fetch temp vihara data
        if temp_livtemple_id or temp_residence_higher_id or temp_residence_permanent_id or temp_higher_ordination_place_id:
            from app.models.temporary_vihara import TemporaryVihara
            
            if temp_livtemple_id:
                temp_vihara = db.query(TemporaryVihara).filter(TemporaryVihara.tv_id == temp_livtemple_id).first()
                if temp_vihara:
                    temp_livtemple_data = {"vh_trn": f"TEMP-{temp_vihara.tv_id}", "vh_vname": temp_vihara.tv_name or ""}
            
            if temp_residence_higher_id:
                temp_vihara = db.query(TemporaryVihara).filter(TemporaryVihara.tv_id == temp_residence_higher_id).first()
                if temp_vihara:
                    temp_residence_higher_data = {"vh_trn": f"TEMP-{temp_vihara.tv_id}", "vh_vname": temp_vihara.tv_name or ""}
            
            if temp_residence_permanent_id:
                temp_vihara = db.query(TemporaryVihara).filter(TemporaryVihara.tv_id == temp_residence_permanent_id).first()
                if temp_vihara:
                    temp_residence_permanent_data = {"vh_trn": f"TEMP-{temp_vihara.tv_id}", "vh_vname": temp_vihara.tv_name or ""}
            
            if temp_higher_ordination_place_id:
                temp_vihara = db.query(TemporaryVihara).filter(TemporaryVihara.tv_id == temp_higher_ordination_place_id).first()
                if temp_vihara:
                    temp_higher_ordination_place_data = {"vh_trn": f"TEMP-{temp_vihara.tv_id}", "vh_vname": temp_vihara.tv_name or ""}
        
        # Fetch related objects
        status_obj = None
        parshawaya_obj = None
        livtemple_obj = None
        residence_higher_obj = None
        residence_permanent_obj = None
        tutor_obj = None
        presiding_obj = None
        karmacharya_obj = None
        upaddhyaya_obj = None
        samanera_obj = None
        higher_ordination_place_obj = None
        
        if direct_bhikku_high.dbh_currstat:
            status_obj = db.query(StatusData).filter(StatusData.st_statcd == direct_bhikku_high.dbh_currstat).first()
        
        if direct_bhikku_high.dbh_parshawaya:
            parshawaya_obj = db.query(ParshawaData).filter(ParshawaData.pr_prn == direct_bhikku_high.dbh_parshawaya).first()
        
        if direct_bhikku_high.dbh_livtemple:
            livtemple_obj = db.query(ViharaData).filter(ViharaData.vh_trn == direct_bhikku_high.dbh_livtemple).first()
        
        if direct_bhikku_high.dbh_residence_higher_ordination_trn:
            residence_higher_obj = db.query(ViharaData).filter(ViharaData.vh_trn == direct_bhikku_high.dbh_residence_higher_ordination_trn).first()
        
        if direct_bhikku_high.dbh_residence_permanent_trn:
            residence_permanent_obj = db.query(ViharaData).filter(ViharaData.vh_trn == direct_bhikku_high.dbh_residence_permanent_trn).first()
        
        if direct_bhikku_high.dbh_tutors_tutor_regn:
            tutor_obj = db.query(Bhikku).filter(Bhikku.br_regn == direct_bhikku_high.dbh_tutors_tutor_regn).first()
        
        if direct_bhikku_high.dbh_presiding_bhikshu_regn:
            presiding_obj = db.query(Bhikku).filter(Bhikku.br_regn == direct_bhikku_high.dbh_presiding_bhikshu_regn).first()
        
        if direct_bhikku_high.dbh_karmacharya_name:
            karmacharya_obj = db.query(Bhikku).filter(Bhikku.br_regn == direct_bhikku_high.dbh_karmacharya_name).first()
        
        if direct_bhikku_high.dbh_upaddhyaya_name:
            upaddhyaya_obj = db.query(Bhikku).filter(Bhikku.br_regn == direct_bhikku_high.dbh_upaddhyaya_name).first()
        
        if direct_bhikku_high.dbh_samanera_serial_no:
            samanera_obj = db.query(Bhikku).filter(Bhikku.br_regn == direct_bhikku_high.dbh_samanera_serial_no).first()
        
        if direct_bhikku_high.dbh_higher_ordination_place:
            higher_ordination_place_obj = db.query(ViharaData).filter(ViharaData.vh_trn == direct_bhikku_high.dbh_higher_ordination_place).first()
        
        # Create the converted dictionary with bhikku_high field names
        converted_dict = {
            # Map direct bhikku high ID to bhikku high format
            "bhr_id": direct_bhikku_high.dbh_id,
            "bhr_regn": direct_bhikku_high.dbh_regn,
            "bhr_reqstdate": direct_bhikku_high.dbh_reqstdate,
            "bhr_samanera_serial_no": temp_samanera_data if temp_samanera_data else (
                {"br_regn": samanera_obj.br_regn, "br_mahananame": samanera_obj.br_mahananame or "", "br_upasampadaname": ""} if samanera_obj else direct_bhikku_high.dbh_samanera_serial_no
            ),
            "bhr_remarks": remarks_display or None,
            
            "bhr_currstat": {
                "st_statcd": status_obj.st_statcd,
                "st_descr": status_obj.st_descr
            } if status_obj else direct_bhikku_high.dbh_currstat,
            
            "bhr_parshawaya": {
                "code": parshawaya_obj.pr_prn,
                "name": parshawaya_obj.pr_pname
            } if parshawaya_obj else direct_bhikku_high.dbh_parshawaya,
            
            "bhr_livtemple": temp_livtemple_data if temp_livtemple_data else (
                {"vh_trn": livtemple_obj.vh_trn, "vh_vname": livtemple_obj.vh_vname} if livtemple_obj else direct_bhikku_high.dbh_livtemple
            ),
            
            "bhr_cc_code": direct_bhikku_high.dbh_cc_code,
            "bhr_candidate_regn": None,  # Direct high bhikku doesn't have candidate_regn
            "bhr_higher_ordination_place": temp_higher_ordination_place_data if temp_higher_ordination_place_data else (
                {"vh_trn": higher_ordination_place_obj.vh_trn, "vh_vname": higher_ordination_place_obj.vh_vname} if higher_ordination_place_obj else direct_bhikku_high.dbh_higher_ordination_place
            ),
            "bhr_higher_ordination_date": direct_bhikku_high.dbh_higher_ordination_date,
            "bhr_karmacharya_name": temp_karmacharya_data if temp_karmacharya_data else (
                {"br_regn": karmacharya_obj.br_regn, "br_mahananame": karmacharya_obj.br_mahananame or "", "br_upasampadaname": ""} if karmacharya_obj else direct_bhikku_high.dbh_karmacharya_name
            ),
            "bhr_upaddhyaya_name": temp_upaddhyaya_data if temp_upaddhyaya_data else (
                {"br_regn": upaddhyaya_obj.br_regn, "br_mahananame": upaddhyaya_obj.br_mahananame or "", "br_upasampadaname": ""} if upaddhyaya_obj else direct_bhikku_high.dbh_upaddhyaya_name
            ),
            "bhr_assumed_name": direct_bhikku_high.dbh_assumed_name,
            
            "bhr_residence_higher_ordination_trn": temp_residence_higher_data if temp_residence_higher_data else (
                {"vh_trn": residence_higher_obj.vh_trn, "vh_vname": residence_higher_obj.vh_vname} if residence_higher_obj else direct_bhikku_high.dbh_residence_higher_ordination_trn
            ),
            
            "bhr_residence_permanent_trn": temp_residence_permanent_data if temp_residence_permanent_data else (
                {"vh_trn": residence_permanent_obj.vh_trn, "vh_vname": residence_permanent_obj.vh_vname} if residence_permanent_obj else direct_bhikku_high.dbh_residence_permanent_trn
            ),
            
            "bhr_declaration_residence_address": direct_bhikku_high.dbh_declaration_residence_address,
            "bhr_tutors_tutor_regn": temp_tutors_tutor_data if temp_tutors_tutor_data else (
                {"br_regn": tutor_obj.br_regn, "br_mahananame": tutor_obj.br_mahananame or "", "br_upasampadaname": ""} if tutor_obj else direct_bhikku_high.dbh_tutors_tutor_regn
            ),
            "bhr_presiding_bhikshu_regn": temp_presiding_bhikshu_data if temp_presiding_bhikshu_data else (
                {"br_regn": presiding_obj.br_regn, "br_mahananame": presiding_obj.br_mahananame or "", "br_upasampadaname": ""} if presiding_obj else direct_bhikku_high.dbh_presiding_bhikshu_regn
            ),
            "bhr_declaration_date": direct_bhikku_high.dbh_declaration_date,
            "bhr_form_id": None,  # Direct high bhikku doesn't use form_id
            "bhr_workflow_status": direct_bhikku_high.dbh_workflow_status,
            "bhr_approval_status": direct_bhikku_high.dbh_approval_status,
            "bhr_approved_by": direct_bhikku_high.dbh_approved_by,
            "bhr_approved_at": direct_bhikku_high.dbh_approved_at,
            "bhr_rejected_by": direct_bhikku_high.dbh_rejected_by,
            "bhr_rejected_at": direct_bhikku_high.dbh_rejected_at,
            "bhr_rejection_reason": direct_bhikku_high.dbh_rejection_reason,
            "bhr_printed_by": direct_bhikku_high.dbh_printed_by,
            "bhr_printed_at": direct_bhikku_high.dbh_printed_at,
            "bhr_scanned_by": direct_bhikku_high.dbh_scanned_by,
            "bhr_scanned_at": direct_bhikku_high.dbh_scanned_at,
            "bhr_scanned_document_path": direct_bhikku_high.dbh_scanned_document_path,
            "bhr_created_by_district": direct_bhikku_high.dbh_created_by_district,
            "bhr_version": direct_bhikku_high.dbh_version,
            "bhr_is_deleted": direct_bhikku_high.dbh_is_deleted,
            "bhr_created_at": direct_bhikku_high.dbh_created_at,
            "bhr_updated_at": direct_bhikku_high.dbh_updated_at,
            "bhr_created_by": direct_bhikku_high.dbh_created_by,
            "bhr_updated_by": direct_bhikku_high.dbh_updated_by,
            "bhr_version_number": direct_bhikku_high.dbh_version_number,
            
            # Additional fields from direct bhikku high (these are from the combined record)
            "br_gihiname": direct_bhikku_high.dbh_gihiname,
            "br_mahananame": direct_bhikku_high.dbh_mahananame,
            "br_dofb": direct_bhikku_high.dbh_dofb,
            "br_mobile": direct_bhikku_high.dbh_mobile,
            "br_email": direct_bhikku_high.dbh_email,
            
            # Flag to indicate this is from direct_bhikku_high table
            "_source": "direct_bhikku_high",
            "form_type": "direct"
        }
        
        return converted_dict
    
    def _old_enrich_code_removed(self):
        """
        Old enrichment code below - kept for reference but not used
        Accessing relationships caused severe performance issues and timeouts
        """
        pass
        """
        bhikku_high_dict_old = {
            "bhr_id": bhikku_high.bhr_id,
            "bhr_regn": bhikku_high.bhr_regn,
            "bhr_reqstdate": bhikku_high.bhr_reqstdate,
            "bhr_samanera_serial_no": bhikku_high.bhr_samanera_serial_no,
            "bhr_remarks": bhikku_high.bhr_remarks,
            
            # Status with nested object
            "bhr_currstat": {
                "st_statcd": bhikku_high.status_rel.st_statcd,
                "st_descr": bhikku_high.status_rel.st_descr
            } if bhikku_high.status_rel else bhikku_high.bhr_currstat,
            
            # Parshawaya with nested object
            "bhr_parshawaya": {
                "code": bhikku_high.parshawaya_rel.pr_prn,
                "name": bhikku_high.parshawaya_rel.pr_pname
            } if bhikku_high.parshawaya_rel else bhikku_high.bhr_parshawaya,
            
            # Livtemple with nested object
            "bhr_livtemple": {
                "vh_trn": bhikku_high.livtemple_rel.vh_trn,
                "vh_vname": bhikku_high.livtemple_rel.vh_vname
            } if bhikku_high.livtemple_rel else bhikku_high.bhr_livtemple,
            
            "bhr_cc_code": bhikku_high.bhr_cc_code,
            "bhr_candidate_regn": bhikku_high.bhr_candidate_regn,
            "bhr_higher_ordination_place": bhikku_high.bhr_higher_ordination_place,
            "bhr_higher_ordination_date": bhikku_high.bhr_higher_ordination_date,
            "bhr_karmacharya_name": bhikku_high.bhr_karmacharya_name,
            "bhr_upaddhyaya_name": bhikku_high.bhr_upaddhyaya_name,
            "bhr_assumed_name": bhikku_high.bhr_assumed_name,
            
            # Residence temples with nested objects
            "bhr_residence_higher_ordination_trn": {
                "vh_trn": bhikku_high.residence_higher_ordination_rel.vh_trn,
                "vh_vname": bhikku_high.residence_higher_ordination_rel.vh_vname
            } if bhikku_high.residence_higher_ordination_rel else bhikku_high.bhr_residence_higher_ordination_trn,
            
            "bhr_residence_permanent_trn": {
                "vh_trn": bhikku_high.residence_permanent_rel.vh_trn,
                "vh_vname": bhikku_high.residence_permanent_rel.vh_vname
            } if bhikku_high.residence_permanent_rel else bhikku_high.bhr_residence_permanent_trn,
            
            "bhr_declaration_residence_address": bhikku_high.bhr_declaration_residence_address,
            
            # Bhikku references with nested objects
            "bhr_tutors_tutor_regn": {
                "br_regn": bhikku_high.tutors_tutor_rel.br_regn,
                "br_mahananame": bhikku_high.tutors_tutor_rel.br_mahananame or "",
                "br_upasampadaname": ""
            } if bhikku_high.tutors_tutor_rel else bhikku_high.bhr_tutors_tutor_regn,
            
            "bhr_presiding_bhikshu_regn": {
                "br_regn": bhikku_high.presiding_bhikshu_rel.br_regn,
                "br_mahananame": bhikku_high.presiding_bhikshu_rel.br_mahananame or "",
                "br_upasampadaname": ""
            } if bhikku_high.presiding_bhikshu_rel else bhikku_high.bhr_presiding_bhikshu_regn,
            
            "bhr_declaration_date": bhikku_high.bhr_declaration_date,
            "bhr_version": bhikku_high.bhr_version,
            "bhr_is_deleted": bhikku_high.bhr_is_deleted,
            "bhr_created_at": bhikku_high.bhr_created_at,
            "bhr_updated_at": bhikku_high.bhr_updated_at,
            "bhr_created_by": bhikku_high.bhr_created_by,
            "bhr_updated_by": bhikku_high.bhr_updated_by,
            "bhr_version_number": bhikku_high.bhr_version_number,
            
            # Workflow fields
            "bhr_workflow_status": bhikku_high.bhr_workflow_status,
            "bhr_printed_by": bhikku_high.bhr_printed_by,
            "bhr_printed_at": bhikku_high.bhr_printed_at,
            "bhr_scanned_by": bhikku_high.bhr_scanned_by,
            "bhr_scanned_at": bhikku_high.bhr_scanned_at,
            "bhr_approved_by": bhikku_high.bhr_approved_by,
            "bhr_approved_at": bhikku_high.bhr_approved_at,
            "bhr_rejected_by": bhikku_high.bhr_rejected_by,
            "bhr_rejected_at": bhikku_high.bhr_rejected_at,
            "bhr_rejection_reason": bhikku_high.bhr_rejection_reason,
            "bhr_scanned_document_path": bhikku_high.bhr_scanned_document_path,
        }
        
        # Add nested objects from candidate bhikku record if available
        if candidate:
            bhikku_high_dict["br_birthpls"] = candidate.br_birthpls
            bhikku_high_dict["br_province"] = {
                "cp_code": candidate.province_rel.cp_code,
                "cp_name": candidate.province_rel.cp_name
            } if candidate.province_rel else candidate.br_province
            bhikku_high_dict["br_district"] = {
                "dd_dcode": candidate.district_rel.dd_dcode,
                "dd_dname": candidate.district_rel.dd_dname
            } if candidate.district_rel else candidate.br_district
            bhikku_high_dict["br_korale"] = candidate.br_korale
            bhikku_high_dict["br_pattu"] = candidate.br_pattu
            bhikku_high_dict["br_division"] = {
                "dv_dvcode": candidate.division_rel.dv_dvcode,
                "dv_dvname": candidate.division_rel.dv_dvname
            } if candidate.division_rel else candidate.br_division
            bhikku_high_dict["br_vilage"] = candidate.br_vilage
            bhikku_high_dict["br_gndiv"] = {
                "gn_gnc": candidate.gndiv_rel.gn_gnc,
                "gn_gnname": candidate.gndiv_rel.gn_gnname
            } if candidate.gndiv_rel else candidate.br_gndiv
            bhikku_high_dict["br_gihiname"] = candidate.br_gihiname
            bhikku_high_dict["br_dofb"] = candidate.br_dofb
            bhikku_high_dict["br_fathrname"] = candidate.br_fathrname
            bhikku_high_dict["br_remarks"] = candidate.br_remarks
            bhikku_high_dict["br_currstat"] = {
                "st_statcd": candidate.status_rel.st_statcd,
                "st_descr": candidate.status_rel.st_descr
            } if candidate.status_rel else candidate.br_currstat
        
        return bhikku_high_dict
        """

    def update_bhikku_high(
        self,
        db: Session,
        *,
        bhr_id: int,
        payload: BhikkuHighUpdate,
        actor_id: Optional[str],
    ) -> BhikkuHighRegist:
        entity = bhikku_high_repo.get(db, bhr_id)
        if not entity:
            raise ValueError("Higher bhikku registration not found.")

        update_data = payload.model_dump(exclude_unset=True)
        update_data = self._strip_strings(update_data)
        if not self._has_meaningful_value(update_data.get("bhr_samanera_serial_no")):
            update_data["bhr_samanera_serial_no"] = None

        # Handle temporary bhikku references - these can't be stored as FK references
        import re
        temp_refs = []
        for field in ["bhr_candidate_regn", "bhr_karmacharya_name", "bhr_upaddhyaya_name", 
                      "bhr_tutors_tutor_regn", "bhr_presiding_bhikshu_regn", "bhr_samanera_serial_no"]:
            value = update_data.get(field)
            if value and isinstance(value, str):
                if value.startswith("TEMP-"):
                    temp_id = value[5:]  # Remove "TEMP-" prefix
                    temp_refs.append(f"[TEMP_{field.upper()}:{temp_id}]")
                    update_data[field] = None
        
        # Handle temporary vihara references
        for field in ["bhr_livtemple", "bhr_residence_higher_ordination_trn", 
                      "bhr_residence_permanent_trn", "bhr_higher_ordination_place"]:
            value = update_data.get(field)
            if value and isinstance(value, str):
                if value.startswith("TEMP-"):
                    temp_id = value[5:]  # Remove "TEMP-" prefix
                    temp_refs.append(f"[TEMP_{field.upper()}:{temp_id}]")
                    update_data[field] = None
        
        # Append temp references to remarks if any
        if temp_refs:
            existing_remarks = update_data.get("bhr_remarks") or entity.bhr_remarks or ""
            existing_remarks = re.sub(r'\[TEMP_BHR_[A-Z_]+:\d+\]', '', existing_remarks).strip()
            temp_refs_str = " ".join(temp_refs)
            update_data["bhr_remarks"] = f"{existing_remarks} {temp_refs_str}".strip() if existing_remarks else temp_refs_str

        if "bhr_regn" in update_data and update_data["bhr_regn"]:
            new_regn = update_data["bhr_regn"]
            if new_regn != entity.bhr_regn:
                raise ValueError("bhr_regn cannot be modified once created.")

        self._validate_foreign_keys(db, update_data)
        self._validate_user_reference(db, actor_id, "bhr_updated_by")
        self._validate_unique_contact_fields(
            db,
            bhr_mobile=update_data.get("bhr_mobile"),
            bhr_email=update_data.get("bhr_email"),
            current_regn=entity.bhr_regn,
        )

        patched_payload = BhikkuHighUpdate(**update_data)
        return bhikku_high_repo.update(
            db, entity=entity, data=patched_payload, actor_id=actor_id
        )

    def delete_bhikku_high(
        self,
        db: Session,
        *,
        bhr_id: int,
        actor_id: Optional[str],
    ) -> BhikkuHighRegist:
        entity = bhikku_high_repo.get(db, bhr_id)
        if not entity:
            raise ValueError("Higher bhikku registration not found.")

        return bhikku_high_repo.soft_delete(db, entity=entity, actor_id=actor_id)

    # ------------------------------------------------------------------ #
    # Workflow Methods
    # ------------------------------------------------------------------ #
    def approve_bhikku_high(
        self,
        db: Session,
        *,
        bhr_id: int,
        actor_id: Optional[str],
    ) -> BhikkuHighRegist:
        """Approve a bhikku high registration - transitions workflow from PEND-APPROVAL to APPROVED and then to COMPLETED status"""
        entity = bhikku_high_repo.get(db, bhr_id)
        if not entity:
            raise ValueError("Higher bhikku registration not found.")
        
        if entity.bhr_workflow_status != "PEND-APPROVAL":
            raise ValueError(f"Cannot approve bhikku high with workflow status: {entity.bhr_workflow_status}. Must be PEND-APPROVAL.")
        
        # Update workflow fields - goes to APPROVED then COMPLETED
        entity.bhr_workflow_status = "COMPLETED"
        entity.bhr_approval_status = "APPROVED"
        entity.bhr_approved_by = actor_id
        entity.bhr_approved_at = datetime.utcnow()
        entity.bhr_updated_by = actor_id
        entity.bhr_updated_at = datetime.utcnow()
        entity.bhr_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def reject_bhikku_high(
        self,
        db: Session,
        *,
        bhr_id: int,
        actor_id: Optional[str],
        rejection_reason: Optional[str] = None,
    ) -> BhikkuHighRegist:
        """Reject a bhikku high registration - transitions workflow from PEND-APPROVAL to REJECTED status"""
        entity = bhikku_high_repo.get(db, bhr_id)
        if not entity:
            raise ValueError("Higher bhikku registration not found.")
        
        if entity.bhr_workflow_status != "PEND-APPROVAL":
            raise ValueError(f"Cannot reject bhikku high with workflow status: {entity.bhr_workflow_status}. Must be PEND-APPROVAL.")
        
        # Update workflow fields
        entity.bhr_workflow_status = "REJECTED"
        entity.bhr_approval_status = "REJECTED"
        entity.bhr_rejected_by = actor_id
        entity.bhr_rejected_at = datetime.utcnow()
        entity.bhr_rejection_reason = rejection_reason
        entity.bhr_updated_by = actor_id
        entity.bhr_updated_at = datetime.utcnow()
        entity.bhr_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_printed(
        self,
        db: Session,
        *,
        bhr_id: int,
        actor_id: Optional[str],
    ) -> BhikkuHighRegist:
        """Mark bhikku high certificate as printed - transitions workflow from PENDING to PRINTED status"""
        entity = bhikku_high_repo.get(db, bhr_id)
        if not entity:
            raise ValueError("Higher bhikku registration not found.")
        
        if entity.bhr_workflow_status != "PENDING":
            raise ValueError(f"Cannot mark as printed bhikku high with workflow status: {entity.bhr_workflow_status}. Must be PENDING.")
        
        # Update workflow fields
        entity.bhr_workflow_status = "PRINTED"
        entity.bhr_printed_by = actor_id
        entity.bhr_printed_at = datetime.utcnow()
        entity.bhr_updated_by = actor_id
        entity.bhr_updated_at = datetime.utcnow()
        entity.bhr_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_scanned(
        self,
        db: Session,
        *,
        bhr_id: int,
        actor_id: Optional[str],
    ) -> BhikkuHighRegist:
        """Mark bhikku high certificate as scanned - transitions workflow from PRINTED to PEND-APPROVAL status"""
        entity = bhikku_high_repo.get(db, bhr_id)
        if not entity:
            raise ValueError("Higher bhikku registration not found.")
        
        if entity.bhr_workflow_status != "PRINTED":
            raise ValueError(f"Cannot mark as scanned bhikku high with workflow status: {entity.bhr_workflow_status}. Must be PRINTED.")
        
        # Update workflow fields
        entity.bhr_workflow_status = "PEND-APPROVAL"
        entity.bhr_scanned_by = actor_id
        entity.bhr_scanned_at = datetime.utcnow()
        entity.bhr_updated_by = actor_id
        entity.bhr_updated_at = datetime.utcnow()
        entity.bhr_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    async def upload_scanned_document(
        self,
        db: Session,
        *,
        bhr_regn: str,
        file,  # UploadFile type
        actor_id: Optional[str],
    ) -> BhikkuHighRegist:
        """
        Upload a scanned document for a Higher Bhikku registration record.
        
        When uploading a new document, the old file is renamed with a version suffix (v1, v2, etc.)
        instead of being deleted, preserving the file history.
        
        Args:
            db: Database session
            bhr_regn: Higher Bhikku registration number
            file: Uploaded file (PDF, JPG, PNG - max size)
            actor_id: User ID performing the upload
            
        Returns:
            Updated BhikkuHighRegist instance with file path stored
            
        Raises:
            ValueError: If higher bhikku registration not found or file upload fails
        """
        from pathlib import Path
        from app.utils.file_storage import file_storage_service
        
        # Get the bhikku high record
        entity = bhikku_high_repo.get_by_regn(db, bhr_regn)
        if not entity:
            raise ValueError(f"Higher bhikku registration with number '{bhr_regn}' not found.")
        
        # Archive old file with version suffix instead of deleting it
        if entity.bhr_scanned_document_path:
            old_file_path = entity.bhr_scanned_document_path
            
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
        # File will be stored at: app/storage/bhikku_high_regist/<year>/<month>/<day>/<bhr_regn>/scanned_document_*.*
        relative_path, _ = await file_storage_service.save_file(
            file,
            bhr_regn,
            "scanned_document",
            subdirectory="bhikku_high_regist"
        )
        
        # Update the bhikku high record with the file path
        entity.bhr_scanned_document_path = relative_path
        entity.bhr_updated_by = actor_id
        entity.bhr_updated_at = datetime.utcnow()
        # Increment version number when new document is uploaded
        entity.bhr_version_number = (entity.bhr_version_number or 0) + 1
        
        # Auto-transition workflow status to PEND-APPROVAL when document is uploaded
        # Only transition if currently in PRINTED status
        if entity.bhr_workflow_status == "PRINTED":
            entity.bhr_workflow_status = "PEND-APPROVAL"
            entity.bhr_scanned_by = actor_id
            entity.bhr_scanned_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        
        return entity

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _validate_unique_contact_fields(
        self,
        db: Session,
        *,
        bhr_mobile: Optional[str],
        bhr_email: Optional[str],
        current_regn: Optional[str],
    ) -> None:
        if self._has_meaningful_value(bhr_mobile):
            existing = bhikku_high_repo.get_by_mobile(db, bhr_mobile)
            if existing and existing.bhr_regn != current_regn:
                raise ValueError(
                    f"bhr_mobile '{bhr_mobile}' is already associated with another higher bhikku."
                )

        if self._has_meaningful_value(bhr_email):
            existing = bhikku_high_repo.get_by_email(db, bhr_email)
            if existing and existing.bhr_regn != current_regn:
                raise ValueError(
                    f"bhr_email '{bhr_email}' is already associated with another higher bhikku."
                )

    def _validate_foreign_keys(
        self,
        db: Session,
        payload: Dict[str, Any],
    ) -> None:
        # Validate bhr_samanera_serial_no -> bhikku_regist.br_regn
        self._validate_bhikku_reference(
            db, payload.get("bhr_samanera_serial_no"), "bhr_samanera_serial_no"
        )
        
        # Validate bhr_cc_code -> cmm_cat.cc_code
        self._validate_category_reference(
            db, payload.get("bhr_cc_code"), "bhr_cc_code"
        )
        
        # Validate bhr_candidate_regn -> bhikku_regist.br_regn
        self._validate_bhikku_reference(
            db, payload.get("bhr_candidate_regn"), "bhr_candidate_regn"
        )
        
        # Validate bhr_residence_higher_ordination_trn -> vihaddata.vh_trn
        self._validate_vihara_reference(
            db, payload.get("bhr_residence_higher_ordination_trn"), "bhr_residence_higher_ordination_trn"
        )
        
        # Validate bhr_residence_permanent_trn -> vihaddata.vh_trn
        self._validate_vihara_reference(
            db, payload.get("bhr_residence_permanent_trn"), "bhr_residence_permanent_trn"
        )
        
        # Validate bhr_tutors_tutor_regn -> bhikku_regist.br_regn
        self._validate_bhikku_reference(
            db, payload.get("bhr_tutors_tutor_regn"), "bhr_tutors_tutor_regn"
        )
        
        # Validate bhr_presiding_bhikshu_regn -> bhikku_regist.br_regn
        self._validate_bhikku_reference(
            db, payload.get("bhr_presiding_bhikshu_regn"), "bhr_presiding_bhikshu_regn"
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

    def _validate_category_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        from sqlalchemy import text
        exists = db.execute(
            text("SELECT 1 FROM cmm_cat WHERE cc_code = :code AND cc_is_deleted = false LIMIT 1"),
            {"code": value}
        ).first()
        
        if not exists:
            raise ValueError(f"Invalid category code: {field_name} '{value}' not found in cmm_cat table.")

    def _validate_bhikku_reference(
        self, db: Session, value: Optional[str], field_name: str
    ) -> None:
        if not self._has_meaningful_value(value):
            return

        exists = bhikku_repo.get_by_regn(db, value)
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


bhikku_high_service = BhikkuHighService()
