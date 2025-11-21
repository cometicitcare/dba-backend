# app/models/silmatha_regist.py
from sqlalchemy import Boolean, Column, Integer, String, Date, TIMESTAMP, Numeric, text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class SilmathaRegist(Base):
    __tablename__ = "silmatha_regist"

    sil_id = Column(Integer, primary_key=True, index=True)
    sil_regn = Column(String(20), unique=True, nullable=False, index=True)
    sil_reqstdate = Column(Date, nullable=False)
    
    # Personal Information
    sil_gihiname = Column(String(50))
    sil_dofb = Column(Date)
    sil_fathrname = Column(String(50))
    sil_email = Column(String(50))
    sil_mobile = Column(String(10))
    sil_fathrsaddrs = Column(String(200))
    sil_fathrsmobile = Column(String(10))
    
    # Geographic/Birth Information
    sil_birthpls = Column(String(50))
    sil_province = Column(String(50), ForeignKey('cmm_province.cp_code'))
    sil_district = Column(String(50), ForeignKey('cmm_districtdata.dd_dcode'))
    sil_korale = Column(String(50))
    sil_pattu = Column(String(50))
    sil_division = Column(String(50), ForeignKey('cmm_dvsec.dv_dvcode'))
    sil_vilage = Column(String(50))
    sil_gndiv = Column(String(10), ForeignKey('cmm_gndata.gn_gnc'), nullable=False)
    
    # Temple/Religious Information
    sil_viharadhipathi = Column(String(20), ForeignKey('bhikku_regist.br_regn'))
    sil_cat = Column(String(5), ForeignKey('cmm_cat.cc_code'))
    sil_currstat = Column(String(5), ForeignKey('statusdata.st_statcd'), nullable=False)
    sil_declaration_date = Column(Date)
    sil_remarks = Column(String(100))
    sil_mahanadate = Column(Date)
    sil_mahananame = Column(String(50))
    sil_mahanaacharyacd = Column(String(12))  # Can be comma-separated br_regn values
    sil_robing_tutor_residence = Column(String(20), ForeignKey('vihaddata.vh_trn'))
    sil_mahanatemple = Column(String(10), ForeignKey('vihaddata.vh_trn'))
    sil_robing_after_residence_temple = Column(String(20), ForeignKey('vihaddata.vh_trn'))
    
    # Document Storage
    sil_scanned_document_path = Column(String(500))
    
    # Workflow Fields
    sil_workflow_status = Column(String(20), server_default=text("'PENDING'"), nullable=False, index=True)
    sil_approval_status = Column(String(20))
    sil_approved_by = Column(String(25))
    sil_approved_at = Column(TIMESTAMP)
    sil_rejected_by = Column(String(25))
    sil_rejected_at = Column(TIMESTAMP)
    sil_rejection_reason = Column(String(500))
    sil_printed_at = Column(TIMESTAMP)
    sil_printed_by = Column(String(25))
    sil_scanned_at = Column(TIMESTAMP)
    sil_scanned_by = Column(String(25))
    
    # Reprint Workflow Fields
    sil_reprint_status = Column(String(20))
    sil_reprint_form_no = Column(String(50), index=True)
    sil_reprint_requested_by = Column(String(25))
    sil_reprint_requested_at = Column(TIMESTAMP)
    sil_reprint_request_reason = Column(String(500))
    sil_reprint_amount = Column(Numeric(10, 2))
    sil_reprint_remarks = Column(String(500))
    sil_reprint_approved_by = Column(String(25))
    sil_reprint_approved_at = Column(TIMESTAMP)
    sil_reprint_rejected_by = Column(String(25))
    sil_reprint_rejected_at = Column(TIMESTAMP)
    sil_reprint_rejection_reason = Column(String(500))
    sil_reprint_completed_by = Column(String(25))
    sil_reprint_completed_at = Column(TIMESTAMP)
    
    # Audit Fields
    sil_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    sil_is_deleted = Column(Boolean, server_default=text('false'))
    sil_created_at = Column(TIMESTAMP, server_default=func.now())
    sil_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    sil_created_by = Column(String(25))
    sil_updated_by = Column(String(25))
    sil_version_number = Column(Integer, server_default=text('1'))
    
    # Relationships - SQLAlchemy ORM relationships for nested responses
    province_rel = relationship("Province", foreign_keys=[sil_province], lazy="joined")
    district_rel = relationship("District", foreign_keys=[sil_district], lazy="joined")
    division_rel = relationship("DivisionalSecretariat", foreign_keys=[sil_division], lazy="joined")
    gndiv_rel = relationship("Gramasewaka", foreign_keys=[sil_gndiv], lazy="joined")
    viharadhipathi_rel = relationship("Bhikku", foreign_keys=[sil_viharadhipathi], lazy="joined")
    category_rel = relationship("BhikkuCategory", foreign_keys=[sil_cat], lazy="joined")
    status_rel = relationship("StatusData", foreign_keys=[sil_currstat], lazy="joined")
    robing_tutor_residence_rel = relationship("ViharaData", foreign_keys=[sil_robing_tutor_residence], lazy="joined")
    mahanatemple_rel = relationship("ViharaData", foreign_keys=[sil_mahanatemple], lazy="joined")
    robing_after_residence_temple_rel = relationship("ViharaData", foreign_keys=[sil_robing_after_residence_temple], lazy="joined")

