# app/models/bhikku.py
from sqlalchemy import Boolean, Column, Integer, String, Date, TIMESTAMP, Numeric, text
from sqlalchemy.orm import relationship, foreign, remote
from sqlalchemy.sql import func
from app.db.base import Base

class Bhikku(Base):
    __tablename__ = "bhikku_regist"

    br_id = Column(Integer, primary_key=True, index=True)
    br_regn = Column(String(20), unique=True, nullable=False, index=True)
    br_reqstdate = Column(Date, nullable=False)
    
    # Geographic/Birth Information
    br_birthpls = Column(String(50))
    br_province = Column(String(50))
    br_district = Column(String(50))
    br_korale = Column(String(50))  # Optional
    br_pattu = Column(String(50))  # Optional
    br_division = Column(String(50))  # Optional - District
    br_vilage = Column(String(50))  # Optional
    br_gndiv = Column(String(10))  # Optional - GN Division (changed from nullable=False)
    
    # Personal Information
    br_gihiname = Column(String(50))
    br_dofb = Column(Date)
    br_fathrname = Column(String(50))
    br_remarks = Column(String(100))
    
    # Status Information
    br_currstat = Column(String(5), nullable=False)
    br_effctdate = Column(Date)
    
    # Temple/Religious Information
    br_parshawaya = Column(String(10), nullable=False)
    br_livtemple = Column(String(10))  # Removed - not in payload
    br_mahanatemple = Column(String(10))  # Made optional
    br_mahanaacharyacd = Column(String(12))  # Made optional
    br_multi_mahanaacharyacd = Column(String(200))
    br_mahananame = Column(String(50))
    br_mahanadate = Column(Date)
    br_cat = Column(String(5))
    
    # Additional Religious/Administrative Fields
    br_viharadhipathi = Column(String(20))
    br_nikaya = Column(String(10))
    br_mahanayaka_name = Column(String(200))
    br_mahanayaka_address = Column(String(500))
    br_residence_at_declaration = Column(String(500))
    br_declaration_date = Column(Date)
    br_robing_tutor_residence = Column(String(20))
    br_robing_after_residence_temple = Column(String(20))
    
    # Contact Information
    br_mobile = Column(String(10))
    br_email = Column(String(50))
    br_fathrsaddrs = Column(String(200))
    br_fathrsmobile = Column(String(10))
    
    # Serial Number
    br_upasampada_serial_no = Column(String(20))
    
    # Form ID
    br_form_id = Column(String(50))
    
    # Document Storage
    br_scanned_document_path = Column(String(500))
    
    # Workflow Fields
    br_workflow_status = Column(String(20), server_default=text("'PENDING'"), nullable=False, index=True)
    br_approval_status = Column(String(20))
    br_approved_by = Column(String(25))
    br_approved_at = Column(TIMESTAMP)
    br_rejected_by = Column(String(25))
    br_rejected_at = Column(TIMESTAMP)
    br_rejection_reason = Column(String(500))
    br_printed_at = Column(TIMESTAMP)
    br_printed_by = Column(String(25))
    br_scanned_at = Column(TIMESTAMP)
    br_scanned_by = Column(String(25))
    
    # Reprint Workflow Fields
    br_reprint_status = Column(String(20))
    br_reprint_requested_by = Column(String(25))
    br_reprint_requested_at = Column(TIMESTAMP)
    br_reprint_request_reason = Column(String(500))
    br_reprint_amount = Column(Numeric(10, 2))
    br_reprint_remarks = Column(String(500))
    br_reprint_approved_by = Column(String(25))
    br_reprint_approved_at = Column(TIMESTAMP)
    br_reprint_rejected_by = Column(String(25))
    br_reprint_rejected_at = Column(TIMESTAMP)
    br_reprint_rejection_reason = Column(String(500))
    br_reprint_completed_by = Column(String(25))
    br_reprint_completed_at = Column(TIMESTAMP)
    
    # Audit Fields
    br_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    br_is_deleted = Column(Boolean, server_default=text('false'))
    br_created_at = Column(TIMESTAMP, server_default=func.now())
    br_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    br_created_by = Column(String(25))
    br_updated_by = Column(String(25))
    br_version_number = Column(Integer, server_default=text('1'))
    
    # Location-based access control - stores district code of creating user
    br_created_by_district = Column(String(10), index=True)
    
    # Relationships
    province_rel = relationship("Province", primaryjoin="foreign(Bhikku.br_province) == Province.cp_code", viewonly=True, lazy="joined")
    district_rel = relationship("District", primaryjoin="foreign(Bhikku.br_district) == District.dd_dcode", viewonly=True, lazy="joined")
    division_rel = relationship("DivisionalSecretariat", primaryjoin="foreign(Bhikku.br_division) == DivisionalSecretariat.dv_dvcode", viewonly=True, lazy="joined")
    gndiv_rel = relationship("Gramasewaka", primaryjoin="foreign(Bhikku.br_gndiv) == Gramasewaka.gn_gnc", viewonly=True, lazy="joined")
    status_rel = relationship("StatusData", primaryjoin="foreign(Bhikku.br_currstat) == StatusData.st_statcd", viewonly=True, lazy="joined")
    parshawaya_rel = relationship("ParshawaData", primaryjoin="foreign(Bhikku.br_parshawaya) == ParshawaData.pr_prn", viewonly=True, lazy="joined")
    livtemple_rel = relationship("ViharaData", primaryjoin="foreign(Bhikku.br_livtemple) == ViharaData.vh_trn", viewonly=True, lazy="joined")
    mahanatemple_rel = relationship("ViharaData", primaryjoin="foreign(Bhikku.br_mahanatemple) == ViharaData.vh_trn", viewonly=True, lazy="joined")
    mahanaacharyacd_rel = relationship("Bhikku", primaryjoin="foreign(Bhikku.br_mahanaacharyacd) == remote(Bhikku.br_regn)", viewonly=True, lazy="joined")
    category_rel = relationship("BhikkuCategory", primaryjoin="foreign(Bhikku.br_cat) == BhikkuCategory.cc_code", viewonly=True, lazy="joined")
    viharadhipathi_rel = relationship("Bhikku", primaryjoin="foreign(Bhikku.br_viharadhipathi) == remote(Bhikku.br_regn)", viewonly=True, lazy="joined")
    nikaya_rel = relationship("NikayaData", primaryjoin="foreign(Bhikku.br_nikaya) == NikayaData.nk_nkn", viewonly=True, lazy="joined")
    mahanayaka_rel = relationship("Bhikku", primaryjoin="foreign(Bhikku.br_mahanayaka_name) == remote(Bhikku.br_regn)", viewonly=True, lazy="joined")
    robing_tutor_residence_rel = relationship("ViharaData", primaryjoin="foreign(Bhikku.br_robing_tutor_residence) == ViharaData.vh_trn", viewonly=True, lazy="joined")
    robing_after_residence_temple_rel = relationship("ViharaData", primaryjoin="foreign(Bhikku.br_robing_after_residence_temple) == ViharaData.vh_trn", viewonly=True, lazy="joined")
