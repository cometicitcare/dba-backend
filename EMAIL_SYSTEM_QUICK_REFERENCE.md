# Email System Quick Reference

## 📧 What Was Created

### Configuration
- ✅ SMTP settings in `.env`
- ✅ Email config in `app/core/config.py`

### Services (3 services)
1. **EmailService** - Core email sending
2. **PasswordResetService** - Password reset with OTP
3. **UsernameRecoveryService** - Username recovery

### Email Templates (3 templates)
1. **new_user.html** - Welcome email for new accounts
2. **password_reset.html** - OTP-based password reset
3. **username_recovery.html** - Recover forgotten username

### Documentation
- `SETUP_README.md` - Complete setup guide
- `EMAIL_AUTHENTICATION_GUIDE.md` - Detailed reference
- `EMAIL_DEPENDENCIES.md` - Dependencies info
- `auth_email_example.py` - Example API endpoints

## 🚀 Quick Start

### 1. Send Email

```python
from app.services.email_service import email_service

email_service.send_email(
    to_email="user@example.com",
    subject="Hello",
    html_content="<p>Hello World</p>"
)
```

### 2. Password Reset Flow

```python
from app.services.password_reset_service import password_reset_service

# Step 1: User clicks "Forgot Password"
password_reset_service.initiate_password_reset(
    user_id=1,
    user_email="john@example.com",
    user_name="John"
)
# OTP sent to email

# Step 2: User enters OTP
is_valid, msg = password_reset_service.validate_otp_for_reset(
    user_id=1,
    otp="123456"
)

# Step 3: User enters new password
if is_valid:
    password_reset_service.complete_password_reset(
        user_id=1,
        new_password="NewPassword123!"
    )
```

### 3. Username Recovery

```python
from app.services.username_recovery_service import username_recovery_service

username_recovery_service.recover_username_by_email(
    email="john@example.com",
    user_data={
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "status": "active"
    }
)
```

## 📁 File Locations

```
.env                                       # SMTP settings
├── SMTP_SERVER=mail.smtp2go.com
├── SMTP_PORT=2525
├── SMTP_USERNAME=no-reply@dbagovlk.com
├── SMTP_PASSWORD=vn5Y7uQeka2qEPlC

app/core/config.py                        # Email config (updated)

app/services/
├── email_service.py                      # Email sending
├── password_reset_service.py             # Password reset with OTP
├── username_recovery_service.py          # Username recovery
└── EMAIL_AUTHENTICATION_GUIDE.md         # Detailed guide

app/templates/
├── new_user.html                         # Welcome email
├── password_reset.html                   # OTP email
└── username_recovery.html                # Username recovery email

app/api/v1/auth_email_example.py          # Example endpoints
```

## 🔧 Key Classes & Methods

### EmailService
```python
email_service.send_email(to_email, subject, html_content, plain_text)
email_service.load_template(template_name, **kwargs)
```

### PasswordResetService
```python
password_reset_service.initiate_password_reset(user_id, user_email, user_name)
password_reset_service.validate_otp_for_reset(user_id, otp)
password_reset_service.complete_password_reset(user_id, new_password)
password_reset_service.get_reset_status(user_id)
```

### UsernameRecoveryService
```python
username_recovery_service.recover_username_by_email(email, user_data)
username_recovery_service.handle_username_recovery_request(email, user_repo)
```

## 📧 Email Template Variables

### new_user.html
```python
{
    "user_name": "John",
    "username": "john_doe",
    "temporary_password": "TempPass123!",
    "email": "john@example.com",
    "login_url": "https://...",
    "support_url": "https://...",
    "privacy_url": "https://...",
    "terms_url": "https://..."
}
```

### password_reset.html
```python
{
    "user_name": "John",
    "otp": "123456",
    "otp_expiry": 10,
    "reset_password_url": "https://...",
    "support_url": "https://..."
}
```

### username_recovery.html
```python
{
    "username": "john_doe",
    "email": "john@example.com",
    "account_status": "Active",
    "user_name": "John",
    "login_url": "https://...",
    "support_url": "https://..."
}
```

## 🔐 OTP Configuration

From `.env`:
```env
OTP_LENGTH=6                          # 6-digit OTP
OTP_EXPIRE_MINUTES=10                 # Valid for 10 minutes
OTP_MAX_ATTEMPTS=3                    # Max 3 attempts to enter OTP
```

## 📋 Password Reset Flow Diagram

```
User → Forgot Password
    ↓
Verify Email
    ↓
Generate 6-digit OTP
    ↓
Send Email with OTP
    ↓
User enters OTP (max 3 attempts)
    ↓
Validate OTP (check expiry)
    ↓
User enters new password
    ↓
Update password in database
    ↓
Clear OTP
    ↓
Success message
    ↓
User logs in with new password
```

## 🔗 API Endpoints (from example)

```
POST /api/v1/auth/forgot-password
  - Sends OTP to email
  - Request: { "email": "..." }

POST /api/v1/auth/validate-otp
  - Validates OTP
  - Request: { "user_id": 1, "otp": "123456" }

POST /api/v1/auth/reset-password
  - Updates password after OTP validation
  - Request: { "user_id": 1, "otp": "123456", "new_password": "..." }

GET /api/v1/auth/reset-status/{user_id}
  - Gets OTP status and time remaining
  - Returns: { "has_otp": true, "time_remaining_minutes": 5, ... }

POST /api/v1/auth/recover-username
  - Sends username to registered email
  - Request: { "email": "..." }

POST /api/v1/auth/register-new-user
  - Creates new user and sends welcome email
  - Request: { "email": "...", "username": "...", ... }
```

## ✅ Integration Checklist

- [ ] SMTP credentials configured in `.env` ✓ Done
- [ ] Services created and tested
- [ ] API endpoints created (copy from example)
- [ ] Template URLs updated to your domain
- [ ] User repository integrated
- [ ] Database schema updated (password_reset tracking)
- [ ] Frontend forms created
- [ ] Rate limiting configured
- [ ] Security logging implemented
- [ ] Testing completed

## 📚 Documentation Files

| File | Content |
|------|---------|
| `SETUP_README.md` | Complete setup and integration guide |
| `EMAIL_AUTHENTICATION_GUIDE.md` | Comprehensive service documentation |
| `EMAIL_DEPENDENCIES.md` | Package requirements |
| `auth_email_example.py` | Example API implementations |
| `EMAIL_SYSTEM_QUICK_REFERENCE.md` | This file |

## 🆘 Troubleshooting

### Email not sending?
1. Check `.env` SMTP credentials
2. Verify email format is valid
3. Check application logs
4. Ensure port 2525 is not blocked

### OTP not working?
1. Verify OTP_EXPIRE_MINUTES value
2. Check system clock is correct
3. Ensure user_id is correct
4. Try generating new OTP

### Import errors?
1. Verify all Python packages installed
2. Check file paths are correct
3. Run tests to verify setup

## 🎯 Next Steps

1. **Copy API endpoints** from `auth_email_example.py` to your router
2. **Update template URLs** to your production domain
3. **Create API tests** for all endpoints
4. **Create frontend forms** for password reset and recovery
5. **Setup monitoring** for email delivery and security events
6. **Deploy to production** with proper security

## 📝 Notes

- All services use dependency injection pattern
- OTP stored in-memory (use Redis in production)
- Email templates use `{{variable}}` syntax
- Services return `(success, message)` tuples
- Generic error messages used for security
- All services are singleton instances

## 🔒 Security Best Practices Implemented

✅ Generic error messages (prevent email enumeration)  
✅ OTP with expiration time  
✅ Maximum OTP attempts (3)  
✅ Secure random OTP generation  
✅ HTML email templates  
✅ Environment-based configuration  
✅ Logging for audit trail  

## Version Info

- Python: 3.10+
- FastAPI: 0.100.0+
- Pydantic: 2.0.0+
- Created: 2025-11-14

---

**Ready to integrate! Follow SETUP_README.md for detailed instructions.**
