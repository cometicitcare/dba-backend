from typing import Optional
from pydantic import BaseModel, Field


class ResidentBhikkhuBase(BaseModel):
    serial_number: int = Field(ge=1)
    bhikkhu_name: Optional[str] = Field(default=None, max_length=200)
    registration_number: Optional[str] = Field(default=None, max_length=100)
    occupation_education: Optional[str] = Field(default=None, max_length=500)


class ResidentBhikkhuCreate(ResidentBhikkhuBase):
    pass


class ResidentBhikkhuUpdate(BaseModel):
    serial_number: Optional[int] = Field(default=None, ge=1)
    bhikkhu_name: Optional[str] = Field(default=None, max_length=200)
    registration_number: Optional[str] = Field(default=None, max_length=100)
    occupation_education: Optional[str] = Field(default=None, max_length=500)


class ResidentBhikkhuInDB(ResidentBhikkhuBase):
    id: int
    vh_id: int

    model_config = {"from_attributes": True}
