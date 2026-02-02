from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import MetaData, Table, inspect, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.models.devala import DevalaData
from app.repositories.devala_repo import devala_repo
from app.schemas.devala import DevalaCreate, DevalaCreatePayload, DevalaUpdate


class DevalaService:
    """Business logic layer for devala data."""

    def __init__(self) -> None:
        self._fk_targets: Optional[dict[str, tuple[Optional[str], str, str]]] = None

    def create_devala(
        self, db: Session, *, payload: DevalaCreate | DevalaCreatePayload, actor_id: Optional[str]
    ) -> DevalaData:
        # Convert camelCase payload to snake_case if it's DevalaCreatePayload
        if isinstance(payload, DevalaCreatePayload):
            payload_dict = {
                "dv_vname": payload.temple_name,
                "dv_addrs": payload.temple_address,
                "dv_mobile": payload.telephone_number,
                "dv_whtapp": payload.whatsapp_number,
                "dv_email": payload.email_address,
                "dv_province": payload.province,
                "dv_district": payload.district,
                "dv_divisional_secretariat": payload.divisional_secretariat,
                "dv_pradeshya_sabha": payload.pradeshya_sabha,
                "dv_gndiv": payload.grama_niladhari_division,
                "dv_nikaya": payload.nikaya,
                "dv_parshawa": payload.parshawaya,
                "dv_viharadhipathi_name": payload.viharadhipathi_name,
                "dv_period_established": payload.period_established,
                "dv_buildings_description": payload.buildings_description,
                "dv_dayaka_families_count": payload.dayaka_families_count,
                "dv_kulangana_committee": payload.kulangana_committee,
                "dv_dayaka_sabha": payload.dayaka_sabha,
                "dv_temple_working_committee": payload.temple_working_committee,
                "dv_other_associations": payload.other_associations,
                "temple_owned_land": [land.model_dump(by_alias=False) for land in payload.temple_owned_land],
                "dv_land_info_certified": payload.land_info_certified,
                "dv_resident_bhikkhus": payload.resident_bhikkhus,
                "dv_resident_bhikkhus_certified": payload.resident_bhikkhus_certified,
                "dv_inspection_report": payload.inspection_report,
                "dv_inspection_code": payload.inspection_code,
                "dv_grama_niladhari_division_ownership": payload.grama_niladhari_division_ownership,
                "dv_sanghika_donation_deed": payload.sanghika_donation_deed,
                "dv_government_donation_deed": payload.government_donation_deed,
                "dv_government_donation_deed_in_progress": payload.government_donation_deed_in_progress,
                "dv_authority_consent_attached": payload.authority_consent_attached,
                "dv_recommend_new_center": payload.recommend_new_center,
                "dv_recommend_registered_temple": payload.recommend_registered_temple,
                "dv_annex2_recommend_construction": payload.annex2_recommend_construction,
                "dv_annex2_land_ownership_docs": payload.annex2_land_ownership_docs,
                "dv_annex2_chief_incumbent_letter": payload.annex2_chief_incumbent_letter,
                "dv_annex2_coordinator_recommendation": payload.annex2_coordinator_recommendation,
                "dv_annex2_divisional_secretary_recommendation": payload.annex2_divisional_secretary_recommendation,
                "dv_annex2_approval_construction": payload.annex2_approval_construction,
                "dv_annex2_referral_resubmission": payload.annex2_referral_resubmission,
            }
        else:
            payload_dict = payload.model_dump(exclude_unset=True)
        
        # Validate contact fields
        dv_mobile = payload_dict.get("dv_mobile")
        dv_whtapp = payload_dict.get("dv_whtapp")
        dv_email = payload_dict.get("dv_email")
        
        contact_fields = (
            ("dv_mobile", dv_mobile, devala_repo.get_by_mobile),
            ("dv_whtapp", dv_whtapp, devala_repo.get_by_whtapp),
            ("dv_email", dv_email, devala_repo.get_by_email),
        )
        for field_name, value, getter in contact_fields:
            if value and getter(db, value):
                raise ValueError(f"{field_name} '{value}' is already registered.")

        now = datetime.utcnow()
        payload_dict = payload.model_dump(exclude_unset=True)
        payload_dict.pop("dv_trn", None)
        payload_dict.pop("dv_id", None)
        payload_dict.pop("dv_version_number", None)
        payload_dict["dv_created_by"] = actor_id
        payload_dict["dv_updated_by"] = actor_id
        payload_dict.setdefault("dv_created_at", now)
        payload_dict.setdefault("dv_updated_at", now)
        payload_dict.setdefault("dv_is_deleted", False)
        payload_dict["dv_version_number"] = 1
        # Set initial workflow status to PENDING (following bhikku_regist pattern)
        payload_dict.setdefault("dv_workflow_status", "PENDING")

        self._validate_foreign_keys(db, payload_dict)
        enriched_payload = DevalaCreate(**payload_dict)
        return devala_repo.create(db, data=enriched_payload)

    def list_devalas(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        dv_trn: Optional[str] = None,
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
        dv_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
        current_user = None,
    ) -> list[DevalaData]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return devala_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
            dv_trn=dv_trn,
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
            dv_typ=dv_typ,
            date_from=date_from,
            date_to=date_to,
            current_user=current_user,
        )

    def count_devalas(
        self, 
        db: Session, 
        *, 
        search: Optional[str] = None,
        dv_trn: Optional[str] = None,
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
        dv_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
    ) -> int:
        return devala_repo.count(
            db,
            search=search,
            dv_trn=dv_trn,
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
            dv_typ=dv_typ,
            date_from=date_from,
            date_to=date_to,
        )

    def get_devala(self, db: Session, dv_id: int) -> Optional[DevalaData]:
        return devala_repo.get(db, dv_id)

    def get_devala_by_trn(self, db: Session, dv_trn: str) -> Optional[DevalaData]:
        return devala_repo.get_by_trn(db, dv_trn)

    def list_devalas_simple(
        self, 
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """Return simplified list of devalas with just dv_trn and dv_vname, with pagination."""
        # Validate and sanitize inputs
        limit = max(1, min(limit, 200))  # Clamp limit between 1 and 200
        skip = max(0, skip)
        
        # Get paginated devalas
        devalas = devala_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
        )
        
        # Get total count for pagination
        total_count = devala_repo.count(
            db,
            search=search,
        )
        
        # Build simplified response
        simplified_devalas = [
            {
                "dv_trn": devala.dv_trn,
                "dv_vname": devala.dv_vname,
            }
            for devala in devalas
            if not devala.dv_is_deleted
        ]
        
        return simplified_devalas, total_count

    def update_devala(
        self,
        db: Session,
        *,
        dv_id: int,
        payload: DevalaUpdate,
        actor_id: Optional[str],
    ) -> DevalaData:
        entity = devala_repo.get(db, dv_id)
        if not entity:
            raise ValueError("Devala record not found.")

        if payload.dv_trn and payload.dv_trn != entity.dv_trn:
            raise ValueError("dv_trn cannot be modified once generated.")

        if payload.dv_mobile and payload.dv_mobile != entity.dv_mobile:
            conflict = devala_repo.get_by_mobile(db, payload.dv_mobile)
            if conflict and conflict.dv_id != entity.dv_id:
                raise ValueError(
                    f"dv_mobile '{payload.dv_mobile}' is already registered."
                )

        if payload.dv_whtapp and payload.dv_whtapp != entity.dv_whtapp:
            conflict = devala_repo.get_by_whtapp(db, payload.dv_whtapp)
            if conflict and conflict.dv_id != entity.dv_id:
                raise ValueError(
                    f"dv_whtapp '{payload.dv_whtapp}' is already registered."
                )

        if payload.dv_email and payload.dv_email != entity.dv_email:
            conflict = devala_repo.get_by_email(db, payload.dv_email)
            if conflict and conflict.dv_id != entity.dv_id:
                raise ValueError(
                    f"dv_email '{payload.dv_email}' is already registered."
                )

        update_data = payload.model_dump(exclude_unset=True)
        update_data.pop("dv_version_number", None)
        update_data["dv_updated_by"] = actor_id
        update_data["dv_updated_at"] = datetime.utcnow()

        fk_values = self._build_fk_validation_payload(entity, update_data)
        self._validate_foreign_keys(db, fk_values)

        patched_payload = DevalaUpdate(**update_data)
        return devala_repo.update(db, entity=entity, data=patched_payload)

    def delete_devala(
        self, db: Session, *, dv_id: int, actor_id: Optional[str]
    ) -> DevalaData:
        entity = devala_repo.get(db, dv_id)
        if not entity:
            raise ValueError("Devala record not found.")

        entity.dv_updated_by = actor_id
        entity.dv_updated_at = datetime.utcnow()
        return devala_repo.soft_delete(db, entity=entity)

    # --------------------------------------------------------------------- #
    # Workflow Methods (following bhikku_regist pattern)
    # --------------------------------------------------------------------- #
    def approve_devala(
        self,
        db: Session,
        *,
        dv_id: int,
        actor_id: Optional[str],
    ) -> DevalaData:
        """Approve a devala registration - transitions workflow from PEND-APPROVAL to COMPLETED status"""
        entity = devala_repo.get(db, dv_id)
        if not entity:
            raise ValueError("Devala record not found.")
        
        if entity.dv_workflow_status != "PEND-APPROVAL":
            raise ValueError(f"Cannot approve devala with workflow status: {entity.dv_workflow_status}. Must be PEND-APPROVAL.")
        
        # Update workflow fields - goes to APPROVED then COMPLETED
        entity.dv_workflow_status = "COMPLETED"
        entity.dv_approval_status = "APPROVED"
        entity.dv_approved_by = actor_id
        entity.dv_approved_at = datetime.utcnow()
        entity.dv_updated_by = actor_id
        entity.dv_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        return entity

    def reject_devala(
        self,
        db: Session,
        *,
        dv_id: int,
        actor_id: Optional[str],
        rejection_reason: Optional[str] = None,
    ) -> DevalaData:
        """Reject a devala registration - transitions workflow from PEND-APPROVAL to REJECTED status"""
        entity = devala_repo.get(db, dv_id)
        if not entity:
            raise ValueError("Devala record not found.")
        
        if entity.dv_workflow_status != "PEND-APPROVAL":
            raise ValueError(f"Cannot reject devala with workflow status: {entity.dv_workflow_status}. Must be PEND-APPROVAL.")
        
        # Update workflow fields
        entity.dv_workflow_status = "REJECTED"
        entity.dv_approval_status = "REJECTED"
        entity.dv_rejected_by = actor_id
        entity.dv_rejected_at = datetime.utcnow()
        entity.dv_rejection_reason = rejection_reason
        entity.dv_updated_by = actor_id
        entity.dv_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_printed(
        self,
        db: Session,
        *,
        dv_id: int,
        actor_id: Optional[str],
    ) -> DevalaData:
        """Mark devala certificate as printed - transitions workflow from PENDING to PRINTED status"""
        entity = devala_repo.get(db, dv_id)
        if not entity:
            raise ValueError("Devala record not found.")
        
        if entity.dv_workflow_status != "PENDING":
            raise ValueError(f"Cannot mark as printed devala with workflow status: {entity.dv_workflow_status}. Must be PENDING.")
        
        # Update workflow fields
        entity.dv_workflow_status = "PRINTED"
        entity.dv_printed_by = actor_id
        entity.dv_printed_at = datetime.utcnow()
        entity.dv_updated_by = actor_id
        entity.dv_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_scanned(
        self,
        db: Session,
        *,
        dv_id: int,
        actor_id: Optional[str],
    ) -> DevalaData:
        """Mark devala certificate as scanned - transitions workflow from PRINTED to PEND-APPROVAL status"""
        entity = devala_repo.get(db, dv_id)
        if not entity:
            raise ValueError("Devala record not found.")
        
        if entity.dv_workflow_status != "PRINTED":
            raise ValueError(f"Cannot mark as scanned devala with workflow status: {entity.dv_workflow_status}. Must be PRINTED.")
        
        # Update workflow fields
        entity.dv_workflow_status = "PEND-APPROVAL"
        entity.dv_scanned_by = actor_id
        entity.dv_scanned_at = datetime.utcnow()
        entity.dv_updated_by = actor_id
        entity.dv_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        return entity

    async def upload_scanned_document(
        self,
        db: Session,
        *,
        dv_id: int,
        file,  # UploadFile
        actor_id: Optional[str],
    ) -> DevalaData:
        """
        Upload a scanned document for a Devala record.
        
        When uploading a new document, the old file is renamed with a version suffix (v1, v2, etc.)
        instead of being deleted, preserving the file history.
        
        Args:
            db: Database session
            dv_id: Devala ID
            file: Uploaded file (PDF, JPG, PNG - max 5MB)
            actor_id: User ID performing the upload
            
        Returns:
            Updated DevalaData instance with file path stored
            
        Raises:
            ValueError: If devala not found or file upload fails
        """
        import os
        from pathlib import Path
        from app.utils.file_storage import file_storage_service
        
        # Get the devala record
        entity = devala_repo.get(db, dv_id)
        if not entity:
            raise ValueError(f"Devala with ID '{dv_id}' not found.")
        
        # Archive old file with version suffix instead of deleting it
        if entity.dv_scanned_document_path:
            old_file_path = entity.dv_scanned_document_path
            
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
        # File will be stored at: app/storage/devala_data/<year>/<month>/<day>/<dv_trn>/scanned_document_*.*
        relative_path, _ = await file_storage_service.save_file(
            file,
            entity.dv_trn,
            "scanned_document",
            subdirectory="devala_data"
        )
        
        # Update the devala record with the file path
        entity.dv_scanned_document_path = relative_path
        entity.dv_updated_by = actor_id
        entity.dv_updated_at = datetime.utcnow()
        # Increment version number when new document is uploaded
        entity.dv_version_number = (entity.dv_version_number or 0) + 1
        
        # Auto-transition workflow status to PEND-APPROVAL when document is uploaded
        # Only transition if currently in PRINTED status
        if entity.dv_workflow_status == "PRINTED":
            entity.dv_workflow_status = "PEND-APPROVAL"
            entity.dv_scanned_by = actor_id
            entity.dv_scanned_at = datetime.utcnow()
        
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
            "dv_gndiv": values.get("dv_gndiv"),
            "dv_ownercd": values.get("dv_ownercd"),
            "dv_parshawa": values.get("dv_parshawa"),
            "dv_ssbmcode": values.get("dv_ssbmcode"),
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
        self, entity: DevalaData, update_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        fk_fields = [
            "dv_gndiv",
            "dv_ownercd",
            "dv_parshawa",
            "dv_ssbmcode",
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
        for fk in inspector.get_foreign_keys(DevalaData.__tablename__):
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


devala_service = DevalaService()
