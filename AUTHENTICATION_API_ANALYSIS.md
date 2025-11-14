# User Authentication APIs - Analysis & Summary

## Overview
Your application uses **cookie-based JWT authentication** with FastAPI. The authentication system is modular and well-organized with proper separation of concerns across services, repositories, and middleware.

---

## 🔑 Authentication Endpoints

### Authentication Routes (`/api/v1/auth/`)
Location: `app/api/v1/routes/auth.py`

#### 1. **POST `/auth/register`**
- **Purpose**: Register a new user with role assignment
- **Request Body**:
  ```json
  {
    "ua_username": "string (3-50 chars)",
    "ua_password": "string (8+ chars, must include uppercase, lowercase, digit, special char)",
    "confirmPassword": "string (must match password)",
    "ua_email": "valid-email@domain.com",
    "ua_first_name": "optional string (max 50)",
    "ua_last_name": "optional string (max 50)",
    "ua_phone": "optional string (max 15)",
    "ro_role_id": "string (role identifier)"
  }
  ```
- **Response**: `UserResponse` (user_id, username, etc.)
- **Status Codes**:
  - `200`: Success
  - `400`: Validation error (username/email exists, weak password, invalid role)
- **Validations**:
  - Username uniqueness
  - Email uniqueness
  - Password strength (lowercase, uppercase, digit, special char)
  - Password confirmation match
  - Role ID exists in database

#### 2. **POST `/auth/login`**
- **Purpose**: Authenticate user and set HTTP-only cookies with tokens
- **Request Body**:
  ```json
  {
    "ua_username": "string",
    "ua_password": "string"
  }
  ```
- **Response**: JSON with user info + Sets cookies:
  ```json
  {
    "user": {
      "ua_user_id": "string",
      "ua_username": "string",
      ...
    }
  }
  ```
- **Cookies Set**:
  - `access_token`: JWT (short-lived, 15 min default)
  - `refresh_token`: JWT (long-lived, 7 days default)
- **Status Codes**:
  - `200`: Success
  - `401`: Invalid credentials
- **Side Effects**:
  - Creates login history record
  - Updates last login timestamp
  - Resets login attempts counter

#### 3. **POST `/auth/logout`**
- **Purpose**: Clear authentication cookies
- **Request Body**: Empty
- **Response**:
  ```json
  {
    "message": "Logout successful"
  }
  ```
- **Cookies Cleared**:
  - `access_token`
  - `refresh_token`

#### 4. **POST `/auth/refresh`**
- **Purpose**: Refresh access token using refresh token
- **Request**: Uses `refresh_token` cookie
- **Response**:
  ```json
  {
    "message": "Token refreshed"
  }
  ```
- **Cookies Updated**:
  - New `access_token` set
- **Status Codes**:
  - `200`: Success
  - `401`: Invalid/missing refresh token
- **Validations**:
  - Refresh token validity
  - User still active

#### 5. **GET `/auth/roles`**
- **Purpose**: Get all available roles for registration
- **Request**: No body needed
- **Response**:
  ```json
  {
    "roles": [
      {
        "ro_role_id": "string",
        "ro_role_name": "string",
        "ro_description": "string",
        ...
      }
    ]
  }
  ```

### User Routes (`/api/v1/users/`)
Location: `app/api/v1/routes/users.py`

#### 1. **POST `/users/`**
- **Purpose**: Create a new user (alternative registration endpoint)
- **Request Body**: `UserCreate` schema
- **Response**: `UserOut` (201 Created)
- **Authentication**: Not required

#### 2. **GET `/users/me`**
- **Purpose**: Get current authenticated user info
- **Request**: No body
- **Authentication**: Required (uses `get_current_user` middleware)
- **Response**:
  ```json
  {
    "user_id": "string",
    "username": "string"
  }
  ```

---

## 🔒 Authentication Architecture

### 1. **Middleware & Dependency Injection**
Location: `app/api/auth_middleware.py`

#### `get_current_user(request, db)` 
- Extracts JWT from HTTP-only `access_token` cookie
- Decodes and validates JWT
- Fetches user from database
- Validates user is active
- Returns `UserAccount` object
- **Raises** `HTTPException` if:
  - Token missing (401)
  - Token invalid/expired (401)
  - User not found (401)
  - User inactive (403)

#### `get_optional_user(request, db)`
- Same as above but returns `None` if not authenticated
- Useful for endpoints that work with/without auth

### 2. **Auth Service**
Location: `app/services/auth_service.py`

```python
class AuthService:
    def authenticate(db, username, password) -> (access_token, refresh_token, user)
    def decode_token(token) -> user_id
```

**Key Logic**:
- Password verification uses: `hash(password + user.ua_salt)`
- Salt-based hashing for added security
- Returns both access and refresh tokens on successful login
- Uses Jose JWT library for token operations

### 3. **Auth Repository**
Location: `app/repositories/auth_repo.py`

**Key Functions**:
- `get_role_by_id()` - Validate role exists
- `get_all_roles()` - List available roles
- `create_user()` - Create new user account
- `get_user_by_username()` - Fetch user for login
- `create_login_history()` - Track login attempts
- `update_user_last_login()` - Update login timestamp
- `get_login_history_by_session_id()` - Get active sessions
- `update_logout_time()` - Mark session as closed

### 4. **Cookie Utilities**
Location: `app/utils/cookies.py`

```python
def set_auth_cookies(response, access_token, refresh_token)
def clear_auth_cookies(response)
```

**Cookie Configuration**:
- `httponly=True` - Prevents JavaScript access (XSS protection)
- `secure=True` - Only sent over HTTPS
- `samesite="none"` - Allows cross-origin cookies
- `max_age` - Auto-expiry time in seconds

---

## 🔐 Security Features

### Password Security
- **Hashing Algorithm**: bcrypt (with passlib)
- **Salt**: Random 32-byte salt per user
- **Validation**: Requires uppercase, lowercase, digit, special character
- **Min Length**: 8 characters

### JWT Tokens
- **Algorithm**: HS256 (HMAC SHA-256)
- **Secret Key**: From `SECRET_KEY` environment variable
- **Access Token Expiry**: 15 minutes (configurable)
- **Refresh Token Expiry**: 7 days (configurable)
- **Payload**: Contains `sub` (user_id) and `exp` (expiration)

### User Status Tracking
- `ua_status`: active/inactive/suspended
- `ua_login_attempts`: Tracks failed login attempts
- `ua_last_login`: Timestamp of last successful login
- `ua_locked_until`: Account lockout timestamp
- `ua_must_change_password`: Force password change flag

### Audit Trail
- `LoginHistory` table tracks every login attempt with:
  - User ID
  - Session ID
  - IP address
  - User agent
  - Success/failure status
  - Login/logout timestamps

---

## ⚙️ Configuration

Location: `app/core/config.py`

### Auth Settings
```python
SECRET_KEY = "change_me_to_a_long_random_string"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### Cookie Settings
```python
COOKIE_DOMAIN = None  # Don't set for localhost
COOKIE_PATH = "/"
COOKIE_SAMESITE = "none"  # For cross-origin
COOKIE_SECURE = True  # HTTPS only in production
```

### CORS Settings
```python
BACKEND_CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
```

---

## 📊 User Account Model

Location: `app/models/user.py`

### Key Fields
- `ua_user_id`: Unique identifier (prefix "UA")
- `ua_username`: Unique username (3-50 chars)
- `ua_email`: Unique email
- `ua_password_hash`: Bcrypt hash of (password + salt)
- `ua_salt`: Per-user random salt
- `ua_status`: active/inactive/suspended
- `ua_login_attempts`: Failed attempts counter
- `ua_two_factor_enabled`: 2FA toggle
- `ua_must_change_password`: Force change flag
- `ua_last_login`: Last successful login time
- `ua_locked_until`: Account lockout expiry
- `ro_role_id`: FK to Role table

### Audit Fields
- `ua_created_by`: User who created account
- `ua_updated_by`: User who last updated
- `ua_created_at`: Creation timestamp
- `ua_updated_at`: Last update timestamp
- `ua_version_number`: Optimistic lock version
- `ua_is_deleted`: Soft delete flag

---

## 🔄 Request/Response Flow

### Login Flow
```
1. Client POST /auth/login with credentials
   ↓
2. AuthService.authenticate():
   - Find user by username
   - Verify password (hash comparison)
   - Generate access + refresh tokens
   ↓
3. Create login history record
   ↓
4. Update last login timestamp
   ↓
5. Response with:
   - User data (JSON body)
   - Set-Cookie: access_token (httponly, 15 min)
   - Set-Cookie: refresh_token (httponly, 7 days)
```

### Protected Endpoint Flow
```
1. Client requests GET /api/v1/users/me
   - Browser automatically includes access_token cookie
   ↓
2. FastAPI calls get_current_user dependency:
   - Extract token from cookies
   - Decode JWT
   - Fetch user from DB
   - Validate user is active
   ↓
3. If valid: Endpoint handler executes with user object
   If invalid: Return 401/403 error
```

### Token Refresh Flow
```
1. Client requests POST /auth/refresh
   - Browser includes refresh_token cookie
   ↓
2. Auth controller:
   - Decode refresh token
   - Validate user still exists and active
   ↓
3. Generate new access_token
   ↓
4. Response with:
   - Set-Cookie: access_token (new, httponly, 15 min)
   - Original refresh_token remains valid
```

---

## 📋 Schemas

### UserCreate (Registration)
```python
{
  "ua_username": str,          # 3-50 chars, unique
  "ua_password": str,          # 8+ chars, strong requirement
  "confirmPassword": str,      # Must match password
  "ua_email": str,             # Valid email, unique
  "ua_first_name": str | None, # Optional, max 50
  "ua_last_name": str | None,  # Optional, max 50
  "ua_phone": str | None,      # Optional, max 15
  "ro_role_id": str            # Must exist in roles table
}
```

### UserLogin
```python
{
  "ua_username": str,  # 3-50 chars
  "ua_password": str   # 8+ chars
}
```

### UserResponse
```python
{
  "ua_user_id": str,
  "ua_username": str,
  "ua_email": str,
  "ua_first_name": str | None,
  "ua_last_name": str | None,
  "ua_phone": str | None,
  "ua_status": str,
  "ro_role_id": str
}
```

---

## 🚀 Common Adjustments You Might Need

### 1. **Add Password Reset**
- Create endpoint: `POST /auth/forgot-password`
- Generate temporary token with short expiry
- Send email with reset link
- Create `POST /auth/reset-password` endpoint
- Validate token and update password

### 2. **Add Email Verification**
- On registration, send verification email
- Create `POST /auth/verify-email/{token}` endpoint
- Mark user as verified before allowing login
- Add `ua_email_verified` field to UserAccount

### 3. **Add 2FA (Two-Factor Authentication)**
- On login, if `ua_two_factor_enabled` is True:
  - Return temporary token (short-lived, marked as "2fa_pending")
  - Send OTP to user's phone/email
  - Create `POST /auth/verify-2fa` endpoint
  - Exchange temporary token + OTP for real access token

### 4. **Add Account Lockout**
- Increment `ua_login_attempts` on failed login
- After N failed attempts (e.g., 5):
  - Set `ua_locked_until` to future timestamp
  - Prevent login until lockout expires
  - Send alert email to user

### 5. **Add Roles & Permissions**
- Use `get_current_user()` dependency to get user
- Check `user.ro_role_id` or role's permissions
- Create helper function: `require_role(roles: List[str])`
- Use in endpoints: `@app.get("/admin", dependencies=[Depends(require_role(["admin"]))])`

### 6. **Add Token Rotation**
- After access token expires, require refresh
- Optionally rotate refresh token on use (issue new refresh, invalidate old)
- Track token families to prevent replay attacks

### 7. **Add Social Login** (OAuth2)
- Integrate Google/Facebook/GitHub OAuth
- Create endpoint to exchange OAuth token for your JWT
- Link OAuth identity to UserAccount
- Allow login via either OAuth or password

### 8. **Add Session Management**
- Store session info: user_id, device, IP, created_at, expires_at
- Allow users to see active sessions
- Allow users to logout from other devices
- Option to revoke all sessions

### 9. **Change Cookie Settings for Development**
In `.env`:
```env
COOKIE_SECURE=false        # Allow HTTP in dev
COOKIE_SAMESITE=lax        # More permissive in dev
COOKIE_DOMAIN=localhost    # Specific domain
```

### 10. **Customize Password Policy**
- Currently requires: uppercase, lowercase, digit, special char
- Could add: minimum length > 8, no sequential chars, no common passwords
- Edit `_validate_password_strength()` in `app/schemas/user.py`

---

## 🧪 Testing Authentication

### Using Postman/cURL

#### 1. Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "ua_username": "testuser",
    "ua_password": "Test@1234",
    "confirmPassword": "Test@1234",
    "ua_email": "test@example.com",
    "ua_first_name": "Test",
    "ua_last_name": "User",
    "ro_role_id": "admin_role"
  }'
```

#### 2. Get Available Roles
```bash
curl -X GET "http://localhost:8000/api/v1/auth/roles"
```

#### 3. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "ua_username": "testuser",
    "ua_password": "Test@1234"
  }' \
  -c cookies.txt
```

#### 4. Get Current User (Uses Cookie)
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -b cookies.txt
```

#### 5. Logout
```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -b cookies.txt
```

---

## 📝 Notes for Adjustments

### Important Files to Modify:
1. **For new endpoints**: `app/api/v1/routes/auth.py`
2. **For business logic**: `app/services/auth_service.py`
3. **For DB operations**: `app/repositories/auth_repo.py`
4. **For schemas**: `app/schemas/user.py`
5. **For configuration**: `app/core/config.py`
6. **For security**: `app/core/security.py`
7. **For middleware**: `app/api/auth_middleware.py`

### Dependency Chain:
```
Routes (auth.py)
  ↓ calls ↓
Services (auth_service.py)
  ↓ calls ↓
Repositories (auth_repo.py)
  ↓ queries ↓
Models (models/user.py)
  ↓ uses ↓
Database (Session from deps.py)
```

### Testing Against APIs:
- Use the Postman collections in `Postman/` folder
- Or write pytest tests (see `PyTest/test_bhikku_workflow.py` as template)
- Check `app/core/logging.py` for logging configuration
- Monitor database via admin panel or tools like pgAdmin

---

## Summary of Current Implementation

✅ **What's Implemented**:
- Cookie-based JWT authentication
- Password hashing with bcrypt + per-user salt
- User registration with role assignment
- Login/logout with automatic token refresh
- Password strength validation
- Email uniqueness checking
- Login history tracking
- User status management
- Proper error handling and validation

⚠️ **What's Missing** (Common Additions):
- Email verification
- Password reset functionality
- Two-factor authentication
- Account lockout after failed attempts
- Session management
- Social/OAuth login
- Permission-based access control

