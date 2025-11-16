# app/models/silmatha_regist.py
from sqlalchemy import Boolean, Column, Integer, String, Date, TIMESTAMP, text
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
    sil_province = Column(String(50))
    sil_district = Column(String(50))
    sil_korale = Column(String(50))
    sil_pattu = Column(String(50))
    sil_division = Column(String(50))
    sil_vilage = Column(String(50))
    sil_gndiv = Column(String(10), nullable=False)
    
    # Temple/Religious Information
    sil_viharadhipathi = Column(String(20))
    sil_cat = Column(String(5))
    sil_currstat = Column(String(5), nullable=False)
    sil_declaration_date = Column(Date)
    sil_remarks = Column(String(100))
    sil_mahanadate = Column(Date)
    sil_mahananame = Column(String(50))
    sil_mahanaacharyacd = Column(String(12))
    sil_robing_tutor_residence = Column(String(20))
    sil_mahanatemple = Column(String(10))
    sil_robing_after_residence_temple = Column(String(20))
    
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
    sil_reprint_requested_by = Column(String(25))
    sil_reprint_requested_at = Column(TIMESTAMP)
    sil_reprint_request_reason = Column(String(500))
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
    
    # Relationships can be added here if needed
