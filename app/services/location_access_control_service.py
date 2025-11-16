# app/services/location_access_control_service.py
from typing import Optional, List
from sqlalchemy.orm import Session, Query
from sqlalchemy import or_, and_

from app.models.user import UserAccount, UserLocationType
from app.models.province_branch import ProvinceBranch
from app.models.district_branch import DistrictBranch


class LocationAccessControlService:
    """
    Service for implementing location-based access control.
    
    Business Rules:
    - MAIN_BRANCH users: Can see all data from all branches, provinces, and districts
    - PROVINCE_BRANCH users: Can only see data from their own province
    - DISTRICT_BRANCH users: Can only see data from their own district
    """
    
    @staticmethod
    def get_user_province_codes(db: Session, user: UserAccount) -> Optional[List[str]]:
        """
        Get the list of province codes that a user has access to.
        
        Args:
            db: Database session
            user: The user to check access for
            
        Returns:
            List of province codes the user can access, or None if user has access to all provinces
        """
        if not user.ua_location_type:
            # No location restriction for users without location type
            return None
            
        if user.ua_location_type == UserLocationType.MAIN_BRANCH:
            # Main branch users can see all provinces
            return None
        
        elif user.ua_location_type == UserLocationType.PROVINCE_BRANCH:
            if not user.ua_province_branch_id:
                return []
            
            # Get the province code(s) associated with this province branch
            province_branch = db.query(ProvinceBranch).filter(
                ProvinceBranch.pb_id == user.ua_province_branch_id,
                ProvinceBranch.pb_is_deleted == False
            ).first()
            
            if province_branch and province_branch.pb_province_code:
                return [province_branch.pb_province_code]
            return []
        
        elif user.ua_location_type == UserLocationType.DISTRICT_BRANCH:
            if not user.ua_district_branch_id:
                return []
            
            # Get the province code through the district branch's province branch
            district_branch = db.query(DistrictBranch).filter(
                DistrictBranch.db_id == user.ua_district_branch_id,
                DistrictBranch.db_is_deleted == False
            ).first()
            
            if not district_branch:
                return []
            
            province_branch = db.query(ProvinceBranch).filter(
                ProvinceBranch.pb_id == district_branch.db_province_branch_id,
                ProvinceBranch.pb_is_deleted == False
            ).first()
            
            if province_branch and province_branch.pb_province_code:
                return [province_branch.pb_province_code]
            return []
        
        return []
    
    @staticmethod
    def get_user_district_codes(db: Session, user: UserAccount) -> Optional[List[str]]:
        """
        Get the list of district codes that a user has access to.
        
        Args:
            db: Database session
            user: The user to check access for
            
        Returns:
            List of district codes the user can access, or None if user has access to all districts
        """
        if not user.ua_location_type:
            # No location restriction for users without location type
            return None
            
        if user.ua_location_type == UserLocationType.MAIN_BRANCH:
            # Main branch users can see all districts
            return None
        
        elif user.ua_location_type == UserLocationType.PROVINCE_BRANCH:
            if not user.ua_province_branch_id:
                return []
            
            # Get all district codes under this province branch
            district_branches = db.query(DistrictBranch).filter(
                DistrictBranch.db_province_branch_id == user.ua_province_branch_id,
                DistrictBranch.db_is_deleted == False
            ).all()
            
            district_codes = [db.db_district_code for db in district_branches if db.db_district_code]
            return district_codes if district_codes else []
        
        elif user.ua_location_type == UserLocationType.DISTRICT_BRANCH:
            if not user.ua_district_branch_id:
                return []
            
            # Get the district code associated with this district branch
            district_branch = db.query(DistrictBranch).filter(
                DistrictBranch.db_id == user.ua_district_branch_id,
                DistrictBranch.db_is_deleted == False
            ).first()
            
            if district_branch and district_branch.db_district_code:
                return [district_branch.db_district_code]
            return []
        
        return []
    
    @staticmethod
    def apply_location_filter_to_query(
        query: Query,
        db: Session,
        user: UserAccount,
        province_field: str,
        district_field: str
    ) -> Query:
        """
        Apply location-based filtering to a SQLAlchemy query.
        
        Args:
            query: The SQLAlchemy query to filter
            db: Database session
            user: The user requesting the data
            province_field: Name of the province field in the queried model (e.g., 'br_province')
            district_field: Name of the district field in the queried model (e.g., 'br_district')
            
        Returns:
            Filtered query
        """
        if not user.ua_location_type:
            # No location restriction
            return query
        
        if user.ua_location_type == UserLocationType.MAIN_BRANCH:
            # Main branch users can see everything
            return query
        
        # Get accessible province and district codes
        province_codes = LocationAccessControlService.get_user_province_codes(db, user)
        district_codes = LocationAccessControlService.get_user_district_codes(db, user)
        
        filters = []
        
        # Add province filter
        if province_codes is not None:  # None means access to all
            if province_codes:
                # Get the model class from the query
                model = query.column_descriptions[0]['entity']
                province_attr = getattr(model, province_field, None)
                if province_attr is not None:
                    filters.append(province_attr.in_(province_codes))
        
        # Add district filter for district-level users
        if user.ua_location_type == UserLocationType.DISTRICT_BRANCH and district_codes:
            model = query.column_descriptions[0]['entity']
            district_attr = getattr(model, district_field, None)
            if district_attr is not None:
                filters.append(district_attr.in_(district_codes))
        
        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))
        
        return query
    
    @staticmethod
    def can_user_access_record(
        db: Session,
        user: UserAccount,
        record_province: Optional[str],
        record_district: Optional[str]
    ) -> bool:
        """
        Check if a user can access a specific record based on its location.
        
        Args:
            db: Database session
            user: The user requesting access
            record_province: The province associated with the record
            record_district: The district associated with the record
            
        Returns:
            True if user can access the record, False otherwise
        """
        if not user.ua_location_type:
            # No location restriction
            return True
        
        if user.ua_location_type == UserLocationType.MAIN_BRANCH:
            # Main branch users can access everything
            return True
        
        # Get accessible codes
        province_codes = LocationAccessControlService.get_user_province_codes(db, user)
        district_codes = LocationAccessControlService.get_user_district_codes(db, user)
        
        # Check province access
        if province_codes is not None:  # None means access to all
            if record_province and record_province not in province_codes:
                return False
        
        # Check district access for district-level users
        if user.ua_location_type == UserLocationType.DISTRICT_BRANCH:
            if district_codes and record_district:
                if record_district not in district_codes:
                    return False
        
        return True
