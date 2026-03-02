"""
Seed script for main branches and district branches
Run this script to populate initial branch data for location-based access control

Usage:
    python -m app.utils.seed_branches
"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.main_branch import MainBranch
from app.models.district_branch import DistrictBranch


def seed_main_branches(db: Session):
    """Create 3 main branches"""
    main_branches = [
        {
            "mb_code": "MB001",
            "mb_name": "Main Branch - Central",
            "mb_description": "Central main branch office",
            "mb_created_by": "SYSTEM",
            "mb_updated_by": "SYSTEM"
        },
        {
            "mb_code": "MB002",
            "mb_name": "Main Branch - North",
            "mb_description": "Northern main branch office",
            "mb_created_by": "SYSTEM",
            "mb_updated_by": "SYSTEM"
        },
        {
            "mb_code": "MB003",
            "mb_name": "Main Branch - South",
            "mb_description": "Southern main branch office",
            "mb_created_by": "SYSTEM",
            "mb_updated_by": "SYSTEM"
        }
    ]
    
    for mb_data in main_branches:
        existing = db.query(MainBranch).filter(MainBranch.mb_code == mb_data["mb_code"]).first()
        if not existing:
            mb = MainBranch(**mb_data)
            db.add(mb)
            print(f"✓ Created main branch: {mb_data['mb_name']}")
        else:
            print(f"- Main branch already exists: {mb_data['mb_name']}")
    
    db.commit()


def seed_district_branches(db: Session):
    """Create 25 district branches (one for each district in Sri Lanka)"""
    # Sri Lankan districts with their codes
    districts = [
        ("DB001", "Colombo", "01"),
        ("DB002", "Gampaha", "02"),
        ("DB003", "Kalutara", "03"),
        ("DB004", "Kandy", "04"),
        ("DB005", "Matale", "05"),
        ("DB006", "Nuwara Eliya", "06"),
        ("DB007", "Galle", "07"),
        ("DB008", "Matara", "08"),
        ("DB009", "Hambantota", "09"),
        ("DB010", "Jaffna", "10"),
        ("DB011", "Kilinochchi", "11"),
        ("DB012", "Mannar", "12"),
        ("DB013", "Vavuniya", "13"),
        ("DB014", "Mullaitivu", "14"),
        ("DB015", "Batticaloa", "15"),
        ("DB016", "Ampara", "16"),
        ("DB017", "Trincomalee", "17"),
        ("DB018", "Kurunegala", "18"),
        ("DB019", "Puttalam", "19"),
        ("DB020", "Anuradhapura", "20"),
        ("DB021", "Polonnaruwa", "21"),
        ("DB022", "Badulla", "22"),
        ("DB023", "Moneragala", "23"),
        ("DB024", "Ratnapura", "24"),
        ("DB025", "Kegalle", "25"),
    ]
    
    for db_code, db_name, district_code in districts:
        db_data = {
            "db_code": db_code,
            "db_name": f"District Branch - {db_name}",
            "db_description": f"{db_name} district branch office",
            "db_province_branch_id": 1,  # Placeholder - not using province branches yet
            "db_district_code": district_code,
            "db_created_by": "SYSTEM",
            "db_updated_by": "SYSTEM"
        }
        
        existing = db.query(DistrictBranch).filter(DistrictBranch.db_code == db_code).first()
        if not existing:
            district_branch = DistrictBranch(**db_data)
            db.add(district_branch)
            print(f"✓ Created district branch: {db_data['db_name']}")
        else:
            print(f"- District branch already exists: {db_data['db_name']}")
    
    db.commit()


def main():
    """Main seeding function"""
    print("=" * 60)
    print("Seeding branches for location-based access control")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        print("\n1. Seeding Main Branches...")
        seed_main_branches(db)
        
        print("\n2. Seeding District Branches...")
        seed_district_branches(db)
        
        print("\n" + "=" * 60)
        print("✓ Branch seeding completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
