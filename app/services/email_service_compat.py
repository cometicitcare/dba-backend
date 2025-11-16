"""
Backward Compatible Email Service Wrapper

This file provides backward compatibility by importing from the new V2 service.
All existing code using 'from app.services.email_service import email_service'
will automatically use the new industry-level service.
"""

# Import the new V2 service
from app.services.email_service_v2 import (
    EmailServiceV2,
    email_service_v2,
    CircuitBreaker,
    RateLimiter,
    SMTPConnectionPool
)

# Create backward compatible aliases
EmailService = EmailServiceV2
email_service = email_service_v2

# Export for external use
__all__ = [
    'EmailService',
    'email_service',
    'EmailServiceV2',
    'email_service_v2',
    'CircuitBreaker',
    'RateLimiter',
    'SMTPConnectionPool'
]
