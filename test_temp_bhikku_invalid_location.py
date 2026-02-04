#!/usr/bin/env python3
"""
Test script for temporary bhikku CREATE with invalid district/province
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.temporary_bhikku_service import temporary_bhikku_service
from app.schemas.temporary_bhikku import TemporaryBhikkuCreate

def test_invalid_location():
    """Test with invalid province/district"""
    print("=" * 80)
    print("Testing with INVALID Province/District")
    print("=" * 80)
    
    db: Session = SessionLocal()
    
    try:
        payload = TemporaryBhikkuCreate(
            tb_bname="TestInvalidLocation",
            tb_name="TestInvalidLocation",
            tb_address="Test Address",
            tb_district="InvalidDistrict999",
            tb_province="InvalidProvince999",
            tb_vihara_name="Test Vihara"
        )
        
        print("\nPayload with INVALID district/province:")
        print(f"  tb_district: {payload.tb_district}")
        print(f"  tb_province: {payload.tb_province}")
        
        result = temporary_bhikku_service.create_temporary_bhikku(
            db=db,
            payload=payload,
            actor_id="TEST_USER"
        )
        
        print("\n✓ Result:")
        print(f"  br_regn: {result.get('br_regn')}")
        print(f"  br_province: {result.get('br_province')}")
        print(f"  br_district: {result.get('br_district')}")
        print(f"  br_remarks: {result.get('br_remarks')}")
        
        if result.get('br_province') is None:
            print("  ✓ Province correctly NULL (invalid province)")
        if result.get('br_district') is None:
            print("  ✓ District correctly NULL (invalid district)")
        if 'InvalidDistrict999' in result.get('br_remarks', ''):
            print("  ✓ Invalid district saved in remarks")
        if 'InvalidProvince999' in result.get('br_remarks', ''):
            print("  ✓ Invalid province saved in remarks")
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = test_invalid_location()
    sys.exit(0 if success else 1)
