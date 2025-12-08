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


class AramaData(Base):
    __tablename__ = "aramadata"

    ar_id = Column(Integer, primary_key=True, index=True)
    ar_trn = Column(String(10), nullable=False, index=True, unique=True)
    ar_vname = Column(String(200))
    ar_addrs = Column(String(200))
    ar_mobile = Column(String(10), nullable=False)
    ar_whtapp = Column(String(10), nullable=False)
    ar_email = Column(String(200), nullable=False, index=True, unique=True)
    ar_typ = Column(String(10), nullable=False)
    ar_gndiv = Column(String(10), nullable=False)
    ar_fmlycnt = Column(Integer)
    ar_bgndate = Column(Date)
    ar_ownercd = Column(String(12), nullable=False)
    ar_parshawa = Column(String(10), nullable=False)
    ar_ssbmcode = Column(String(10))
    ar_syojakarmakrs = Column(String(100))
    ar_syojakarmdate = Column(Date)
    ar_landownrship = Column(String(150))
    ar_pralename = Column(String(50))
    ar_pralesigdate = Column(Date)
    ar_bacgrecmn = Column(String(100))
    ar_bacgrcmdate = Column(Date)
    ar_minissecrsigdate = Column(Date)
    ar_minissecrmrks = Column(String(200))
    ar_ssbmsigdate = Column(Date)
    
    # Extended Fields
    ar_province = Column(String(100))
    ar_district = Column(String(100))
    ar_divisional_secretariat = Column(String(100))
    ar_pradeshya_sabha = Column(String(100))
    ar_nikaya = Column(String(50))
    ar_viharadhipathi_name = Column(String(200))
    ar_period_established = Column(String(100))
    ar_buildings_description = Column(String(1000))
    ar_dayaka_families_count = Column(String(50))
    ar_kulangana_committee = Column(String(500))
    ar_dayaka_sabha = Column(String(500))
    ar_temple_working_committee = Column(String(500))
    ar_other_associations = Column(String(500))
    ar_land_info_certified = Column(Boolean)
    ar_inspection_report = Column(String(1000))
    ar_inspection_code = Column(String(100))
    ar_grama_niladhari_division_ownership = Column(String(200))
    ar_sanghika_donation_deed = Column(Boolean)
    ar_government_donation_deed = Column(Boolean)
    ar_government_donation_deed_in_progress = Column(Boolean)
    ar_authority_consent_attached = Column(Boolean)
    ar_recommend_new_center = Column(Boolean)
    ar_recommend_registered_temple = Column(Boolean)
    ar_annex2_recommend_construction = Column(Boolean)
    ar_annex2_land_ownership_docs = Column(Boolean)
    ar_annex2_chief_incumbent_letter = Column(Boolean)
    ar_annex2_coordinator_recommendation = Column(Boolean)
    ar_annex2_divisional_secretary_recommendation = Column(Boolean)
    ar_annex2_approval_construction = Column(Boolean)
    ar_annex2_referral_resubmission = Column(Boolean)
    
    # Document Storage
    ar_scanned_document_path = Column(String(500))
    ar_form_id = Column(String(50), index=True)
    
    # Workflow Fields (following bhikku_regist pattern)
    ar_workflow_status = Column(String(20), server_default=text("'PENDING'"), nullable=False, index=True)
    ar_approval_status = Column(String(20))
    ar_approved_by = Column(String(25))
    ar_approved_at = Column(DateTime(timezone=True))
    ar_rejected_by = Column(String(25))
    ar_rejected_at = Column(DateTime(timezone=True))
    ar_rejection_reason = Column(String(500))
    ar_printed_at = Column(DateTime(timezone=True))
    ar_printed_by = Column(String(25))
    ar_scanned_at = Column(DateTime(timezone=True))
    ar_scanned_by = Column(String(25))
    
    ar_version = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    ar_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    ar_created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ar_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    ar_created_by = Column(String(25))
    ar_updated_by = Column(String(25))
    ar_version_number = Column(Integer, nullable=False, server_default="1")
    
    # Relationships
    arama_lands = relationship("AramaLand", back_populates="arama", cascade="all, delete-orphan")
