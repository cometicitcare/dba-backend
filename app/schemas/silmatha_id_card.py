# app/schemas/silmatha_id_card.py
from __future__ import annotations

from datetime import date, datetime
from typing import Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.bhikku_id_card import CRUDAction


class SilmathaIDCardBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    sic_regn: Optional[int] = Field(default=None, ge=1)
    sic_br_id: Optional[int] = Field(default=None, ge=1)
    sic_form_no: Optional[str] = Field(default=None, max_length=20)
    sic_title_post: Optional[str] = Field(default=None, max_length=100)
    sic_robing_date: Optional[date] = None
    sic_robing_place: Optional[str] = Field(default=None, max_length=150)
    sic_robing_nikaya: Optional[str] = Field(default=None, max_length=20)
    sic_robing_parshawaya: Optional[str] = Field(default=None, max_length=20)
    sic_samanera_reg_no: Optional[str] = Field(default=None, max_length=50)
    sic_upasampada_reg_no: Optional[str] = Field(default=None, max_length=50)
    sic_higher_ord_date: Optional[date] = None
    sic_higher_ord_name: Optional[str] = Field(default=None, max_length=150)
    sic_perm_residence: Optional[str] = None
    sic_national_id: Optional[str] = Field(default=None, max_length=20)
    sic_stay_history: Optional[Any] = None
    sic_left_thumbprint_url: Optional[str] = Field(default=None, max_length=255)
    sic_applicant_image_url: Optional[str] = Field(default=None, max_length=255)
    sic_acharya_name: Optional[str] = Field(default=None, max_length=150)
    sic_current_chief_incumbent: Optional[str] = Field(
        default=None, max_length=150
    )
    sic_current_chief_address: Optional[str] = None
    sic_nikaya_chapter_declared: Optional[bool] = None
    sic_grama_niladari_declared: Optional[bool] = None
    sic_final_approved: Optional[bool] = None


class SilmathaIDCardCreate(SilmathaIDCardBase):
    sic_regn: int = Field(ge=1)
    sic_br_id: int = Field(ge=1)
    sic_form_no: str = Field(max_length=20)


class SilmathaIDCardUpdate(SilmathaIDCardBase):
    pass


class SilmathaIDCard(SilmathaIDCardBase):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    sic_id: int
    sic_regn: int
    sic_br_id: int
    sic_form_no: str
    sic_version: datetime
    sic_is_deleted: bool
    sic_created_at: datetime
    sic_updated_at: datetime
    sic_created_by: Optional[str] = None
    sic_updated_by: Optional[str] = None
    sic_version_number: Optional[int] = None


class SilmathaIDCardListResponse(BaseModel):
    status: str
    message: str
    data: List[SilmathaIDCard]
    totalRecords: int
    page: int
    limit: int


class SilmathaIDCardResponse(BaseModel):
    status: str
    message: str
    data: Optional[SilmathaIDCard] = None


class SilmathaIDCardRequestPayload(BaseModel):
    sic_id: Optional[int] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=200)
    page: Optional[int] = Field(default=1, ge=1)
    search_key: Optional[str] = ""
    data: Optional[Union[SilmathaIDCardCreate, SilmathaIDCardUpdate]] = None


class SilmathaIDCardManagementRequest(BaseModel):
    action: CRUDAction
    payload: SilmathaIDCardRequestPayload


class SilmathaIDCardManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[SilmathaIDCard, List[SilmathaIDCard]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
