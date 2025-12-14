# app/models/direct_bhikku_high.py
"""
Direct High Bhikku Registration Model
Combines both bhikku registration and high bhikku registration in a single table.
This allows direct high bhikku registration without needing a pre-existing bhikku record.
"""
from sqlalchemy import Boolean, Column, Integer, String, Date, TIMESTAMP, Numeric, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class DirectBhikkuHigh(Base):
    __tablename__ = "direct_bhikku_high"

    # Primary Key
    dbh_id = Column(Integer, primary_key=True, index=True)
    dbh_regn = Column(String(20), unique=True, nullable=False, index=True)
    dbh_reqstdate = Column(Date, nullable=False)
    
    # ==================== BHIKKU REGIST FIELDS ====================
    # Geographic/Birth Information
    dbh_birthpls = Column(String(50))
    dbh_province = Column(String(50))
    dbh_district = Column(String(50))
    dbh_korale = Column(String(50))
    dbh_pattu = Column(String(50))
    dbh_division = Column(String(50))
    dbh_vilage = Column(String(50))
    dbh_gndiv = Column(String(10))
    
    # Personal Information
    dbh_gihiname = Column(String(50))
    dbh_dofb = Column(Date)
    dbh_fathrname = Column(String(50))
    dbh_remarks = Column(String(100))
    
    # Status Information
    dbh_currstat = Column(String(5), nullable=False)
    dbh_effctdate = Column(Date)
    
    # Temple/Religious Information (from bhikku_regist)
    dbh_parshawaya = Column(String(10), nullable=False)
    dbh_livtemple = Column(String(10))
    dbh_mahanatemple = Column(String(10))
    dbh_mahanaacharyacd = Column(String(12))
    dbh_multi_mahanaacharyacd = Column(String(200))
    dbh_mahananame = Column(String(50))
    dbh_mahanadate = Column(Date)
    dbh_cat = Column(String(5))
    
    # Additional Religious/Administrative Fields
    dbh_viharadhipathi = Column(String(20))
    dbh_nikaya = Column(String(10))
    dbh_mahanayaka_name = Column(String(200))
    dbh_mahanayaka_address = Column(String(500))
    dbh_residence_at_declaration = Column(String(500))
    dbh_declaration_date = Column(Date)
    dbh_robing_tutor_residence = Column(String(20))
    dbh_robing_after_residence_temple = Column(String(20))
    
    # Contact Information
    dbh_mobile = Column(String(10))
    dbh_email = Column(String(50))
    dbh_fathrsaddrs = Column(String(200))
    dbh_fathrsmobile = Column(String(10))
    
    # Serial Number (from bhikku_regist)
    dbh_upasampada_serial_no = Column(String(20))
    
    # ==================== BHIKKU HIGH REGIST FIELDS ====================
    # High Bhikku Specific Fields
    dbh_samanera_serial_no = Column(String(20))
    dbh_cc_code = Column(String(5))
    dbh_higher_ordination_place = Column(String(50))
    dbh_higher_ordination_date = Column(Date)
    dbh_karmacharya_name = Column(String(100))
    dbh_upaddhyaya_name = Column(String(100))
    dbh_assumed_name = Column(String(50))
    dbh_residence_higher_ordination_trn = Column(String(50))
    dbh_residence_permanent_trn = Column(String(50))
    dbh_declaration_residence_address = Column(String(200))
    dbh_tutors_tutor_regn = Column(String(200))
    dbh_presiding_bhikshu_regn = Column(String(200))
    
    # Additional Fields
    dbh_form_id = Column(String(50))
    dbh_remarks_upasampada = Column(String(500))
    
    # ==================== WORKFLOW FIELDS ====================
    # Document Storage
    dbh_scanned_document_path = Column(String(500))
    
    # Workflow Status
    dbh_workflow_status = Column(String(20), server_default=text("'PENDING'"), nullable=False, index=True)
    dbh_approval_status = Column(String(20))
    
    # Approval Tracking
    dbh_approved_by = Column(String(25))
    dbh_approved_at = Column(TIMESTAMP)
    
    # Rejection Tracking
    dbh_rejected_by = Column(String(25))
    dbh_rejected_at = Column(TIMESTAMP)
    dbh_rejection_reason = Column(String(500))
    
    # Printing Tracking
    dbh_printed_at = Column(TIMESTAMP)
    dbh_printed_by = Column(String(25))
    
    # Scanning Tracking
    dbh_scanned_at = Column(TIMESTAMP)
    dbh_scanned_by = Column(String(25))
    
    # ==================== AUDIT FIELDS ====================
    dbh_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    dbh_is_deleted = Column(Boolean, server_default=text('false'))
    dbh_created_at = Column(TIMESTAMP, server_default=func.now())
    dbh_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    dbh_created_by = Column(String(25))
    dbh_updated_by = Column(String(25))
    dbh_version_number = Column(Integer, server_default=text('1'))
    
    # Location-based access control
    dbh_created_by_district = Column(String(10), index=True)
    
    # ==================== RELATIONSHIPS ====================
    # Geographic relationships
    province_rel = relationship(
        "Province",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_province) == Province.cp_code",
        viewonly=True,
        lazy="select"
    )
    district_rel = relationship(
        "District",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_district) == District.dd_dcode",
        viewonly=True,
        lazy="select"
    )
    division_rel = relationship(
        "DivisionalSecretariat",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_division) == DivisionalSecretariat.dv_dvcode",
        viewonly=True,
        lazy="select"
    )
    gndiv_rel = relationship(
        "Gramasewaka",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_gndiv) == Gramasewaka.gn_gnc",
        viewonly=True,
        lazy="select"
    )
    
    # Status and administrative relationships
    status_rel = relationship(
        "StatusData",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_currstat) == StatusData.st_statcd",
        viewonly=True,
        lazy="select"
    )
    parshawaya_rel = relationship(
        "ParshawaData",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_parshawaya) == ParshawaData.pr_prn",
        viewonly=True,
        lazy="select"
    )
    category_rel = relationship(
        "BhikkuCategory",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_cat) == BhikkuCategory.cc_code",
        viewonly=True,
        lazy="select"
    )
    nikaya_rel = relationship(
        "NikayaData",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_nikaya) == NikayaData.nk_nkn",
        viewonly=True,
        lazy="select"
    )
    
    # Temple/Vihara relationships
    livtemple_rel = relationship(
        "ViharaData",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_livtemple) == ViharaData.vh_trn",
        viewonly=True,
        lazy="select"
    )
    mahanatemple_rel = relationship(
        "ViharaData",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_mahanatemple) == ViharaData.vh_trn",
        viewonly=True,
        lazy="select"
    )
    robing_tutor_residence_rel = relationship(
        "ViharaData",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_robing_tutor_residence) == ViharaData.vh_trn",
        viewonly=True,
        lazy="select"
    )
    robing_after_residence_temple_rel = relationship(
        "ViharaData",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_robing_after_residence_temple) == ViharaData.vh_trn",
        viewonly=True,
        lazy="select"
    )
    residence_higher_ordination_rel = relationship(
        "ViharaData",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_residence_higher_ordination_trn) == ViharaData.vh_trn",
        viewonly=True,
        lazy="select"
    )
    residence_permanent_rel = relationship(
        "ViharaData",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_residence_permanent_trn) == ViharaData.vh_trn",
        viewonly=True,
        lazy="select"
    )
    
    # Bhikku relationships (for references to other bhikkus)
    mahanaacharyacd_rel = relationship(
        "Bhikku",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_mahanaacharyacd) == remote(Bhikku.br_regn)",
        viewonly=True,
        lazy="select"
    )
    viharadhipathi_rel = relationship(
        "Bhikku",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_viharadhipathi) == remote(Bhikku.br_regn)",
        viewonly=True,
        lazy="select"
    )
    mahanayaka_rel = relationship(
        "Bhikku",
        primaryjoin="foreign(DirectBhikkuHigh.dbh_mahanayaka_name) == remote(Bhikku.br_regn)",
        viewonly=True,
        lazy="select"
    )
