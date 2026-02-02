from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ResidentBhikkhuBase(BaseModel):
    serial_number: int = Field(ge=1, alias="serialNumber")
    bhikkhu_name: Optional[str] = Field(default=None, max_length=200, alias="bhikkhuName")
    registration_number: Optional[str] = Field(default=None, max_length=100, alias="registrationNumber")
    occupation_education: Optional[str] = Field(default=None, max_length=500, alias="occupationEducation")
    
    model_config = ConfigDict(populate_by_name=True)


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

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
