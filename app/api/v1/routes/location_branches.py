# app/api/v1/routes/location_branches.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.auth_middleware import get_current_user
from app.api.auth_dependencies import has_permission
from app.models.user import UserAccount
from app.schemas.location_branch import (
    MainBranchCreate,
    MainBranchResponse,
    ProvinceBranchCreate,
    ProvinceBranchResponse,
    DistrictBranchCreate,
    DistrictBranchResponse,
)
from app.repositories.location_branch_repo import (
    main_branch_repo,
    province_branch_repo,
    district_branch_repo,
)

router = APIRouter()


# Main Branch Endpoints
@router.get(
    "/main-branches",
    response_model=List[MainBranchResponse],
    dependencies=[has_permission("location:read")],
)
def list_main_branches(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Get all main branches"""
    return main_branch_repo.get_all(db, skip=skip, limit=limit)


@router.get(
    "/main-branches/{mb_id}",
    response_model=MainBranchResponse,
    dependencies=[has_permission("location:read")],
)
def get_main_branch(
    mb_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Get a specific main branch by ID"""
    branch = main_branch_repo.get_by_id(db, mb_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Main branch not found")
    return branch


@router.post(
    "/main-branches",
    response_model=MainBranchResponse,
    status_code=201,
    dependencies=[has_permission("location:create")],
)
def create_main_branch(
    branch: MainBranchCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Create a new main branch"""
    # Check if code already exists
    existing = main_branch_repo.get_by_code(db, branch.mb_code)
    if existing:
        raise HTTPException(status_code=400, detail="Main branch code already exists")
    
    branch_dict = branch.model_dump()
    branch_dict["mb_created_by"] = current_user.ua_username
    return main_branch_repo.create(db, branch_dict)


# Province Branch Endpoints
@router.get(
    "/province-branches",
    response_model=List[ProvinceBranchResponse],
    dependencies=[has_permission("location:read")],
)
def list_province_branches(
    skip: int = 0,
    limit: int = 100,
    main_branch_id: int = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Get all province branches, optionally filtered by main branch"""
    if main_branch_id:
        return province_branch_repo.get_by_main_branch(db, main_branch_id)
    return province_branch_repo.get_all(db, skip=skip, limit=limit)


@router.get(
    "/province-branches/{pb_id}",
    response_model=ProvinceBranchResponse,
    dependencies=[has_permission("location:read")],
)
def get_province_branch(
    pb_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Get a specific province branch by ID"""
    branch = province_branch_repo.get_by_id(db, pb_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Province branch not found")
    return branch


@router.post(
    "/province-branches",
    response_model=ProvinceBranchResponse,
    status_code=201,
    dependencies=[has_permission("location:create")],
)
def create_province_branch(
    branch: ProvinceBranchCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Create a new province branch"""
    # Check if code already exists
    existing = province_branch_repo.get_by_code(db, branch.pb_code)
    if existing:
        raise HTTPException(status_code=400, detail="Province branch code already exists")
    
    # Verify main branch exists
    main_branch = main_branch_repo.get_by_id(db, branch.pb_main_branch_id)
    if not main_branch:
        raise HTTPException(status_code=400, detail="Main branch not found")
    
    branch_dict = branch.model_dump()
    branch_dict["pb_created_by"] = current_user.ua_username
    return province_branch_repo.create(db, branch_dict)


# District Branch Endpoints
@router.get(
    "/district-branches",
    response_model=List[DistrictBranchResponse],
    dependencies=[has_permission("location:read")],
)
def list_district_branches(
    skip: int = 0,
    limit: int = 100,
    province_branch_id: int = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Get all district branches, optionally filtered by province branch"""
    if province_branch_id:
        return district_branch_repo.get_by_province_branch(db, province_branch_id)
    return district_branch_repo.get_all(db, skip=skip, limit=limit)


@router.get(
    "/district-branches/{db_id}",
    response_model=DistrictBranchResponse,
    dependencies=[has_permission("location:read")],
)
def get_district_branch(
    db_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Get a specific district branch by ID"""
    branch = district_branch_repo.get_by_id(db, db_id)
    if not branch:
        raise HTTPException(status_code=404, detail="District branch not found")
    return branch


@router.post(
    "/district-branches",
    response_model=DistrictBranchResponse,
    status_code=201,
    dependencies=[has_permission("location:create")],
)
def create_district_branch(
    branch: DistrictBranchCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Create a new district branch"""
    # Check if code already exists
    existing = district_branch_repo.get_by_code(db, branch.db_code)
    if existing:
        raise HTTPException(status_code=400, detail="District branch code already exists")
    
    # Verify province branch exists
    province_branch = province_branch_repo.get_by_id(db, branch.db_province_branch_id)
    if not province_branch:
        raise HTTPException(status_code=400, detail="Province branch not found")
    
    branch_dict = branch.model_dump()
    branch_dict["db_created_by"] = current_user.ua_username
    return district_branch_repo.create(db, branch_dict)
