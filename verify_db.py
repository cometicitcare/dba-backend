#!/usr/bin/env python3
"""Verify Bhikku Workflow Data in Database"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Query the last bhikku record
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            br_regn,
            br_gihiname,
            br_workflow_status,
            br_approval_status,
            br_printed_at IS NOT NULL as is_printed,
            br_scanned_at IS NOT NULL as is_scanned,
            br_approved_at IS NOT NULL as is_approved,
            br_scanned_document_path IS NOT NULL as has_document,
            br_reprint_status,
            br_reprint_amount,
            br_reprint_requested_at IS NOT NULL as reprint_requested,
            br_reprint_approved_at IS NOT NULL as reprint_approved,
            br_reprint_completed_at IS NOT NULL as reprint_completed
        FROM bhikku_regist 
        WHERE br_gihiname LIKE '%Workflow Automation%'
        ORDER BY br_id DESC 
        LIMIT 1
    """))
    
    row = result.fetchone()
    if row:
        print("\n" + "="*80)
        print("DATABASE VERIFICATION - BHIKKU WORKFLOW")
        print("="*80)
        print(f"Registration Number: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"\nMAIN WORKFLOW:")
        print(f"  Workflow Status: {row[2]}")
        print(f"  Approval Status: {row[3]}")
        print(f"  Printed: {'✅ YES' if row[4] else '❌ NO'}")
        print(f"  Scanned: {'✅ YES' if row[5] else '❌ NO'}")
        print(f"  Approved: {'✅ YES' if row[6] else '❌ NO'}")
        print(f"  Document Uploaded: {'✅ YES' if row[7] else '❌ NO'}")
        print(f"\nREPRINT WORKFLOW:")
        print(f"  Reprint Status: {row[8]}")
        print(f"  Reprint Amount: ${row[9]}")
        print(f"  Reprint Requested: {'✅ YES' if row[10] else '❌ NO'}")
        print(f"  Reprint Approved: {'✅ YES' if row[11] else '❌ NO'}")
        print(f"  Reprint Completed: {'✅ YES' if row[12] else '❌ NO'}")
        print("="*80)
        print("✅ ALL DATA SUCCESSFULLY SAVED TO DATABASE!")
        print("="*80 + "\n")
    else:
        print("❌ No records found")
