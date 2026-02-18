"""create_dayakasaba_regist_table

Revision ID: 20260218000001
Revises: 20260209000001
Create Date: 2026-02-18 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260218000001"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dayakasaba_regist",
        # ── Primary Key ──────────────────────────────────────────────────────
        sa.Column("ds_id", sa.Integer(), autoincrement=True, nullable=False),

        # ── Temple / Location ─────────────────────────────────────────────
        sa.Column("ds_temple_trn", sa.String(255), nullable=False, comment="Vihara TRN (FK → vihaddata)"),
        sa.Column("ds_phone_number", sa.String(20), nullable=True),
        sa.Column("ds_nikaya", sa.String(10), nullable=True, comment="Nikaya code (FK → cmm_nikayadata)"),
        sa.Column("ds_parshawa", sa.String(20), nullable=True, comment="Parshawa code (FK → cmm_parshawadata)"),
        sa.Column("ds_district", sa.String(10), nullable=True, comment="District code (FK → cmm_districtdata)"),
        sa.Column("ds_ds_division", sa.String(10), nullable=True, comment="DS Division code (FK → cmm_dvsec)"),

        # ── Sabha Details ─────────────────────────────────────────────────
        sa.Column("ds_dayaka_sabha_name", sa.String(255), nullable=True),
        sa.Column("ds_meeting_date", sa.Date(), nullable=True),
        sa.Column("ds_devotee_family_count", sa.Integer(), nullable=True),

        # ── President ────────────────────────────────────────────────────
        sa.Column("ds_president_name", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_president", sa.Boolean(), server_default=sa.text("false"), nullable=True),

        # ── Vice President ───────────────────────────────────────────────
        sa.Column("ds_vice_president_name", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_vice_president", sa.Boolean(), server_default=sa.text("false"), nullable=True),

        # ── Secretary ────────────────────────────────────────────────────
        sa.Column("ds_secretary_name", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_secretary", sa.Boolean(), server_default=sa.text("false"), nullable=True),

        # ── Asst. Secretary ──────────────────────────────────────────────
        sa.Column("ds_asst_secretary_name", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_asst_secretary", sa.Boolean(), server_default=sa.text("false"), nullable=True),

        # ── Treasurer ────────────────────────────────────────────────────
        sa.Column("ds_treasurer_name", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_treasurer", sa.Boolean(), server_default=sa.text("false"), nullable=True),

        # ── Committee Members 1–10 ───────────────────────────────────────
        sa.Column("ds_committee_member_1", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_member_1", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_committee_member_2", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_member_2", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_committee_member_3", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_member_3", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_committee_member_4", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_member_4", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_committee_member_5", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_member_5", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_committee_member_6", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_member_6", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_committee_member_7", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_member_7", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_committee_member_8", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_member_8", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_committee_member_9", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_member_9", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_committee_member_10", sa.String(255), nullable=True),
        sa.Column("ds_is_signed_member_10", sa.Boolean(), server_default=sa.text("false"), nullable=True),

        # ── Banking ───────────────────────────────────────────────────────
        sa.Column("ds_bank_name", sa.String(255), nullable=True),
        sa.Column("ds_bank_branch", sa.String(255), nullable=True),
        sa.Column("ds_account_number", sa.String(100), nullable=True),

        # ── Certification Signatures ─────────────────────────────────────
        sa.Column("ds_is_temple_registered", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_is_signed_cert_secretary", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_is_signed_cert_president", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_is_signed_sasana_sec", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_is_signed_ds", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_is_signed_commissioner", sa.Boolean(), server_default=sa.text("false"), nullable=True),

        # ── Workflow ──────────────────────────────────────────────────────
        sa.Column(
            "ds_workflow_status",
            sa.String(20),
            server_default=sa.text("'PENDING'"),
            nullable=False,
            comment="PENDING | PEND-APPROVAL | COMPLETED | REJECTED",
        ),
        sa.Column("ds_scanned_document_path", sa.String(500), nullable=True),
        sa.Column("ds_approved_by", sa.String(25), nullable=True),
        sa.Column("ds_approved_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("ds_rejected_by", sa.String(25), nullable=True),
        sa.Column("ds_rejected_at", sa.TIMESTAMP(), nullable=True),
        sa.Column("ds_rejection_reason", sa.String(500), nullable=True),

        # ── Audit ─────────────────────────────────────────────────────────
        sa.Column("ds_is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("ds_created_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=True),
        sa.Column("ds_updated_at", sa.TIMESTAMP(), server_default=sa.func.now(), nullable=True),
        sa.Column("ds_created_by", sa.String(25), nullable=True),
        sa.Column("ds_updated_by", sa.String(25), nullable=True),
        sa.Column("ds_version_number", sa.Integer(), server_default=sa.text("1"), nullable=True),

        sa.PrimaryKeyConstraint("ds_id"),
    )

    # Indexes
    op.create_index("ix_dayakasaba_regist_ds_id", "dayakasaba_regist", ["ds_id"])
    op.create_index("ix_dayakasaba_regist_workflow_status", "dayakasaba_regist", ["ds_workflow_status"])

    # Foreign Keys
    op.create_foreign_key(
        "fk_dayakasaba_regist_temple_trn",
        "dayakasaba_regist", "vihaddata",
        ["ds_temple_trn"], ["vh_trn"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dayakasaba_regist_nikaya",
        "dayakasaba_regist", "cmm_nikayadata",
        ["ds_nikaya"], ["nk_nkn"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dayakasaba_regist_parshawa",
        "dayakasaba_regist", "cmm_parshawadata",
        ["ds_parshawa"], ["pr_prn"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dayakasaba_regist_district",
        "dayakasaba_regist", "cmm_districtdata",
        ["ds_district"], ["dd_dcode"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_dayakasaba_regist_ds_division",
        "dayakasaba_regist", "cmm_dvsec",
        ["ds_ds_division"], ["dv_dvcode"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_dayakasaba_regist_ds_division", "dayakasaba_regist", type_="foreignkey")
    op.drop_constraint("fk_dayakasaba_regist_district", "dayakasaba_regist", type_="foreignkey")
    op.drop_constraint("fk_dayakasaba_regist_parshawa", "dayakasaba_regist", type_="foreignkey")
    op.drop_constraint("fk_dayakasaba_regist_nikaya", "dayakasaba_regist", type_="foreignkey")
    op.drop_constraint("fk_dayakasaba_regist_temple_trn", "dayakasaba_regist", type_="foreignkey")
    op.drop_index("ix_dayakasaba_regist_workflow_status", table_name="dayakasaba_regist")
    op.drop_index("ix_dayakasaba_regist_ds_id", table_name="dayakasaba_regist")
    op.drop_table("dayakasaba_regist")
