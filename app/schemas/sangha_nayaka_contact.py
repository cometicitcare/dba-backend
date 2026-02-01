# app/schemas/sangha_nayaka_contact.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class SanghaNayakaContactBase(BaseModel):
    """Base schema for Sangha Nayaka Contact."""
    snc_nikaya_code: Optional[str] = None
    snc_parshawa_code: Optional[str] = None
    snc_nikaya_name: Optional[str] = None
    snc_parshawa_name: Optional[str] = None
    snc_name: str
    snc_address: Optional[str] = None
    snc_phone1: Optional[str] = None
    snc_phone2: Optional[str] = None
    snc_phone3: Optional[str] = None
    snc_designation: Optional[str] = None
    snc_order_no: Optional[int] = None


class SanghaNayakaContactCreate(SanghaNayakaContactBase):
    """Schema for creating a new Sangha Nayaka Contact."""
    pass


class SanghaNayakaContactUpdate(BaseModel):
    """Schema for updating a Sangha Nayaka Contact."""
    snc_nikaya_code: Optional[str] = None
    snc_parshawa_code: Optional[str] = None
    snc_nikaya_name: Optional[str] = None
    snc_parshawa_name: Optional[str] = None
    snc_name: Optional[str] = None
    snc_address: Optional[str] = None
    snc_phone1: Optional[str] = None
    snc_phone2: Optional[str] = None
    snc_phone3: Optional[str] = None
    snc_designation: Optional[str] = None
    snc_order_no: Optional[int] = None


class SanghaNayakaContactOut(SanghaNayakaContactBase):
    """Schema for returning a Sangha Nayaka Contact."""
    snc_id: int
    snc_created_at: Optional[datetime] = None
    snc_updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SanghaNayakaContactListItem(BaseModel):
    """Schema for list item in response."""
    id: int
    nikaya_code: Optional[str] = None
    nikaya_name: Optional[str] = None
    parshawa_code: Optional[str] = None
    parshawa_name: Optional[str] = None
    name: str
    designation: Optional[str] = None
    address: Optional[str] = None
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    phone3: Optional[str] = None
    order_no: Optional[int] = None


class SanghaNayakaContactListResponse(BaseModel):
    """Response schema for listing Sangha Nayaka Contacts."""
    status: str
    message: str
    total: int
    data: List[SanghaNayakaContactListItem]


class SanghaNayakaContactByNikayaItem(BaseModel):
    """Schema for contacts grouped by Nikaya."""
    nikaya_code: str
    nikaya_name: str
    contacts: List[SanghaNayakaContactListItem]


class SanghaNayakaContactByNikayaResponse(BaseModel):
    """Response schema for contacts grouped by Nikaya."""
    status: str
    message: str
    data: List[SanghaNayakaContactByNikayaItem]
