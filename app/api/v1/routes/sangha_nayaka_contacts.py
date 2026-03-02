# app/api/v1/routes/sangha_nayaka_contacts.py
"""
API endpoints for Sangha Nayaka (Senior Monks) contact information.
Provides access to contact details of Mahanayakas, Anunayakas, and Lekhakadikaris.
"""

from collections import defaultdict
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.auth_dependencies import has_permission
from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.sangha_nayaka_contact import SanghaNayakaContact
from app.models.user import UserAccount
from app.schemas.sangha_nayaka_contact import (
    SanghaNayakaContactByNikayaItem,
    SanghaNayakaContactByNikayaResponse,
    SanghaNayakaContactListItem,
    SanghaNayakaContactListResponse,
)

router = APIRouter()


def _serialize_contact(contact: SanghaNayakaContact) -> SanghaNayakaContactListItem:
    """Serialize a SanghaNayakaContact record to a response item."""
    return SanghaNayakaContactListItem(
        id=contact.snc_id,
        nikaya_code=contact.snc_nikaya_code,
        nikaya_name=contact.snc_nikaya_name,
        parshawa_code=contact.snc_parshawa_code,
        parshawa_name=contact.snc_parshawa_name,
        name=contact.snc_name,
        designation=contact.snc_designation,
        address=contact.snc_address,
        phone1=contact.snc_phone1,
        phone2=contact.snc_phone2,
        phone3=contact.snc_phone3,
        order_no=contact.snc_order_no,
    )


@router.get(
    "/",
    response_model=SanghaNayakaContactListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_sangha_nayaka_contacts(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
    nikaya_code: Optional[str] = Query(None, description="Filter by nikaya code"),
    parshawa_code: Optional[str] = Query(None, description="Filter by parshawa code"),
    search: Optional[str] = Query(None, description="Search by name or designation"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
):
    """
    List all Sangha Nayaka contacts with optional filtering.
    
    Filter by:
    - nikaya_code: Filter by specific nikaya
    - parshawa_code: Filter by specific parshawa
    - search: Search in name and designation
    
    Requires: bhikku:read permission
    """
    query = db.query(SanghaNayakaContact).filter(
        SanghaNayakaContact.snc_is_deleted.is_(False)
    )
    
    if nikaya_code:
        query = query.filter(SanghaNayakaContact.snc_nikaya_code == nikaya_code)
    
    if parshawa_code:
        query = query.filter(SanghaNayakaContact.snc_parshawa_code == parshawa_code)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (SanghaNayakaContact.snc_name.ilike(search_term)) |
            (SanghaNayakaContact.snc_designation.ilike(search_term)) |
            (SanghaNayakaContact.snc_nikaya_name.ilike(search_term)) |
            (SanghaNayakaContact.snc_parshawa_name.ilike(search_term))
        )
    
    total = query.count()
    contacts = query.order_by(SanghaNayakaContact.snc_order_no).offset(skip).limit(limit).all()
    
    return SanghaNayakaContactListResponse(
        status="success",
        message=f"Retrieved {len(contacts)} Sangha Nayaka contacts",
        total=total,
        data=[_serialize_contact(c) for c in contacts],
    )


@router.get(
    "/by-nikaya",
    response_model=SanghaNayakaContactByNikayaResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_contacts_by_nikaya(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    List all Sangha Nayaka contacts grouped by Nikaya.
    
    Returns contacts organized under their respective Nikayas for easy navigation.
    
    Requires: bhikku:read permission
    """
    contacts = (
        db.query(SanghaNayakaContact)
        .filter(SanghaNayakaContact.snc_is_deleted.is_(False))
        .order_by(
            SanghaNayakaContact.snc_nikaya_code,
            SanghaNayakaContact.snc_order_no,
        )
        .all()
    )
    
    # Group by nikaya
    grouped: dict[str, dict] = defaultdict(lambda: {"name": "", "contacts": []})
    
    for contact in contacts:
        nikaya_code = contact.snc_nikaya_code or "UNKNOWN"
        if not grouped[nikaya_code]["name"]:
            grouped[nikaya_code]["name"] = contact.snc_nikaya_name or nikaya_code
        grouped[nikaya_code]["contacts"].append(_serialize_contact(contact))
    
    # Convert to response format
    result: List[SanghaNayakaContactByNikayaItem] = []
    for nikaya_code, data in sorted(grouped.items()):
        result.append(
            SanghaNayakaContactByNikayaItem(
                nikaya_code=nikaya_code,
                nikaya_name=data["name"],
                contacts=data["contacts"],
            )
        )
    
    return SanghaNayakaContactByNikayaResponse(
        status="success",
        message=f"Retrieved contacts for {len(result)} Nikayas",
        data=result,
    )


@router.get(
    "/mahanayakas",
    response_model=SanghaNayakaContactListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_mahanayakas(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    List only Mahanayaka contacts (head monks).
    
    Filters contacts whose designation includes "මහානායක".
    
    Requires: bhikku:read permission
    """
    contacts = (
        db.query(SanghaNayakaContact)
        .filter(
            SanghaNayakaContact.snc_is_deleted.is_(False),
            SanghaNayakaContact.snc_designation.ilike("%මහානායක%"),
        )
        .order_by(SanghaNayakaContact.snc_order_no)
        .all()
    )
    
    return SanghaNayakaContactListResponse(
        status="success",
        message=f"Retrieved {len(contacts)} Mahanayaka contacts",
        total=len(contacts),
        data=[_serialize_contact(c) for c in contacts],
    )


@router.get(
    "/anunayakas",
    response_model=SanghaNayakaContactListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_anunayakas(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    List only Anunayaka contacts (deputy head monks).
    
    Filters contacts whose designation includes "අනුනායක".
    
    Requires: bhikku:read permission
    """
    contacts = (
        db.query(SanghaNayakaContact)
        .filter(
            SanghaNayakaContact.snc_is_deleted.is_(False),
            SanghaNayakaContact.snc_designation.ilike("%අනුනායක%"),
        )
        .order_by(SanghaNayakaContact.snc_order_no)
        .all()
    )
    
    return SanghaNayakaContactListResponse(
        status="success",
        message=f"Retrieved {len(contacts)} Anunayaka contacts",
        total=len(contacts),
        data=[_serialize_contact(c) for c in contacts],
    )


@router.get(
    "/lekhakadikaris",
    response_model=SanghaNayakaContactListResponse,
    dependencies=[has_permission("bhikku:read")],
)
def list_lekhakadikaris(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    List only Lekhakadikari contacts (chief secretaries).
    
    Filters contacts whose designation includes "ලේඛකාධිකාරී".
    
    Requires: bhikku:read permission
    """
    contacts = (
        db.query(SanghaNayakaContact)
        .filter(
            SanghaNayakaContact.snc_is_deleted.is_(False),
            SanghaNayakaContact.snc_designation.ilike("%ලේඛකාධිකාරී%"),
        )
        .order_by(SanghaNayakaContact.snc_order_no)
        .all()
    )
    
    return SanghaNayakaContactListResponse(
        status="success",
        message=f"Retrieved {len(contacts)} Lekhakadikari contacts",
        total=len(contacts),
        data=[_serialize_contact(c) for c in contacts],
    )
