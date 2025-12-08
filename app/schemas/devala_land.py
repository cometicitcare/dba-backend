from typing import Optional
from pydantic import BaseModel, Field


class DevalaLandBase(BaseModel):
    serial_number: int = Field(ge=1, alias="serialNumber")
    land_name: Optional[str] = Field(default=None, max_length=200, alias="landName")
    village: Optional[str] = Field(default=None, max_length=200)
    district: Optional[str] = Field(default=None, max_length=100)
    extent: Optional[str] = Field(default=None, max_length=100)
    cultivation_description: Optional[str] = Field(default=None, max_length=500, alias="cultivationDescription")
    ownership_nature: Optional[str] = Field(default=None, max_length=200, alias="ownershipNature")
    deed_number: Optional[str] = Field(default=None, max_length=100, alias="deedNumber")
    title_registration_number: Optional[str] = Field(default=None, max_length=100, alias="titleRegistrationNumber")
    tax_details: Optional[str] = Field(default=None, max_length=500, alias="taxDetails")
    land_occupants: Optional[str] = Field(default=None, max_length=500, alias="landOccupants")

    class Config:
        populate_by_name = True


class DevalaLandCreate(DevalaLandBase):
    pass


class DevalaLandUpdate(BaseModel):
    serial_number: Optional[int] = Field(default=None, ge=1, alias="serialNumber")
    land_name: Optional[str] = Field(default=None, max_length=200, alias="landName")
    village: Optional[str] = Field(default=None, max_length=200)
    district: Optional[str] = Field(default=None, max_length=100)
    extent: Optional[str] = Field(default=None, max_length=100)
    cultivation_description: Optional[str] = Field(default=None, max_length=500, alias="cultivationDescription")
    ownership_nature: Optional[str] = Field(default=None, max_length=200, alias="ownershipNature")
    deed_number: Optional[str] = Field(default=None, max_length=100, alias="deedNumber")
    title_registration_number: Optional[str] = Field(default=None, max_length=100, alias="titleRegistrationNumber")
    tax_details: Optional[str] = Field(default=None, max_length=500, alias="taxDetails")
    land_occupants: Optional[str] = Field(default=None, max_length=500, alias="landOccupants")

    class Config:
        populate_by_name = True


class DevalaLandInDB(DevalaLandBase):
    id: int
    dv_id: int

    model_config = {"from_attributes": True}
