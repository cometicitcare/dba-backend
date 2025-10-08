# app/repositories/bhikku_repo.py
from sqlalchemy.orm import Session
from app.models import bhikku as models
from app.schemas import bhikku as schemas

def get_by_regn(db: Session, br_regn: str):
    return db.query(models.Bhikku).filter(
        models.Bhikku.br_regn == br_regn,
        models.Bhikku.br_is_deleted == False
    ).first()

def get_all(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bhikku).filter(
        models.Bhikku.br_is_deleted == False
    ).offset(skip).limit(limit).all()

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