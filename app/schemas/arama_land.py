from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AramaLandBase(BaseModel):
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

    model_config = ConfigDict(populate_by_name=True)


class AramaLandCreate(AramaLandBase):
    pass


class AramaLandUpdate(BaseModel):
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

    model_config = ConfigDict(populate_by_name=True)


class AramaLandInDB(AramaLandBase):
    id: int
    ar_id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
