# app/services/dayakasaba_regist_service.py
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.dayakasaba_regist import DayakasabaRegist
from app.repositories.dayakasaba_regist_repo import dayakasaba_regist_repo
from app.schemas.dayakasaba_regist import (
    DayakasabaRegistCreate,
    DayakasabaRegistResponse,
    DayakasabaRegistUpdate,
)

# Max upload size: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


class DayakasabaRegistService:
    """Business logic for Dayaka Sabha Registration."""

    # ── helpers ───────────────────────────────────────────────────────────────

    def _to_response(self, record: DayakasabaRegist) -> DayakasabaRegistResponse:
        return DayakasabaRegistResponse.from_orm_map(record)

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def create(
        self,
        db: Session,
        *,
        payload: DayakasabaRegistCreate,
        actor_id: Optional[str] = None,
    ) -> DayakasabaRegistResponse:
        """Create a new Dayaka Sabha registration.  Starts in PENDING status."""
        record = dayakasaba_regist_repo.create(db, obj_in=payload, created_by=actor_id)
        return self._to_response(record)

    def get_by_id(
        self, db: Session, ds_id: int
    ) -> Optional[DayakasabaRegistResponse]:
        record = dayakasaba_regist_repo.get_by_id(db, ds_id)
        return self._to_response(record) if record else None

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search_key: Optional[str] = None,
        workflow_status: Optional[str] = None,
        temple_trn: Optional[str] = None,
    ) -> Tuple[List[DayakasabaRegistResponse], int]:
        records, total = dayakasaba_regist_repo.get_all(
            db,
            skip=skip,
            limit=limit,
            search_key=search_key,
            workflow_status=workflow_status,
            temple_trn=temple_trn,
        )
        return [self._to_response(r) for r in records], total

    def update(
        self,
        db: Session,
        *,
        ds_id: int,
        payload: DayakasabaRegistUpdate,
        actor_id: Optional[str] = None,
    ) -> Optional[DayakasabaRegistResponse]:
        db_obj = dayakasaba_regist_repo.get_by_id(db, ds_id)
        if not db_obj:
            return None
        updated = dayakasaba_regist_repo.update(
            db, db_obj=db_obj, obj_in=payload, updated_by=actor_id
        )
        return self._to_response(updated)

    def delete(
        self,
        db: Session,
        *,
        ds_id: int,
        actor_id: Optional[str] = None,
    ) -> bool:
        result = dayakasaba_regist_repo.soft_delete(db, ds_id=ds_id, deleted_by=actor_id)
        return result is not None

    # ── Workflow ──────────────────────────────────────────────────────────────

    def approve(
        self,
        db: Session,
        *,
        ds_id: int,
        actor_id: Optional[str] = None,
    ) -> DayakasabaRegistResponse:
        """
        Approve a Dayaka Sabha registration.
        Allowed only when workflow_status == PEND-APPROVAL.
        Transitions to COMPLETED.
        """
        entity = dayakasaba_regist_repo.get_by_id(db, ds_id)
        if not entity:
            raise ValueError(f"Dayaka Sabha registration with ID {ds_id} not found.")

        if entity.ds_workflow_status != "PEND-APPROVAL":
            raise ValueError(
                f"Cannot approve record with status '{entity.ds_workflow_status}'. "
                "Record must be in PEND-APPROVAL status."
            )

        now = datetime.utcnow()
        entity.ds_workflow_status = "COMPLETED"
        entity.ds_approved_by = actor_id
        entity.ds_approved_at = now
        entity.ds_updated_by = actor_id
        entity.ds_updated_at = now
        entity.ds_version_number = (entity.ds_version_number or 0) + 1

        db.commit()
        db.refresh(entity)
        return self._to_response(entity)

    def reject(
        self,
        db: Session,
        *,
        ds_id: int,
        rejection_reason: str,
        actor_id: Optional[str] = None,
    ) -> DayakasabaRegistResponse:
        """
        Reject a Dayaka Sabha registration.
        Allowed only when workflow_status == PEND-APPROVAL.
        Transitions to REJECTED.
        """
        entity = dayakasaba_regist_repo.get_by_id(db, ds_id)
        if not entity:
            raise ValueError(f"Dayaka Sabha registration with ID {ds_id} not found.")

        if entity.ds_workflow_status != "PEND-APPROVAL":
            raise ValueError(
                f"Cannot reject record with status '{entity.ds_workflow_status}'. "
                "Record must be in PEND-APPROVAL status."
            )

        now = datetime.utcnow()
        entity.ds_workflow_status = "REJECTED"
        entity.ds_rejected_by = actor_id
        entity.ds_rejected_at = now
        entity.ds_rejection_reason = rejection_reason
        entity.ds_updated_by = actor_id
        entity.ds_updated_at = now
        entity.ds_version_number = (entity.ds_version_number or 0) + 1

        db.commit()
        db.refresh(entity)
        return self._to_response(entity)

    # ── Document upload ───────────────────────────────────────────────────────

    async def upload_scanned_document(
        self,
        db: Session,
        *,
        ds_id: int,
        file: UploadFile,
        actor_id: Optional[str] = None,
    ) -> DayakasabaRegistResponse:
        """
        Upload a scanned document for a Dayaka Sabha record.

        - Validates file size (max 5 MB) and extension (PDF / JPG / PNG).
        - Archives any previous file with a versioned suffix.
        - Saves the new file under:
          ``app/storage/dayakasaba_regist/<year>/<month>/<day>/<ds_id>/scanned_doc_<ts>.<ext>``
        - If workflow_status == PENDING  →  transitions to PEND-APPROVAL automatically.
        """
        from app.utils.file_storage import file_storage_service

        entity = dayakasaba_regist_repo.get_by_id(db, ds_id)
        if not entity:
            raise ValueError(f"Dayaka Sabha registration with ID {ds_id} not found.")

        # Validate extension
        original_filename = file.filename or ""
        ext = Path(original_filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File type '{ext}' not allowed. Allowed: PDF, JPG, JPEG, PNG."
            )

        # Archive old file (non-fatal)
        if entity.ds_scanned_document_path:
            old_path = entity.ds_scanned_document_path
            clean = old_path[9:] if old_path.startswith("/storage/") else old_path
            path_obj = Path(clean)
            storage_dir = Path("app/storage") / path_obj.parent
            stem = path_obj.stem
            file_ext_old = path_obj.suffix
            max_v = 0
            if storage_dir.exists():
                for f_existing in storage_dir.glob(f"{stem}_v*{file_ext_old}"):
                    parts = f_existing.stem.rsplit("_v", 1)
                    if len(parts) == 2 and parts[1].isdigit():
                        max_v = max(max_v, int(parts[1]))
            versioned_name = f"{stem}_v{max_v + 1}{file_ext_old}"
            try:
                file_storage_service.rename_file(
                    old_path,
                    str(path_obj.parent / versioned_name),
                )
            except Exception as exc:
                print(f"Warning: could not archive old dayakasaba doc {old_path}: {exc}")

        # Save new file
        # File will be stored at: app/storage/dayakasaba_regist/<year>/<month>/<day>/<ds_id>/scanned_document_*.*
        relative_path, _ = await file_storage_service.save_file(
            file,
            f"ds-{ds_id}",
            "scanned_document",
            subdirectory="dayakasaba_regist",
        )

        # Update record (save_file already returns a /storage/-prefixed path)
        entity.ds_scanned_document_path = relative_path
        entity.ds_updated_by = actor_id
        entity.ds_updated_at = datetime.utcnow()
        entity.ds_version_number = (entity.ds_version_number or 0) + 1

        # Auto-transition PENDING → PEND-APPROVAL on first upload
        if entity.ds_workflow_status == "PENDING":
            entity.ds_workflow_status = "PEND-APPROVAL"

        db.commit()
        db.refresh(entity)
        return self._to_response(entity)


dayakasaba_regist_service = DayakasabaRegistService()
