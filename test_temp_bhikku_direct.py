#!/usr/bin/env python3
"""
Direct database test for temporary bhikku functionality
Tests the service layer directly without HTTP authentication
"""
import sys
import os
from datetime import date

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.temporary_bhikku_service import temporary_bhikku_service
from app.schemas.temporary_bhikku import TemporaryBhikkuCreate

def test_temporary_bhikku_create():
    """Test creating a temporary bhikku record"""
    print("=" * 80)
    print("Testing Temporary Bhikku CREATE (Direct Service Layer)")
    print("=" * 80)
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Create test payload
        payload = TemporaryBhikkuCreate(
            tb_bname="DirectTestBhikku",
            tb_name="DirectTestBhikku",
            tb_address="Direct Test Address",
            tb_district="කොළඹ",
            tb_province="Western Province",
            tb_vihara_name="Test Vihara Name"
        )
        
        print("\nPayload:")
        print(f"  tb_bname: {payload.tb_bname}")
        print(f"  tb_name: {payload.tb_name}")
        print(f"  tb_address: {payload.tb_address}")
        print(f"  tb_district: {payload.tb_district}")
        print(f"  tb_province: {payload.tb_province}")
        print(f"  tb_vihara_name: {payload.tb_vihara_name}")
        
        print("\nCreating bhikku record...")
        
        # Call service layer
        result = temporary_bhikku_service.create_temporary_bhikku(
            db=db,
            payload=payload,
            actor_id="TEST_USER"
        )
        
        print("\n" + "=" * 80)
        print("✓ SUCCESS! Bhikku created in bhikku_regist table")
        print("=" * 80)
        
        print("\nResult Summary:")
        print(f"  ✓ br_regn (BH Number): {result.get('br_regn')}")
        print(f"  ✓ br_mahananame: {result.get('br_mahananame')}")
        print(f"  ✓ br_fathrsaddrs: {result.get('br_fathrsaddrs')}")
        print(f"  ✓ br_cat: {result.get('br_cat')}")
        print(f"  ✓ br_currstat: {result.get('br_currstat')}")
        print(f"  ✓ br_workflow_status: {result.get('br_workflow_status')}")
        print(f"  ✓ br_mahanatemple: {result.get('br_mahanatemple') or 'None (as expected for text vihara name)'}")
        
        # Check nested objects
        print("\nNested Objects (Foreign Keys):")
        if isinstance(result.get('br_province'), dict):
            print(f"  ✓ br_province: {result.get('br_province')}")
        else:
            print(f"  ✗ br_province: {result.get('br_province')} (not a nested object)")
        
        if isinstance(result.get('br_district'), dict):
            print(f"  ✓ br_district: {result.get('br_district')}")
        else:
            print(f"  ✗ br_district: {result.get('br_district')} (not a nested object)")
        
        if isinstance(result.get('br_currstat'), dict):
            print(f"  ✓ br_currstat: {result.get('br_currstat')}")
        else:
            print(f"  ✗ br_currstat: {result.get('br_currstat')} (not a nested object)")
        
        if isinstance(result.get('br_parshawaya'), dict):
            print(f"  ✓ br_parshawaya: {result.get('br_parshawaya')}")
        else:
            print(f"  ✗ br_parshawaya: {result.get('br_parshawaya')} (not a nested object)")
        
        if isinstance(result.get('br_cat'), dict):
            print(f"  ✓ br_cat: {result.get('br_cat')}")
        else:
            print(f"  ✗ br_cat: {result.get('br_cat')} (not a nested object)")
        
        print("\n" + "=" * 80)
        print("Test completed successfully!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("✗ ERROR!")
        print("=" * 80)
        print(f"\n{type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = test_temporary_bhikku_create()
    sys.exit(0 if success else 1)
