from typing import Optional
from pydantic import BaseModel, Field


class TempleLandBase(BaseModel):
    serial_number: int = Field(ge=1)
    land_name: Optional[str] = Field(default=None, max_length=200)
    village: Optional[str] = Field(default=None, max_length=200)
    district: Optional[str] = Field(default=None, max_length=100)
    extent: Optional[str] = Field(default=None, max_length=100)
    cultivation_description: Optional[str] = Field(default=None, max_length=500)
    ownership_nature: Optional[str] = Field(default=None, max_length=200)
    deed_number: Optional[str] = Field(default=None, max_length=100)
    title_registration_number: Optional[str] = Field(default=None, max_length=100)
    tax_details: Optional[str] = Field(default=None, max_length=500)
    land_occupants: Optional[str] = Field(default=None, max_length=500)


class TempleLandCreate(TempleLandBase):
    pass


class TempleLandUpdate(BaseModel):
    serial_number: Optional[int] = Field(default=None, ge=1)
    land_name: Optional[str] = Field(default=None, max_length=200)
    village: Optional[str] = Field(default=None, max_length=200)
    district: Optional[str] = Field(default=None, max_length=100)
    extent: Optional[str] = Field(default=None, max_length=100)
    cultivation_description: Optional[str] = Field(default=None, max_length=500)
    ownership_nature: Optional[str] = Field(default=None, max_length=200)
    deed_number: Optional[str] = Field(default=None, max_length=100)
    title_registration_number: Optional[str] = Field(default=None, max_length=100)
    tax_details: Optional[str] = Field(default=None, max_length=500)
    land_occupants: Optional[str] = Field(default=None, max_length=500)


class TempleLandInDB(TempleLandBase):
    id: int
    vh_id: int

    model_config = {"from_attributes": True}
