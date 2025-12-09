from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AramaLandBase(BaseModel):
    serial_number: int = Field(ge=1, alias="serialNumber")
    plot_number: Optional[str] = Field(default=None, max_length=100, alias="plotNumber")
    survey_number: Optional[str] = Field(default=None, max_length=100, alias="surveyNumber")
    title_number: Optional[str] = Field(default=None, max_length=100, alias="titleNumber")
    land_name: Optional[str] = Field(default=None, max_length=200, alias="landName")
    village: Optional[str] = Field(default=None, max_length=200)
    district: Optional[str] = Field(default=None, max_length=100)
    extent: Optional[str] = Field(default=None, max_length=100)
    extent_unit: Optional[str] = Field(default=None, max_length=50, alias="extentUnit")
    cultivation_description: Optional[str] = Field(default=None, max_length=500, alias="cultivationDescription")
    ownership_nature: Optional[str] = Field(default=None, max_length=200, alias="ownershipNature")
    ownership_type: Optional[str] = Field(default=None, max_length=200, alias="ownershipType")
    deed_number: Optional[str] = Field(default=None, max_length=100, alias="deedNumber")
    title_registration_number: Optional[str] = Field(default=None, max_length=100, alias="titleRegistrationNumber")
    tax_details: Optional[str] = Field(default=None, max_length=500, alias="taxDetails")
    land_occupants: Optional[str] = Field(default=None, max_length=500, alias="landOccupants")
    land_notes: Optional[str] = Field(default=None, max_length=1000, alias="landNotes")

    model_config = ConfigDict(populate_by_name=True)


class AramaLandCreate(AramaLandBase):
    pass


class AramaLandUpdate(BaseModel):
    serial_number: Optional[int] = Field(default=None, ge=1, alias="serialNumber")
    plot_number: Optional[str] = Field(default=None, max_length=100, alias="plotNumber")
    survey_number: Optional[str] = Field(default=None, max_length=100, alias="surveyNumber")
    title_number: Optional[str] = Field(default=None, max_length=100, alias="titleNumber")
    land_name: Optional[str] = Field(default=None, max_length=200, alias="landName")
    village: Optional[str] = Field(default=None, max_length=200)
    district: Optional[str] = Field(default=None, max_length=100)
    extent: Optional[str] = Field(default=None, max_length=100)
    extent_unit: Optional[str] = Field(default=None, max_length=50, alias="extentUnit")
    cultivation_description: Optional[str] = Field(default=None, max_length=500, alias="cultivationDescription")
    ownership_nature: Optional[str] = Field(default=None, max_length=200, alias="ownershipNature")
    ownership_type: Optional[str] = Field(default=None, max_length=200, alias="ownershipType")
    deed_number: Optional[str] = Field(default=None, max_length=100, alias="deedNumber")
    title_registration_number: Optional[str] = Field(default=None, max_length=100, alias="titleRegistrationNumber")
    tax_details: Optional[str] = Field(default=None, max_length=500, alias="taxDetails")
    land_occupants: Optional[str] = Field(default=None, max_length=500, alias="landOccupants")
    land_notes: Optional[str] = Field(default=None, max_length=1000, alias="landNotes")

    model_config = ConfigDict(populate_by_name=True)


class AramaLandInDB(AramaLandBase):
    id: int
    ar_id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
