from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.db.base import Base


class DevalaData(Base):
    __tablename__ = "devaladata"

    dv_id = Column(Integer, primary_key=True, index=True)
    dv_trn = Column(String(10), nullable=False, index=True, unique=True)
    dv_vname = Column(String(200))
    dv_addrs = Column(String(200))
    dv_mobile = Column(String(10), nullable=False)
    dv_whtapp = Column(String(10), nullable=False)
    dv_email = Column(String(200), nullable=False, index=True, unique=True)
    dv_typ = Column(String(10), nullable=False)
    dv_gndiv = Column(String(10), nullable=False)
    dv_fmlycnt = Column(Integer)
    dv_bgndate = Column(Date)
    dv_ownercd = Column(String(12), nullable=False)
    dv_parshawa = Column(String(10), nullable=False)
    dv_ssbmcode = Column(String(10))
    dv_syojakarmakrs = Column(String(100))
    dv_syojakarmdate = Column(Date)
    dv_landownrship = Column(String(150))
    dv_pralename = Column(String(50))
    dv_pralesigdate = Column(Date)
    dv_bacgrecmn = Column(String(100))
    dv_bacgrcmdate = Column(Date)
    dv_minissecrsigdate = Column(Date)
    dv_minissecrmrks = Column(String(200))
    dv_ssbmsigdate = Column(Date)
    
    # Extended Fields
    dv_province = Column(String(100))
    dv_district = Column(String(100))
    dv_divisional_secretariat = Column(String(100))
    dv_pradeshya_sabha = Column(String(100))
    dv_nikaya = Column(String(50))
    dv_viharadhipathi_name = Column(String(200))
    dv_period_established = Column(String(100))
    dv_buildings_description = Column(String(1000))
    dv_dayaka_families_count = Column(String(50))
    dv_kulangana_committee = Column(String(500))
    dv_dayaka_sabha = Column(String(500))
    dv_temple_working_committee = Column(String(500))
    dv_other_associations = Column(String(500))
    dv_temple_owned_land = Column(String(2000))
    dv_land_info_certified = Column(Boolean)
    dv_resident_bhikkhus = Column(String(2000))
    dv_resident_bhikkhus_certified = Column(Boolean)
    dv_inspection_report = Column(String(1000))
    dv_inspection_code = Column(String(100))
    dv_grama_niladhari_division_ownership = Column(String(200))
    dv_sanghika_donation_deed = Column(Boolean)
    dv_government_donation_deed = Column(Boolean)
    dv_government_donation_deed_in_progress = Column(Boolean)
    dv_authority_consent_attached = Column(Boolean)
    dv_recommend_new_center = Column(Boolean)
    dv_recommend_registered_temple = Column(Boolean)
    dv_annex2_recommend_construction = Column(Boolean)
    dv_annex2_land_ownership_docs = Column(Boolean)
    dv_annex2_chief_incumbent_letter = Column(Boolean)
    dv_annex2_coordinator_recommendation = Column(Boolean)
    dv_annex2_divisional_secretary_recommendation = Column(Boolean)
    dv_annex2_approval_construction = Column(Boolean)
    dv_annex2_referral_resubmission = Column(Boolean)
    
    # Document Storage
    dv_scanned_document_path = Column(String(500))
    dv_form_id = Column(String(50), index=True)
    
    # Workflow Fields (following bhikku_regist pattern)
    dv_workflow_status = Column(String(20), server_default=text("'PENDING'"), nullable=False, index=True)
    dv_approval_status = Column(String(20))
    dv_approved_by = Column(String(25))
    dv_approved_at = Column(DateTime(timezone=True))
    dv_rejected_by = Column(String(25))
    dv_rejected_at = Column(DateTime(timezone=True))
    dv_rejection_reason = Column(String(500))
    dv_printed_at = Column(DateTime(timezone=True))
    dv_printed_by = Column(String(25))
    dv_scanned_at = Column(DateTime(timezone=True))
    dv_scanned_by = Column(String(25))
    
    dv_version = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    dv_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    dv_created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    dv_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    dv_created_by = Column(String(25))
    dv_updated_by = Column(String(25))
    dv_version_number = Column(Integer, nullable=False, server_default="1")
    
    # Relationships
    devala_lands = relationship("DevalaLand", back_populates="devala", cascade="all, delete-orphan")
