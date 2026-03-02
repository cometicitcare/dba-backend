# app/services/sasanarakshaka_service.py
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.sasanarakshaka import SasanarakshakaBalaMandalaya
from app.repositories.sasanarakshaka_repo import sasanarakshaka_repo
from app.schemas.sasanarakshaka import (
    SasanarakshakaBalaMandalayaCreate,
    SasanarakshakaBalaMandalayaUpdate,
    SasanarakshakaBalaMandalayaResponseWithNested,
    DivisionalSecretariatResponse,
    BhikkuNayakahimiResponse,
)


class SasanarakshakaBalaMandalayaService:
    """Business logic and validation for Sasanarakshaka Bala Mandalaya operations."""

    def _validate_foreign_keys(self, db: Session, sr_dvcd: Optional[str], sr_sbmnayakahimi: Optional[str]) -> None:
        """
        Validate foreign key references:
        - sr_dvcd -> cmm_dvsec.dv_dvcode
        - sr_sbmnayakahimi -> bhikku_regist.br_regn
        """
        # Validate divisional secretariat code
        if sr_dvcd:
            from sqlalchemy import text
            result = db.execute(
                text("SELECT 1 FROM cmm_dvsec WHERE dv_dvcode = :code AND dv_is_deleted = false LIMIT 1"),
                {"code": sr_dvcd}
            ).first()
            if not result:
                raise ValueError(f"Invalid divisional secretariat code: {sr_dvcd}")

        # Validate bhikku registration number
        if sr_sbmnayakahimi:
            from sqlalchemy import text
            result = db.execute(
                text("SELECT 1 FROM bhikku_regist WHERE br_regn = :regn AND br_is_deleted = false LIMIT 1"),
                {"regn": sr_sbmnayakahimi}
            ).first()
            if not result:
                raise ValueError(f"Invalid bhikku registration number: {sr_sbmnayakahimi}")

    def _validate_unique_code(self, db: Session, sr_ssbmcode: str, current_id: Optional[int] = None) -> None:
        """Validate that the code is unique"""
        existing = sasanarakshaka_repo.get_by_code(db, sr_ssbmcode)
        if existing and (current_id is None or existing.sr_id != current_id):
            raise ValueError(f"Sasanarakshaka Bala Mandalaya code '{sr_ssbmcode}' already exists.")

    def _convert_to_response_with_nested(
        self, record: SasanarakshakaBalaMandalaya
    ) -> SasanarakshakaBalaMandalayaResponseWithNested:
        """Convert a model record to response schema with nested objects"""
        # Get base dict from model
        response_dict = {
            "sr_id": record.sr_id,
            "sr_ssbmcode": record.sr_ssbmcode,
            "sr_dvcd": record.sr_dvcd,
            "sr_ssbname": record.sr_ssbname,
            "sr_sbmnayakahimi": record.sr_sbmnayakahimi,
            "sr_version": record.sr_version,
            "sr_is_deleted": record.sr_is_deleted,
            "sr_created_at": record.sr_created_at,
            "sr_updated_at": record.sr_updated_at,
            "sr_created_by": record.sr_created_by,
            "sr_updated_by": record.sr_updated_by,
            "sr_version_number": record.sr_version_number,
        }
        
        # Add nested divisional secretariat object
        if record.divisional_secretariat_ref:
            response_dict["sr_divisional_secretariat"] = DivisionalSecretariatResponse(
                dv_dvcode=record.divisional_secretariat_ref.dv_dvcode,
                dv_dvname=record.divisional_secretariat_ref.dv_dvname,
            )
        else:
            response_dict["sr_divisional_secretariat"] = None
        
        # Add nested bhikku nayakahimi object
        if record.bhikku_nayakahimi_ref:
            response_dict["sr_nayakahimi"] = BhikkuNayakahimiResponse(
                br_regn=record.bhikku_nayakahimi_ref.br_regn,
                br_gihiname=record.bhikku_nayakahimi_ref.br_gihiname,
                br_mobile=record.bhikku_nayakahimi_ref.br_mobile,
            )
        else:
            response_dict["sr_nayakahimi"] = None
        
        return SasanarakshakaBalaMandalayaResponseWithNested(**response_dict)

    def create_sasanarakshaka(
        self,
        db: Session,
        *,
        payload: SasanarakshakaBalaMandalayaCreate,
        actor_id: Optional[str] = None,
    ) -> SasanarakshakaBalaMandalaya:
        """Create a new Sasanarakshaka Bala Mandalaya record"""
        # Validate unique code
        self._validate_unique_code(db, payload.sr_ssbmcode)

        # Validate foreign keys
        self._validate_foreign_keys(db, payload.sr_dvcd, payload.sr_sbmnayakahimi)

        try:
            return sasanarakshaka_repo.create(db, obj_in=payload, created_by=actor_id)
        except IntegrityError as e:
            db.rollback()
            # Handle database constraint violations
            if "foreign key" in str(e).lower():
                raise ValueError("Foreign key constraint violation. Please check divisional secretariat code and bhikku registration number.")
            elif "unique" in str(e).lower():
                raise ValueError(f"Sasanarakshaka Bala Mandalaya code '{payload.sr_ssbmcode}' already exists.")
            else:
                raise ValueError(f"Database error: {str(e)}")

    def get_sasanarakshaka_by_id(
        self, db: Session, sr_id: int
    ) -> Optional[SasanarakshakaBalaMandalaya]:
        """Get a single Sasanarakshaka Bala Mandalaya by ID"""
        return sasanarakshaka_repo.get_by_id(db, sr_id)

    def get_sasanarakshaka_by_code(
        self, db: Session, sr_ssbmcode: str
    ) -> Optional[SasanarakshakaBalaMandalaya]:
        """Get a single Sasanarakshaka Bala Mandalaya by code"""
        return sasanarakshaka_repo.get_by_code(db, sr_ssbmcode)

    def get_all_sasanarakshaka(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search_key: Optional[str] = None,
        sr_dvcd: Optional[str] = None,
    ) -> Tuple[List[SasanarakshakaBalaMandalaya], int]:
        """Get paginated list with optional search and filters"""
        return sasanarakshaka_repo.get_all(
            db, skip=skip, limit=limit, search_key=search_key, sr_dvcd=sr_dvcd
        )

    def get_sasanarakshaka_by_divisional_secretariat(
        self,
        db: Session,
        sr_dvcd: str,
    ) -> List[SasanarakshakaBalaMandalayaResponseWithNested]:
        """
        Get all Sasanarakshaka records for a given divisional secretariat code.
        Returns records with nested foreign key objects.
        """
        records = sasanarakshaka_repo.get_by_divisional_secretariat(db, sr_dvcd)
        return [self._convert_to_response_with_nested(record) for record in records]

    def update_sasanarakshaka(
        self,
        db: Session,
        *,
        sr_id: int,
        payload: SasanarakshakaBalaMandalayaUpdate,
        actor_id: Optional[str] = None,
    ) -> SasanarakshakaBalaMandalaya:
        """Update an existing Sasanarakshaka Bala Mandalaya record"""
        db_obj = sasanarakshaka_repo.get_by_id(db, sr_id)
        if not db_obj:
            raise ValueError(f"Sasanarakshaka Bala Mandalaya with ID {sr_id} not found")

        # Validate unique code if being updated
        if payload.sr_ssbmcode and payload.sr_ssbmcode != db_obj.sr_ssbmcode:
            self._validate_unique_code(db, payload.sr_ssbmcode, current_id=sr_id)

        # Validate foreign keys if being updated
        sr_dvcd = payload.sr_dvcd if payload.sr_dvcd else None
        sr_sbmnayakahimi = payload.sr_sbmnayakahimi if payload.sr_sbmnayakahimi else None
        if sr_dvcd or sr_sbmnayakahimi:
            self._validate_foreign_keys(db, sr_dvcd, sr_sbmnayakahimi)

        try:
            return sasanarakshaka_repo.update(
                db, db_obj=db_obj, obj_in=payload, updated_by=actor_id
            )
        except IntegrityError as e:
            db.rollback()
            # Handle database constraint violations
            if "foreign key" in str(e).lower():
                raise ValueError("Foreign key constraint violation. Please check divisional secretariat code and bhikku registration number.")
            elif "unique" in str(e).lower():
                raise ValueError(f"Sasanarakshaka Bala Mandalaya code already exists.")
            else:
                raise ValueError(f"Database error: {str(e)}")

    def delete_sasanarakshaka(
        self, db: Session, *, sr_id: int, actor_id: Optional[str] = None
    ) -> Optional[SasanarakshakaBalaMandalaya]:
        """Soft delete a Sasanarakshaka Bala Mandalaya record"""
        db_obj = sasanarakshaka_repo.get_by_id(db, sr_id)
        if not db_obj:
            raise ValueError(f"Sasanarakshaka Bala Mandalaya with ID {sr_id} not found")

        return sasanarakshaka_repo.delete(db, sr_id=sr_id, deleted_by=actor_id)


# Create a singleton instance
sasanarakshaka_service = SasanarakshakaBalaMandalayaService()
