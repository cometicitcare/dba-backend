from datetime import date
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AramaResidentSilmathaBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    name: Annotated[str, Field(min_length=1, max_length=200)]
    national_id: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    date_of_birth: Optional[date] = None
    ordination_date: Optional[date] = None
    position: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    notes: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    is_head_nun: bool = False

    @field_validator("name", "national_id", "position", "notes", mode="before")
    @classmethod
    def _strip_strings(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None
        return value

    @field_validator("date_of_birth", "ordination_date", mode="before")
    @classmethod
    def _parse_dates(cls, value):
        if isinstance(value, str):
            if value.strip() == "":
                return None
            # Let Pydantic handle the actual date parsing
        return value


class AramaResidentSilmathaCreate(AramaResidentSilmathaBase):
    """Schema for creating a resident silmatha record"""
    model_config = ConfigDict(extra="ignore")


class AramaResidentSilmathaUpdate(BaseModel):
    """Schema for updating a resident silmatha record"""
    name: Annotated[Optional[str], Field(default=None, min_length=1, max_length=200)] = None
    national_id: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    date_of_birth: Optional[date] = None
    ordination_date: Optional[date] = None
    position: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    notes: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    is_head_nun: Optional[bool] = None


class AramaResidentSilmathaInDB(AramaResidentSilmathaBase):
    id: int
    ar_id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
