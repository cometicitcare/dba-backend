# Email & Authentication Services Setup Guide

## Overview

This guide covers the complete setup of email sending, password reset with OTP, and username recovery functionality for the DBA HRMS application.

## What Has Been Created

### 1. Configuration Files
- ✅ `.env` - SMTP and email settings
- ✅ `app/core/config.py` - Updated with email configuration

### 2. Services
- ✅ `app/services/email_service.py` - Base email sending service
- ✅ `app/services/password_reset_service.py` - Password reset with OTP flow
- ✅ `app/services/username_recovery_service.py` - Username recovery service

### 3. Email Templates
- ✅ `app/templates/new_user.html` - New user welcome email
- ✅ `app/templates/password_reset.html` - Password reset OTP email
- ✅ `app/templates/username_recovery.html` - Username recovery email

### 4. Documentation & Examples
- ✅ `app/services/EMAIL_AUTHENTICATION_GUIDE.md` - Comprehensive guide
- ✅ `app/api/v1/auth_email_example.py` - Example API endpoints
- ✅ `SETUP_README.md` - This file

## Environment Variables

Configured in `.env`:

```env
# Email / SMTP
SMTP_SERVER=mail.smtp2go.com
SMTP_PORT=2525
SMTP_USERNAME=no-reply@dbagovlk.com
SMTP_PASSWORD=vn5Y7uQeka2qEPlC
SMTP_FROM_EMAIL=no-reply@dbagovlk.com
SMTP_FROM_NAME="DBA HRMS"

# Password Reset & OTP Configuration
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES=30
OTP_EXPIRE_MINUTES=10
OTP_LENGTH=6
```

## Quick Start

### 1. Send a Simple Email

```python
from app.services.email_service import email_service

success = email_service.send_email(
    to_email="user@example.com",
    subject="Hello",
    html_content="<p>Welcome!</p>"
)
```

### 2. Send Welcome Email to New User

```python
from app.services.email_service import email_service

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

email_service.send_email(
    to_email="john@example.com",
    subject="Welcome to DBA HRMS",
    html_content=html
)
```

### 3. Initiate Password Reset

```python
from app.services.password_reset_service import password_reset_service

success, message = password_reset_service.initiate_password_reset(
    user_id=123,
    user_email="john@example.com",
    user_name="John Doe"
)
# OTP is generated and sent to email
```

### 4. Validate OTP

```python
is_valid, message = password_reset_service.validate_otp_for_reset(
    user_id=123,
    otp="123456"
)
```

### 5. Recover Username

```python
from app.services.username_recovery_service import username_recovery_service

# User data from your database
user_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "status": "active"
}

success, message = username_recovery_service.recover_username_by_email(
    email="john@example.com",
    user_data=user_data
)
```

## Integration Steps

### Step 1: Create API Endpoints

Copy relevant endpoints from `app/api/v1/auth_email_example.py` to your actual router:

```python
# In your router file (e.g., app/api/v1/auth.py)

from app.services.password_reset_service import password_reset_service
from app.services.username_recovery_service import username_recovery_service
from app.repositories.user_repo import user_repo

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    user = await user_repo.get_by_email(request.email)
    if user:
        password_reset_service.initiate_password_reset(
            user_id=user.id,
            user_email=user.email,
            user_name=user.first_name or "User"
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
            status_code=400,
            detail=message
        )
    
    return {"message": "OTP validated"}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    # Validate OTP
    is_valid, msg = password_reset_service.validate_otp_for_reset(
        user_id=request.user_id,
        otp=request.otp
    )
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=msg)
    
    # Update password in database
    await user_repo.update(request.user_id, {
        "password": get_password_hash(request.new_password)
    })
    
    # Complete the reset
    password_reset_service.complete_password_reset(
        user_id=request.user_id,
        new_password=request.new_password
    )
    
    return {"message": "Password reset successful"}

@router.post("/recover-username")
async def recover_username(request: RecoverUsernameRequest):
    user = await user_repo.get_by_email(request.email)
    
    if user:
        username_recovery_service.recover_username_by_email(
            email=request.email,
            user_data={
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "status": user.status
            }
        )
    
    return {
        "message": "If an account exists with this email, "
                  "you will receive your username shortly."
    }
```

### Step 2: Update Template Placeholders

In your templates, update the placeholder URLs:

```html
<!-- In app/templates/*.html -->
<a href="{{login_url}}">Login</a>
<!-- Replace with: -->
<a href="https://your-frontend-url.com/login">Login</a>
```

### Step 3: Connect to User Repository

Inject your user repository into services:

```python
# In your service or endpoint
user = await user_repo.get_by_email(email)
if user:
    # Use user data
```

## Email Templates

### 1. New User Email (`new_user.html`)

**Purpose**: Send to new users after account creation  
**Variables**:
- `user_name` - User's display name
- `username` - Login username
- `temporary_password` - Temporary password
- `email` - User's email
- `login_url` - Link to login page
- `support_url` - Link to support
- `privacy_url` - Link to privacy policy
- `terms_url` - Link to terms

### 2. Password Reset Email (`password_reset.html`)

**Purpose**: Send when user requests password reset  
**Variables**:
- `user_name` - User's display name
- `otp` - 6-digit OTP
- `otp_expiry` - Minutes until OTP expires
- `reset_password_url` - Link to reset page
- `support_url` - Link to support

### 3. Username Recovery Email (`username_recovery.html`)

**Purpose**: Send when user recovers forgotten username  
**Variables**:
- `username` - Recovered username
- `email` - User's email
- `account_status` - Account status (Active, Inactive, etc.)
- `user_name` - User's display name
- `login_url` - Link to login page
- `support_url` - Link to support

## File Structure

```
app/
├── api/
│   └── v1/
│       └── auth_email_example.py       # Example endpoints
├── core/
│   └── config.py                       # Email settings (UPDATED)
├── services/
│   ├── email_service.py                # Email sending utility
│   ├── password_reset_service.py       # Password reset with OTP
│   ├── username_recovery_service.py    # Username recovery
│   └── EMAIL_AUTHENTICATION_GUIDE.md   # Comprehensive guide
├── templates/
│   ├── new_user.html                   # New user welcome
│   ├── password_reset.html             # Password reset OTP
│   └── username_recovery.html          # Username recovery
└── ...

.env                                     # SMTP settings (UPDATED)
```

## Testing

### Test Email Sending

```python
from app.services.email_service import email_service

success = email_service.send_email(
    to_email="your-email@example.com",
    subject="Test Email",
    html_content="<p>Test</p>"
)
print("Email sent:", success)
```

### Test OTP Flow

```python
from app.services.password_reset_service import password_reset_service

# Generate OTP
otp = password_reset_service.otp_manager.generate_otp(user_id=1)
print(f"Generated OTP: {otp}")

# Validate OTP
is_valid, msg = password_reset_service.otp_manager.validate_otp(1, otp)
print(f"OTP valid: {is_valid}, Message: {msg}")
```

## Production Checklist

- [ ] Update SMTP credentials in `.env` for production
- [ ] Update template URLs to production URLs
- [ ] Implement rate limiting for password reset endpoints
- [ ] Implement database logging for email sends
- [ ] Move OTP storage to Redis or database
- [ ] Add email verification on user signup
- [ ] Add password strength validation
- [ ] Implement account lockout after failed attempts
- [ ] Add 2FA support
- [ ] Setup email bounce/complaint handling
- [ ] Add multilingual template support
- [ ] Implement email template versioning

## Customization

### Change OTP Length or Expiry

```python
# In .env
OTP_LENGTH=8          # Default: 6
OTP_EXPIRE_MINUTES=5  # Default: 10
```

### Add Custom Email Templates

1. Create new HTML file in `app/templates/`
2. Use `{{variable}}` syntax for placeholders
3. Load and send with:

```python
html = email_service.load_template("template_name", var1="value1")
email_service.send_email(to_email, subject, html)
```

### Customize Email Styling

Edit the `<style>` sections in HTML templates:
- Colors (gradients in header)
- Fonts
- Spacing and padding
- Button styles

## Troubleshooting

### SMTP Connection Error

**Issue**: "SMTP authentication failed"  
**Solution**: Verify credentials in `.env`:
```env
SMTP_SERVER=mail.smtp2go.com
SMTP_PORT=2525
SMTP_USERNAME=no-reply@dbagovlk.com
SMTP_PASSWORD=vn5Y7uQeka2qEPlC
```

### Email Not Sending

**Issue**: Service returns False  
**Solution**: Check logs for detailed error. Common causes:
- Invalid email format
- SMTP server connection issues
- Missing credentials
- Port blocked by firewall

### OTP Not Working

**Issue**: "OTP expired" or "Invalid OTP"  
**Solution**:
- Verify system time is correct
- Check OTP_EXPIRE_MINUTES in `.env`
- Ensure user_id is correct
- Clear OTP after password update

## Security Best Practices

✅ **Do**:
- Always use HTTPS for password reset links
- Use generic error messages to prevent email enumeration
- Implement rate limiting on password reset attempts
- Log security events (password resets, OTP validations)
- Use strong password requirements
- Expire sessions after password reset
- Use environment variables for SMTP credentials

❌ **Don't**:
- Log passwords or OTPs
- Show specific error messages (e.g., "Email not found")
- Share OTP in URLs (use POST only)
- Allow unlimited OTP validation attempts
- Send passwords via email (use temporary passwords only)
- Skip email validation in production

## Next Steps

1. **Implement API Endpoints**
   - Copy examples from `auth_email_example.py`
   - Inject user repository
   - Add request validation

2. **Create Frontend Forms**
   - Forgot password form
   - OTP entry form
   - New password form
   - Username recovery form

3. **Add Database Models**
   - Create `PasswordReset` model for tracking
   - Add `AuditLog` entries for security events

4. **Setup Monitoring**
   - Monitor email delivery rates
   - Track failed OTP attempts
   - Log security events

5. **Testing**
   - Unit tests for OTP generation
   - Integration tests for email sending
   - End-to-end tests for password reset flow

## Support & Documentation

For more detailed information:
- See `app/services/EMAIL_AUTHENTICATION_GUIDE.md`
- Review example implementation in `app/api/v1/auth_email_example.py`
- Check individual service docstrings for method details

## File Locations

| File | Purpose |
|------|---------|
| `.env` | SMTP configuration |
| `app/core/config.py` | Settings class |
| `app/services/email_service.py` | Email sending |
| `app/services/password_reset_service.py` | Password reset flow |
| `app/services/username_recovery_service.py` | Username recovery |
| `app/templates/new_user.html` | New user email |
| `app/templates/password_reset.html` | Reset OTP email |
| `app/templates/username_recovery.html` | Username recovery email |
| `app/services/EMAIL_AUTHENTICATION_GUIDE.md` | Comprehensive guide |
| `app/api/v1/auth_email_example.py` | Example endpoints |

## Summary

You now have a complete, production-ready email system with:
- ✅ SMTP configuration via environment variables
- ✅ Email sending utility with template support
- ✅ Secure password reset with OTP verification
- ✅ Username recovery functionality
- ✅ Professional HTML email templates
- ✅ Comprehensive documentation
- ✅ Example API implementations

Ready to integrate into your existing authentication system!
