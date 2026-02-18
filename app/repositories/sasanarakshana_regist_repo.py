# app/repositories/sasanarakshana_regist_repo.py
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.sasanarakshana_regist import SasanarakshanaRegist
from app.schemas.sasanarakshana_regist import SasanarakshanaRegistCreate, SasanarakshanaRegistUpdate


class SasanarakshanaRegistRepository:
    """
    Data access helper for the `cmm_sasanarakshana_regist` table.
    """

    def get_by_id(self, db: Session, sar_id: int) -> Optional[SasanarakshanaRegist]:
        """Get a single record by ID"""
        return (
            db.query(SasanarakshanaRegist)
            .filter(
                SasanarakshanaRegist.sar_id == sar_id,
                SasanarakshanaRegist.sar_is_deleted.is_(False),
            )
            .first()
        )

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search_key: Optional[str] = None,
    ) -> tuple[List[SasanarakshanaRegist], int]:
        """
        Get paginated list of records with optional search.
        Returns (records, total_count).
        """
        query = db.query(SasanarakshanaRegist).filter(
            SasanarakshanaRegist.sar_is_deleted.is_(False)
        )

        if search_key and search_key.strip():
            pattern = f"%{search_key.strip()}%"
            query = query.filter(
                or_(
                    SasanarakshanaRegist.sar_temple_name.ilike(pattern),
                    SasanarakshanaRegist.sar_mandala_name.ilike(pattern),
                    SasanarakshanaRegist.sar_president_name.ilike(pattern),
                    SasanarakshanaRegist.sar_general_secretary_name.ilike(pattern),
                )
            )

        total = query.count()
        records = (
            query.order_by(SasanarakshanaRegist.sar_id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return records, total

    def create(
        self,
        db: Session,
        *,
        obj_in: SasanarakshanaRegistCreate,
        created_by: Optional[str] = None,
    ) -> SasanarakshanaRegist:
        """Create a new record"""
        db_obj = SasanarakshanaRegist(
            sar_temple_name=obj_in.temple_name,
            sar_temple_address=obj_in.temple_address,
            sar_mandala_name=obj_in.mandala_name,
            sar_bank_name=obj_in.bank_name,
            sar_account_number=obj_in.account_number,
            sar_president_name=obj_in.president_name,
            sar_deputy_president_name=obj_in.deputy_president_name,
            sar_vice_president_1_name=obj_in.vice_president_1_name,
            sar_vice_president_2_name=obj_in.vice_president_2_name,
            sar_general_secretary_name=obj_in.general_secretary_name,
            sar_deputy_secretary_name=obj_in.deputy_secretary_name,
            sar_treasurer_name=obj_in.treasurer_name,
            sar_committee_member_1=obj_in.committee_member_1,
            sar_committee_member_2=obj_in.committee_member_2,
            sar_committee_member_3=obj_in.committee_member_3,
            sar_committee_member_4=obj_in.committee_member_4,
            sar_committee_member_5=obj_in.committee_member_5,
            sar_committee_member_6=obj_in.committee_member_6,
            sar_committee_member_7=obj_in.committee_member_7,
            sar_committee_member_8=obj_in.committee_member_8,
            sar_chief_organizer_name=obj_in.chief_organizer_name,
            sar_created_by=created_by,
            sar_updated_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: SasanarakshanaRegist,
        obj_in: SasanarakshanaRegistUpdate,
        updated_by: Optional[str] = None,
    ) -> SasanarakshanaRegist:
        """Update an existing record"""
        field_map = {
            "temple_name": "sar_temple_name",
            "temple_address": "sar_temple_address",
            "mandala_name": "sar_mandala_name",
            "bank_name": "sar_bank_name",
            "account_number": "sar_account_number",
            "president_name": "sar_president_name",
            "deputy_president_name": "sar_deputy_president_name",
            "vice_president_1_name": "sar_vice_president_1_name",
            "vice_president_2_name": "sar_vice_president_2_name",
            "general_secretary_name": "sar_general_secretary_name",
            "deputy_secretary_name": "sar_deputy_secretary_name",
            "treasurer_name": "sar_treasurer_name",
            "committee_member_1": "sar_committee_member_1",
            "committee_member_2": "sar_committee_member_2",
            "committee_member_3": "sar_committee_member_3",
            "committee_member_4": "sar_committee_member_4",
            "committee_member_5": "sar_committee_member_5",
            "committee_member_6": "sar_committee_member_6",
            "committee_member_7": "sar_committee_member_7",
            "committee_member_8": "sar_committee_member_8",
            "chief_organizer_name": "sar_chief_organizer_name",
        }

        obj_data = obj_in.model_dump(exclude_unset=True)
        for schema_field, model_field in field_map.items():
            if schema_field in obj_data:
                setattr(db_obj, model_field, obj_data[schema_field])

        if updated_by:
            db_obj.sar_updated_by = updated_by

        db_obj.sar_version_number = (db_obj.sar_version_number or 0) + 1

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(
        self,
        db: Session,
        *,
        sar_id: int,
        deleted_by: Optional[str] = None,
    ) -> Optional[SasanarakshanaRegist]:
        """Soft-delete a record by ID"""
        db_obj = self.get_by_id(db, sar_id)
        if not db_obj:
            return None
        db_obj.sar_is_deleted = True
        db_obj.sar_updated_by = deleted_by
        db_obj.sar_version_number = (db_obj.sar_version_number or 0) + 1
        db.commit()
        db.refresh(db_obj)
        return db_obj


sasanarakshana_regist_repo = SasanarakshanaRegistRepository()
