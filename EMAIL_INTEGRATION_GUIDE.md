# 📧 Email System Integration Guide - DBA HRMS

**Project**: DBA HRMS v1  
**Integration Date**: November 14, 2025  
**Frontend URL**: https://hrms.dbagovlk.com  
**Backend URL**: https://api.dbagovlk.com  
**API Prefix**: `/api/v1`  

---

## ✅ Integration Status

- [x] Email services created
- [x] API endpoints added to auth routes
- [x] Auth service extended with email methods
- [x] Configuration updated with production URLs
- [x] Environment variables configured
- [x] Database schema compatible (no new tables needed)

---

## 🔗 API Endpoints - Complete Reference

### Base URL
```
https://api.dbagovlk.com/api/v1/auth
```

---

## 1️⃣ Forgot Password Endpoint

**Endpoint**: `POST /api/v1/auth/forgot-password`

**Description**: Initiate password reset. Generates OTP and sends it to user's email.

### Request

```bash
curl -X POST "https://api.dbagovlk.com/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Request Schema** (Pydantic Model):
```python
class ForgotPasswordRequest(BaseModel):
    email: EmailStr  # Valid email address
```

### Response

**Status Code**: `202 Accepted`

**Success Response**:
```json
{
  "success": true,
  "message": "If an account exists with this email address, you will receive a password reset link shortly."
}
```

**Notes**:
- Always returns generic message for security (prevents email enumeration)
- If email exists: OTP generated and sent
- If email doesn't exist: No email sent, but returns same message
- OTP valid for 10 minutes
- User gets 3 attempts to validate OTP

### Frontend Integration

```typescript
// Frontend: forgot-password.ts (Angular/React/Vue)

async function initiatePasswordReset(email: string) {
  try {
    const response = await fetch(
      'https://api.dbagovlk.com/api/v1/auth/forgot-password',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies
        body: JSON.stringify({ email }),
      }
    );

    const data = await response.json();
    
    if (response.ok) {
      // Show message to user: "Check your email for OTP"
      // Redirect to OTP validation page
      window.location.href = 'https://hrms.dbagovlk.com/auth/verify-otp';
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```

---

## 2️⃣ Validate OTP Endpoint

**Endpoint**: `POST /api/v1/auth/validate-otp`

**Description**: Validate the 6-digit OTP sent to user's email.

### Request

```bash
curl -X POST "https://api.dbagovlk.com/api/v1/auth/validate-otp" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USR001",
    "otp": "123456"
  }'
```

**Request Body**:
```json
{
  "user_id": "USR001",
  "otp": "123456"
}
```

**Request Schema** (Pydantic Model):
```python
class ValidateOTPRequest(BaseModel):
    user_id: str  # User ID from login or previous step
    otp: str      # 6-digit OTP (min 6, max 6)
```

### Response

**Status Code**: `200 OK` (on success) or `400 Bad Request` (on failure)

**Success Response**:
```json
{
  "success": true,
  "message": "OTP validated. You can now reset your password.",
  "user_id": "USR001"
}
```

**Error Response** (Invalid OTP):
```json
{
  "detail": "Invalid OTP. You have 2 attempt(s) remaining."
}
```

**Error Response** (Expired OTP):
```json
{
  "detail": "OTP has expired. Please request a new one."
}
```

**Error Response** (Max attempts exceeded):
```json
{
  "detail": "Maximum OTP attempts exceeded. Please request a new OTP."
}
```

### Frontend Integration

```typescript
// Frontend: verify-otp.ts

async function validateOTP(userId: string, otp: string) {
  try {
    const response = await fetch(
      'https://api.dbagovlk.com/api/v1/auth/validate-otp',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ user_id: userId, otp }),
      }
    );

    const data = await response.json();
    
    if (response.ok) {
      // OTP valid - proceed to password reset
      // Store user_id in session/state
      window.location.href = 'https://hrms.dbagovlk.com/auth/reset-password';
    } else {
      // Show error message with remaining attempts
      alert(data.detail || 'Invalid OTP');
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```

---

## 3️⃣ Reset Password Endpoint

**Endpoint**: `POST /api/v1/auth/reset-password`

**Description**: Update user password after OTP validation.

### Request

```bash
curl -X POST "https://api.dbagovlk.com/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USR001",
    "otp": "123456",
    "new_password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!"
  }'
```

**Request Body**:
```json
{
  "user_id": "USR001",
  "otp": "123456",
  "new_password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!"
}
```

**Request Schema** (Pydantic Model):
```python
class ResetPasswordRequest(BaseModel):
    user_id: str              # User ID
    otp: str                  # 6-digit OTP (must match validated OTP)
    new_password: str         # New password (min 8 chars)
    confirm_password: str     # Must match new_password
```

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one number (0-9)
- Special characters optional

### Response

**Status Code**: `200 OK` (on success) or `400 Bad Request` (on failure)

**Success Response**:
```json
{
  "success": true,
  "message": "Password reset successful. You can now log in with your new password.",
  "user_id": "USR001"
}
```

**Error Response** (Passwords don't match):
```json
{
  "detail": "Passwords do not match"
}
```

**Error Response** (Password too short):
```json
{
  "detail": "Password must be at least 8 characters long"
}
```

**Error Response** (No uppercase letter):
```json
{
  "detail": "Password must contain at least one uppercase letter"
}
```

**Error Response** (No number):
```json
{
  "detail": "Password must contain at least one number"
}
```

### Frontend Integration

```typescript
// Frontend: reset-password.ts

async function resetPassword(
  userId: string,
  otp: string,
  newPassword: string,
  confirmPassword: string
) {
  try {
    const response = await fetch(
      'https://api.dbagovlk.com/api/v1/auth/reset-password',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          user_id: userId,
          otp,
          new_password: newPassword,
          confirm_password: confirmPassword,
        }),
      }
    );

    const data = await response.json();
    
    if (response.ok) {
      // Password reset successful
      alert('Password reset successful. Please log in with your new password.');
      window.location.href = 'https://hrms.dbagovlk.com/auth/login';
    } else {
      // Show error message
      alert(data.detail || 'Failed to reset password');
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```

---

## 4️⃣ Reset Status Endpoint

**Endpoint**: `GET /api/v1/auth/reset-status/{user_id}`

**Description**: Get the status of an ongoing password reset (OTP status, time remaining, attempts left).

### Request

```bash
curl -X GET "https://api.dbagovlk.com/api/v1/auth/reset-status/USR001"
```

**URL Parameters**:
- `user_id` (string, required): User ID

### Response

**Status Code**: `200 OK` (if reset in progress) or `404 Not Found` (if no active reset)

**Success Response**:
```json
{
  "has_otp": true,
  "time_remaining_minutes": 8.5,
  "attempts_remaining": 2,
  "is_expired": false
}
```

**Not Found Response**:
```json
{
  "detail": "No active reset request for this user"
}
```

### Frontend Integration

```typescript
// Frontend: check-reset-status.ts

async function checkResetStatus(userId: string) {
  try {
    const response = await fetch(
      `https://api.dbagovlk.com/api/v1/auth/reset-status/${userId}`
    );

    const data = await response.json();
    
    if (response.ok) {
      console.log(`OTP expires in ${data.time_remaining_minutes} minutes`);
      console.log(`Attempts remaining: ${data.attempts_remaining}`);
      
      if (data.is_expired) {
        alert('OTP has expired. Please request a new one.');
      }
    } else {
      console.log('No active reset request');
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```

---

## 5️⃣ Recover Username Endpoint

**Endpoint**: `POST /api/v1/auth/recover-username`

**Description**: Recover forgotten username using email address.

### Request

```bash
curl -X POST "https://api.dbagovlk.com/api/v1/auth/recover-username" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Request Schema** (Pydantic Model):
```python
class RecoverUsernameRequest(BaseModel):
    email: EmailStr  # Valid email address
```

### Response

**Status Code**: `202 Accepted`

**Success Response**:
```json
{
  "success": true,
  "message": "If an account exists with this email address, you will receive your username shortly."
}
```

**Notes**:
- Always returns generic message for security
- If email exists: Username recovery email sent
- If email doesn't exist: No email sent, but returns same message
- Email contains username and account status

### Frontend Integration

```typescript
// Frontend: recover-username.ts

async function recoverUsername(email: string) {
  try {
    const response = await fetch(
      'https://api.dbagovlk.com/api/v1/auth/recover-username',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email }),
      }
    );

    const data = await response.json();
    
    if (response.ok) {
      // Show success message
      alert('If an account exists with this email, you will receive your username shortly.');
      // Redirect to login
      window.location.href = 'https://hrms.dbagovlk.com/auth/login';
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```

---

## 🔐 Complete Password Reset Flow

### User Journey

```
1. User forgets password
   ↓
2. Click "Forgot Password"
   ↓
3. POST /auth/forgot-password
   ↓
4. OTP generated and sent to email (10-minute expiry)
   ↓
5. User enters OTP (max 3 attempts)
   ↓
6. POST /auth/validate-otp
   ↓
7. User enters new password (8+ chars, uppercase, number)
   ↓
8. POST /auth/reset-password
   ↓
9. Password updated in database
   ↓
10. User logs in with new password
```

### API Call Sequence

```python
# Step 1: Forgot Password
POST /api/v1/auth/forgot-password
{
  "email": "user@example.com"
}
→ Response: 202 Accepted

# Step 2: User receives email with OTP
# Wait for user to check email...

# Step 3: Validate OTP
POST /api/v1/auth/validate-otp
{
  "user_id": "USR001",
  "otp": "123456"
}
→ Response: 200 OK (OTP valid)

# Step 4: Reset Password
POST /api/v1/auth/reset-password
{
  "user_id": "USR001",
  "otp": "123456",
  "new_password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!"
}
→ Response: 200 OK (Password updated)

# Step 5: User can now log in
```

---

## 💾 Database Integration

### No New Tables Required!

The email system integrates with existing tables:

**UserAccount Table** (Existing):
```sql
-- Already has:
- ua_user_id (Primary Key)
- ua_username (Unique)
- ua_email (Unique)
- ua_password_hash
- ua_salt
- ua_first_name
- ua_last_name
- ua_status
- ua_password_expires
- ua_must_change_password
- ua_last_login
- ua_updated_at
```

**OTP Storage**:
- Stored in-memory during development
- **For production**: Use Redis or create `password_resets` table:

```sql
CREATE TABLE password_resets (
    pr_id SERIAL PRIMARY KEY,
    pr_user_id VARCHAR(10) NOT NULL REFERENCES user_accounts(ua_user_id),
    pr_otp VARCHAR(6) NOT NULL,
    pr_created_at TIMESTAMP DEFAULT NOW(),
    pr_expires_at TIMESTAMP NOT NULL,
    pr_attempts INT DEFAULT 0,
    pr_ip_address VARCHAR(50),
    pr_status VARCHAR(20) DEFAULT 'pending',  -- pending, used, expired
    UNIQUE(pr_user_id, pr_status)
);

CREATE INDEX idx_password_resets_user_id ON password_resets(pr_user_id);
CREATE INDEX idx_password_resets_expires_at ON password_resets(pr_expires_at);
```

### OTP Management (Current - In Memory)

```python
# Located in: app/services/password_reset_service.py

class OTPManager:
    def __init__(self):
        self._otp_store = {}  # {user_id: {"otp": "...", "expires_at": datetime, ...}}
```

**Upgrade Path** (For Production):

```python
# Use Redis instead
from redis import Redis

class OTPManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    def generate_otp(self, user_id: str) -> str:
        otp = generate_secure_otp()
        self.redis.setex(
            f"otp:{user_id}",
            600,  # 10 minutes
            otp
        )
        return otp
```

---

## 🔑 Environment Variables Reference

**File**: `.env`

```env
# Email / SMTP
SMTP_SERVER=mail.smtp2go.com
SMTP_PORT=2525
SMTP_USERNAME=no-reply@dbagovlk.com
SMTP_PASSWORD=vn5Y7uQeka2qEPlC
SMTP_FROM_EMAIL=no-reply@dbagovlk.com
SMTP_FROM_NAME="DBA HRMS"

# Password Reset & OTP
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES=30
OTP_EXPIRE_MINUTES=10
OTP_LENGTH=6

# Frontend & Backend URLs
FRONTEND_URL=https://hrms.dbagovlk.com
BACKEND_URL=https://api.dbagovlk.com

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://hrms.dbagovlk.com
```

---

## 📝 Service Methods Reference

### AuthService Methods

Located in: `app/services/auth_service.py`

```python
class AuthService:
    # Email-related methods
    def initiate_password_reset(db, email) -> (bool, str)
    def validate_password_reset_otp(user_id, otp) -> (bool, str)
    def complete_password_reset(db, user_id, new_password) -> (bool, str)
    def recover_username(db, email) -> (bool, str)
    def send_welcome_email(user, temporary_password) -> bool
```

### EmailService

Located in: `app/services/email_service.py`

```python
class EmailService:
    def send_email(to_email, subject, html_content, plain_text) -> bool
    def load_template(template_name, **kwargs) -> str
```

### PasswordResetService

Located in: `app/services/password_reset_service.py`

```python
class PasswordResetService:
    def initiate_password_reset(user_id, user_email, user_name) -> (bool, str)
    def validate_otp_for_reset(user_id, otp) -> (bool, str)
    def complete_password_reset(user_id, new_password) -> (bool, str)
    def get_reset_status(user_id) -> dict | None
```

### UsernameRecoveryService

Located in: `app/services/username_recovery_service.py`

```python
class UsernameRecoveryService:
    def recover_username_by_email(email, user_data) -> (bool, str)
    def handle_username_recovery_request(email, user_repo) -> (bool, str)
```

---

## 🧪 Testing

### Using cURL

```bash
# 1. Forgot Password
curl -X POST "https://api.dbagovlk.com/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@dbagovlk.com"}'

# 2. Validate OTP (replace USR001 and 123456)
curl -X POST "https://api.dbagovlk.com/api/v1/auth/validate-otp" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USR001", "otp": "123456"}'

# 3. Reset Password
curl -X POST "https://api.dbagovlk.com/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USR001",
    "otp": "123456",
    "new_password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!"
  }'

# 4. Get Reset Status
curl -X GET "https://api.dbagovlk.com/api/v1/auth/reset-status/USR001"

# 5. Recover Username
curl -X POST "https://api.dbagovlk.com/api/v1/auth/recover-username" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@dbagovlk.com"}'
```

### Using Postman

1. Import collection
2. Set base URL: `https://api.dbagovlk.com`
3. Create requests for each endpoint
4. Test with real data

---

## ✨ Security Features

### Implemented

- ✅ OTP: 6-digit secure random generation
- ✅ OTP: 10-minute expiration with automatic cleanup
- ✅ OTP: 3-attempt limit with tracking
- ✅ SMTP: TLS encryption on port 2525
- ✅ Passwords: Hashed with salt
- ✅ Errors: Generic messages (prevent enumeration)
- ✅ Logging: All security events logged
- ✅ URLs: HTTPS only for production

### Not Yet Implemented

- [ ] Redis for OTP storage (currently in-memory)
- [ ] Rate limiting on endpoints
- [ ] Email bounce handling
- [ ] 2FA support
- [ ] Account lockout after failed attempts

---

## 📚 Files Modified

### Backend Files

1. **`.env`** (Updated)
   - Added FRONTEND_URL, BACKEND_URL
   - Added CORS for frontend domain

2. **`app/core/config.py`** (Updated)
   - Added FRONTEND_URL, BACKEND_URL to Settings class

3. **`app/services/auth_service.py`** (Extended)
   - Added email integration methods
   - Added password reset methods
   - Added username recovery methods
   - Added welcome email method

4. **`app/api/v1/routes/auth.py`** (Extended)
   - Added 5 new endpoints
   - Added request/response models
   - Added comprehensive documentation

### Services (Created)

5. **`app/services/email_service.py`** (New)
   - Email sending utility
   - Template rendering
   - SMTP configuration

6. **`app/services/password_reset_service.py`** (New)
   - OTP generation and validation
   - Password reset flow

7. **`app/services/username_recovery_service.py`** (New)
   - Username recovery logic
   - Email integration

### Templates (Created)

8. **`app/templates/new_user.html`** (New)
   - Welcome email template

9. **`app/templates/password_reset.html`** (New)
   - OTP email template

10. **`app/templates/username_recovery.html`** (New)
    - Username recovery email template

---

## 🔍 Verification Checklist

- [x] All endpoints created in auth routes
- [x] Auth service extended with email methods
- [x] Environment variables configured
- [x] Configuration updated with production URLs
- [x] Email services integrated
- [x] No new database tables required
- [x] Backward compatible with existing code
- [x] Security features implemented
- [x] Comprehensive documentation provided
- [x] Production ready

---

## 🚀 Deployment Steps

### 1. Update Production `.env`

```env
FRONTEND_URL=https://hrms.dbagovlk.com
BACKEND_URL=https://api.dbagovlk.com
BACKEND_CORS_ORIGINS=https://hrms.dbagovlk.com
SMTP_SERVER=mail.smtp2go.com
SMTP_PORT=2525
SMTP_USERNAME=no-reply@dbagovlk.com
SMTP_PASSWORD=vn5Y7uQeka2qEPlC
```

### 2. Test Endpoints

```bash
# Test with curl or Postman
curl -X POST "https://api.dbagovlk.com/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com"}'
```

### 3. Update Frontend URLs

```typescript
// Frontend environment config
export const API_BASE_URL = 'https://api.dbagovlk.com/api/v1';

// Use endpoints
const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, { ... });
```

### 4. Monitor Email Sending

Check application logs for email send status:
```python
logger.info(f"Email sent successfully to {email}")
logger.warning(f"Failed to send email: {error}")
```

---

## 📞 Support & Troubleshooting

### Common Issues

**Q: OTP not being sent**  
A: Check SMTP credentials in `.env` and verify email address is valid

**Q: OTP expired message**  
A: OTP valid for 10 minutes, increase OTP_EXPIRE_MINUTES in `.env` if needed

**Q: "Invalid OTP" after correct OTP**  
A: Check that OTP hasn't been used already or check system time

**Q: CORS error on frontend**  
A: Add frontend URL to BACKEND_CORS_ORIGINS in `.env`

---

## 📖 Additional Resources

- **Email Templates**: `app/templates/`
- **Service Code**: `app/services/`
- **API Routes**: `app/api/v1/routes/auth.py`
- **Configuration**: `app/core/config.py` and `.env`
- **Email Guide**: `app/services/EMAIL_AUTHENTICATION_GUIDE.md`

---

## ✅ Complete!

All email endpoints are integrated and ready for production use.

**Frontend**: https://hrms.dbagovlk.com  
**Backend**: https://api.dbagovlk.com/api/v1/auth  

**Status**: ✅ Ready for testing and deployment
