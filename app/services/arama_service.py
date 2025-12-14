from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import MetaData, Table, inspect, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.models.arama import AramaData
from app.repositories.arama_repo import arama_repo
from app.schemas.arama import AramaCreate, AramaCreatePayload, AramaUpdate


class AramaService:
    """Business logic layer for arama data."""

    def __init__(self) -> None:
        self._fk_targets: Optional[dict[str, tuple[Optional[str], str, str]]] = None

    def create_arama(
        self, db: Session, *, payload: AramaCreate | AramaCreatePayload, actor_id: Optional[str]
    ) -> AramaData:
        # Convert camelCase payload to snake_case if it's AramaCreatePayload
        if isinstance(payload, AramaCreatePayload):
            payload_dict = {
                "ar_vname": payload.temple_name,
                "ar_addrs": payload.temple_address,
                "ar_mobile": payload.telephone_number,
                "ar_whtapp": payload.whatsapp_number,
                "ar_email": payload.email_address,
                "ar_province": payload.province,
                "ar_district": payload.district,
                "ar_divisional_secretariat": payload.divisional_secretariat,
                "ar_pradeshya_sabha": payload.pradeshya_sabha,
                "ar_gndiv": payload.grama_niladhari_division,
                "ar_nikaya": payload.nikaya,
                "ar_parshawa": payload.parshawaya,
                "ar_viharadhipathi_name": payload.viharadhipathi_name,
                "ar_period_established": payload.period_established,
                "ar_buildings_description": payload.buildings_description,
                "ar_dayaka_families_count": payload.dayaka_families_count,
                "ar_kulangana_committee": payload.kulangana_committee,
                "ar_dayaka_sabha": payload.dayaka_sabha,
                "ar_temple_working_committee": payload.temple_working_committee,
                "ar_other_associations": payload.other_associations,
                "temple_owned_land": [land.model_dump(by_alias=False) for land in payload.temple_owned_land],
                "ar_land_info_certified": payload.land_info_certified,
                "resident_silmathas": [silmatha.model_dump(by_alias=False) for silmatha in payload.resident_silmathas],
                "ar_resident_silmathas_certified": payload.resident_silmathas_certified,
                "ar_inspection_report": payload.inspection_report,
                "ar_inspection_code": payload.inspection_code,
                "ar_grama_niladhari_division_ownership": payload.grama_niladhari_division_ownership,
                "ar_sanghika_donation_deed": payload.sanghika_donation_deed,
                "ar_government_donation_deed": payload.government_donation_deed,
                "ar_government_donation_deed_in_progress": payload.government_donation_deed_in_progress,
                "ar_authority_consent_attached": payload.authority_consent_attached,
                "ar_recommend_new_center": payload.recommend_new_center,
                "ar_recommend_registered_temple": payload.recommend_registered_temple,
                "ar_annex2_recommend_construction": payload.annex2_recommend_construction,
                "ar_annex2_land_ownership_docs": payload.annex2_land_ownership_docs,
                "ar_annex2_chief_incumbent_letter": payload.annex2_chief_incumbent_letter,
                "ar_annex2_coordinator_recommendation": payload.annex2_coordinator_recommendation,
                "ar_annex2_divisional_secretary_recommendation": payload.annex2_divisional_secretary_recommendation,
                "ar_annex2_approval_construction": payload.annex2_approval_construction,
                "ar_annex2_referral_resubmission": payload.annex2_referral_resubmission,
            }
        else:
            payload_dict = payload.model_dump(exclude_unset=True)
        
        # Validate contact fields
        ar_mobile = payload_dict.get("ar_mobile")
        ar_whtapp = payload_dict.get("ar_whtapp")
        ar_email = payload_dict.get("ar_email")
        
        contact_fields = (
            ("ar_mobile", ar_mobile, arama_repo.get_by_mobile),
            ("ar_whtapp", ar_whtapp, arama_repo.get_by_whtapp),
            ("ar_email", ar_email, arama_repo.get_by_email),
        )
        for field_name, value, getter in contact_fields:
            if value and getter(db, value):
                raise ValueError(f"{field_name} '{value}' is already registered.")

        now = datetime.utcnow()
        payload_dict.pop("ar_trn", None)
        payload_dict.pop("ar_id", None)
        payload_dict.pop("ar_version_number", None)
        
        # Keep nested data for repository to handle
        temple_lands = payload_dict.get("temple_owned_land", [])
        
        payload_dict["ar_created_by"] = actor_id
        payload_dict["ar_updated_by"] = actor_id
        payload_dict.setdefault("ar_created_at", now)
        payload_dict.setdefault("ar_updated_at", now)
        payload_dict.setdefault("ar_is_deleted", False)
        payload_dict["ar_version_number"] = 1
        # Set initial workflow status to PENDING (following bhikku_regist pattern)
        payload_dict.setdefault("ar_workflow_status", "PENDING")

        self._validate_foreign_keys(db, payload_dict)
        enriched_payload = AramaCreate(**payload_dict)
        return arama_repo.create(db, data=enriched_payload)

    def list_aramas(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        ar_trn: Optional[str] = None,
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
        ar_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
        current_user = None,
    ) -> list[AramaData]:
        limit = max(1, min(limit, 200))
        skip = max(0, skip)
        return arama_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
            ar_trn=ar_trn,
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
            ar_typ=ar_typ,
            date_from=date_from,
            date_to=date_to,
            current_user=current_user,
        )

    def count_aramas(
        self, 
        db: Session, 
        *, 
        search: Optional[str] = None,
        ar_trn: Optional[str] = None,
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
        ar_typ: Optional[str] = None,
        date_from: Optional[Any] = None,
        date_to: Optional[Any] = None,
    ) -> int:
        return arama_repo.count(
            db,
            search=search,
            ar_trn=ar_trn,
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
            ar_typ=ar_typ,
            date_from=date_from,
            date_to=date_to,
        )

    def get_arama(self, db: Session, ar_id: int) -> Optional[AramaData]:
        return arama_repo.get(db, ar_id)

    def get_arama_by_trn(self, db: Session, ar_trn: str) -> Optional[AramaData]:
        return arama_repo.get_by_trn(db, ar_trn)

    def list_aramas_simple(
        self, 
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """Return simplified list of aramas with just ar_trn and ar_vname, with pagination."""
        # Validate and sanitize inputs
        limit = max(1, min(limit, 200))  # Clamp limit between 1 and 200
        skip = max(0, skip)
        
        # Get paginated aramas
        aramas = arama_repo.list(
            db,
            skip=skip,
            limit=limit,
            search=search,
        )
        
        # Get total count for pagination
        total_count = arama_repo.count(
            db,
            search=search,
        )
        
        # Build simplified response
        simplified_aramas = [
            {
                "ar_trn": arama.ar_trn,
                "ar_vname": arama.ar_vname,
            }
            for arama in aramas
            if not arama.ar_is_deleted
        ]
        
        return simplified_aramas, total_count

    def update_arama(
        self,
        db: Session,
        *,
        ar_id: int,
        payload: AramaUpdate,
        actor_id: Optional[str],
    ) -> AramaData:
        entity = arama_repo.get(db, ar_id)
        if not entity:
            raise ValueError("Arama record not found.")

        if payload.ar_trn and payload.ar_trn != entity.ar_trn:
            raise ValueError("ar_trn cannot be modified once generated.")

        if payload.ar_mobile and payload.ar_mobile != entity.ar_mobile:
            conflict = arama_repo.get_by_mobile(db, payload.ar_mobile)
            if conflict and conflict.ar_id != entity.ar_id:
                raise ValueError(
                    f"ar_mobile '{payload.ar_mobile}' is already registered."
                )

        if payload.ar_whtapp and payload.ar_whtapp != entity.ar_whtapp:
            conflict = arama_repo.get_by_whtapp(db, payload.ar_whtapp)
            if conflict and conflict.ar_id != entity.ar_id:
                raise ValueError(
                    f"ar_whtapp '{payload.ar_whtapp}' is already registered."
                )

        if payload.ar_email and payload.ar_email != entity.ar_email:
            conflict = arama_repo.get_by_email(db, payload.ar_email)
            if conflict and conflict.ar_id != entity.ar_id:
                raise ValueError(
                    f"ar_email '{payload.ar_email}' is already registered."
                )

        update_data = payload.model_dump(exclude_unset=True)
        update_data.pop("ar_version_number", None)
        update_data["ar_updated_by"] = actor_id
        update_data["ar_updated_at"] = datetime.utcnow()

        fk_values = self._build_fk_validation_payload(entity, update_data)
        self._validate_foreign_keys(db, fk_values)

        patched_payload = AramaUpdate(**update_data)
        return arama_repo.update(db, entity=entity, data=patched_payload)

    def delete_arama(
        self, db: Session, *, ar_id: int, actor_id: Optional[str]
    ) -> AramaData:
        entity = arama_repo.get(db, ar_id)
        if not entity:
            raise ValueError("Arama record not found.")

        entity.ar_updated_by = actor_id
        entity.ar_updated_at = datetime.utcnow()
        return arama_repo.soft_delete(db, entity=entity)

    # --------------------------------------------------------------------- #
    # Workflow Methods (following bhikku_regist pattern)
    # --------------------------------------------------------------------- #
    def approve_arama(
        self,
        db: Session,
        *,
        ar_id: int,
        actor_id: Optional[str],
    ) -> AramaData:
        """Approve a arama registration - transitions workflow from PEND-APPROVAL to COMPLETED status"""
        entity = arama_repo.get(db, ar_id)
        if not entity:
            raise ValueError("Arama record not found.")
        
        if entity.ar_workflow_status != "PEND-APPROVAL":
            raise ValueError(f"Cannot approve arama with workflow status: {entity.ar_workflow_status}. Must be PEND-APPROVAL.")
        
        # Update workflow fields - goes to APPROVED then COMPLETED
        entity.ar_workflow_status = "COMPLETED"
        entity.ar_approval_status = "APPROVED"
        entity.ar_approved_by = actor_id
        entity.ar_approved_at = datetime.utcnow()
        entity.ar_updated_by = actor_id
        entity.ar_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        return entity

    def reject_arama(
        self,
        db: Session,
        *,
        ar_id: int,
        actor_id: Optional[str],
        rejection_reason: Optional[str] = None,
    ) -> AramaData:
        """Reject a arama registration - transitions workflow from PEND-APPROVAL to REJECTED status"""
        entity = arama_repo.get(db, ar_id)
        if not entity:
            raise ValueError("Arama record not found.")
        
        if entity.ar_workflow_status != "PEND-APPROVAL":
            raise ValueError(f"Cannot reject arama with workflow status: {entity.ar_workflow_status}. Must be PEND-APPROVAL.")
        
        # Update workflow fields
        entity.ar_workflow_status = "REJECTED"
        entity.ar_approval_status = "REJECTED"
        entity.ar_rejected_by = actor_id
        entity.ar_rejected_at = datetime.utcnow()
        entity.ar_rejection_reason = rejection_reason
        entity.ar_updated_by = actor_id
        entity.ar_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_printed(
        self,
        db: Session,
        *,
        ar_id: int,
        actor_id: Optional[str],
    ) -> AramaData:
        """Mark arama certificate as printed - transitions workflow from PENDING to PRINTED status"""
        entity = arama_repo.get(db, ar_id)
        if not entity:
            raise ValueError("Arama record not found.")
        
        if entity.ar_workflow_status != "PENDING":
            raise ValueError(f"Cannot mark as printed arama with workflow status: {entity.ar_workflow_status}. Must be PENDING.")
        
        # Update workflow fields
        entity.ar_workflow_status = "PRINTED"
        entity.ar_printed_by = actor_id
        entity.ar_printed_at = datetime.utcnow()
        entity.ar_updated_by = actor_id
        entity.ar_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        return entity

    def mark_scanned(
        self,
        db: Session,
        *,
        ar_id: int,
        actor_id: Optional[str],
    ) -> AramaData:
        """Mark arama certificate as scanned - transitions workflow from PRINTED to PEND-APPROVAL status"""
        entity = arama_repo.get(db, ar_id)
        if not entity:
            raise ValueError("Arama record not found.")
        
        if entity.ar_workflow_status != "PRINTED":
            raise ValueError(f"Cannot mark as scanned arama with workflow status: {entity.ar_workflow_status}. Must be PRINTED.")
        
        # Update workflow fields
        entity.ar_workflow_status = "PEND-APPROVAL"
        entity.ar_scanned_by = actor_id
        entity.ar_scanned_at = datetime.utcnow()
        entity.ar_updated_by = actor_id
        entity.ar_updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entity)
        return entity

    async def upload_scanned_document(
        self,
        db: Session,
        *,
        ar_id: int,
        file,  # UploadFile
        actor_id: Optional[str],
    ) -> AramaData:
        """
        Upload a scanned document for a Arama record.
        
        When uploading a new document, the old file is renamed with a version suffix (v1, v2, etc.)
        instead of being deleted, preserving the file history.
        
        Args:
            db: Database session
            ar_id: Arama ID
            file: Uploaded file (PDF, JPG, PNG - max 5MB)
            actor_id: User ID performing the upload
            
        Returns:
            Updated AramaData instance with file path stored
            
        Raises:
            ValueError: If arama not found or file upload fails
        """
        import os
        from pathlib import Path
        from app.utils.file_storage import file_storage_service
        
        # Get the arama record
        entity = arama_repo.get(db, ar_id)
        if not entity:
            raise ValueError(f"Arama with ID '{ar_id}' not found.")
        
        # Archive old file with version suffix instead of deleting it
        if entity.ar_scanned_document_path:
            old_file_path = entity.ar_scanned_document_path
            
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
        # File will be stored at: app/storage/arama_data/<year>/<month>/<day>/<ar_trn>/scanned_document_*.*
        relative_path, _ = await file_storage_service.save_file(
            file,
            entity.ar_trn,
            "scanned_document",
            subdirectory="arama_data"
        )
        
        # Update the arama record with the file path
        entity.ar_scanned_document_path = relative_path
        entity.ar_updated_by = actor_id
        entity.ar_updated_at = datetime.utcnow()
        # Increment version number when new document is uploaded
        entity.ar_version_number = (entity.ar_version_number or 0) + 1
        
        # Auto-transition workflow status to PEND-APPROVAL when document is uploaded
        # Only transition if currently in PRINTED status
        if entity.ar_workflow_status == "PRINTED":
            entity.ar_workflow_status = "PEND-APPROVAL"
            entity.ar_scanned_by = actor_id
            entity.ar_scanned_at = datetime.utcnow()
        
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
            "ar_gndiv": values.get("ar_gndiv"),
            "ar_ownercd": values.get("ar_ownercd"),
            "ar_parshawa": values.get("ar_parshawa"),
            "ar_ssbmcode": values.get("ar_ssbmcode"),
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
        self, entity: AramaData, update_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        fk_fields = [
            "ar_gndiv",
            "ar_ownercd",
            "ar_parshawa",
            "ar_ssbmcode",
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
        for fk in inspector.get_foreign_keys(AramaData.__tablename__):
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


arama_service = AramaService()
