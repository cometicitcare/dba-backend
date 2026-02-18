# app/models/sasanarakshana_regist.py
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class SasanarakshanaRegist(Base):
    """
    Model for Sasanaarakshana Registration Management (sasanarakshana_regist table).
    Stores information about Sasanaarakshana organization registrations including
    temple details, bank details, and committee members.
    """
    __tablename__ = "sasanarakshana_regist"

    # Primary Key
    sar_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Temple / Organization Details — FK to vihaddata.vh_trn
    sar_temple_trn = Column(String(255), ForeignKey("vihaddata.vh_trn", ondelete="RESTRICT"), nullable=False, comment="Vihara TRN (FK to vihaddata)")
    temple = relationship("ViharaData", primaryjoin="foreign(SasanarakshanaRegist.sar_temple_trn) == ViharaData.vh_trn", viewonly=True, lazy="joined")
    sar_temple_address = Column(String(500), nullable=True, comment="Temple Address")
    sar_mandala_name = Column(String(255), nullable=True, comment="Mandala Name")

    # Bank Details
    sar_bank_name = Column(String(255), nullable=True, comment="Bank Name")
    sar_account_number = Column(String(100), nullable=True, comment="Bank Account Number")

    # Committee Members
    sar_president_name = Column(String(255), nullable=True, comment="President Name")
    sar_deputy_president_name = Column(String(255), nullable=True, comment="Deputy President Name")
    sar_vice_president_1_name = Column(String(255), nullable=True, comment="Vice President 1 Name")
    sar_vice_president_2_name = Column(String(255), nullable=True, comment="Vice President 2 Name")
    sar_general_secretary_name = Column(String(255), nullable=True, comment="General Secretary Name")
    sar_deputy_secretary_name = Column(String(255), nullable=True, comment="Deputy Secretary Name")
    sar_treasurer_name = Column(String(255), nullable=True, comment="Treasurer Name")
    sar_committee_member_1 = Column(String(255), nullable=True, comment="Committee Member 1")
    sar_committee_member_2 = Column(String(255), nullable=True, comment="Committee Member 2")
    sar_committee_member_3 = Column(String(255), nullable=True, comment="Committee Member 3")
    sar_committee_member_4 = Column(String(255), nullable=True, comment="Committee Member 4")
    sar_committee_member_5 = Column(String(255), nullable=True, comment="Committee Member 5")
    sar_committee_member_6 = Column(String(255), nullable=True, comment="Committee Member 6")
    sar_committee_member_7 = Column(String(255), nullable=True, comment="Committee Member 7")
    sar_committee_member_8 = Column(String(255), nullable=True, comment="Committee Member 8")
    sar_chief_organizer_name = Column(String(255), nullable=True, comment="Chief Organizer Name")

    # Audit Fields
    sar_is_deleted = Column(Boolean, server_default=text('false'), nullable=True, comment="Soft delete flag")
    sar_created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True, comment="Creation timestamp")
    sar_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=True, comment="Last update timestamp")
    sar_created_by = Column(String(25), nullable=True, comment="User who created the record")
    sar_updated_by = Column(String(25), nullable=True, comment="User who last updated the record")
    sar_version_number = Column(Integer, server_default=text('1'), nullable=True, comment="Version number for optimistic locking")
