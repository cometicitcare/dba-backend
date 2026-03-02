from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.db.base import Base


class ViharaData(Base):
    __tablename__ = "vihaddata"

    vh_id = Column(Integer, primary_key=True, index=True)
    vh_trn = Column(String(10), nullable=False, index=True, unique=True)
    vh_vname = Column(String(200))
    vh_addrs = Column(String(200))
    vh_mobile = Column(String(10), nullable=True)
    vh_whtapp = Column(String(10), nullable=True)
    vh_email = Column(String(200), nullable=True, index=True, unique=True)
    vh_typ = Column(String(10), nullable=True)
    vh_gndiv = Column(String(10), ForeignKey('cmm_gndata.gn_gnc', ondelete='RESTRICT'), nullable=True)
    vh_fmlycnt = Column(Integer)
    vh_bgndate = Column(Date)
    vh_ownercd = Column(String(12), nullable=True)
    vh_parshawa = Column(String(10), nullable=True)
    vh_ssbmcode = Column(String(10))
    vh_syojakarmakrs = Column(String(100))
    vh_syojakarmdate = Column(Date)
    vh_landownrship = Column(String(150))
    vh_pralename = Column(String(50))
    vh_pralesigdate = Column(Date)
    vh_bacgrecmn = Column(String(100))
    vh_bacgrcmdate = Column(Date)
    vh_minissecrsigdate = Column(Date)
    vh_minissecrmrks = Column(String(200))
    vh_ssbmsigdate = Column(Date)
    vh_mahanayake_date = Column(Date)
    vh_mahanayake_letter_nu = Column(String(50))
    vh_mahanayake_remarks = Column(String(500))
    
    # Registration status
    vh_is_registered = Column(Boolean, nullable=False, server_default=text("true"))
    vh_unregistered_reason = Column(String(500), nullable=True)

    # Stage F / Stage B: Bypass Toggle Fields
    vh_bypass_no_detail = Column(Boolean, nullable=True, server_default=text("false"))
    vh_bypass_no_chief = Column(Boolean, nullable=True, server_default=text("false"))
    vh_bypass_ltr_cert = Column(Boolean, nullable=True, server_default=text("false"))
    # Stage B: Bypass Audit Columns
    vh_bypass_no_detail_by = Column(String(25), nullable=True)
    vh_bypass_no_detail_at = Column(DateTime, nullable=True)
    vh_bypass_no_chief_by = Column(String(25), nullable=True)
    vh_bypass_no_chief_at = Column(DateTime, nullable=True)
    vh_bypass_ltr_cert_by = Column(String(25), nullable=True)
    vh_bypass_ltr_cert_at = Column(DateTime, nullable=True)
    vh_bypass_unlocked_by = Column(String(25), nullable=True)
    vh_bypass_unlocked_at = Column(DateTime, nullable=True)
    
    # Stage F: Historical Period Fields
    vh_period_era = Column(String(50))    # "AD" | "BC" | "BUDDHIST_ERA"
    vh_period_year = Column(String(10))   # free text e.g. '1890', '~600'
    vh_period_month = Column(String(2))   # 01-12
    vh_period_day = Column(String(2))     # 01-31
    vh_period_notes = Column(String(500)) # Optional historical notes
    
    # Stage F: Date Fields
    viharadhipathi_date = Column(Date)  # Viharadhipathi appointment date
    
    # File / Code fields
    vh_file_number = Column(String(50))
    vh_vihara_code = Column(String(50))
    
    # Extended Fields
    vh_province = Column(String(100), ForeignKey('cmm_province.cp_code', ondelete='SET NULL'))
    vh_district = Column(String(100), ForeignKey('cmm_districtdata.dd_dcode', ondelete='SET NULL'))
    vh_divisional_secretariat = Column(String(100), ForeignKey('cmm_dvsec.dv_dvcode', ondelete='SET NULL'))
    vh_pradeshya_sabha = Column(String(100))  # No reference table available
    vh_nikaya = Column(String(50), ForeignKey('cmm_nikayadata.nk_nkn', ondelete='SET NULL'))
    vh_viharadhipathi_name = Column(String(200))
    vh_viharadhipathi_regn = Column(String(50))
    vh_period_established = Column(String(100))
    vh_buildings_description = Column(String(1000))
    vh_dayaka_families_count = Column(String(50))
    vh_kulangana_committee = Column(String(500))
    vh_dayaka_sabha = Column(String(500))
    vh_temple_working_committee = Column(String(500))
    vh_other_associations = Column(String(500))
    vh_land_info_certified = Column(Boolean)
    vh_resident_bhikkhus_certified = Column(Boolean)
    vh_inspection_report = Column(String(1000))
    vh_inspection_code = Column(String(100))
    vh_grama_niladhari_division_ownership = Column(String(200))
    vh_sanghika_donation_deed = Column(Boolean)
    vh_government_donation_deed = Column(Boolean)
    vh_government_donation_deed_in_progress = Column(Boolean)
    vh_authority_consent_attached = Column(Boolean)
    vh_recommend_new_center = Column(Boolean)
    vh_recommend_registered_temple = Column(Boolean)
    vh_annex2_recommend_construction = Column(Boolean)
    vh_annex2_land_ownership_docs = Column(Boolean)
    vh_annex2_chief_incumbent_letter = Column(Boolean)
    vh_annex2_coordinator_recommendation = Column(Boolean)
    vh_annex2_divisional_secretary_recommendation = Column(Boolean)
    vh_annex2_approval_construction = Column(Boolean)
    vh_annex2_referral_resubmission = Column(Boolean)
    
    # Document Storage - Stage 1 and Stage 2 documents
    vh_scanned_document_path = Column(String(500))  # Stage 1 scanned document
    vh_stage2_document_path = Column(String(500))   # Stage 2 scanned document
    vh_form_id = Column(String(50), index=True)
    
    # Workflow Fields - Staged workflow
    # Main workflow status: S1_PENDING, S1_PRINTING, S1_PEND_APPROVAL, S1_APPROVED, S1_REJECTED,
    #                       S2_PENDING, S2_PEND_APPROVAL, COMPLETED, REJECTED
    vh_workflow_status = Column(String(25), server_default=text("'S1_PENDING'"), nullable=False, index=True)
    vh_approval_status = Column(String(20))
    
    # Stage 1 workflow fields
    vh_s1_printed_at = Column(DateTime(timezone=True))
    vh_s1_printed_by = Column(String(25))
    vh_s1_scanned_at = Column(DateTime(timezone=True))
    vh_s1_scanned_by = Column(String(25))
    vh_s1_approved_by = Column(String(25))
    vh_s1_approved_at = Column(DateTime(timezone=True))
    vh_s1_rejected_by = Column(String(25))
    vh_s1_rejected_at = Column(DateTime(timezone=True))
    vh_s1_rejection_reason = Column(String(500))
    
    # Stage 2 workflow fields
    vh_s2_scanned_at = Column(DateTime(timezone=True))
    vh_s2_scanned_by = Column(String(25))
    vh_s2_approved_by = Column(String(25))
    vh_s2_approved_at = Column(DateTime(timezone=True))
    vh_s2_rejected_by = Column(String(25))
    vh_s2_rejected_at = Column(DateTime(timezone=True))
    vh_s2_rejection_reason = Column(String(500))
    
    # Legacy fields (kept for backward compatibility)
    vh_approved_by = Column(String(25))
    vh_approved_at = Column(DateTime(timezone=True))
    vh_rejected_by = Column(String(25))
    vh_rejected_at = Column(DateTime(timezone=True))
    vh_rejection_reason = Column(String(500))
    vh_printed_at = Column(DateTime(timezone=True))
    vh_printed_by = Column(String(25))
    vh_scanned_at = Column(DateTime(timezone=True))
    vh_scanned_by = Column(String(25))
    
    vh_version = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    vh_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    vh_created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    vh_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    vh_created_by = Column(String(25))
    vh_updated_by = Column(String(25))
    vh_version_number = Column(Integer, nullable=False, server_default="1")
    
    # Relationships
    temple_lands = relationship("TempleLand", back_populates="vihara", cascade="all, delete-orphan")
    resident_bhikkhus = relationship("ResidentBhikkhu", back_populates="vihara", cascade="all, delete-orphan")
    vihara_lands = relationship("ViharaLand", back_populates="vihara", cascade="all, delete-orphan")
    
    # Foreign key relationships - only for fields with ForeignKey constraints
    province_info = relationship("Province", foreign_keys=[vh_province], lazy="select")
    district_info = relationship("District", foreign_keys=[vh_district], lazy="select")
    divisional_secretariat_info = relationship("DivisionalSecretariat", foreign_keys=[vh_divisional_secretariat], lazy="select")
    gn_division_info = relationship("Gramasewaka", foreign_keys=[vh_gndiv], lazy="select")
    nikaya_info = relationship("NikayaData", foreign_keys=[vh_nikaya], lazy="select")
    
    # Additional FK relationships (DB-level FKs exist, using explicit primaryjoin)
    # Changed from lazy="joined" to lazy="select" to prevent circular joins
    parshawa_info = relationship(
        "ParshawaData",
        primaryjoin="ViharaData.vh_parshawa == ParshawaData.pr_prn",
        foreign_keys="[ViharaData.vh_parshawa]",
        lazy="select",
        viewonly=True,
    )
    ssbm_info = relationship(
        "SasanarakshakaBalaMandalaya",
        primaryjoin="ViharaData.vh_ssbmcode == SasanarakshakaBalaMandalaya.sr_ssbmcode",
        foreign_keys="[ViharaData.vh_ssbmcode]",
        lazy="select",
        viewonly=True,
    )
    owner_bhikku_info = relationship(
        "Bhikku",
        primaryjoin="ViharaData.vh_ownercd == Bhikku.br_regn",
        foreign_keys="[ViharaData.vh_ownercd]",
        lazy="select",
        viewonly=True,
    )
