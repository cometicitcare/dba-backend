from datetime import date
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


class AramaResidentSilmathaBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=200)]
    national_id: Annotated[Optional[str], Field(default=None, max_length=20)] = None
    date_of_birth: Optional[date] = None
    ordination_date: Optional[date] = None
    position: Annotated[Optional[str], Field(default=None, max_length=200)] = None
    notes: Annotated[Optional[str], Field(default=None, max_length=1000)] = None
    is_head_nun: bool = False


class AramaResidentSilmathaCreate(AramaResidentSilmathaBase):
    """Schema for creating a resident silmatha record"""
    pass


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
