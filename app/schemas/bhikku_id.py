from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer


class BhikkuIDDeclaration(BaseModel):
    full_bhikku_name: Optional[str] = None
    title_or_post: Optional[str] = None


class BhikkuIDBirthDetails(BaseModel):
    lay_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    place_of_birth: Optional[str] = None


class BhikkuIDOrdinationDetails(BaseModel):
    date_of_robing: Optional[date] = None
    place_of_robing: Optional[str] = None
    nikaya: Optional[str] = None
    parshawaya: Optional[str] = None


class BhikkuIDHigherOrdination(BaseModel):
    samanera_reg_no: Optional[str] = None
    upasampada_reg_no: Optional[str] = None
    higher_ordination_date: Optional[date] = None


class BhikkuIDStayRecord(BaseModel):
    temple_name: Optional[str] = None
    address: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class BhikkuIDDocuments(BaseModel):
    left_thumbprint_url: Optional[str] = None
    applicant_image_url: Optional[str] = None


class BhikkuIDReferences(BaseModel):
    acharya_name: Optional[str] = None
    chief_incumbent_name: Optional[str] = None
    chief_incumbent_address: Optional[str] = None


class BhikkuIDDeclarationDetail(BaseModel):
    approved: Optional[bool] = None
    date: Optional[date] = None
    phone_number: Optional[str] = None

    @field_serializer("date", when_used="json")
    def serialize_date(self, value: Optional[date], _info) -> Optional[str]:
        return value.isoformat() if value else None


class BhikkuIDDeclarations(BaseModel):
    acharya_declaration: BhikkuIDDeclarationDetail = Field(
        default_factory=BhikkuIDDeclarationDetail
    )
    grama_niladari_declaration: BhikkuIDDeclarationDetail = Field(
        default_factory=BhikkuIDDeclarationDetail
    )
    devotional_secretariat_declaration: BhikkuIDDeclarationDetail = Field(
        default_factory=BhikkuIDDeclarationDetail
    )


class BhikkuIDCardData(BaseModel):
    form_no: Optional[str] = None
    divisional_secretariat: Optional[str] = None
    district: Optional[str] = None
    declaration: BhikkuIDDeclaration = Field(default_factory=BhikkuIDDeclaration)
    birth_certificate: BhikkuIDBirthDetails = Field(default_factory=BhikkuIDBirthDetails)
    ordination: BhikkuIDOrdinationDetails = Field(default_factory=BhikkuIDOrdinationDetails)
    higher_ordination: BhikkuIDHigherOrdination = Field(
        default_factory=BhikkuIDHigherOrdination
    )
    higher_ordination_name: Optional[str] = None
    permanent_residence: Optional[str] = None
    national_id: Optional[str] = None
    stay_history: List[BhikkuIDStayRecord] = Field(default_factory=list)
    documents: BhikkuIDDocuments = Field(default_factory=BhikkuIDDocuments)
    references: BhikkuIDReferences = Field(default_factory=BhikkuIDReferences)
    declarations: BhikkuIDDeclarations = Field(default_factory=BhikkuIDDeclarations)


class BhikkuIDCardResponse(BaseModel):
    status: str
    message: str
    data: BhikkuIDCardData
