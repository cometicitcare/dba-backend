from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field


class ObjectionTypeBase(BaseModel):
    """Base schema for objection type"""
    ot_code: Annotated[str, Field(min_length=1, max_length=20)]
    ot_name_en: Annotated[str, Field(min_length=1, max_length=200)]
    ot_name_si: Optional[str] = Field(None, max_length=200)
    ot_name_ta: Optional[str] = Field(None, max_length=200)
    ot_description: Optional[str] = Field(None, max_length=500)
    ot_is_active: bool = True


class ObjectionTypeCreate(ObjectionTypeBase):
    """Schema for creating objection type"""
    pass


class ObjectionTypeUpdate(BaseModel):
    """Schema for updating objection type"""
    ot_code: Optional[str] = Field(None, max_length=20)
    ot_name_en: Optional[str] = Field(None, max_length=200)
    ot_name_si: Optional[str] = Field(None, max_length=200)
    ot_name_ta: Optional[str] = Field(None, max_length=200)
    ot_description: Optional[str] = Field(None, max_length=500)
    ot_is_active: Optional[bool] = None


class ObjectionTypeOut(ObjectionTypeBase):
    """Schema for objection type output"""
    model_config = ConfigDict(from_attributes=True)
    
    ot_id: int
    ot_is_deleted: bool
    ot_created_at: datetime
    ot_updated_at: Optional[datetime] = None
    ot_created_by: Optional[str] = None
    ot_updated_by: Optional[str] = None
