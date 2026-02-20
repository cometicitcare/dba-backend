#!/usr/bin/env python3
"""Debug script to test SAVE_STAGE_ONE endpoint with detailed error logging."""

import sys
import os
import json
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.vihara_service import vihara_service
from app.repositories.vihara_repo import vihara_repo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from datetime import datetime

def test_save_stage_one():
    """Test SAVE_STAGE_ONE handler directly."""
    
    # Create DB connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("[TEST] Testing SAVE_STAGE_ONE handler")
        print("=" * 80)
        
        # Test data
        payload_data = {
            "vh_vname": f"Test Vihara {datetime.utcnow().isoformat()}",
            "vh_addrs": "Test Address",
            "vh_mobile": "0771234567",
            "vh_whtapp": "0771234567",
            "vh_email": "test@test.local",
            "vh_typ": "TEMP",
            "vh_gndiv": "N/A",
            "vh_ownercd": "N/A",
            "vh_parshawa": "N/A",
            "vh_province": "WP",
            "vh_district": "CMB",
        }
        
        print(f"\n[INPUT] Payload: {json.dumps(payload_data, indent=2)}")
        
        print(f"\n[SERVICE] Calling vihara_service.save_stage_one()...")
        result = vihara_service.save_stage_one(
            db,
            payload_data=payload_data,
            actor_id="test_user",
            vh_id=None
        )
        
        print(f"\n[SUCCESS] Result VH_ID: {result.vh_id}")
        print(f"[SUCCESS] Status: {result.vh_workflow_status}")
        print(f"[SUCCESS] TRN: {result.vh_trn}")
        
    except Exception as exc:
        print(f"\n❌ [ERROR] Exception occurred:")
        print(f"   Type: {type(exc).__name__}")
        print(f"   Message: {str(exc)}")
        print(f"\n[TRACEBACK]")
        traceback.print_exc()
        
        # Try to extract more details
        import sqlalchemy
        if isinstance(exc, sqlalchemy.exc.IntegrityError):
            print(f"\n[DB_ERROR] IntegrityError details:")
            print(f"   Original: {exc.orig}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_save_stage_one()
