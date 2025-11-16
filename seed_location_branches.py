"""
Seed data for Location-Based Access Control

This script populates the main_branches, province_branches, and district_branches tables
with initial data representing the organizational hierarchy:
- 3 Main Branches
- 9 Province Branches (3 per main branch)
- 25 District Branches (distributed across province branches)

Run this script after applying the location-based access control migration.
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.main_branch import MainBranch
from app.models.province_branch import ProvinceBranch
from app.models.district_branch import DistrictBranch


def seed_location_branches():
    """Seed location branch data"""
    db: Session = SessionLocal()
    
    try:
        # Check if data already exists
        existing_main = db.query(MainBranch).filter(MainBranch.mb_is_deleted == False).count()
        if existing_main > 0:
            print(f"Location branches already exist ({existing_main} main branches found). Skipping seed.")
            return
        
        print("Seeding location branches...")
        
        # Create 3 Main Branches
        main_branches = [
            {
                "mb_code": "MB001",
                "mb_name": "Main Branch - Central",
                "mb_description": "Central region main branch",
                "mb_created_by": "system"
            },
            {
                "mb_code": "MB002",
                "mb_name": "Main Branch - Southern",
                "mb_description": "Southern region main branch",
                "mb_created_by": "system"
            },
            {
                "mb_code": "MB003",
                "mb_name": "Main Branch - Northern",
                "mb_description": "Northern region main branch",
                "mb_created_by": "system"
            }
        ]
        
        mb_objects = []
        for mb_data in main_branches:
            mb = MainBranch(**mb_data)
            db.add(mb)
            mb_objects.append(mb)
        
        db.flush()  # Flush to get IDs
        print(f"Created {len(mb_objects)} main branches")
        
        # Create 9 Province Branches (3 per main branch)
        # Note: Adjust province codes to match your actual cmm_province data
        province_branches = [
            # Main Branch 1 - Central (3 provinces)
            {
                "pb_code": "PB001",
                "pb_name": "Province Branch - Western",
                "pb_description": "Western Province Branch",
                "pb_main_branch_id": mb_objects[0].mb_id,
                "pb_province_code": "1",  # Adjust to actual province code
                "pb_created_by": "system"
            },
            {
                "pb_code": "PB002",
                "pb_name": "Province Branch - Central",
                "pb_description": "Central Province Branch",
                "pb_main_branch_id": mb_objects[0].mb_id,
                "pb_province_code": "2",  # Adjust to actual province code
                "pb_created_by": "system"
            },
            {
                "pb_code": "PB003",
                "pb_name": "Province Branch - Sabaragamuwa",
                "pb_description": "Sabaragamuwa Province Branch",
                "pb_main_branch_id": mb_objects[0].mb_id,
                "pb_province_code": "9",  # Adjust to actual province code
                "pb_created_by": "system"
            },
            # Main Branch 2 - Southern (3 provinces)
            {
                "pb_code": "PB004",
                "pb_name": "Province Branch - Southern",
                "pb_description": "Southern Province Branch",
                "pb_main_branch_id": mb_objects[1].mb_id,
                "pb_province_code": "3",  # Adjust to actual province code
                "pb_created_by": "system"
            },
            {
                "pb_code": "PB005",
                "pb_name": "Province Branch - Uva",
                "pb_description": "Uva Province Branch",
                "pb_main_branch_id": mb_objects[1].mb_id,
                "pb_province_code": "8",  # Adjust to actual province code
                "pb_created_by": "system"
            },
            {
                "pb_code": "PB006",
                "pb_name": "Province Branch - Eastern",
                "pb_description": "Eastern Province Branch",
                "pb_main_branch_id": mb_objects[1].mb_id,
                "pb_province_code": "5",  # Adjust to actual province code
                "pb_created_by": "system"
            },
            # Main Branch 3 - Northern (3 provinces)
            {
                "pb_code": "PB007",
                "pb_name": "Province Branch - Northern",
                "pb_description": "Northern Province Branch",
                "pb_main_branch_id": mb_objects[2].mb_id,
                "pb_province_code": "4",  # Adjust to actual province code
                "pb_created_by": "system"
            },
            {
                "pb_code": "PB008",
                "pb_name": "Province Branch - North Western",
                "pb_description": "North Western Province Branch",
                "pb_main_branch_id": mb_objects[2].mb_id,
                "pb_province_code": "6",  # Adjust to actual province code
                "pb_created_by": "system"
            },
            {
                "pb_code": "PB009",
                "pb_name": "Province Branch - North Central",
                "pb_description": "North Central Province Branch",
                "pb_main_branch_id": mb_objects[2].mb_id,
                "pb_province_code": "7",  # Adjust to actual province code
                "pb_created_by": "system"
            }
        ]
        
        pb_objects = []
        for pb_data in province_branches:
            pb = ProvinceBranch(**pb_data)
            db.add(pb)
            pb_objects.append(pb)
        
        db.flush()  # Flush to get IDs
        print(f"Created {len(pb_objects)} province branches")
        
        # Create 25 District Branches
        # Note: Adjust district codes to match your actual cmm_districtdata data
        # This is a sample distribution - adjust based on actual requirements
        district_branches = [
            # Western Province (3 districts)
            {"db_code": "DB001", "db_name": "District Branch - Colombo", "db_province_branch_id": pb_objects[0].pb_id, "db_district_code": "1", "db_created_by": "system"},
            {"db_code": "DB002", "db_name": "District Branch - Gampaha", "db_province_branch_id": pb_objects[0].pb_id, "db_district_code": "2", "db_created_by": "system"},
            {"db_code": "DB003", "db_name": "District Branch - Kalutara", "db_province_branch_id": pb_objects[0].pb_id, "db_district_code": "3", "db_created_by": "system"},
            
            # Central Province (3 districts)
            {"db_code": "DB004", "db_name": "District Branch - Kandy", "db_province_branch_id": pb_objects[1].pb_id, "db_district_code": "4", "db_created_by": "system"},
            {"db_code": "DB005", "db_name": "District Branch - Matale", "db_province_branch_id": pb_objects[1].pb_id, "db_district_code": "5", "db_created_by": "system"},
            {"db_code": "DB006", "db_name": "District Branch - Nuwara Eliya", "db_province_branch_id": pb_objects[1].pb_id, "db_district_code": "6", "db_created_by": "system"},
            
            # Sabaragamuwa Province (2 districts)
            {"db_code": "DB007", "db_name": "District Branch - Kegalle", "db_province_branch_id": pb_objects[2].pb_id, "db_district_code": "21", "db_created_by": "system"},
            {"db_code": "DB008", "db_name": "District Branch - Ratnapura", "db_province_branch_id": pb_objects[2].pb_id, "db_district_code": "22", "db_created_by": "system"},
            
            # Southern Province (3 districts)
            {"db_code": "DB009", "db_name": "District Branch - Galle", "db_province_branch_id": pb_objects[3].pb_id, "db_district_code": "7", "db_created_by": "system"},
            {"db_code": "DB010", "db_name": "District Branch - Matara", "db_province_branch_id": pb_objects[3].pb_id, "db_district_code": "8", "db_created_by": "system"},
            {"db_code": "DB011", "db_name": "District Branch - Hambantota", "db_province_branch_id": pb_objects[3].pb_id, "db_district_code": "9", "db_created_by": "system"},
            
            # Uva Province (2 districts)
            {"db_code": "DB012", "db_name": "District Branch - Badulla", "db_province_branch_id": pb_objects[4].pb_id, "db_district_code": "23", "db_created_by": "system"},
            {"db_code": "DB013", "db_name": "District Branch - Monaragala", "db_province_branch_id": pb_objects[4].pb_id, "db_district_code": "24", "db_created_by": "system"},
            
            # Eastern Province (3 districts)
            {"db_code": "DB014", "db_name": "District Branch - Trincomalee", "db_province_branch_id": pb_objects[5].pb_id, "db_district_code": "13", "db_created_by": "system"},
            {"db_code": "DB015", "db_name": "District Branch - Batticaloa", "db_province_branch_id": pb_objects[5].pb_id, "db_district_code": "14", "db_created_by": "system"},
            {"db_code": "DB016", "db_name": "District Branch - Ampara", "db_province_branch_id": pb_objects[5].pb_id, "db_district_code": "15", "db_created_by": "system"},
            
            # Northern Province (5 districts)
            {"db_code": "DB017", "db_name": "District Branch - Jaffna", "db_province_branch_id": pb_objects[6].pb_id, "db_district_code": "10", "db_created_by": "system"},
            {"db_code": "DB018", "db_name": "District Branch - Kilinochchi", "db_province_branch_id": pb_objects[6].pb_id, "db_district_code": "11", "db_created_by": "system"},
            {"db_code": "DB019", "db_name": "District Branch - Mannar", "db_province_branch_id": pb_objects[6].pb_id, "db_district_code": "12", "db_created_by": "system"},
            {"db_code": "DB020", "db_name": "District Branch - Vavuniya", "db_province_branch_id": pb_objects[6].pb_id, "db_district_code": "25", "db_created_by": "system"},
            {"db_code": "DB021", "db_name": "District Branch - Mullaitivu", "db_province_branch_id": pb_objects[6].pb_id, "db_district_code": "11", "db_created_by": "system"},
            
            # North Western Province (2 districts)
            {"db_code": "DB022", "db_name": "District Branch - Kurunegala", "db_province_branch_id": pb_objects[7].pb_id, "db_district_code": "16", "db_created_by": "system"},
            {"db_code": "DB023", "db_name": "District Branch - Puttalam", "db_province_branch_id": pb_objects[7].pb_id, "db_district_code": "17", "db_created_by": "system"},
            
            # North Central Province (2 districts)
            {"db_code": "DB024", "db_name": "District Branch - Anuradhapura", "db_province_branch_id": pb_objects[8].pb_id, "db_district_code": "18", "db_created_by": "system"},
            {"db_code": "DB025", "db_name": "District Branch - Polonnaruwa", "db_province_branch_id": pb_objects[8].pb_id, "db_district_code": "19", "db_created_by": "system"},
        ]
        
        db_objects = []
        for db_data in district_branches:
            district = DistrictBranch(**db_data)
            db.add(district)
            db_objects.append(district)
        
        db.commit()
        print(f"Created {len(db_objects)} district branches")
        
        print("\n✅ Location branch seeding completed successfully!")
        print(f"   - {len(mb_objects)} Main Branches")
        print(f"   - {len(pb_objects)} Province Branches")
        print(f"   - {len(db_objects)} District Branches")
        
    except Exception as e:
        print(f"❌ Error seeding location branches: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_location_branches()
