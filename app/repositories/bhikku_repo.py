# app/repositories/bhikku_repo.py
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.models import bhikku as models
from app.schemas import bhikku as schemas
from typing import Optional

def get_by_regn(db: Session, br_regn: str):
    return db.query(models.Bhikku).filter(
        models.Bhikku.br_regn == br_regn,
        models.Bhikku.br_is_deleted == False
    ).first()

def get_all(db: Session, skip: int = 0, limit: int = 100, search_key: Optional[str] = None):
    """Get paginated bhikkus with optional search functionality across all text fields"""
    query = db.query(models.Bhikku).filter(
        models.Bhikku.br_is_deleted == False
    )
    
    # Apply search filter if search_key is provided and not empty
    if search_key and search_key.strip():
        search_pattern = f"%{search_key.strip()}%"
        query = query.filter(
            or_(
                # Registration and identification
                models.Bhikku.br_regn.ilike(search_pattern),
                models.Bhikku.br_upasampada_serial_no.ilike(search_pattern),
                
                # Personal information
                models.Bhikku.br_gihiname.ilike(search_pattern),
                models.Bhikku.br_fathrname.ilike(search_pattern),
                models.Bhikku.br_mahananame.ilike(search_pattern),
                
                # Geographic information
                models.Bhikku.br_birthpls.ilike(search_pattern),
                models.Bhikku.br_province.ilike(search_pattern),
                models.Bhikku.br_district.ilike(search_pattern),
                models.Bhikku.br_korale.ilike(search_pattern),
                models.Bhikku.br_pattu.ilike(search_pattern),
                models.Bhikku.br_division.ilike(search_pattern),
                models.Bhikku.br_vilage.ilike(search_pattern),
                models.Bhikku.br_gndiv.ilike(search_pattern),
                
                # Contact information
                models.Bhikku.br_mobile.ilike(search_pattern),
                models.Bhikku.br_email.ilike(search_pattern),
                models.Bhikku.br_fathrsaddrs.ilike(search_pattern),
                models.Bhikku.br_fathrsmobile.ilike(search_pattern),
                
                # Temple/Religious codes
                models.Bhikku.br_parshawaya.ilike(search_pattern),
                models.Bhikku.br_livtemple.ilike(search_pattern),
                models.Bhikku.br_mahanatemple.ilike(search_pattern),
                models.Bhikku.br_mahanaacharyacd.ilike(search_pattern),
                models.Bhikku.br_currstat.ilike(search_pattern),
                models.Bhikku.br_cat.ilike(search_pattern),
            )
        )
    
    # CRITICAL: Add explicit ordering for consistent pagination
    return query.order_by(models.Bhikku.br_id).offset(skip).limit(limit).all()

def get_total_count(db: Session, search_key: Optional[str] = None):
    """Get total count of non-deleted bhikkus for pagination with optional search"""
    query = db.query(func.count(models.Bhikku.br_id)).filter(
        models.Bhikku.br_is_deleted == False
    )
    
    # Apply same search filter as get_all
    if search_key and search_key.strip():
        search_pattern = f"%{search_key.strip()}%"
        query = query.filter(
            or_(
                # Registration and identification
                models.Bhikku.br_regn.ilike(search_pattern),
                models.Bhikku.br_upasampada_serial_no.ilike(search_pattern),
                
                # Personal information
                models.Bhikku.br_gihiname.ilike(search_pattern),
                models.Bhikku.br_fathrname.ilike(search_pattern),
                models.Bhikku.br_mahananame.ilike(search_pattern),
                
                # Geographic information
                models.Bhikku.br_birthpls.ilike(search_pattern),
                models.Bhikku.br_province.ilike(search_pattern),
                models.Bhikku.br_district.ilike(search_pattern),
                models.Bhikku.br_korale.ilike(search_pattern),
                models.Bhikku.br_pattu.ilike(search_pattern),
                models.Bhikku.br_division.ilike(search_pattern),
                models.Bhikku.br_vilage.ilike(search_pattern),
                models.Bhikku.br_gndiv.ilike(search_pattern),
                
                # Contact information
                models.Bhikku.br_mobile.ilike(search_pattern),
                models.Bhikku.br_email.ilike(search_pattern),
                models.Bhikku.br_fathrsaddrs.ilike(search_pattern),
                models.Bhikku.br_fathrsmobile.ilike(search_pattern),
                
                # Temple/Religious codes
                models.Bhikku.br_parshawaya.ilike(search_pattern),
                models.Bhikku.br_livtemple.ilike(search_pattern),
                models.Bhikku.br_mahanatemple.ilike(search_pattern),
                models.Bhikku.br_mahanaacharyacd.ilike(search_pattern),
                models.Bhikku.br_currstat.ilike(search_pattern),
                models.Bhikku.br_cat.ilike(search_pattern),
            )
        )
    
    return query.scalar()

def create(db: Session, bhikku: schemas.BhikkuCreate):
    db_bhikku = models.Bhikku(**bhikku.model_dump())
    db.add(db_bhikku)
    db.commit()
    db.refresh(db_bhikku)
    return db_bhikku

def update(db: Session, br_regn: str, bhikku_update: schemas.BhikkuUpdate):
    db_bhikku = get_by_regn(db, br_regn)
    if not db_bhikku:
        return None

    update_data = bhikku_update.model_dump(exclude_unset=True)
    db_bhikku.br_version_number = (db_bhikku.br_version_number or 1) + 1

    for key, value in update_data.items():
        setattr(db_bhikku, key, value)

    db.commit()
    db.refresh(db_bhikku)
    return db_bhikku

def delete(db: Session, br_regn: str):
    db_bhikku = get_by_regn(db, br_regn)
    if not db_bhikku:
        return None

    db_bhikku.br_is_deleted = True
    db_bhikku.br_version_number += 1
    db.commit()
    db.refresh(db_bhikku)
    return db_bhikku