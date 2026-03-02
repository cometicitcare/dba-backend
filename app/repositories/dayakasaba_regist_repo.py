# app/repositories/dayakasaba_regist_repo.py
from typing import List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.dayakasaba_regist import DayakasabaRegist
from app.schemas.dayakasaba_regist import DayakasabaRegistCreate, DayakasabaRegistUpdate


class DayakasabaRegistRepository:
    """Data-access layer for the ``dayakasaba_regist`` table."""

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_by_id(self, db: Session, ds_id: int) -> Optional[DayakasabaRegist]:
        return (
            db.query(DayakasabaRegist)
            .filter(
                DayakasabaRegist.ds_id == ds_id,
                DayakasabaRegist.ds_is_deleted.is_(False),
            )
            .first()
        )

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search_key: Optional[str] = None,
        workflow_status: Optional[str] = None,
        temple_trn: Optional[str] = None,
    ) -> Tuple[List[DayakasabaRegist], int]:
        query = db.query(DayakasabaRegist).filter(
            DayakasabaRegist.ds_is_deleted.is_(False)
        )

        if search_key and search_key.strip():
            pattern = f"%{search_key.strip()}%"
            query = query.filter(
                or_(
                    DayakasabaRegist.ds_temple_trn.ilike(pattern),
                    DayakasabaRegist.ds_dayaka_sabha_name.ilike(pattern),
                    DayakasabaRegist.ds_president_name.ilike(pattern),
                    DayakasabaRegist.ds_secretary_name.ilike(pattern),
                )
            )

        if workflow_status:
            query = query.filter(DayakasabaRegist.ds_workflow_status == workflow_status)

        if temple_trn:
            query = query.filter(DayakasabaRegist.ds_temple_trn == temple_trn)

        total = query.count()
        records = (
            query.order_by(DayakasabaRegist.ds_id.desc()).offset(skip).limit(limit).all()
        )
        return records, total

    # ── Mutations ─────────────────────────────────────────────────────────────

    def create(
        self,
        db: Session,
        *,
        obj_in: DayakasabaRegistCreate,
        created_by: Optional[str] = None,
    ) -> DayakasabaRegist:
        db_obj = DayakasabaRegist(
            ds_temple_trn=obj_in.temple_trn,
            ds_phone_number=obj_in.phone_number,
            ds_nikaya=obj_in.nikaya,
            ds_parshawa=obj_in.parshawa,
            ds_district=obj_in.district,
            ds_ds_division=obj_in.ds_division,
            ds_dayaka_sabha_name=obj_in.dayaka_sabha_name,
            ds_meeting_date=obj_in.meeting_date,
            ds_devotee_family_count=obj_in.devotee_family_count,
            ds_president_name=obj_in.president_name,
            ds_is_signed_president=obj_in.is_signed_president,
            ds_vice_president_name=obj_in.vice_president_name,
            ds_is_signed_vice_president=obj_in.is_signed_vice_president,
            ds_secretary_name=obj_in.secretary_name,
            ds_is_signed_secretary=obj_in.is_signed_secretary,
            ds_asst_secretary_name=obj_in.asst_secretary_name,
            ds_is_signed_asst_secretary=obj_in.is_signed_asst_secretary,
            ds_treasurer_name=obj_in.treasurer_name,
            ds_is_signed_treasurer=obj_in.is_signed_treasurer,
            ds_committee_member_1=obj_in.committee_member_1,
            ds_is_signed_member_1=obj_in.is_signed_member_1,
            ds_committee_member_2=obj_in.committee_member_2,
            ds_is_signed_member_2=obj_in.is_signed_member_2,
            ds_committee_member_3=obj_in.committee_member_3,
            ds_is_signed_member_3=obj_in.is_signed_member_3,
            ds_committee_member_4=obj_in.committee_member_4,
            ds_is_signed_member_4=obj_in.is_signed_member_4,
            ds_committee_member_5=obj_in.committee_member_5,
            ds_is_signed_member_5=obj_in.is_signed_member_5,
            ds_committee_member_6=obj_in.committee_member_6,
            ds_is_signed_member_6=obj_in.is_signed_member_6,
            ds_committee_member_7=obj_in.committee_member_7,
            ds_is_signed_member_7=obj_in.is_signed_member_7,
            ds_committee_member_8=obj_in.committee_member_8,
            ds_is_signed_member_8=obj_in.is_signed_member_8,
            ds_committee_member_9=obj_in.committee_member_9,
            ds_is_signed_member_9=obj_in.is_signed_member_9,
            ds_committee_member_10=obj_in.committee_member_10,
            ds_is_signed_member_10=obj_in.is_signed_member_10,
            ds_bank_name=obj_in.bank_name,
            ds_bank_branch=obj_in.bank_branch,
            ds_account_number=obj_in.account_number,
            ds_is_temple_registered=obj_in.is_temple_registered,
            ds_is_signed_cert_secretary=obj_in.is_signed_cert_secretary,
            ds_is_signed_cert_president=obj_in.is_signed_cert_president,
            ds_is_signed_sasana_sec=obj_in.is_signed_sasana_sec,
            ds_is_signed_ds=obj_in.is_signed_ds,
            ds_is_signed_commissioner=obj_in.is_signed_commissioner,
            ds_workflow_status="PENDING",
            ds_created_by=created_by,
            ds_updated_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: DayakasabaRegist,
        obj_in: DayakasabaRegistUpdate,
        updated_by: Optional[str] = None,
    ) -> DayakasabaRegist:
        field_map = {
            "temple_trn": "ds_temple_trn",
            "phone_number": "ds_phone_number",
            "nikaya": "ds_nikaya",
            "parshawa": "ds_parshawa",
            "district": "ds_district",
            "ds_division": "ds_ds_division",
            "dayaka_sabha_name": "ds_dayaka_sabha_name",
            "meeting_date": "ds_meeting_date",
            "devotee_family_count": "ds_devotee_family_count",
            "president_name": "ds_president_name",
            "is_signed_president": "ds_is_signed_president",
            "vice_president_name": "ds_vice_president_name",
            "is_signed_vice_president": "ds_is_signed_vice_president",
            "secretary_name": "ds_secretary_name",
            "is_signed_secretary": "ds_is_signed_secretary",
            "asst_secretary_name": "ds_asst_secretary_name",
            "is_signed_asst_secretary": "ds_is_signed_asst_secretary",
            "treasurer_name": "ds_treasurer_name",
            "is_signed_treasurer": "ds_is_signed_treasurer",
            "committee_member_1": "ds_committee_member_1",
            "is_signed_member_1": "ds_is_signed_member_1",
            "committee_member_2": "ds_committee_member_2",
            "is_signed_member_2": "ds_is_signed_member_2",
            "committee_member_3": "ds_committee_member_3",
            "is_signed_member_3": "ds_is_signed_member_3",
            "committee_member_4": "ds_committee_member_4",
            "is_signed_member_4": "ds_is_signed_member_4",
            "committee_member_5": "ds_committee_member_5",
            "is_signed_member_5": "ds_is_signed_member_5",
            "committee_member_6": "ds_committee_member_6",
            "is_signed_member_6": "ds_is_signed_member_6",
            "committee_member_7": "ds_committee_member_7",
            "is_signed_member_7": "ds_is_signed_member_7",
            "committee_member_8": "ds_committee_member_8",
            "is_signed_member_8": "ds_is_signed_member_8",
            "committee_member_9": "ds_committee_member_9",
            "is_signed_member_9": "ds_is_signed_member_9",
            "committee_member_10": "ds_committee_member_10",
            "is_signed_member_10": "ds_is_signed_member_10",
            "bank_name": "ds_bank_name",
            "bank_branch": "ds_bank_branch",
            "account_number": "ds_account_number",
            "is_temple_registered": "ds_is_temple_registered",
            "is_signed_cert_secretary": "ds_is_signed_cert_secretary",
            "is_signed_cert_president": "ds_is_signed_cert_president",
            "is_signed_sasana_sec": "ds_is_signed_sasana_sec",
            "is_signed_ds": "ds_is_signed_ds",
            "is_signed_commissioner": "ds_is_signed_commissioner",
        }

        obj_data = obj_in.model_dump(exclude_unset=True)
        for schema_field, model_field in field_map.items():
            if schema_field in obj_data:
                setattr(db_obj, model_field, obj_data[schema_field])

        if updated_by:
            db_obj.ds_updated_by = updated_by
        db_obj.ds_version_number = (db_obj.ds_version_number or 0) + 1

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(
        self,
        db: Session,
        *,
        ds_id: int,
        deleted_by: Optional[str] = None,
    ) -> Optional[DayakasabaRegist]:
        db_obj = self.get_by_id(db, ds_id)
        if not db_obj:
            return None
        db_obj.ds_is_deleted = True
        db_obj.ds_updated_by = deleted_by
        db_obj.ds_version_number = (db_obj.ds_version_number or 0) + 1
        db.commit()
        db.refresh(db_obj)
        return db_obj


dayakasaba_regist_repo = DayakasabaRegistRepository()
