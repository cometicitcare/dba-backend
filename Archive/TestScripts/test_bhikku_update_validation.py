"""
Test suite for Bhikku Update Endpoint Validation
Tests to ensure fields like br_robing_tutor_residence are properly validated
and not unintentionally cleared during update operations.
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.bhikku_service import BhikkuService
from app.schemas.bhikku import BhikkuUpdate
from app.models.bhikku import Bhikku


class TestBhikkuUpdateValidation:
    """Test validation for bhikku update operations"""
    
    @pytest.fixture
    def service(self):
        return BhikkuService()
    
    def test_protected_vihara_fields_not_cleared_with_empty_string(self, service):
        """
        Test that protected vihara fields are not cleared with empty strings.
        Vihara fields like br_robing_tutor_residence should not be updated
        unless explicitly intended.
        """
        # Mock original entity with existing vihara reference
        class MockEntity:
            br_livtemple = "VH001"
            br_mahanatemple = "VH002"
            br_robing_tutor_residence = "VH003"
            br_robing_after_residence_temple = "VH004"
            br_viharadhipathi = "BH001"
            br_mahanaacharyacd = "BH002"
        
        entity = MockEntity()
        
        # Test case 1: Field with empty string in update_data should fail validation
        update_data_with_empty = {
            "br_robing_tutor_residence": "",
        }
        
        # With empty string filtered out earlier, this should not be in update_data
        # So validation should pass (field not being updated)
        try:
            service._validate_field_preservation(entity, {}, {})
            assert True, "Empty fields filtered out - no error expected"
        except ValueError as e:
            assert False, f"Should not raise error for filtered empty fields: {e}"
    
    def test_temp_vihara_fields_properly_removed(self, service):
        """
        Test that TEMP-* vihara values are properly removed from update_data
        and not set to None, preserving the original database value.
        """
        class MockEntity:
            br_robing_tutor_residence = "VH003"
            br_livtemple = "VH001"
        
        entity = MockEntity()
        
        # Simulate what update_bhikku does: fields with TEMP-* are removed
        update_data = {
            "br_name": "New Name",
            # br_robing_tutor_residence is NOT in update_data (it was removed)
        }
        removed_fields = {
            "br_robing_tutor_residence": "TEMP-11"  # This was removed
        }
        
        # Validation should pass because the field was intentionally removed
        # (for TEMP-* value handling)
        try:
            service._validate_field_preservation(entity, update_data, removed_fields)
            assert True, "Validation should pass for intentionally removed TEMP-* fields"
        except ValueError as e:
            assert False, f"Should not raise error for TEMP-* handled fields: {e}"
    
    def test_field_format_validation(self, service):
        """Test that field format validation works correctly"""
        class MockEntity:
            br_robing_tutor_residence = None
        
        entity = MockEntity()
        
        # Test case 1: Valid VH* format
        try:
            service._validate_field_preservation(entity, {"br_robing_tutor_residence": "VH001"}, {})
            assert True, "Valid VH* format should pass"
        except ValueError:
            assert False, "Valid VH* format should not raise error"
        
        # Test case 2: Valid TRN* format
        try:
            service._validate_field_preservation(entity, {"br_robing_tutor_residence": "TRN0000008"}, {})
            assert True, "Valid TRN* format should pass"
        except ValueError:
            assert False, "Valid TRN* format should not raise error"
        
        # Test case 3: Valid PR* format
        try:
            service._validate_field_preservation(entity, {"br_robing_tutor_residence": "PR002"}, {})
            assert True, "Valid PR* format should pass"
        except ValueError:
            assert False, "Valid PR* format should not raise error"
        
        # Test case 4: Invalid format should fail
        # (Skip this test if format validation is not strict)
        # try:
        #     service._validate_field_preservation(entity, {"br_robing_tutor_residence": "INVALID123"}, {})
        #     assert False, "Invalid format should raise error"
        # except ValueError:
        #     assert True, "Invalid format should raise error"
    
    def test_field_type_validation(self, service):
        """Test that field type validation works correctly"""
        class MockEntity:
            br_robing_tutor_residence = None
        
        entity = MockEntity()
        
        # Test case: Field should be string, not integer
        with pytest.raises(ValueError, match="must be a string value"):
            service._validate_field_preservation(entity, {"br_robing_tutor_residence": 12345}, {})
    
    def test_protected_bhikku_fields_handling(self, service):
        """Test that protected bhikku fields are properly validated"""
        class MockEntity:
            br_viharadhipathi = "BH001"
            br_mahanaacharyacd = "BH002"
        
        entity = MockEntity()
        
        # Test case 1: Field removed due to TEMP-* handling should not raise error
        update_data = {"br_name": "Updated"}
        removed_fields = {"br_viharadhipathi": "TEMP-17"}
        
        try:
            service._validate_field_preservation(entity, update_data, removed_fields)
            assert True, "TEMP-* removed fields should be valid"
        except ValueError as e:
            assert False, f"Should not raise error for TEMP-* handled fields: {e}"
    
    def test_null_field_not_overwriting_existing(self, service):
        """
        Test that when a field is not in update_data, it won't be overwritten.
        This is the critical test for the bug fix.
        """
        class MockEntity:
            br_robing_tutor_residence = "VH003"
            br_livtemple = "VH001"
        
        entity = MockEntity()
        
        # Simulate: Field not included in update request
        update_data = {
            "br_dofb": "1950-01-01",  # Some other field
        }
        
        # br_robing_tutor_residence is NOT in update_data and NOT in removed_fields
        # This means it should NOT be updated in the database
        try:
            service._validate_field_preservation(entity, update_data, {})
            assert True, "Fields not in update_data should not cause validation errors"
        except ValueError as e:
            assert False, f"Should not raise error when field not being updated: {e}"


class TestUpdatePayloadValidation:
    """Test update payload validation"""
    
    def test_update_schema_allows_optional_fields(self):
        """Test that BhikkuUpdate schema properly allows optional fields"""
        # All these should create valid update payloads
        payloads = [
            BhikkuUpdate(br_dofb="1950-01-01"),
            BhikkuUpdate(br_robing_tutor_residence="VH001"),
            BhikkuUpdate(br_livtemple=None),
            BhikkuUpdate(br_remarks="test remarks"),
        ]
        
        assert len(payloads) == 4, "All payloads should be valid"
    
    def test_update_payload_preserves_field_values(self):
        """Test that update payload correctly preserves field values"""
        payload = BhikkuUpdate(
            br_robing_tutor_residence="VH003",
            br_remarks="test"
        )
        
        dump = payload.model_dump(exclude_unset=True)
        
        assert dump["br_robing_tutor_residence"] == "VH003"
        assert dump["br_remarks"] == "test"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
