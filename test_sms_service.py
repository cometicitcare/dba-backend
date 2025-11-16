"""
Test Script for SMS Service

This script tests sending an SMS to verify the SMS service is working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.sms_service_v2 import sms_service_v2
from app.core.config import settings


def test_sms_send():
    """Test sending an SMS."""
    
    print("=" * 70)
    print("SMS Service Test")
    print("=" * 70)
    
    # Check if SMS is enabled
    print(f"\n1. Configuration Check:")
    print(f"   SMS Enabled: {settings.SMS_ENABLED}")
    print(f"   SMS API URL: {settings.SMS_API_URL}")
    print(f"   Bearer Token: {'***' + settings.SMS_BEARER_TOKEN[-4:] if settings.SMS_BEARER_TOKEN else 'NOT SET'}")
    print(f"   Sender ID: {settings.SMS_DEFAULT_SENDER_ID}")
    
    if not settings.SMS_ENABLED:
        print("\n❌ ERROR: SMS is disabled!")
        print("   Please set SMS_ENABLED=true in your .env file")
        return False
    
    if not settings.SMS_BEARER_TOKEN:
        print("\n❌ ERROR: SMS Bearer Token not configured!")
        print("   Please add SMS_BEARER_TOKEN to your .env file")
        return False
    
    # Test phone number
    test_number = "+94701272525"
    test_message = "Hello! This is a test message from DBA HRMS. Your SMS service is working correctly! 🎉"
    
    print(f"\n2. Phone Number Validation:")
    is_valid, formatted, msg = sms_service_v2.validate_phone_number(test_number, country="LK")
    print(f"   Original: {test_number}")
    print(f"   Valid: {is_valid}")
    print(f"   Formatted: {formatted}")
    print(f"   Message: {msg}")
    
    if not is_valid:
        print(f"\n❌ ERROR: Invalid phone number!")
        return False
    
    # Send SMS
    print(f"\n3. Sending SMS:")
    print(f"   To: {formatted}")
    print(f"   Message: {test_message}")
    print(f"   Sending...")
    
    result = sms_service_v2.send_sms(
        recipient=test_number,
        message=test_message,
        validate_number=True,
        country="LK"
    )
    
    print(f"\n4. Result:")
    print(f"   Success: {result.get('success', False)}")
    
    if result.get('success'):
        print(f"   ✅ SMS sent successfully!")
        print(f"   Status Code: {result.get('status_code')}")
        if 'uid' in result:
            print(f"   Message ID: {result.get('uid')}")
        if 'cost' in result:
            print(f"   Cost: {result.get('cost')}")
        if 'sms_count' in result:
            print(f"   SMS Count: {result.get('sms_count')}")
    else:
        print(f"   ❌ SMS failed!")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        if 'status_code' in result:
            print(f"   Status Code: {result.get('status_code')}")
    
    # Show metrics
    print(f"\n5. Service Metrics:")
    metrics = sms_service_v2.get_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 70)
    
    return result.get('success', False)


if __name__ == "__main__":
    try:
        success = test_sms_send()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
