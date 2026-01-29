#!/usr/bin/env python3
"""
Test by directly calling the service layer, bypassing the API
"""

import sys
import os

# Add the project root to path
sys.path.insert(0, '/mnt/d/DBA Work/DBHRMS/26Jan2026/dba-backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date

# Import database
from app.db.base import Base
from app.db.session import SessionLocal

# Import services and schemas
from app.services.silmatha_regist_service import silmatha_regist_service
from app.schemas.silmatha_regist import SilmathaRegistCreate, SilmathaRegistUpdate
from app.models.user import UserAccount

print("\n" + "="*80)
print("SILMATHA CRUD TEST - Direct Service Layer Test")
print("="*80)

# Get database session
db = SessionLocal()

try:
    # Create a test user object (for audit trail)
    test_user = db.query(UserAccount).filter(
        UserAccount.ua_username == "silmatha_admin"
    ).first()
    
    if not test_user:
        print("\n✗ Test user 'silmatha_admin' not found")
        sys.exit(1)
    
    print(f"\n✓ Using user: {test_user.ua_username}")
    
    # Step 1: CREATE
    print("\n\n" + "="*80)
    print("STEP 1: CREATE Silmatha Record")
    print("="*80)
    
    create_data = SilmathaRegistCreate(
        sil_reqstdate=date(2025, 12, 31),
        sil_form_id="0005",
        sil_gihiname="TestSilmatha123",
        sil_dofb=date(1999, 12, 29),
        sil_fathrname="Father Name",
        sil_email="test123@example.com",
        sil_mobile="0712345678",
        sil_fathrsaddrs="Test Address",
        sil_fathrsmobile="0787654321",
        sil_birthpls="colombo",
        sil_province="CP",
        sil_district="DC006",
        sil_aramadhipathi="TEMP-11",
        sil_mahananame="Mahana Name",
        sil_mahanadate=date(2020, 1, 7),
        sil_mahanaacharyacd="TEMP-12",
        sil_robing_tutor_residence="ARN0000002",
        sil_mahanatemple="ARN0000001",
        sil_robing_after_residence_temple="ARN0000001",
        sil_declaration_date=date(2025, 12, 31),
        sil_remarks="Test record",
        sil_currstat="ST01",
        sil_cat="CAT01",
        sil_student_signature=True,
        sil_acharya_signature=True,
        sil_aramadhipathi_signature=True,
        sil_district_secretary_signature=True,
    )
    
    print("\n📤 Creating record...")
    created = silmatha_regist_service.create_silmatha(
        db, 
        payload=create_data, 
        actor_id=test_user.ua_user_id,
        current_user=test_user
    )
    
    created_regn = created.sil_regn
    print(f"✓ Created: {created_regn}")
    
    # Store for later comparison
    before_update_dict = {
        "sil_gihiname": created.sil_gihiname,
        "sil_mahananame": created.sil_mahananame,
        "sil_email": created.sil_email,
        "sil_mobile": created.sil_mobile,
        "sil_fathrname": created.sil_fathrname,
        "sil_fathrsaddrs": created.sil_fathrsaddrs,
        "sil_fathrsmobile": created.sil_fathrsmobile,
        "sil_aramadhipathi": created.sil_aramadhipathi,
        "sil_mahanaacharyacd": created.sil_mahanaacharyacd,
        "sil_robing_tutor_residence": created.sil_robing_tutor_residence,
        "sil_mahanatemple": created.sil_mahanatemple,
        "sil_robing_after_residence_temple": created.sil_robing_after_residence_temple,
    }
    
    print(f"\n  Values after CREATE:")
    print(f"    sil_gihiname:                  {created.sil_gihiname}")
    print(f"    sil_mahananame:                {created.sil_mahananame}")
    print(f"    sil_email:                     {created.sil_email}")
    print(f"    sil_mobile:                    {created.sil_mobile}")
    print(f"    sil_fathrname:                 {created.sil_fathrname}")
    
    # Step 2: UPDATE (only gihiname and mahananame)
    print("\n\n" + "="*80)
    print("STEP 2: UPDATE Record (Only 2 Fields)")
    print("="*80)
    
    print(f"\n  Updating:")
    print(f"    sil_gihiname:   'TestSilmatha123' → 'UpdatedGihi999'")
    print(f"    sil_mahananame: 'Mahana Name'     → 'UpdatedMahana999'")
    
    update_data = SilmathaRegistUpdate(
        sil_gihiname="UpdatedGihi999",
        sil_mahananame="UpdatedMahana999"
    )
    
    print(f"\n📤 Sending UPDATE...")
    updated = silmatha_regist_service.update_silmatha(
        db,
        sil_regn=created_regn,
        payload=update_data,
        actor_id=test_user.ua_user_id
    )
    
    print(f"✓ Record updated")
    
    # Step 3: Verify Field Preservation
    print("\n\n" + "="*80)
    print("STEP 3: Verify Field Preservation (No Data Loss)")
    print("="*80)
    
    fields_to_check = [
        ("sil_email", "Email"),
        ("sil_mobile", "Mobile"),
        ("sil_fathrname", "Father Name"),
        ("sil_fathrsaddrs", "Father Address"),
        ("sil_fathrsmobile", "Father Mobile"),
        ("sil_aramadhipathi", "Arama Dhipathi"),
        ("sil_mahanaacharyacd", "Mahanaacharya Code"),
        ("sil_robing_tutor_residence", "Robing Tutor Residence"),
        ("sil_mahanatemple", "Mahana Temple"),
        ("sil_robing_after_residence_temple", "Robing After Residence Temple"),
    ]
    
    all_preserved = True
    
    print("\n📋 Fields NOT updated (should be unchanged):")
    for field_name, field_label in fields_to_check:
        before_val = before_update_dict[field_name]
        after_val = getattr(updated, field_name)
        
        if before_val == after_val:
            status_icon = "✓"
        else:
            status_icon = "✗"
            all_preserved = False
        
        print(f"  {status_icon} {field_label:40} {field_name}")
        if before_val != after_val:
            print(f"     Before: {before_val}")
            print(f"     After:  {after_val}")
    
    print("\n📝 Fields that WERE updated (should have changed):")
    updated_fields = [
        ("sil_gihiname", "Gihi Name", "UpdatedGihi999"),
        ("sil_mahananame", "Mahana Name", "UpdatedMahana999")
    ]
    
    for field_name, field_label, expected_value in updated_fields:
        actual_value = getattr(updated, field_name)
        if actual_value == expected_value:
            status_icon = "✓"
            print(f"  {status_icon} {field_label:40} {field_name}")
            print(f"     Value: {actual_value}")
        else:
            status_icon = "✗"
            all_preserved = False
            print(f"  {status_icon} {field_label:40} {field_name}")
            print(f"     Expected: {expected_value}")
            print(f"     Got:      {actual_value}")
    
    # Final Summary
    print("\n\n" + "="*80)
    print("TEST RESULT")
    print("="*80)
    
    if all_preserved:
        print("\n✓✓✓ ALL TESTS PASSED ✓✓✓\n")
        print(f"✓ Record created:        {created_regn}")
        print(f"✓ Partial UPDATE:        2 fields updated, 10 fields preserved")
        print(f"✓ Field preservation:    All non-updated fields unchanged")
        print(f"\n✓ No data loss during UPDATE operations!")
        sys.exit(0)
    else:
        print("\n✗✗✗ TESTS FAILED ✗✗✗\n")
        print(f"✗ Some fields were lost or not updated correctly")
        sys.exit(1)

except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    db.close()
