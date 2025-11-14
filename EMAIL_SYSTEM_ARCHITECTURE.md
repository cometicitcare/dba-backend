# Email System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DBA HRMS Email System                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                        User/Client Layer                             │
│  (Frontend - Password Reset, Username Recovery, New User Forms)      │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────────┐
│                        API Layer                                      │
│  POST /api/v1/auth/forgot-password                                   │
│  POST /api/v1/auth/validate-otp                                      │
│  POST /api/v1/auth/reset-password                                    │
│  GET  /api/v1/auth/reset-status/{user_id}                           │
│  POST /api/v1/auth/recover-username                                  │
│  POST /api/v1/auth/register-new-user                                 │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────────┐
│                        Services Layer                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  PasswordResetService          UsernameRecoveryService       │   │
│  │  ├── initiate_password_reset  ├── recover_username_by_email  │   │
│  │  ├── validate_otp_for_reset   ├── verify_email_exists       │   │
│  │  ├── complete_password_reset  └── handle_recovery_request    │   │
│  │  └── get_reset_status                                        │   │
│  └──────────────┬──────────────────────────────────┬────────────┘   │
│                 │                                  │                 │
│  ┌──────────────▼──────────────────────────────────▼────────────┐   │
│  │              EmailService                                    │   │
│  │  ├── send_email(to, subject, html_content)                  │   │
│  │  └── load_template(name, **kwargs)                          │   │
│  └──────────────┬───────────────────────────────────────────────┘   │
└────────────────┼──────────────────────────────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────────────────────────────┐
│                   External Services                                    │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  SMTP (mail.smtp2go.com:2525)                                   │ │
│  │  Username: no-reply@dbagovlk.com                                │ │
│  │  Port: 2525 (TLS)                                               │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Email Client   │
                    │  (User Inbox)   │
                    └─────────────────┘
```

## Component Architecture

```
app/
│
├── services/
│   ├── email_service.py
│   │   └── EmailService
│   │       ├── send_email()
│   │       └── load_template()
│   │
│   ├── password_reset_service.py
│   │   ├── OTPManager
│   │   │   ├── generate_otp()
│   │   │   ├── validate_otp()
│   │   │   ├── clear_otp()
│   │   │   └── get_otp_status()
│   │   │
│   │   └── PasswordResetService
│   │       ├── initiate_password_reset()
│   │       ├── validate_otp_for_reset()
│   │       ├── complete_password_reset()
│   │       └── get_reset_status()
│   │
│   └── username_recovery_service.py
│       └── UsernameRecoveryService
│           ├── recover_username_by_email()
│           ├── verify_email_exists()
│           └── handle_username_recovery_request()
│
├── templates/
│   ├── new_user.html
│   ├── password_reset.html
│   └── username_recovery.html
│
├── core/
│   └── config.py
│       └── Settings (Email config)
│
└── api/v1/
    └── auth_email_example.py
        ├── forgot_password()
        ├── validate_otp()
        ├── reset_password()
        ├── get_reset_status()
        ├── recover_username()
        └── register_new_user()
```

## Data Flow - Password Reset

```
┌──────────────┐
│  User        │
│  (Browser)   │
└──────┬───────┘
       │ 1. Submits email
       │    POST /forgot-password
       ▼
┌──────────────────────────────┐
│  API Endpoint                │
│  forgot_password()           │
└──────┬───────────────────────┘
       │ 2. Lookup user by email
       ▼
┌──────────────────────────────┐
│  User Repository             │
│  get_by_email(email)        │
└──────┬───────────────────────┘
       │ 3. Initiate password reset
       ▼
┌──────────────────────────────┐
│  PasswordResetService        │
│  initiate_password_reset()   │
│  ├─ Generate OTP             │
│  └─ Call EmailService        │
└──────┬───────────────────────┘
       │ 4. Send email
       ▼
┌──────────────────────────────┐
│  EmailService                │
│  ├─ Load template            │
│  ├─ Render variables         │
│  └─ send_email()             │
└──────┬───────────────────────┘
       │ 5. Connect to SMTP
       ▼
┌──────────────────────────────┐
│  SMTP Server                 │
│  (mail.smtp2go.com:2525)    │
└──────┬───────────────────────┘
       │ 6. Send email with OTP
       ▼
┌──────────────────────────────┐
│  User Email Inbox            │
│  (Contains OTP)              │
└──────────────────────────────┘

Later: User enters OTP
       │ 7. POST /validate-otp
       ▼
┌──────────────────────────────┐
│  PasswordResetService        │
│  validate_otp_for_reset()    │
│  ├─ Check expiry             │
│  ├─ Check attempts           │
│  └─ Validate OTP             │
└──────┬───────────────────────┘
       │ Valid? ✓
       ▼
┌──────────────────────────────┐
│  User enters new password    │
│  POST /reset-password        │
└──────┬───────────────────────┘
       │ 8. Update password
       ▼
┌──────────────────────────────┐
│  Auth Service                │
│  update_password()           │
└──────┬───────────────────────┘
       │ 9. Password updated
       ▼
┌──────────────────────────────┐
│  PasswordResetService        │
│  complete_password_reset()   │
│  ├─ Clear OTP                │
│  └─ Success                  │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  User can now login          │
│  with new password           │
└──────────────────────────────┘
```

## Data Flow - Username Recovery

```
┌──────────────┐
│  User        │
│  (Browser)   │
└──────┬───────┘
       │ 1. Submits email
       │    POST /recover-username
       ▼
┌──────────────────────────────┐
│  API Endpoint                │
│  recover_username()          │
└──────┬───────────────────────┘
       │ 2. Lookup user by email
       ▼
┌──────────────────────────────┐
│  User Repository             │
│  get_by_email(email)        │
└──────┬───────────────────────┘
       │ 3. If found, send recovery email
       │    (If NOT found, still say success)
       ▼
┌──────────────────────────────┐
│  UsernameRecoveryService     │
│  recover_username_by_email() │
│  ├─ Prepare user data        │
│  └─ Call EmailService        │
└──────┬───────────────────────┘
       │ 4. Send email
       ▼
┌──────────────────────────────┐
│  EmailService                │
│  ├─ Load template            │
│  ├─ Render variables         │
│  └─ send_email()             │
└──────┬───────────────────────┘
       │ 5. Connect to SMTP
       ▼
┌──────────────────────────────┐
│  SMTP Server                 │
│  (mail.smtp2go.com:2525)    │
└──────┬───────────────────────┘
       │ 6. Send email with username
       ▼
┌──────────────────────────────┐
│  User Email Inbox            │
│  (Contains username)         │
└──────────────────────────────┘

Security: Always return "If account exists..."
message to prevent email enumeration attacks
```

## OTP Lifecycle

```
Generate OTP
├─ Generate 6 random digits: "123456"
├─ Calculate expiry time: now + 10 minutes
├─ Store in OTPManager
│  {
│    "otp": "123456",
│    "expires_at": 2025-11-14 15:10:00,
│    "attempts": 0,
│    "created_at": 2025-11-14 15:00:00
│  }
└─ Return OTP to PasswordResetService

Email OTP
├─ Load password_reset.html template
├─ Replace {{otp}} with "123456"
├─ Send via SMTP
└─ User receives email

Validate OTP
├─ User enters OTP in form
├─ Check if OTP exists for user
├─ Check if OTP not expired
│  └─ If expired: Delete OTP, return error
├─ Check attempts < 3
│  └─ If >= 3: Delete OTP, return error
├─ Compare OTP (123456 == 123456?)
│  ├─ Match: Return success
│  └─ No match: Increment attempts, return error
└─ Continue with password reset

Clear OTP
├─ After successful password reset
├─ Delete OTP from OTPManager
└─ User cannot reuse same OTP

OTP Expiry
└─ After 10 minutes, OTP becomes invalid
   └─ User must request new OTP
```

## Template Variable Injection

```
Template File: password_reset.html
Contains: {{otp}}, {{user_name}}, {{otp_expiry}}

EmailService.load_template("password_reset", 
    otp="123456",
    user_name="John",
    otp_expiry=10
)

Process:
├─ Load HTML file
├─ Replace {{otp}} → "123456"
├─ Replace {{user_name}} → "John"
├─ Replace {{otp_expiry}} → "10"
└─ Return rendered HTML

Output: Full HTML with all variables replaced
```

## Configuration Hierarchy

```
.env (Environment Variables)
├─ SMTP_SERVER=mail.smtp2go.com
├─ SMTP_PORT=2525
├─ SMTP_USERNAME=no-reply@dbagovlk.com
├─ SMTP_PASSWORD=vn5Y7uQeka2qEPlC
├─ SMTP_FROM_EMAIL=no-reply@dbagovlk.com
├─ SMTP_FROM_NAME="DBA HRMS"
├─ RESET_PASSWORD_TOKEN_EXPIRE_MINUTES=30
├─ OTP_EXPIRE_MINUTES=10
└─ OTP_LENGTH=6
        │
        ▼
app/core/config.py (Settings Class)
├─ SMTP_SERVER
├─ SMTP_PORT
├─ SMTP_USERNAME
├─ SMTP_PASSWORD
├─ SMTP_FROM_EMAIL
├─ SMTP_FROM_NAME
├─ RESET_PASSWORD_TOKEN_EXPIRE_MINUTES
├─ OTP_EXPIRE_MINUTES
└─ OTP_LENGTH
        │
        ▼
Services (Use settings)
├─ EmailService
├─ PasswordResetService
└─ UsernameRecoveryService
```

## Request/Response Flow

### Password Reset Request
```
Client Request:
┌─────────────────────────────────────────┐
│ POST /api/v1/auth/forgot-password      │
│                                         │
│ {                                       │
│   "email": "john@example.com"          │
│ }                                       │
└─────────────────────────────────────────┘
                    │
                    ▼
Server Processing:
┌─────────────────────────────────────────┐
│ 1. Find user by email                  │
│ 2. Generate OTP                        │
│ 3. Send email                          │
└─────────────────────────────────────────┘
                    │
                    ▼
Server Response:
┌─────────────────────────────────────────┐
│ HTTP 202 Accepted                       │
│                                         │
│ {                                       │
│   "success": true,                      │
│   "message": "If account exists..."    │
│ }                                       │
└─────────────────────────────────────────┘
```

### OTP Validation Request
```
Client Request:
┌─────────────────────────────────────────┐
│ POST /api/v1/auth/validate-otp         │
│                                         │
│ {                                       │
│   "user_id": 1,                        │
│   "otp": "123456"                      │
│ }                                       │
└─────────────────────────────────────────┘
                    │
                    ▼
Server Processing:
┌─────────────────────────────────────────┐
│ 1. Check OTP exists                    │
│ 2. Check not expired                   │
│ 3. Check attempts < 3                  │
│ 4. Validate OTP matches                │
└─────────────────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
      Valid                 Invalid
         │                     │
         ▼                     ▼
    Success          Error Response
    {                {
      "success":       "success": false,
      true,            "message": "Invalid..."
      "message":   }
      "OTP valid"
    }
```

## Security Considerations

```
┌────────────────────────────────────────────────────────┐
│              Security Measures                         │
└────────────────────────────────────────────────────────┘

Input Validation
├─ Email format validation
├─ OTP format validation (6 digits)
├─ Password strength requirements
│  └─ Min 8 characters
│  └─ Uppercase letter
│  └─ Lowercase letter
│  └─ Number
│  └─ Special character (optional)
└─ User input sanitization

Output Security
├─ Generic error messages (no email enumeration)
├─ Never log passwords
├─ Never log OTPs
├─ Hash passwords before storage
└─ Use HTTPS for all endpoints

Rate Limiting
├─ Limit password reset attempts per email
├─ Limit OTP generation attempts
├─ Limit OTP validation attempts (3 max)
└─ Limit username recovery attempts

Session Security
├─ Clear sessions on password reset
├─ Force password change on first login
├─ Invalidate all existing sessions
└─ Send security notification email

Data Protection
├─ SMTP uses TLS encryption
├─ Store passwords hashed
├─ OTP expires after 10 minutes
├─ Clear OTP after use
└─ Audit log all security events
```

## Integration Points

```
Email System
    │
    ├─ Connects to: User Repository
    │  └─ get_by_email()
    │  └─ get_by_id()
    │  └─ update()
    │
    ├─ Connects to: Auth Service
    │  └─ get_password_hash()
    │  └─ update_password()
    │
    ├─ Connects to: Audit Service
    │  └─ log_event()
    │
    └─ Connects to: API Layer
       └─ HTTP endpoints
       └─ Request/response models
       └─ Authentication middleware
```

---

**This architecture ensures:**
- ✅ Clear separation of concerns
- ✅ Reusable services
- ✅ Secure OTP handling
- ✅ Template-based emails
- ✅ Dependency injection
- ✅ Configuration management
- ✅ Error handling & logging
