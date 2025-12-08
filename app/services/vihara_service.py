from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import MetaData, Table, inspect, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.models.vihara import ViharaData
from app.repositories.vihara_repo import vihara_repo
from app.schemas.vihara import ViharaCreate, ViharaCreatePayload, ViharaUpdate


class ViharaService:
    """Business logic layer for vihara data."""

    def __init__(self) -> None:
        self._fk_targets: Optional[dict[str, tuple[Optional[str], str, str]]] = None

    def create_vihara(
        self, db: Session, *, payload: ViharaCreate | ViharaCreatePayload, actor_id: Optional[str]
    ) -> ViharaData:
        # Convert camelCase payload to snake_case if it's ViharaCreatePayload
        if isinstance(payload, ViharaCreatePayload):
            payload_dict = {
                "vh_vname": payload.temple_name,
                "vh_addrs": payload.temple_address,
                "vh_mobile": payload.telephone_number,
                "vh_whtapp": payload.whatsapp_number,
                "vh_email": payload.email_address,
                "vh_province": payload.province,
                "vh_district": payload.district,
                "vh_divisional_secretariat": payload.divisional_secretariat,
                "vh_pradeshya_sabha": payload.pradeshya_sabha,
                "vh_gndiv": payload.grama_niladhari_division,
                "vh_nikaya": payload.nikaya,
                "vh_parshawa": payload.parshawaya,
                "vh_viharadhipathi_name": payload.viharadhipathi_name,
                "vh_period_established": payload.period_established,
                "vh_buildings_description": payload.buildings_description,
                "vh_dayaka_families_count": payload.dayaka_families_count,
                "vh_kulangana_committee": payload.kulangana_committee,
                "vh_dayaka_sabha": payload.dayaka_sabha,
                "vh_temple_working_committee": payload.temple_working_committee,
                "vh_other_associations": payload.other_associations,
                "temple_owned_land": [land.model_dump(by_alias=False) for land in payload.temple_owned_land],
                "vh_land_info_certified": payload.land_info_certified,
                "resident_bhikkhus": [bhikkhu.model_dump(by_alias=False) for bhikkhu in payload.resident_bhikkhus],
                "vh_resident_bhikkhus_certified": payload.resident_bhikkhus_certified,
                "vh_inspection_report": payload.inspection_report,
                "vh_inspection_code": payload.inspection_code,
                "vh_grama_niladhari_division_ownership": payload.grama_niladhari_division_ownership,
                "vh_sanghika_donation_deed": payload.sanghika_donation_deed,
                "vh_government_donation_deed": payload.government_donation_deed,
                "vh_government_donation_deed_in_progress": payload.government_donation_deed_in_progress,
                "vh_authority_consent_attached": payload.authority_consent_attached,
                "vh_recommend_new_center": payload.recommend_new_center,
                "vh_recommend_registered_temple": payload.recommend_registered_temple,
                "vh_annex2_recommend_construction": payload.annex2_recommend_construction,
                "vh_annex2_land_ownership_docs": payload.annex2_land_ownership_docs,
                "vh_annex2_chief_incumbent_letter": payload.annex2_chief_incumbent_letter,
                "vh_annex2_coordinator_recommendation": payload.annex2_coordinator_recommendation,
                "vh_annex2_divisional_secretary_recommendation": payload.annex2_divisional_secretary_recommendation,
                "vh_annex2_approval_construction": payload.annex2_approval_construction,
                "vh_annex2_referral_resubmission": payload.annex2_referral_resubmission,
                "vh_form_id": payload.form_id,
            }
        else:
            payload_dict = payload.model_dump(exclude_unset=True)
        
        # Validate contact fields
        vh_mobile = payload_dict.get("vh_mobile")
        vh_whtapp = payload_dict.get("vh_whtapp")
        vh_email = payload_dict.get("vh_email")
        
        contact_fields = (
            ("vh_mobile", vh_mobile, vihara_repo.get_by_mobile),
            ("vh_whtapp", vh_whtapp, vihara_repo.get_by_whtapp),
            ("vh_email", vh_email, vihara_repo.get_by_email),
        )
        for field_name, value, getter in contact_fields:
            if value and getter(db, value):
                raise ValueError(f"{field_name} '{value}' is already registered.")

        now = datetime.utcnow()
        payload_dict.pop("vh_trn", None)
        payload_dict.pop("vh_id", None)
        payload_dict.pop("vh_version_number", None)
        
        # Keep nested data for repository to handle
        temple_lands = payload_dict.get("temple_owned_land", [])
        resident_bhikkhus = payload_dict.get("resident_bhikkhus", [])
        
        payload_dict["vh_created_by"] = actor_id
        payload_dict["vh_updated_by"] = actor_id
        payload_dict.setdefault("vh_created_at", now)
        payload_dict.setdefault("vh_updated_at", now)
        payload_dict.setdefault("vh_is_deleted", False)
        payload_dict["vh_version_number"] = 1
        # Set initial workflow status to PENDING (following bhikku_regist pattern)
        payload_dict.setdefault("vh_workflow_status", "PENDING")

        self._validate_foreign_keys(db, payload_dict)
        enriched_payload = ViharaCreate(**payload_dict)
        return vihara_repo.create(db, data=enriched_payload)

    def list_viharas(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
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
        category: Optional[str] = None,
        status: Optional[str] = None,
        vh_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
    ) -> list[ViharaData]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return vihara_repo.list(
            db,
            skip=skip,
            limit=limit,
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
            category=category,
            status=status,
            vh_typ=vh_typ,
            date_from=date_from,
            date_to=date_to,
        )

    def count_viharas(
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
        category: Optional[str] = None,
        status: Optional[str] = None,
        vh_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
    ) -> int:
        return vihara_repo.count(
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
            category=category,
            status=status,
            vh_typ=vh_typ,
            date_from=date_from,
            date_to=date_to,
        )

    def get_vihara(self, db: Session, vh_id: int) -> Optional[ViharaData]:
        return vihara_repo.get(db, vh_id)

    def get_vihara_by_trn(self, db: Session, vh_trn: str) -> Optional[ViharaData]:
        return vihara_repo.get_by_trn(db, vh_trn)

    def list_viharas_simple(
        self, 
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """Return simplified list of viharas with just vh_trn and vh_vname, with pagination."""
        # Validate and sanitize inputs
        limit = max(1, min(limit, 200))  # Clamp limit between 1 and 200
        skip = max(0, skip)
        
        # Get paginated viharas
        viharas = vihara_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
        )
        
        # Get total count for pagination
        total_count = vihara_repo.count(
            db,
            search=search,
        )
        
        # Build simplified response
        simplified_viharas = [
            {
                "vh_trn": vihara.vh_trn,
                "vh_vname": vihara.vh_vname,
            }
            for vihara in viharas
            if not vihara.vh_is_deleted
        ]
        
        return simplified_viharas, total_count

    def update_vihara(
        self,
        db: Session,
        *,
        vh_id: int,
        payload: ViharaUpdate,
        actor_id: Optional[str],
    ) -> ViharaData:
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")

        if payload.vh_trn and payload.vh_trn != entity.vh_trn:
            raise ValueError("vh_trn cannot be modified once generated.")

        if payload.vh_mobile and payload.vh_mobile != entity.vh_mobile:
            conflict = vihara_repo.get_by_mobile(db, payload.vh_mobile)
            if conflict and conflict.vh_id != entity.vh_id:
                raise ValueError(
                    f"vh_mobile '{payload.vh_mobile}' is already registered."
                )

        if payload.vh_whtapp and payload.vh_whtapp != entity.vh_whtapp:
            conflict = vihara_repo.get_by_whtapp(db, payload.vh_whtapp)
            if conflict and conflict.vh_id != entity.vh_id:
                raise ValueError(
                    f"vh_whtapp '{payload.vh_whtapp}' is already registered."
                )

        if payload.vh_email and payload.vh_email != entity.vh_email:
            conflict = vihara_repo.get_by_email(db, payload.vh_email)
            if conflict and conflict.vh_id != entity.vh_id:
                raise ValueError(
                    f"vh_email '{payload.vh_email}' is already registered."
                )

        update_data = payload.model_dump(exclude_unset=True)
        update_data.pop("vh_version_number", None)
        update_data["vh_updated_by"] = actor_id
        update_data["vh_updated_at"] = datetime.utcnow()

        fk_values = self._build_fk_validation_payload(entity, update_data)
        self._validate_foreign_keys(db, fk_values)

        patched_payload = ViharaUpdate(**update_data)
        return vihara_repo.update(db, entity=entity, data=patched_payload)

    def delete_vihara(
        self, db: Session, *, vh_id: int, actor_id: Optional[str]
    ) -> ViharaData:
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")

        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        return vihara_repo.soft_delete(db, entity=entity)

    # --------------------------------------------------------------------- #
    # Workflow Methods (following bhikku_regist pattern)
    # --------------------------------------------------------------------- #
    def approve_vihara(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
    ) -> ViharaData:
        """Approve a vihara registration - transitions workflow from PEND-APPROVAL to COMPLETED status"""
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        if entity.vh_workflow_status != "PEND-APPROVAL":
            raise ValueError(f"Cannot approve vihara with workflow status: {entity.vh_workflow_status}. Must be PEND-APPROVAL.")
        
        # Update workflow fields - goes to APPROVED then COMPLETED
        entity.vh_workflow_status = "COMPLETED"
        entity.vh_approval_status = "APPROVED"
        entity.vh_approved_by = actor_id
        entity.vh_approved_at = datetime.utcnow()
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        entity.vh_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def reject_vihara(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
        rejection_reason: Optional[str] = None,
    ) -> ViharaData:
        """Reject a vihara registration - transitions workflow from PEND-APPROVAL to REJECTED status"""
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        if entity.vh_workflow_status != "PEND-APPROVAL":
            raise ValueError(f"Cannot reject vihara with workflow status: {entity.vh_workflow_status}. Must be PEND-APPROVAL.")
        
        # Update workflow fields
        entity.vh_workflow_status = "REJECTED"
        entity.vh_approval_status = "REJECTED"
        entity.vh_rejected_by = actor_id
        entity.vh_rejected_at = datetime.utcnow()
        entity.vh_rejection_reason = rejection_reason
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        entity.vh_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_printed(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
    ) -> ViharaData:
        """Mark vihara certificate as printed - transitions workflow from PENDING to PRINTED status"""
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        if entity.vh_workflow_status != "PENDING":
            raise ValueError(f"Cannot mark as printed vihara with workflow status: {entity.vh_workflow_status}. Must be PENDING.")
        
        # Update workflow fields
        entity.vh_workflow_status = "PRINTED"
        entity.vh_printed_by = actor_id
        entity.vh_printed_at = datetime.utcnow()
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        entity.vh_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_scanned(
        self,
        db: Session,
        *,
        vh_id: int,
        actor_id: Optional[str],
    ) -> ViharaData:
        """Mark vihara certificate as scanned - transitions workflow from PRINTED to PEND-APPROVAL status"""
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError("Vihara record not found.")
        
        if entity.vh_workflow_status != "PRINTED":
            raise ValueError(f"Cannot mark as scanned vihara with workflow status: {entity.vh_workflow_status}. Must be PRINTED.")
        
        # Update workflow fields
        entity.vh_workflow_status = "PEND-APPROVAL"
        entity.vh_scanned_by = actor_id
        entity.vh_scanned_at = datetime.utcnow()
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        entity.vh_version_number += 1
        
        db.commit()
        db.refresh(entity)
        return entity

    async def upload_scanned_document(
        self,
        db: Session,
        *,
        vh_id: int,
        file,  # UploadFile
        actor_id: Optional[str],
    ) -> ViharaData:
        """
        Upload a scanned document for a Vihara record.
        
        When uploading a new document, the old file is renamed with a version suffix (v1, v2, etc.)
        instead of being deleted, preserving the file history.
        
        Args:
            db: Database session
            vh_id: Vihara ID
            file: Uploaded file (PDF, JPG, PNG - max 5MB)
            actor_id: User ID performing the upload
            
        Returns:
            Updated ViharaData instance with file path stored
            
        Raises:
            ValueError: If vihara not found or file upload fails
        """
        import os
        from pathlib import Path
        from app.utils.file_storage import file_storage_service
        
        # Get the vihara record
        entity = vihara_repo.get(db, vh_id)
        if not entity:
            raise ValueError(f"Vihara with ID '{vh_id}' not found.")
        
        # Archive old file with version suffix instead of deleting it
        if entity.vh_scanned_document_path:
            old_file_path = entity.vh_scanned_document_path
            
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
        # File will be stored at: app/storage/vihara_data/<year>/<month>/<day>/<vh_trn>/scanned_document_*.*
        relative_path, _ = await file_storage_service.save_file(
            file,
            entity.vh_trn,
            "scanned_document",
            subdirectory="vihara_data"
        )
        
        # Update the vihara record with the file path
        entity.vh_scanned_document_path = relative_path
        entity.vh_updated_by = actor_id
        entity.vh_updated_at = datetime.utcnow()
        # Increment version number when new document is uploaded
        entity.vh_version_number = (entity.vh_version_number or 0) + 1
        
        # Auto-transition workflow status to PEND-APPROVAL when document is uploaded
        # Only transition if currently in PRINTED status
        if entity.vh_workflow_status == "PRINTED":
            entity.vh_workflow_status = "PEND-APPROVAL"
            entity.vh_scanned_by = actor_id
            entity.vh_scanned_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        
        return entity

    def _validate_foreign_keys(self, db: Session, values: Dict[str, Any]) -> None:
        try:
            fk_targets = self._get_foreign_key_targets(db)
        except OperationalError as exc:
            raise ValueError(
                "Unable to verify references due to temporary database connectivity issues."
            ) from exc
        fields_to_validate = {
            "vh_gndiv": values.get("vh_gndiv"),
            "vh_ownercd": values.get("vh_ownercd"),
            "vh_parshawa": values.get("vh_parshawa"),
            "vh_ssbmcode": values.get("vh_ssbmcode"),
        }

        for field, raw_value in fields_to_validate.items():
            value = raw_value
            if value is None:
                continue
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    continue

            target = fk_targets.get(field)
            if not target:
                # Skip validation if no foreign key metadata exists (e.g., for audit fields)
                continue

            schema, table_name, column_name = target
            try:
                exists = self._reference_exists(
                    db,
                    schema=schema,
                    table_name=table_name,
                    column_name=column_name,
                    value=value,
                )
            except OperationalError as exc:
                raise ValueError(
                    "Unable to verify references due to temporary database connectivity issues."
                ) from exc

            if not exists:
                raise ValueError(f"Invalid reference: {field} not found")

    def _build_fk_validation_payload(
        self, entity: ViharaData, update_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        fk_fields = [
            "vh_gndiv",
            "vh_ownercd",
            "vh_parshawa",
            "vh_ssbmcode",
        ]
        payload: Dict[str, Any] = {}
        for field in fk_fields:
            if field in update_values:
                payload[field] = update_values[field]
            else:
                payload[field] = getattr(entity, field, None)
        return payload

    def _get_foreign_key_targets(
        self, db: Session
    ) -> dict[str, tuple[Optional[str], str, str]]:
        if self._fk_targets is not None:
            return self._fk_targets

        inspector = inspect(db.get_bind())
        mapping: dict[str, tuple[Optional[str], str, str]] = {}
        for fk in inspector.get_foreign_keys(ViharaData.__tablename__):
            constrained_columns = fk.get("constrained_columns") or []
            referred_columns = fk.get("referred_columns") or []
            table_name = fk.get("referred_table")
            schema = fk.get("referred_schema")
            if not table_name:
                continue

            for column, referred_column in zip(constrained_columns, referred_columns):
                if not column or not referred_column:
                    continue
                mapping[column] = (schema, table_name, referred_column)

        self._fk_targets = mapping
        return mapping

    def _reference_exists(
        self,
        db: Session,
        *,
        schema: Optional[str],
        table_name: str,
        column_name: str,
        value: Any,
    ) -> bool:
        metadata = MetaData()
        table = Table(table_name, metadata, schema=schema, autoload_with=db.get_bind())
        column = table.c.get(column_name)
        if column is None:
            raise RuntimeError(
                f"Invalid foreign key configuration: column '{column_name}' "
                f"not found in table '{table_name}'."
            )

        stmt = select(column).where(column == value).limit(1)
        result = db.execute(stmt).first()
        return result is not None


vihara_service = ViharaService()
