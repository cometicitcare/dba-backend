# app/schemas/bhikku_id_card.py
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class CRUDAction(str, Enum):
    CREATE = "CREATE"
    READ_ONE = "READ_ONE"
    READ_ALL = "READ_ALL"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class BhikkuIDCardBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    bic_regn: Optional[int] = Field(default=None, ge=1)
    bic_br_id: Optional[int] = Field(default=None, ge=1)
    bic_form_no: Optional[str] = Field(default=None, max_length=20)
    bic_title_post: Optional[str] = Field(default=None, max_length=100)
    bic_robing_date: Optional[date] = None
    bic_robing_place: Optional[str] = Field(default=None, max_length=150)
    bic_robing_nikaya: Optional[str] = Field(default=None, max_length=20)
    bic_robing_parshawaya: Optional[str] = Field(default=None, max_length=20)
    bic_samanera_reg_no: Optional[str] = Field(default=None, max_length=50)
    bic_upasampada_reg_no: Optional[str] = Field(default=None, max_length=50)
    bic_higher_ord_date: Optional[date] = None
    bic_higher_ord_name: Optional[str] = Field(default=None, max_length=150)
    bic_perm_residence: Optional[str] = None
    bic_national_id: Optional[str] = Field(default=None, max_length=20)
    bic_stay_history: Optional[Any] = None
    bic_left_thumbprint_url: Optional[str] = Field(default=None, max_length=255)
    bic_applicant_image_url: Optional[str] = Field(default=None, max_length=255)
    bic_acharya_name: Optional[str] = Field(default=None, max_length=150)
    bic_current_chief_incumbent: Optional[str] = Field(default=None, max_length=150)
    bic_current_chief_address: Optional[str] = None
    bic_nikaya_chapter_declared: Optional[bool] = None
    bic_grama_niladari_declared: Optional[bool] = None
    bic_final_approved: Optional[bool] = None


class BhikkuIDCardCreate(BhikkuIDCardBase):
    bic_regn: int = Field(ge=1)
    bic_br_id: int = Field(ge=1)
    bic_form_no: str = Field(max_length=20)


class BhikkuIDCardUpdate(BhikkuIDCardBase):
    pass


class BhikkuIDCard(BhikkuIDCardBase):
    model_config = ConfigDict(
        from_attributes=True, str_strip_whitespace=True, populate_by_name=True
    )

    bic_id: int
    bic_regn: int
    bic_br_id: int
    bic_form_no: str
    bic_version: datetime
    bic_is_deleted: bool
    bic_created_at: datetime
    bic_updated_at: datetime
    bic_created_by: Optional[str] = None
    bic_updated_by: Optional[str] = None
    bic_version_number: Optional[int] = None


class BhikkuIDCardListResponse(BaseModel):
    status: str
    message: str
    data: List[BhikkuIDCard]
    totalRecords: int
    page: int
    limit: int


class BhikkuIDCardResponse(BaseModel):
    status: str
    message: str
    data: Optional[BhikkuIDCard] = None


class BhikkuIDCardRequestPayload(BaseModel):
    bic_id: Optional[int] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=200)
    page: Optional[int] = Field(default=1, ge=1)
    search_key: Optional[str] = ""
    data: Optional[Union[BhikkuIDCardCreate, BhikkuIDCardUpdate]] = None


class BhikkuIDCardManagementRequest(BaseModel):
    action: CRUDAction
    payload: BhikkuIDCardRequestPayload


class BhikkuIDCardManagementResponse(BaseModel):
    status: str
    message: str
    data: Optional[Union[BhikkuIDCard, List[BhikkuIDCard]]] = None
    totalRecords: Optional[int] = None
    page: Optional[int] = None
    limit: Optional[int] = None
