# app/schemas/location_branch.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MainBranchBase(BaseModel):
    """Base schema for MainBranch"""
    mb_code: str = Field(..., max_length=10)
    mb_name: str = Field(..., max_length=200)
    mb_description: Optional[str] = Field(None, max_length=500)


class MainBranchCreate(MainBranchBase):
    """Schema for creating a new MainBranch"""
    pass


class MainBranchUpdate(BaseModel):
    """Schema for updating a MainBranch"""
    mb_name: Optional[str] = Field(None, max_length=200)
    mb_description: Optional[str] = Field(None, max_length=500)


class MainBranchResponse(MainBranchBase):
    """Schema for MainBranch response"""
    mb_id: int
    mb_is_deleted: bool
    mb_created_at: datetime
    mb_updated_at: datetime
    mb_version_number: int

    model_config = ConfigDict(from_attributes=True)


class ProvinceBranchBase(BaseModel):
    """Base schema for ProvinceBranch"""
    pb_code: str = Field(..., max_length=10)
    pb_name: str = Field(..., max_length=200)
    pb_description: Optional[str] = Field(None, max_length=500)
    pb_main_branch_id: int
    pb_province_code: Optional[str] = Field(None, max_length=10)


class ProvinceBranchCreate(ProvinceBranchBase):
    """Schema for creating a new ProvinceBranch"""
    pass


class ProvinceBranchUpdate(BaseModel):
    """Schema for updating a ProvinceBranch"""
    pb_name: Optional[str] = Field(None, max_length=200)
    pb_description: Optional[str] = Field(None, max_length=500)
    pb_main_branch_id: Optional[int] = None
    pb_province_code: Optional[str] = Field(None, max_length=10)


class ProvinceBranchResponse(ProvinceBranchBase):
    """Schema for ProvinceBranch response"""
    pb_id: int
    pb_is_deleted: bool
    pb_created_at: datetime
    pb_updated_at: datetime
    pb_version_number: int

    model_config = ConfigDict(from_attributes=True)


class DistrictBranchBase(BaseModel):
    """Base schema for DistrictBranch"""
    db_code: str = Field(..., max_length=10)
    db_name: str = Field(..., max_length=200)
    db_description: Optional[str] = Field(None, max_length=500)
    db_province_branch_id: int
    db_district_code: Optional[str] = Field(None, max_length=10)


class DistrictBranchCreate(DistrictBranchBase):
    """Schema for creating a new DistrictBranch"""
    pass


class DistrictBranchUpdate(BaseModel):
    """Schema for updating a DistrictBranch"""
    db_name: Optional[str] = Field(None, max_length=200)
    db_description: Optional[str] = Field(None, max_length=500)
    db_province_branch_id: Optional[int] = None
    db_district_code: Optional[str] = Field(None, max_length=10)


class DistrictBranchResponse(DistrictBranchBase):
    """Schema for DistrictBranch response"""
    db_id: int
    db_is_deleted: bool
    db_created_at: datetime
    db_updated_at: datetime
    db_version_number: int

    model_config = ConfigDict(from_attributes=True)
