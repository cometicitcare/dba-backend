# app/models/dayakasaba_regist.py
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class DayakasabaRegist(Base):
    """
    Model for Dayaka Sabha Registration (dayakasaba_regist table).
    Stores information about Dayaka Sabha committee registrations linked to a vihara.

    Workflow:  PENDING  ──upload──►  PEND-APPROVAL  ──approve──►  COMPLETED
                                                      └──reject──►  REJECTED
    """
    __tablename__ = "dayakasaba_regist"

    # ── Primary Key ──────────────────────────────────────────────────────────
    ds_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ── Temple / Location ──────────────────────────────────────────────────
    ds_temple_trn = Column(
        String(255),
        ForeignKey("vihaddata.vh_trn", ondelete="RESTRICT"),
        nullable=False,
        comment="Vihara TRN (FK → vihaddata)",
    )
    ds_phone_number = Column(String(20), nullable=True, comment="Contact phone number")
    ds_nikaya = Column(
        String(10),
        ForeignKey("cmm_nikayadata.nk_nkn", ondelete="RESTRICT"),
        nullable=True,
        comment="Nikaya code (FK → cmm_nikayadata)",
    )
    ds_parshawa = Column(
        String(20),
        ForeignKey("cmm_parshawadata.pr_prn", ondelete="RESTRICT"),
        nullable=True,
        comment="Parshawa code (FK → cmm_parshawadata)",
    )
    ds_district = Column(
        String(10),
        ForeignKey("cmm_districtdata.dd_dcode", ondelete="RESTRICT"),
        nullable=True,
        comment="District code (FK → cmm_districtdata)",
    )
    ds_ds_division = Column(
        String(10),
        ForeignKey("cmm_dvsec.dv_dvcode", ondelete="RESTRICT"),
        nullable=True,
        comment="DS Division code (FK → cmm_dvsec)",
    )

    # ── Sabha Details ─────────────────────────────────────────────────────
    ds_dayaka_sabha_name = Column(String(255), nullable=True, comment="Dayaka Sabha name")
    ds_meeting_date = Column(Date, nullable=True, comment="Meeting date")
    ds_devotee_family_count = Column(Integer, nullable=True, comment="Number of devotee families")

    # ── President ────────────────────────────────────────────────────────
    ds_president_name = Column(String(255), nullable=True)
    ds_is_signed_president = Column(Boolean, server_default=text("false"), nullable=True)

    # ── Vice President ───────────────────────────────────────────────────
    ds_vice_president_name = Column(String(255), nullable=True)
    ds_is_signed_vice_president = Column(Boolean, server_default=text("false"), nullable=True)

    # ── Secretary ────────────────────────────────────────────────────────
    ds_secretary_name = Column(String(255), nullable=True)
    ds_is_signed_secretary = Column(Boolean, server_default=text("false"), nullable=True)

    # ── Asst. Secretary ──────────────────────────────────────────────────
    ds_asst_secretary_name = Column(String(255), nullable=True)
    ds_is_signed_asst_secretary = Column(Boolean, server_default=text("false"), nullable=True)

    # ── Treasurer ────────────────────────────────────────────────────────
    ds_treasurer_name = Column(String(255), nullable=True)
    ds_is_signed_treasurer = Column(Boolean, server_default=text("false"), nullable=True)

    # ── Committee Members 1–10 ────────────────────────────────────────────
    ds_committee_member_1 = Column(String(255), nullable=True)
    ds_is_signed_member_1 = Column(Boolean, server_default=text("false"), nullable=True)
    ds_committee_member_2 = Column(String(255), nullable=True)
    ds_is_signed_member_2 = Column(Boolean, server_default=text("false"), nullable=True)
    ds_committee_member_3 = Column(String(255), nullable=True)
    ds_is_signed_member_3 = Column(Boolean, server_default=text("false"), nullable=True)
    ds_committee_member_4 = Column(String(255), nullable=True)
    ds_is_signed_member_4 = Column(Boolean, server_default=text("false"), nullable=True)
    ds_committee_member_5 = Column(String(255), nullable=True)
    ds_is_signed_member_5 = Column(Boolean, server_default=text("false"), nullable=True)
    ds_committee_member_6 = Column(String(255), nullable=True)
    ds_is_signed_member_6 = Column(Boolean, server_default=text("false"), nullable=True)
    ds_committee_member_7 = Column(String(255), nullable=True)
    ds_is_signed_member_7 = Column(Boolean, server_default=text("false"), nullable=True)
    ds_committee_member_8 = Column(String(255), nullable=True)
    ds_is_signed_member_8 = Column(Boolean, server_default=text("false"), nullable=True)
    ds_committee_member_9 = Column(String(255), nullable=True)
    ds_is_signed_member_9 = Column(Boolean, server_default=text("false"), nullable=True)
    ds_committee_member_10 = Column(String(255), nullable=True)
    ds_is_signed_member_10 = Column(Boolean, server_default=text("false"), nullable=True)

    # ── Banking ───────────────────────────────────────────────────────────
    ds_bank_name = Column(String(255), nullable=True)
    ds_bank_branch = Column(String(255), nullable=True)
    ds_account_number = Column(String(100), nullable=True)

    # ── Certification Signatures ──────────────────────────────────────────
    ds_is_temple_registered = Column(Boolean, server_default=text("false"), nullable=True)
    ds_is_signed_cert_secretary = Column(Boolean, server_default=text("false"), nullable=True)
    ds_is_signed_cert_president = Column(Boolean, server_default=text("false"), nullable=True)
    ds_is_signed_sasana_sec = Column(Boolean, server_default=text("false"), nullable=True)
    ds_is_signed_ds = Column(Boolean, server_default=text("false"), nullable=True)
    ds_is_signed_commissioner = Column(Boolean, server_default=text("false"), nullable=True)

    # ── Workflow ──────────────────────────────────────────────────────────
    ds_workflow_status = Column(
        String(20),
        server_default=text("'PENDING'"),
        nullable=False,
        index=True,
        comment="Workflow status: PENDING | PEND-APPROVAL | COMPLETED | REJECTED",
    )
    ds_scanned_document_path = Column(String(500), nullable=True, comment="Path to the uploaded scanned document")
    ds_approved_by = Column(String(25), nullable=True)
    ds_approved_at = Column(TIMESTAMP, nullable=True)
    ds_rejected_by = Column(String(25), nullable=True)
    ds_rejected_at = Column(TIMESTAMP, nullable=True)
    ds_rejection_reason = Column(String(500), nullable=True)

    # ── Audit ─────────────────────────────────────────────────────────────
    ds_is_deleted = Column(Boolean, server_default=text("false"), nullable=True)
    ds_created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    ds_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=True)
    ds_created_by = Column(String(25), nullable=True)
    ds_updated_by = Column(String(25), nullable=True)
    ds_version_number = Column(Integer, server_default=text("1"), nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────
    temple = relationship(
        "ViharaData",
        primaryjoin="foreign(DayakasabaRegist.ds_temple_trn) == ViharaData.vh_trn",
        viewonly=True,
        lazy="joined",
    )
    nikaya = relationship(
        "NikayaData",
        primaryjoin="foreign(DayakasabaRegist.ds_nikaya) == NikayaData.nk_nkn",
        viewonly=True,
        lazy="joined",
    )
    parshawa = relationship(
        "ParshawaData",
        primaryjoin="foreign(DayakasabaRegist.ds_parshawa) == ParshawaData.pr_prn",
        viewonly=True,
        lazy="joined",
    )
    district = relationship(
        "District",
        primaryjoin="foreign(DayakasabaRegist.ds_district) == District.dd_dcode",
        viewonly=True,
        lazy="joined",
    )
    ds_division = relationship(
        "DivisionalSecretariat",
        primaryjoin="foreign(DayakasabaRegist.ds_ds_division) == DivisionalSecretariat.dv_dvcode",
        viewonly=True,
        lazy="joined",
    )
