# app/models/silmatha_id_card.py
from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class SilmathaIDCard(Base):
    """
    Silmatha ID Card model - comprehensive fields matching the Silmatha ID Card application form.
    
    This model includes:
    - Auto-generated form number (SIC{YEAR}{SEQUENCE})
    - Foreign key to silmatha_regist table
    - Complete personal, robing, and ordination details
    - Stay history as JSON array
    - Workflow status and approval tracking
    - File uploads: left thumbprint and applicant photo
    """
    __tablename__ = "silmatha_id_card"

    # --- Primary Key ---
    sic_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # --- Auto-generated Form Number (Unique) ---
    sic_form_no = Column(String(20), nullable=False, unique=True, index=True)
    # Format: SIC{YEAR}{SEQUENCE} e.g. SIC2025000001
    
    # --- Foreign Key to silmatha_regist ---
    sic_sil_regn = Column(String(20), ForeignKey("silmatha_regist.sil_regn"), nullable=False, unique=True, index=True)
    
    # --- Top Section: Divisional Secretariat & District ---
    sic_divisional_secretariat = Column(String(100), nullable=True)
    sic_district = Column(String(100), nullable=True)
    
    # --- 01. Declaration Full Name ---
    sic_full_silmatha_name = Column(String(200), nullable=False)
    sic_title_post = Column(String(100), nullable=True)
    
    # --- 02. As per birth certificate ---
    sic_lay_name_full = Column(String(200), nullable=False)
    sic_dob = Column(Date, nullable=False)
    sic_birth_place = Column(String(200), nullable=True)
    
    # --- 03. Ordination details ---
    sic_robing_date = Column(Date, nullable=True)
    sic_robing_place = Column(String(200), nullable=True)
    sic_robing_nikaya = Column(String(100), nullable=True)
    sic_robing_parshawaya = Column(String(100), nullable=True)
    
    # --- 04. Registration numbers & higher ordination ---
    sic_samaneri_reg_no = Column(String(50), nullable=True)
    sic_dasa_sil_mata_reg_no = Column(String(50), nullable=True)
    sic_higher_ord_date = Column(Date, nullable=True)
    
    # --- 05. Name at Higher Ordinance ---
    sic_higher_ord_name = Column(String(200), nullable=True)
    
    # --- 06. Permanent residence ---
    sic_perm_residence = Column(Text, nullable=True)
    
    # --- 07. National ID ---
    sic_national_id = Column(String(20), nullable=True)
    
    # --- 08. Places stayed so far (JSON array) ---
    sic_stay_history = Column(JSON, nullable=True)
    # Format: [{"temple_name": "...", "temple_address": "...", "from_date": "YYYY-MM-DD", "to_date": "YYYY-MM-DD"}]
    
    # --- File Upload URLs ---
    sic_left_thumbprint_url = Column(String, nullable=True)
    sic_applicant_photo_url = Column(String, nullable=True)
    
    # --- Workflow Status ---
    sic_workflow_status = Column(String(50), nullable=False, default="PENDING")
    # Possible values: PENDING, APPROVED, REJECTED, PRINTING_COMPLETE, COMPLETED
    
    # --- Approval/Rejection Tracking ---
    sic_approved_by = Column(String(100), nullable=True)
    sic_approved_at = Column(DateTime(timezone=True), nullable=True)
    sic_rejection_reason = Column(Text, nullable=True)
    sic_rejected_by = Column(String(100), nullable=True)
    sic_rejected_at = Column(DateTime(timezone=True), nullable=True)
    
    # --- Printing Tracking ---
    sic_printed_by = Column(String(100), nullable=True)
    sic_printed_at = Column(DateTime(timezone=True), nullable=True)
    
    # --- Audit Fields ---
    sic_created_by = Column(String(100), nullable=True)
    sic_created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sic_updated_by = Column(String(100), nullable=True)
    sic_updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # --- Relationship to silmatha_regist ---
    silmatha_regist = relationship("SilmathaRegist", foreign_keys=[sic_sil_regn])


