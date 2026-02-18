# app/models/bhikku_id_card.py
from sqlalchemy import Boolean, Column, Integer, String, Date, TIMESTAMP, Text, ForeignKey, JSON, text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class BhikkuIDCard(Base):
    """
    Bhikku ID Card Model - Stores all information from the Bhikku ID application form.
    
    This table is linked to bhikku_regist via br_regn (foreign key).
    Each Bhikku can have one ID card record.
    """
    __tablename__ = "bhikku_id_card"

    # Primary Key
    bic_id = Column(Integer, primary_key=True, index=True, comment="Primary key")
    
    # Foreign Key to bhikku_regist table (br_regn)
    bic_br_regn = Column(
        String(20), 
        ForeignKey("bhikku_regist.br_regn", ondelete="CASCADE"),
        nullable=False, 
        unique=True,  # One ID card per Bhikku
        index=True,
        comment="Bhikku registration number (FK to bhikku_regist.br_regn)"
    )
    
    # Auto-generated Form Number - UNIQUE
    bic_form_no = Column(
        String(30), 
        unique=True, 
        nullable=False, 
        index=True,
        comment="Auto-generated unique form number (e.g., FORM-2025-0001)"
    )
    
    # Category
    bic_category = Column(String(100), comment="Category of ID card")

    # Top Section Fields
    bic_divisional_secretariat = Column(String(100), comment="Division (English)")
    bic_division_s = Column(String(100), comment="Division (Sinhala)")
    bic_district = Column(String(100), comment="District (English)")
    bic_district_s = Column(String(100), comment="District (Sinhala)")

    # 01. Declaration Full Name
    bic_full_bhikku_name = Column(String(200), nullable=False, comment="Full Bhikku Name (English / nameE)")
    bic_name_s = Column(String(200), comment="Full Bhikku Name (Sinhala / nameS)")
    bic_title_post = Column(String(100), comment="Title/Post (English / padawiyaE)")
    bic_padawiya_s = Column(String(100), comment="Title/Post (Sinhala / padawiyaS)")
    
    # 02. As per birth certificate
    bic_lay_name_full = Column(String(200), nullable=False, comment="Gihi/Lay Name in full")
    bic_dob = Column(Date, nullable=False, comment="Date of Birth")
    bic_birth_place = Column(String(200), comment="Place of Birth")
    
    # 03. Ordination details
    bic_robing_date = Column(Date, comment="Date of Robing")
    bic_robing_place = Column(String(200), comment="Place of Robing")
    bic_robing_nikaya = Column(String(100), comment="Nikaya (English / nikayaE)")
    bic_nikaya_s = Column(String(100), comment="Nikaya (Sinhala / nikayaS)")
    bic_robing_parshawaya = Column(String(100), comment="Parshwaya (English / parshwayaE)")
    bic_parshwaya_s = Column(String(100), comment="Parshwaya (Sinhala / parshwayaS)")

    # Temple Name (current/main temple)
    bic_temple_name_e = Column(String(200), comment="Temple Name (English / templeE)")
    bic_temple_name_s = Column(String(200), comment="Temple Name (Sinhala / templeS)")
    
    # 04. Registration numbers & higher ordination
    bic_samanera_reg_no = Column(String(50), comment="Samanera Registration Number")
    bic_upasampada_reg_no = Column(String(50), comment="Upasampada Registration Number")
    bic_higher_ord_date = Column(Date, comment="Date of Higher Ordinance")
    
    # 05. Name at Higher Ordinance
    bic_higher_ord_name = Column(String(200), comment="Name taken at Higher Ordinance")
    
    # 06. Permanent residence
    bic_perm_residence = Column(Text, comment="Permanent residence address")
    
    # 07. National ID
    bic_national_id = Column(String(20), comment="National ID Card Number")
    
    # 08. Places stayed so far (JSONB array of objects)
    bic_stay_history = Column(
        JSON,
        comment="Array of stay history: [{temple_name, temple_address, from_date, to_date}]"
    )
    
    # Issue Date
    bic_issue_date = Column(Date, comment="ID Card issue date")

    # File Upload Fields (storing file paths on disk)
    bic_left_thumbprint_url = Column(
        String(500), 
        comment="File path for left thumbprint image"
    )
    bic_applicant_photo_url = Column(
        String(500), 
        comment="File path for applicant photo (3cm x 2.5cm)"
    )
    bic_signature_url = Column(
        Boolean,
        server_default=text('false'),
        nullable=False,
        comment="Whether applicant signature has been uploaded (true/false)"
    )
    bic_authorized_signature_url = Column(
        Boolean,
        server_default=text('false'),
        nullable=False,
        comment="Whether authorized signature has been uploaded (true/false)"
    )
    
    # Workflow Status - defaults to PENDING
    bic_workflow_status = Column(
        String(20), 
        server_default=text("'PENDING'"), 
        nullable=False, 
        index=True,
        comment="Workflow status: PENDING, APPROVED, REJECTED, PRINTING_COMPLETE, COMPLETED"
    )
    
    # Approval/Rejection tracking
    bic_approved_by = Column(String(50), comment="User who approved the ID card")
    bic_approved_at = Column(TIMESTAMP, comment="Timestamp of approval")
    bic_rejected_by = Column(String(50), comment="User who rejected the ID card")
    bic_rejected_at = Column(TIMESTAMP, comment="Timestamp of rejection")
    bic_rejection_reason = Column(Text, comment="Reason for rejection")
    
    # Print tracking
    bic_printed_by = Column(String(50), comment="User who marked as printed")
    bic_printed_at = Column(TIMESTAMP, comment="Timestamp when marked as printed")
    
    # Completion tracking
    bic_completed_by = Column(String(50), comment="User who marked as completed")
    bic_completed_at = Column(TIMESTAMP, comment="Timestamp when marked as completed")
    
    # Audit Fields
    bic_is_deleted = Column(Boolean, server_default=text('false'), nullable=False)
    bic_created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    bic_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    bic_created_by = Column(String(50), comment="User who created the record")
    bic_updated_by = Column(String(50), comment="User who last updated the record")
    bic_version_number = Column(Integer, server_default=text('1'), nullable=False)
    
    # Relationship to Bhikku model (optional - for ORM navigation)
    bhikku = relationship("Bhikku", backref="id_card", foreign_keys=[bic_br_regn])
