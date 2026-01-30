#!/usr/bin/env python3
"""
Test script to understand the arama creation validation issue
"""
import sys
import os
sys.path.append('/Users/shanuka/Desktop/Work project/dba-backend')

from pydantic import ValidationError
from app.schemas.arama import AramaCreate

# Test payload from user
test_payload = {
    "ar_mobile": "0784561234",
    "ar_whtapp": "0789456123", 
    "ar_email": "",  # Empty email to test if optional works
    "ar_typ": "ARAMA",
    "ar_gndiv": "1-1-03-100",
    "ar_ownercd": "SL2025001",
    "ar_parshawa": "PR005",
    "ar_vname": "Helan Aramaya",
    "ar_addrs": "123, Test lane, Colombo",
    "ar_province": "WP",
    "ar_district": "DC001",
    "ar_divisional_secretariat": "DS0001",
    "ar_pradeshya_sabha": "Test Sasanarakshaka",
    "ar_nikaya": "",
    "ar_viharadhipathi_name": "TEMP-13",
    "ar_period_established": "2026-01-01",
    "ar_buildings_description": "Dageba", 
    "ar_dayaka_families_count": "12",
    "ar_fmlycnt": 12,
    "ar_bgndate": "2026-01-01",
    "ar_kulangana_committee": "Test Comity",
    "ar_dayaka_sabha": "",
    "ar_temple_working_committee": "",
    "ar_other_associations": "",
    "temple_owned_land": [{
        "serialNumber": 1,
        "landName": "Main",
        "village": "Colombo", 
        "district": "කොළඹ (Colombo)",
        "extent": "20 Perch",
        "cultivationDescription": "Coconut",
        "ownershipNature": "Bandara",
        "deedNumber": "454",
        "titleRegistrationNumber": "787",
        "taxDetails": "N/A",
        "landOccupants": "10"
    }],
    "ar_land_info_certified": True,
    "resident_silmathas": [{
        "name": "TEMP-13",
        "national_id": "TEMP-13",
        "date_of_birth": "",
        "ordination_date": "", 
        "position": "",
        "is_head_nun": True,
        "notes": ""
    }],
    "ar_resident_silmathas_certified": True,
    "ar_inspection_report": "Good",
    "ar_inspection_code": "Testcode",
    "ar_grama_niladhari_division_ownership": "අළුත්කඩේ  නැගෙනහිර / Aluthkade East / புதுக்கடை கிழக்கு",
    "ar_sanghika_donation_deed": True,
    "ar_government_donation_deed": True,
    "ar_government_donation_deed_in_progress": True,
    "ar_authority_consent_attached": True,
    "ar_recommend_new_center": False,
    "ar_recommend_registered_temple": False,
    "ar_annex2_recommend_construction": False,
    "ar_annex2_land_ownership_docs": True,
    "ar_annex2_chief_incumbent_letter": True,
    "ar_annex2_coordinator_recommendation": True,
    "ar_annex2_divisional_secretary_recommendation": True,
    "ar_annex2_approval_construction": False,
    "ar_annex2_referral_resubmission": False
}

try:
    arama_create = AramaCreate.model_validate(test_payload)
    print("✅ Validation successful!")
    print(f"Email value: {arama_create.ar_email}")
except ValidationError as e:
    print("❌ Validation failed!")
    for error in e.errors():
        print(f"Field: {error['loc']}, Message: {error['msg']}")