from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_serializer


class DeclarationWithDate(BaseModel):
    approved: Optional[bool] = None
    date: Optional[date] = None
    phone_number: Optional[str] = None

    @field_serializer("date", when_used="json")
    def serialize_date(self, value: Optional[date], _info) -> Optional[str]:
        return value.isoformat() if value else None


class SilmathaIDAcharyaInfo(BaseModel):
    full_name: Optional[str] = None
    residence: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_robing: Optional[date] = None
    date_registered: Optional[date] = None
    registration_number: Optional[str] = None


class SilmathaIDApplicantInfo(BaseModel):
    full_name: Optional[str] = None
    aramaya_address: Optional[str] = None
    date_registered: Optional[date] = None
    registration_number: Optional[str] = None
    certificate_copy_attached: Optional[bool] = None
    date_of_birth: Optional[date] = None
    national_id: Optional[str] = None
    date_of_robing: Optional[date] = None
    lay_name: Optional[str] = None
    birth_certificate_attached: Optional[bool] = None
    highest_education: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_address: Optional[str] = None
    guardian_phone_number: Optional[str] = None
    permanent_residence: Optional[str] = None
    left_thumbprint_url: Optional[str] = None
    applicant_image_url: Optional[str] = None
    application_date: Optional[date] = None
    acharya_declaration: DeclarationWithDate = Field(
        default_factory=DeclarationWithDate
    )
    grama_niladari_declaration: DeclarationWithDate = Field(
        default_factory=DeclarationWithDate
    )
    devotional_secretariat_declaration: DeclarationWithDate = Field(
        default_factory=DeclarationWithDate
    )


class SilmathaIDCardData(BaseModel):
    form_id: Optional[str] = None
    district: Optional[str] = None
    acharya: SilmathaIDAcharyaInfo = Field(default_factory=SilmathaIDAcharyaInfo)
    applicant: SilmathaIDApplicantInfo = Field(default_factory=SilmathaIDApplicantInfo)


class SilmathaIDCardResponse(BaseModel):
    status: str
    message: str
    data: SilmathaIDCardData
