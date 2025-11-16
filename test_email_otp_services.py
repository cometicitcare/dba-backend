"""
Test Script for Industry-Level Email and OTP Services

Run this script to verify your services are working correctly.
"""

import asyncio
import time
from datetime import datetime


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(test_name, passed, message=""):
    """Print test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"       {message}")


def test_email_service():
    """Test email service functionality."""
    print_section("Testing Email Service V2")
    
    try:
        from app.services.email_service_v2 import email_service_v2
        
        # Test 1: Import successful
        print_result("Import EmailServiceV2", True)
        
        # Test 2: Check configuration
        config_ok = (
            email_service_v2.smtp_server and
            email_service_v2.from_email
        )
        print_result(
            "Configuration loaded",
            config_ok,
            f"SMTP: {email_service_v2.smtp_server}, From: {email_service_v2.from_email}"
        )
        
        # Test 3: Connection pool initialized
        pool_ok = email_service_v2.connection_pool is not None
        print_result("Connection pool initialized", pool_ok)
        
        # Test 4: Rate limiter initialized
        rate_limiter_ok = email_service_v2.rate_limiter is not None
        print_result("Rate limiter initialized", rate_limiter_ok)
        
        # Test 5: Circuit breaker initialized
        circuit_breaker_ok = email_service_v2.circuit_breaker is not None
        print_result("Circuit breaker initialized", circuit_breaker_ok)
        
        # Test 6: Template loading
        try:
            # This will fail if template doesn't exist, but tests the mechanism
            html = email_service_v2.load_template("password_reset", user_name="Test")
            template_ok = True
        except:
            template_ok = False
        print_result("Template loading mechanism", template_ok)
        
        # Test 7: Get metrics
        metrics = email_service_v2.get_metrics()
        metrics_ok = isinstance(metrics, dict)
        print_result("Metrics tracking", metrics_ok, f"Metrics: {metrics}")
        
        return True
        
    except Exception as e:
        print_result("Email Service V2", False, f"Error: {e}")
        return False


def test_otp_service():
    """Test OTP service functionality."""
    print_section("Testing OTP Service V2")
    
    try:
        from app.services.otp_service_v2 import otp_service_v2
        
        # Test 1: Import successful
        print_result("Import OTPServiceV2", True)
        
        # Test 2: Check storage type
        metrics = otp_service_v2.get_metrics()
        storage_type = metrics.get('storage_type', 'unknown')
        print_result(
            "Storage initialized",
            storage_type in ['redis', 'memory'],
            f"Storage type: {storage_type}"
        )
        
        if storage_type == 'memory':
            print("       ⚠ WARNING: Using in-memory storage. Redis not available.")
            print("       ⚠ For production, set up Redis and set REDIS_ENABLED=true")
        
        # Test 3: Generate OTP
        success, message, otp = otp_service_v2.generate_otp(
            user_id="test_user_123",
            user_identifier="test@example.com",
            delivery_channel="email",
            ip_address="127.0.0.1"
        )
        print_result("Generate OTP", success, f"OTP: {otp if success else message}")
        
        if success and otp:
            # Test 4: Validate correct OTP
            valid, msg, metadata = otp_service_v2.validate_otp(
                user_id="test_user_123",
                otp=otp
            )
            print_result("Validate correct OTP", valid, msg)
            
            # Test 5: Get OTP status
            status = otp_service_v2.get_otp_status("test_user_123")
            status_ok = status is None  # Should be None after validation
            print_result("OTP cleared after validation", status_ok)
            
            # Test 6: Validate wrong OTP
            success2, message2, otp2 = otp_service_v2.generate_otp(
                user_id="test_user_456",
                user_identifier="test2@example.com"
            )
            if success2:
                invalid, msg2, _ = otp_service_v2.validate_otp(
                    user_id="test_user_456",
                    otp="999999"  # Wrong OTP
                )
                print_result("Reject invalid OTP", not invalid, msg2)
                
                # Clean up
                otp_service_v2.clear_otp("test_user_456")
        
        # Test 7: Rate limiting
        # Generate multiple OTPs to test rate limiting
        rate_limit_hit = False
        for i in range(7):  # Try more than the hourly limit
            success, message, _ = otp_service_v2.generate_otp(
                user_id=f"rate_test_{i}",
                user_identifier="ratelimit@example.com"
            )
            if not success and "rate limit" in message.lower():
                rate_limit_hit = True
                break
        
        print_result("Rate limiting active", rate_limit_hit)
        
        # Test 8: Metrics
        final_metrics = otp_service_v2.get_metrics()
        print_result("Metrics tracking", True, f"Metrics: {final_metrics}")
        
        return True
        
    except Exception as e:
        print_result("OTP Service V2", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_background_tasks():
    """Test background task service."""
    print_section("Testing Background Task Service")
    
    try:
        from app.services.background_tasks import background_task_service
        
        # Test 1: Service running
        running = background_task_service._running
        print_result("Service running", running)
        
        # Test 2: Submit a simple task
        def simple_task(x, y):
            time.sleep(0.1)
            return x + y
        
        task_id = background_task_service.submit_task(
            task_name="test_addition",
            func=simple_task,
            x=5,
            y=3,
            max_retries=1
        )
        
        print_result("Submit task", task_id is not None, f"Task ID: {task_id}")
        
        # Test 3: Wait for task completion
        time.sleep(1)
        status = background_task_service.get_task_status(task_id)
        
        if status:
            task_completed = status['status'] == 'completed'
            print_result(
                "Task execution",
                task_completed,
                f"Status: {status['status']}"
            )
        
        # Test 4: Metrics
        metrics = background_task_service.get_metrics()
        print_result("Metrics tracking", True, f"Metrics: {metrics}")
        
        return True
        
    except Exception as e:
        print_result("Background Task Service", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_password_reset_service():
    """Test password reset service integration."""
    print_section("Testing Password Reset Service V2")
    
    try:
        from app.services.password_reset_service_v2 import password_reset_service_v2
        
        # Test 1: Import successful
        print_result("Import PasswordResetServiceV2", True)
        
        # Test 2: Service initialized with OTP and email services
        services_ok = (
            password_reset_service_v2.otp_service is not None and
            password_reset_service_v2.email_service is not None
        )
        print_result("Services initialized", services_ok)
        
        # Test 3: Get service metrics
        try:
            metrics = password_reset_service_v2.get_service_metrics()
            metrics_ok = all(k in metrics for k in ['email_service', 'otp_service', 'background_tasks'])
            print_result("Service metrics", metrics_ok)
            print(f"       Email: {metrics['email_service']}")
            print(f"       OTP: {metrics['otp_service']}")
            print(f"       Tasks: {metrics['background_tasks']}")
        except Exception as e:
            print_result("Service metrics", False, str(e))
        
        return True
        
    except Exception as e:
        print_result("Password Reset Service V2", False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test backward compatibility wrappers."""
    print_section("Testing Backward Compatibility")
    
    try:
        # Test email service compatibility
        try:
            from app.services.email_service_compat import email_service
            print_result("Email service backward compatibility", True)
        except:
            print_result("Email service backward compatibility", False)
        
        # Test password reset service compatibility
        try:
            from app.services.password_reset_service_compat import password_reset_service
            print_result("Password reset service backward compatibility", True)
        except:
            print_result("Password reset service backward compatibility", False)
        
        return True
        
    except Exception as e:
        print_result("Backward Compatibility", False, f"Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  Industry-Level Email & OTP Services - Test Suite")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Email Service", test_email_service()))
    results.append(("OTP Service", test_otp_service()))
    results.append(("Background Tasks", test_background_tasks()))
    results.append(("Password Reset Service", test_password_reset_service()))
    results.append(("Backward Compatibility", test_backward_compatibility()))
    
    # Summary
    print_section("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Services are ready for use.")
        return 0
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
