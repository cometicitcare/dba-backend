# app/repositories/location_branch_repo.py
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.main_branch import MainBranch
from app.models.province_branch import ProvinceBranch
from app.models.district_branch import DistrictBranch


class MainBranchRepository:
    """Repository for MainBranch operations"""
    
    def create(self, db: Session, obj_in: dict) -> MainBranch:
        """Create a new main branch"""
        db_obj = MainBranch(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, db: Session, mb_id: int) -> Optional[MainBranch]:
        """Get main branch by ID"""
        return db.query(MainBranch).filter(
            MainBranch.mb_id == mb_id,
            MainBranch.mb_is_deleted == False
        ).first()
    
    def get_by_code(self, db: Session, mb_code: str) -> Optional[MainBranch]:
        """Get main branch by code"""
        return db.query(MainBranch).filter(
            MainBranch.mb_code == mb_code,
            MainBranch.mb_is_deleted == False
        ).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[MainBranch]:
        """Get all active main branches"""
        return db.query(MainBranch).filter(
            MainBranch.mb_is_deleted == False
        ).offset(skip).limit(limit).all()


class ProvinceBranchRepository:
    """Repository for ProvinceBranch operations"""
    
    def create(self, db: Session, obj_in: dict) -> ProvinceBranch:
        """Create a new province branch"""
        db_obj = ProvinceBranch(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, db: Session, pb_id: int) -> Optional[ProvinceBranch]:
        """Get province branch by ID"""
        return db.query(ProvinceBranch).filter(
            ProvinceBranch.pb_id == pb_id,
            ProvinceBranch.pb_is_deleted == False
        ).first()
    
    def get_by_code(self, db: Session, pb_code: str) -> Optional[ProvinceBranch]:
        """Get province branch by code"""
        return db.query(ProvinceBranch).filter(
            ProvinceBranch.pb_code == pb_code,
            ProvinceBranch.pb_is_deleted == False
        ).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ProvinceBranch]:
        """Get all active province branches"""
        return db.query(ProvinceBranch).filter(
            ProvinceBranch.pb_is_deleted == False
        ).offset(skip).limit(limit).all()
    
    def get_by_main_branch(self, db: Session, mb_id: int) -> List[ProvinceBranch]:
        """Get all province branches for a main branch"""
        return db.query(ProvinceBranch).filter(
            ProvinceBranch.pb_main_branch_id == mb_id,
            ProvinceBranch.pb_is_deleted == False
        ).all()


class DistrictBranchRepository:
    """Repository for DistrictBranch operations"""
    
    def create(self, db: Session, obj_in: dict) -> DistrictBranch:
        """Create a new district branch"""
        db_obj = DistrictBranch(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, db: Session, db_id: int) -> Optional[DistrictBranch]:
        """Get district branch by ID"""
        return db.query(DistrictBranch).filter(
            DistrictBranch.db_id == db_id,
            DistrictBranch.db_is_deleted == False
        ).first()
    
    def get_by_code(self, db: Session, db_code: str) -> Optional[DistrictBranch]:
        """Get district branch by code"""
        return db.query(DistrictBranch).filter(
            DistrictBranch.db_code == db_code,
            DistrictBranch.db_is_deleted == False
        ).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[DistrictBranch]:
        """Get all active district branches"""
        return db.query(DistrictBranch).filter(
            DistrictBranch.db_is_deleted == False
        ).offset(skip).limit(limit).all()
    
    def get_by_province_branch(self, db: Session, pb_id: int) -> List[DistrictBranch]:
        """Get all district branches for a province branch"""
        return db.query(DistrictBranch).filter(
            DistrictBranch.db_province_branch_id == pb_id,
            DistrictBranch.db_is_deleted == False
        ).all()


# Create singleton instances
main_branch_repo = MainBranchRepository()
province_branch_repo = ProvinceBranchRepository()
district_branch_repo = DistrictBranchRepository()
