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
    ) -> list[BhikkuHighRegist]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return bhikku_high_repo.list(db, skip=skip, limit=limit, search=search, current_user=current_user)

    def count_bhikku_highs(self, db: Session, *, search: Optional[str] = None) -> int:
        total = bhikku_high_repo.count(db, search=search)
        return int(total or 0)

    def get_bhikku_high(self, db: Session, *, bhr_id: int) -> Optional[BhikkuHighRegist]:
        return bhikku_high_repo.get(db, bhr_id)

    def get_bhikku_high_by_regn(
        self, db: Session, *, bhr_regn: str
    ) -> Optional[BhikkuHighRegist]:
        return bhikku_high_repo.get_by_regn(db, bhr_regn)

    def enrich_bhikku_high_dict(self, bhikku_high: BhikkuHighRegist) -> dict:
        """Transform BhikkuHighRegist model to dictionary with resolved nested objects"""
        
        # Get candidate bhikku's location and status data through the relationship
        candidate = bhikku_high.candidate_rel
        
        bhikku_high_dict = {
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
        """Approve a bhikku high registration - transitions workflow from SCANNED to APPROVED and then to COMPLETED status"""
        entity = bhikku_high_repo.get(db, bhr_id)
        if not entity:
            raise ValueError("Higher bhikku registration not found.")
        
        if entity.bhr_workflow_status != "SCANNED":
            raise ValueError(f"Cannot approve bhikku high with workflow status: {entity.bhr_workflow_status}. Must be SCANNED.")
        
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
        """Reject a bhikku high registration - transitions workflow from SCANNED to REJECTED status"""
        entity = bhikku_high_repo.get(db, bhr_id)
        if not entity:
            raise ValueError("Higher bhikku registration not found.")
        
        if entity.bhr_workflow_status != "SCANNED":
            raise ValueError(f"Cannot reject bhikku high with workflow status: {entity.bhr_workflow_status}. Must be SCANNED.")
        
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
        """Mark bhikku high certificate as scanned - transitions workflow from PRINTED to SCANNED status"""
        entity = bhikku_high_repo.get(db, bhr_id)
        if not entity:
            raise ValueError("Higher bhikku registration not found.")
        
        if entity.bhr_workflow_status != "PRINTED":
            raise ValueError(f"Cannot mark as scanned bhikku high with workflow status: {entity.bhr_workflow_status}. Must be PRINTED.")
        
        # Update workflow fields
        entity.bhr_workflow_status = "SCANNED"
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
            file: Uploaded file (PDF, JPG, PNG - max 5MB)
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
        
        # Auto-transition workflow status to SCANNED when document is uploaded
        # Only transition if currently in PRINTED status
        if entity.bhr_workflow_status == "PRINTED":
            entity.bhr_workflow_status = "SCANNED"
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
