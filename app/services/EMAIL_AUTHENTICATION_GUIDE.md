"""
Email & Authentication Services Documentation

This module provides comprehensive email sending, password reset, and username
recovery functionality for the DBA HRMS application.

## Overview

The email system is organized into three main components:

1. **EmailService** - Base email sending utility
2. **PasswordResetService** - OTP-based password reset flow
3. **UsernameRecoveryService** - Email-based username recovery

## Configuration

All email settings are configured in `.env`:

```env
SMTP_SERVER=mail.smtp2go.com
SMTP_PORT=2525
SMTP_USERNAME=no-reply@dbagovlk.com
SMTP_PASSWORD=vn5Y7uQeka2qEPlC
SMTP_FROM_EMAIL=no-reply@dbagovlk.com
SMTP_FROM_NAME="DBA HRMS"
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES=30
OTP_EXPIRE_MINUTES=10
OTP_LENGTH=6
```

## Services

### 1. EmailService (`services/email_service.py`)

**Purpose**: Low-level email sending via SMTP

**Key Methods**:

- `send_email(to_email, subject, html_content, plain_text)` 
  - Sends an email to a recipient
  - Returns: bool (success/failure)

- `load_template(template_name, **kwargs)`
  - Loads and renders HTML email templates
  - Supports variable substitution with {{variable}} syntax
  - Returns: str (rendered HTML)

**Example Usage**:

```python
from app.services.email_service import email_service

# Send a simple email
success = email_service.send_email(
    to_email="user@example.com",
    subject="Welcome!",
    html_content="<p>Welcome to DBA HRMS</p>"
)

# Send email with template
html = email_service.load_template(
    "new_user",
    user_name="John Doe",
    username="john_doe",
    temporary_password="TempPass123!",
    email="john@example.com",
    login_url="https://your-app.com/login",
    support_url="https://your-app.com/support",
    privacy_url="https://your-app.com/privacy",
    terms_url="https://your-app.com/terms"
)

success = email_service.send_email(
    to_email="john@example.com",
    subject="Welcome to DBA HRMS",
    html_content=html
)
```

### 2. PasswordResetService (`services/password_reset_service.py`)

**Purpose**: Manage password reset flows with OTP verification

**Key Components**:

- **OTPManager** - Manages OTP generation, validation, and expiration
- **PasswordResetService** - Orchestrates the password reset flow

**Configuration**:
- OTP Length: 6 digits (configurable in .env)
- OTP Expiry: 10 minutes (configurable in .env)
- Max Attempts: 3 (hardcoded, can be made configurable)

**Key Methods**:

1. `initiate_password_reset(user_id, user_email, user_name)`
   - Generates OTP
   - Sends password reset email
   - Returns: (bool, str) - (success, message)

2. `validate_otp_for_reset(user_id, otp)`
   - Validates OTP with attempt tracking
   - Returns: (bool, str) - (is_valid, message)

3. `complete_password_reset(user_id, new_password)`
   - Clears OTP after successful validation
   - Returns: (bool, str) - (success, message)

4. `get_reset_status(user_id)`
   - Returns OTP status, time remaining, attempts
   - Returns: dict or None

**Example Flow**:

```python
from app.services.password_reset_service import password_reset_service

# Step 1: User requests password reset
success, msg = password_reset_service.initiate_password_reset(
    user_id=123,
    user_email="john@example.com",
    user_name="John Doe"
)
# OTP sent to email, user checks inbox

# Step 2: User enters OTP
is_valid, msg = password_reset_service.validate_otp_for_reset(
    user_id=123,
    otp="123456"
)

# Step 3: If OTP valid, user creates new password
if is_valid:
    success, msg = password_reset_service.complete_password_reset(
        user_id=123,
        new_password="NewSecurePassword123!"
    )
```

**OTP Flow Diagram**:

```
User Request Password Reset
        ↓
Generate OTP (6 digits)
        ↓
Send email with OTP
        ↓
User enters OTP (max 3 attempts)
        ↓
Validate OTP (check expiry, attempts)
        ↓
User enters new password
        ↓
Update password in database
        ↓
Clear OTP
        ↓
User logs in with new password
```

### 3. UsernameRecoveryService (`services/username_recovery_service.py`)

**Purpose**: Help users recover forgotten usernames using email

**Key Methods**:

1. `recover_username_by_email(email, user_data)`
   - Sends username recovery email
   - Returns: (bool, str) - (success, message)

2. `verify_email_exists(email, user_repo)`
   - Verifies email in system (requires user repository)
   - Returns: (bool, user_data)

3. `handle_username_recovery_request(email, user_repo)`
   - Complete flow: verify email → send recovery email
   - Returns: (bool, str) - (success, generic_message)
   - Always returns generic message for security

**Example Usage**:

```python
from app.services.username_recovery_service import username_recovery_service
from app.repositories.user_repo import user_repo

# Handle username recovery request
success, message = username_recovery_service.handle_username_recovery_request(
    email="john@example.com",
    user_repo=user_repo
)

# Returns: (True, "If an account exists with this email, you will receive...")
# Message is generic for security (prevents email enumeration)
```

**Security Note**: The service always returns a generic success message to prevent
email enumeration attacks, which is a security best practice.

## Email Templates

Located in `app/templates/`:

### 1. `new_user.html` - New User Welcome Email

**Template Variables**:
- `{{user_name}}` - User's display name
- `{{username}}` - Login username
- `{{temporary_password}}` - Temporary password
- `{{email}}` - User's email
- `{{login_url}}` - Link to login page
- `{{support_url}}` - Link to support
- `{{privacy_url}}` - Link to privacy policy
- `{{terms_url}}` - Link to terms

**Use Case**: Send to new users after account creation

### 2. `password_reset.html` - Password Reset OTP Email

**Template Variables**:
- `{{user_name}}` - User's display name
- `{{otp}}` - One-Time Password (6 digits)
- `{{otp_expiry}}` - OTP validity in minutes
- `{{reset_password_url}}` - Link to password reset page
- `{{support_url}}` - Link to support

**Use Case**: Send when user requests password reset

### 3. `username_recovery.html` - Username Recovery Email

**Template Variables**:
- `{{username}}` - The recovered username
- `{{email}}` - User's email address
- `{{account_status}}` - Account status (Active, Inactive, etc.)
- `{{user_name}}` - User's display name
- `{{login_url}}` - Link to login page
- `{{support_url}}` - Link to support

**Use Case**: Send when user recovers forgotten username

## API Integration Examples

### Password Reset API Endpoints

```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.password_reset_service import password_reset_service
from app.repositories.user_repo import user_repo

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ValidateOTPRequest(BaseModel):
    user_id: int
    otp: str

class ResetPasswordRequest(BaseModel):
    user_id: int
    otp: str
    new_password: str
    confirm_password: str

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    # Find user by email
    user = await user_repo.get_by_email(request.email)
    
    if not user:
        # Return generic message for security
        return {
            "message": "If an account exists with this email, "
                      "you will receive a password reset link."
        }
    
    # Initiate password reset
    success, message = password_reset_service.initiate_password_reset(
        user_id=user.id,
        user_email=user.email,
        user_name=user.first_name or "User"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reset email"
        )
    
    return {
        "message": "If an account exists with this email, "
                  "you will receive a password reset link."
    }

@router.post("/validate-otp")
async def validate_otp(request: ValidateOTPRequest):
    is_valid, message = password_reset_service.validate_otp_for_reset(
        user_id=request.user_id,
        otp=request.otp
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"message": "OTP validated"}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    # Validate password requirements
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Validate OTP
    is_valid, message = password_reset_service.validate_otp_for_reset(
        user_id=request.user_id,
        otp=request.otp
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Update password (call your auth service)
    success, message = password_reset_service.complete_password_reset(
        user_id=request.user_id,
        new_password=request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )
    
    return {"message": "Password reset successful"}
```

### Username Recovery API Endpoint

```python
@router.post("/recover-username")
async def recover_username(request: ForgotPasswordRequest):
    # Find user by email
    user = await user_repo.get_by_email(request.email)
    
    user_data = None
    if user:
        user_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "status": user.status
        }
    
    # Send recovery email if user found
    success, message = username_recovery_service.recover_username_by_email(
        email=request.email,
        user_data=user_data
    )
    
    # Always return generic message for security
    return {
        "message": "If an account exists with this email, "
                  "you will receive your username shortly."
    }
```

## Production Considerations

### 1. OTP Storage
Currently, OTP is stored in-memory. For production:
- Use Redis for distributed OTP storage
- Or use database with TTL index

```python
# Future Redis implementation
from redis import Redis

class OTPManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    def generate_otp(self, user_id: str | int) -> str:
        otp = generate_secure_otp()
        self.redis.setex(
            f"otp:{user_id}",
            self.otp_expiry * 60,
            otp
        )
        return otp
```

### 2. SMTP Configuration
- Use environment variables (already implemented)
- Consider using AWS SES, SendGrid, or similar for production
- Add retry logic and exponential backoff

### 3. Email Logging
- Log all email sends in database for audit trail
- Implement webhook handling for delivery status
- Monitor bounce/complaint rates

### 4. Rate Limiting
- Limit password reset attempts per email (5 per hour)
- Limit OTP generation attempts (3 per 30 minutes)
- Limit username recovery attempts (5 per day)

### 5. Template Management
- Move templates to database or template engine (Jinja2)
- Add multilingual support
- Add template versioning

## File Structure

```
app/
├── services/
│   ├── email_service.py          # Base email service
│   ├── password_reset_service.py # Password reset flow
│   └── username_recovery_service.py # Username recovery
├── templates/
│   ├── new_user.html             # New user welcome
│   ├── password_reset.html       # Password reset OTP
│   └── username_recovery.html    # Username recovery
├── core/
│   └── config.py                 # Email settings
└── .env                          # Environment variables
```

## Testing

Example test cases:

```python
import pytest
from app.services.password_reset_service import password_reset_service
from app.services.username_recovery_service import username_recovery_service

def test_otp_generation():
    otp = password_reset_service.otp_manager.generate_otp(user_id=1)
    assert len(otp) == 6
    assert otp.isdigit()

def test_otp_validation():
    otp = password_reset_service.otp_manager.generate_otp(user_id=1)
    is_valid, msg = password_reset_service.otp_manager.validate_otp(1, otp)
    assert is_valid is True

def test_otp_expiry():
    otp = password_reset_service.otp_manager.generate_otp(user_id=1)
    # Simulate expiry (adjust time in test)
    password_reset_service.otp_manager._otp_store[1]["expires_at"] = datetime.utcnow() - timedelta(minutes=1)
    is_valid, msg = password_reset_service.otp_manager.validate_otp(1, otp)
    assert is_valid is False
    assert "expired" in msg.lower()
```

## Next Steps

1. **Integrate with User Repository**
   - Update `verify_email_exists()` to use actual user repository
   - Add user lookup by email in password reset flow

2. **Add API Endpoints**
   - Create `/api/v1/auth/forgot-password` endpoint
   - Create `/api/v1/auth/validate-otp` endpoint
   - Create `/api/v1/auth/reset-password` endpoint
   - Create `/api/v1/auth/recover-username` endpoint

3. **Database Models**
   - Create `PasswordReset` model to track reset requests
   - Create `AuditLog` entries for security events

4. **Frontend Integration**
   - Create password reset form
   - Create OTP verification form
   - Create new password entry form
   - Create username recovery form

5. **Enhanced Features**
   - Add rate limiting to prevent abuse
   - Add email verification on signup
   - Add 2FA support
   - Add account lockout after failed attempts

## Troubleshooting

### SMTP Connection Issues
- Verify SMTP credentials in .env
- Check firewall allows port 2525
- Verify TLS is enabled

### Emails Not Sending
- Check SMTP_USERNAME and SMTP_PASSWORD
- Verify email address format
- Check application logs

### OTP Not Working
- Verify OTP_EXPIRE_MINUTES is reasonable
- Check system time is correct
- Clear OTP after password update

## Security Best Practices

1. ✅ Always use HTTPS for password reset links
2. ✅ Never log passwords or OTPs
3. ✅ Use generic error messages for security
4. ✅ Implement rate limiting
5. ✅ Use secure password requirements
6. ✅ Log security events for audit trail
7. ✅ Expire sessions after password reset
8. ✅ Send confirmation email after password change
"""

# This file is for documentation only
# Import services from the actual modules as needed
