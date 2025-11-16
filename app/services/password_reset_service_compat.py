"""
Backward Compatible Password Reset Service Wrapper

This file provides backward compatibility by importing from the new V2 service.
All existing code will automatically use the new industry-level service.
"""

# Import the new V2 service
from app.services.password_reset_service_v2 import (
    PasswordResetServiceV2,
    password_reset_service_v2
)
from app.services.otp_service_v2 import (
    OTPServiceV2,
    otp_service_v2
)

# Create backward compatible aliases
PasswordResetService = PasswordResetServiceV2
password_reset_service = password_reset_service_v2

OTPManager = OTPServiceV2  # For backward compatibility
otp_manager = otp_service_v2

# Export for external use
__all__ = [
    'PasswordResetService',
    'password_reset_service',
    'PasswordResetServiceV2',
    'password_reset_service_v2',
    'OTPManager',
    'otp_manager',
    'OTPServiceV2',
    'otp_service_v2'
]
