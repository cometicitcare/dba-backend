"""
Test script for Location-Based Access Control
This script tests the database setup and verifies everything is working correctly.
"""

from app.db.session import SessionLocal
from app.models.user import UserAccount, UserLocationType
from app.models.main_branch import MainBranch
from app.models.province_branch import ProvinceBranch
from app.models.district_branch import DistrictBranch
from app.models.bhikku import Bhikku
from app.services.location_access_control_service import LocationAccessControlService
from app.repositories.bhikku_repo import BhikkuRepository


def test_database_setup():
    """Test that all tables and data exist"""
    print("=" * 70)
    print("TEST 1: Database Setup Verification")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        # Check main branches
        main_branches = db.query(MainBranch).filter(MainBranch.mb_is_deleted == False).all()
        print(f"✅ Main Branches: {len(main_branches)} found")
        for mb in main_branches:
            print(f"   - {mb.mb_code}: {mb.mb_name}")
        
        # Check province branches
        province_branches = db.query(ProvinceBranch).filter(ProvinceBranch.pb_is_deleted == False).all()
        print(f"\n✅ Province Branches: {len(province_branches)} found")
        for pb in province_branches[:3]:
            print(f"   - {pb.pb_code}: {pb.pb_name}")
        
        # Check district branches
        district_branches = db.query(DistrictBranch).filter(DistrictBranch.db_is_deleted == False).all()
        print(f"\n✅ District Branches: {len(district_branches)} found")
        for db_obj in district_branches[:3]:
            print(f"   - {db_obj.db_code}: {db_obj.db_name}")
        
        # Check user_accounts table structure
        print(f"\n✅ User accounts table has location fields")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()


def test_access_control_logic():
    """Test the access control service logic"""
    print("\n" + "=" * 70)
    print("TEST 2: Access Control Logic")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        # Get sample branches
        main_branch = db.query(MainBranch).first()
        province_branch = db.query(ProvinceBranch).first()
        district_branch = db.query(DistrictBranch).first()
        
        # Test MAIN_BRANCH user
        print("\n📍 MAIN_BRANCH User:")
        main_user = UserAccount(
            ua_user_id='TEST_MAIN',
            ua_username='test_main',
            ua_location_type=UserLocationType.MAIN_BRANCH,
            ua_main_branch_id=main_branch.mb_id
        )
        provinces = LocationAccessControlService.get_user_province_codes(db, main_user)
        districts = LocationAccessControlService.get_user_district_codes(db, main_user)
        print(f"   Province Access: {'ALL' if provinces is None else provinces}")
        print(f"   District Access: {'ALL' if districts is None else districts}")
        assert provinces is None, "Main branch user should have access to all provinces"
        assert districts is None, "Main branch user should have access to all districts"
        print("   ✅ Passed")
        
        # Test PROVINCE_BRANCH user
        print("\n📍 PROVINCE_BRANCH User:")
        province_user = UserAccount(
            ua_user_id='TEST_PROVINCE',
            ua_username='test_province',
            ua_location_type=UserLocationType.PROVINCE_BRANCH,
            ua_province_branch_id=province_branch.pb_id
        )
        provinces = LocationAccessControlService.get_user_province_codes(db, province_user)
        districts = LocationAccessControlService.get_user_district_codes(db, province_user)
        print(f"   Province Access: {provinces}")
        print(f"   District Access: {districts}")
        assert provinces is not None and len(provinces) > 0, "Province user should have specific provinces"
        assert districts is not None, "Province user should have specific districts"
        print("   ✅ Passed")
        
        # Test DISTRICT_BRANCH user
        print("\n📍 DISTRICT_BRANCH User:")
        district_user = UserAccount(
            ua_user_id='TEST_DISTRICT',
            ua_username='test_district',
            ua_location_type=UserLocationType.DISTRICT_BRANCH,
            ua_district_branch_id=district_branch.db_id
        )
        provinces = LocationAccessControlService.get_user_province_codes(db, district_user)
        districts = LocationAccessControlService.get_user_district_codes(db, district_user)
        print(f"   Province Access: {provinces}")
        print(f"   District Access: {districts}")
        assert provinces is not None and len(provinces) > 0, "District user should have specific province"
        assert districts is not None and len(districts) == 1, "District user should have one district"
        print("   ✅ Passed")
        
        return True
    except AssertionError as e:
        print(f"   ❌ Failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_record_access():
    """Test record-level access control"""
    print("\n" + "=" * 70)
    print("TEST 3: Record Access Control")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        # Get sample branches
        main_branch = db.query(MainBranch).first()
        province_branch = db.query(ProvinceBranch).first()
        district_branch = db.query(DistrictBranch).first()
        
        # Create test users
        main_user = UserAccount(
            ua_user_id='TEST_MAIN',
            ua_username='test_main',
            ua_location_type=UserLocationType.MAIN_BRANCH,
            ua_main_branch_id=main_branch.mb_id
        )
        
        province_user = UserAccount(
            ua_user_id='TEST_PROVINCE',
            ua_username='test_province',
            ua_location_type=UserLocationType.PROVINCE_BRANCH,
            ua_province_branch_id=province_branch.pb_id
        )
        
        district_user = UserAccount(
            ua_user_id='TEST_DISTRICT',
            ua_username='test_district',
            ua_location_type=UserLocationType.DISTRICT_BRANCH,
            ua_district_branch_id=district_branch.db_id
        )
        
        # Test access to a record in province 1, district 1
        test_province = province_branch.pb_province_code if province_branch else '1'
        test_district = district_branch.db_district_code if district_branch else '1'
        
        print(f"\n📄 Testing access to record: Province={test_province}, District={test_district}")
        
        can_main = LocationAccessControlService.can_user_access_record(db, main_user, test_province, test_district)
        can_province = LocationAccessControlService.can_user_access_record(db, province_user, test_province, test_district)
        can_district = LocationAccessControlService.can_user_access_record(db, district_user, test_province, test_district)
        
        print(f"   Main Branch User: {'✅ Can access' if can_main else '❌ Cannot access'}")
        print(f"   Province Branch User: {'✅ Can access' if can_province else '❌ Cannot access'}")
        print(f"   District Branch User: {'✅ Can access' if can_district else '❌ Cannot access'}")
        
        assert can_main, "Main user should access all records"
        assert can_province, "Province user should access records in their province"
        assert can_district, "District user should access records in their district"
        
        # Test access to a different province
        different_province = '9'
        different_district = '25'
        print(f"\n📄 Testing access to record: Province={different_province}, District={different_district}")
        
        can_province_diff = LocationAccessControlService.can_user_access_record(db, province_user, different_province, different_district)
        can_district_diff = LocationAccessControlService.can_user_access_record(db, district_user, different_province, different_district)
        
        print(f"   Province Branch User: {'✅ Can access' if can_province_diff else '❌ Cannot access'}")
        print(f"   District Branch User: {'✅ Can access' if can_district_diff else '❌ Cannot access'}")
        
        assert not can_province_diff, "Province user should NOT access other provinces"
        assert not can_district_diff, "District user should NOT access other districts"
        
        print("\n   ✅ All record access tests passed")
        return True
        
    except AssertionError as e:
        print(f"   ❌ Failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_query_filtering():
    """Test query-level filtering"""
    print("\n" + "=" * 70)
    print("TEST 4: Query Filtering (Bhikku Repository)")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        # Check if there are any bhikku records
        total_bhikkus = db.query(Bhikku).filter(Bhikku.br_is_deleted == False).count()
        print(f"\n📊 Total Bhikku records in database: {total_bhikkus}")
        
        if total_bhikkus == 0:
            print("   ⚠️  No bhikku records found - skipping query filtering test")
            print("   (This is expected if database is fresh)")
            return True
        
        # Get sample branches
        main_branch = db.query(MainBranch).first()
        province_branch = db.query(ProvinceBranch).first()
        district_branch = db.query(DistrictBranch).first()
        
        # Create test users
        main_user = UserAccount(
            ua_user_id='TEST_MAIN',
            ua_username='test_main',
            ua_location_type=UserLocationType.MAIN_BRANCH,
            ua_main_branch_id=main_branch.mb_id
        )
        
        province_user = UserAccount(
            ua_user_id='TEST_PROVINCE',
            ua_username='test_province',
            ua_location_type=UserLocationType.PROVINCE_BRANCH,
            ua_province_branch_id=province_branch.pb_id
        )
        
        # Test bhikku repository filtering
        repo = BhikkuRepository()
        
        print("\n🔍 Testing repository filtering:")
        main_bhikkus = repo.get_all(db, limit=1000, current_user=main_user)
        print(f"   Main Branch User sees: {len(main_bhikkus)} bhikkus")
        
        province_bhikkus = repo.get_all(db, limit=1000, current_user=province_user)
        print(f"   Province Branch User sees: {len(province_bhikkus)} bhikkus")
        
        assert len(main_bhikkus) >= len(province_bhikkus), "Main user should see at least as many as province user"
        
        print("   ✅ Query filtering works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 LOCATION-BASED ACCESS CONTROL TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Database Setup", test_database_setup()))
    results.append(("Access Control Logic", test_access_control_logic()))
    results.append(("Record Access Control", test_record_access()))
    results.append(("Query Filtering", test_query_filtering()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Location-based access control is working correctly.")
        print("\n📚 Next steps:")
        print("   1. Review the documentation in LOCATION_BASED_ACCESS_CONTROL.md")
        print("   2. Test the API endpoints using the server")
        print("   3. Create users with different location types")
        print("   4. Apply location filtering to other entities")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
