# app/schemas/main_bhikku.py
from __future__ import annotations

from datetime import date, datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict


# ─────────────────────────────────────────────
# Nested info helpers (for response enrichment)
# ─────────────────────────────────────────────

class AssignedBhikkuInfo(BaseModel):
    regn: Optional[str] = None
    gihiname: Optional[str] = None
    mahananame: Optional[str] = None
    address: Optional[str] = None
    current_status: Optional[str] = None


class NikayaInfo(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None


class ParshawaInfo(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None


# ─────────────────────────────────────────────
# Core output schema
# ─────────────────────────────────────────────

class MainBhikkuOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mb_id: int
    mb_type: str
    mb_nikaya_cd: str
    mb_parshawa_cd: Optional[str] = None
    mb_bhikku_regn: str
    mb_start_date: Optional[date] = None
    mb_end_date: Optional[date] = None
    mb_remarks: Optional[str] = None
    mb_is_active: bool
    mb_is_deleted: bool
    mb_created_at: Optional[datetime] = None
    mb_updated_at: Optional[datetime] = None
    mb_created_by: Optional[str] = None
    mb_updated_by: Optional[str] = None
    mb_version_number: int


# ─────────────────────────────────────────────
# Request: set parshawa mahanayaka
# ─────────────────────────────────────────────

class SetParshawaMahanayakaRequest(BaseModel):
    """Assign (or re-assign) the Mahanayaka for a Parshawaya."""
    mb_nikaya_cd: str
    mb_parshawa_cd: str
    br_regn: str                          # bhikku registration number
    mb_start_date: Optional[date] = None
    mb_remarks: Optional[str] = None


# ─────────────────────────────────────────────
# Request: set nikaya mahanayaka
# ─────────────────────────────────────────────

class SetNikayaMahanayakaRequest(BaseModel):
    """Assign (or re-assign) the Mahanayaka for a Nikaya."""
    mb_nikaya_cd: str
    br_regn: str
    mb_start_date: Optional[date] = None
    mb_remarks: Optional[str] = None


# ─────────────────────────────────────────────
# Response
# ─────────────────────────────────────────────

class SetMahanayakaResponse(BaseModel):
    status: str
    message: str
    data: MainBhikkuOut
    assigned_bhikku: Optional[AssignedBhikkuInfo] = None
    nikaya: Optional[NikayaInfo] = None
    parshawa: Optional[ParshawaInfo] = None
