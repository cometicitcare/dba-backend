# RBAC System Guide - DBA HRMS

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [User Types & Roles](#user-types--roles)
4. [Permissions](#permissions)
5. [Managing Users & Roles](#managing-users--roles)
6. [API Endpoints](#api-endpoints)
7. [Frontend Integration](#frontend-integration)

---

## System Overview

The DBA HRMS uses a comprehensive Role-Based Access Control (RBAC) system with three-tier hierarchy:

```
Groups (Departments) → Roles → Individual User Overrides
```

### Key Features
- ✅ 13 user types across 6 departments
- ✅ 17 predefined roles with hierarchical levels
- ✅ 40 granular permissions (resource:action format)
- ✅ Temporal access control (role expiration)
- ✅ User-level permission overrides
- ✅ Audit trail for all RBAC changes
- ✅ Super admin with bypass capabilities

---

## Architecture

### Three-Tier Permission Hierarchy

1. **Group Level (Department)**
   - Users inherit permissions from their department groups
   - Groups: Bhikku Management, Silmatha Management, Damma School, Divisional Secretariat, Multi-Department, Public Services

2. **Role Level**
   - Specific job functions with defined permissions
   - Roles can be assigned with expiration dates
   - Hierarchy: SUPER_ADMIN > ADMIN > MANAGER > DATA_ENTRY > VIEWER > PUBLIC

3. **User Level (Overrides)**
   - Individual permission grants or denials
   - Overrides all group and role permissions
   - Can be temporary (with expiration)

### Permission Resolution Priority
```
User Overrides > Role Permissions > Group Permissions > Deny All
```

---

## User Types & Roles

### 1. System Administration

| User Type | Role ID | Role Name | Level | Permissions |
|-----------|---------|-----------|-------|-------------|
| Super Administrator | `SA001` | Super Administrator | SUPER_ADMIN | ALL + system:* |
| System Admin | `SYS_ADMIN` | System Administrator | ADMIN | system:*, user:*, audit:* |

### 2. Bhikku Management Department

| User Type | Role ID | Role Name | Level | Permissions |
|-----------|---------|-----------|-------|-------------|
| Bhikku Admin | `BH_ADMIN` | Bhikku Administrator | ADMIN | bhikku:*, vihara:*, certificate:* |
| Bhikku Data Entry | `BH_DATAENTRY` | Bhikku Data Entry | DATA_ENTRY | bhikku:create, bhikku:update, bhikku:read |
| Bhikku Viewer | `BH_VIEW` | Bhikku Viewer | VIEWER | bhikku:read |

### 3. Silmatha Management Department

| User Type | Role ID | Role Name | Level | Permissions |
|-----------|---------|-----------|-------|-------------|
| Silmatha Admin | `SL_ADMIN` | Silmatha Administrator | ADMIN | silmatha:*, vihara:read, certificate:* |
| Silmatha Data Entry | `SL_DATAENTRY` | Silmatha Data Entry | DATA_ENTRY | silmatha:create, silmatha:update, silmatha:read |

### 4. Damma School Department

| User Type | Role ID | Role Name | Level | Permissions |
|-----------|---------|-----------|-------|-------------|
| Damma Admin | `DS_ADMIN` | Damma School Admin | ADMIN | dammaschool:*, vihara:read, certificate:* |
| Damma Data Entry | `DS_DATAENTRY` | Damma School Data Entry | DATA_ENTRY | dammaschool:create, dammaschool:update, dammaschool:read |

### 5. Divisional Secretariat

| User Type | Role ID | Role Name | Level | Permissions |
|-----------|---------|-----------|-------|-------------|
| Divisional Admin | `DIV_ADMIN` | Divisional Admin | ADMIN | divsec:*, vihara:read, bhikku:read |
| Divisional Data Entry | `DIV_DATAENTRY` | Divisional Data Entry | DATA_ENTRY | divsec:create, divsec:update, divsec:read |

### 6. Multi-Department & Public

| User Type | Role ID | Role Name | Level | Permissions |
|-----------|---------|-----------|-------|-------------|
| Multi-Department Admin | `MULTI_ADMIN` | Multi-Department Admin | MANAGER | All department read + selective write |
| Multi-Department Data Entry | `MULTI_DATAENTRY` | Multi-Department Data Entry | DATA_ENTRY | Cross-department create/update |
| Public User | `PUB_USER` | Public User | PUBLIC | public:*, certificate:verify |
| Temporary User | `TEMP_USER` | Temporary User | PUBLIC | Limited read access |

---

## Permissions

### Permission Format
All permissions follow the pattern: `resource:action`

### Permission Categories

#### 1. System Management (`system:*`)
- `system:manage_users` - Create, update, delete users
- `system:manage_roles` - Assign/revoke roles
- `system:manage_groups` - Manage department groups
- `system:manage_permissions` - Override permissions
- `system:view_audit_logs` - View audit trail
- `system:view_users` - View user list and details

#### 2. Bhikku Management (`bhikku:*`)
- `bhikku:create` - Register new bhikku
- `bhikku:read` - View bhikku details
- `bhikku:update` - Update bhikku information
- `bhikku:delete` - Remove bhikku records
- `bhikku:approve` - Approve bhikku registrations
- `bhikku:export` - Export bhikku data

#### 3. Vihara Management (`vihara:*`)
- `vihara:create`, `vihara:read`, `vihara:update`, `vihara:delete`

#### 4. Silmatha Management (`silmatha:*`)
- `silmatha:create`, `silmatha:read`, `silmatha:update`, `silmatha:delete`

#### 5. Certificate Management (`certificate:*`)
- `certificate:create` - Issue certificates
- `certificate:read` - View certificates
- `certificate:update` - Modify certificates
- `certificate:verify` - Verify certificate authenticity
- `certificate:revoke` - Revoke certificates

#### 6. Damma School (`dammaschool:*`)
- `dammaschool:create`, `dammaschool:read`, `dammaschool:update`, `dammaschool:delete`

#### 7. Divisional Secretariat (`divsec:*`)
- `divsec:create`, `divsec:read`, `divsec:update`, `divsec:delete`

#### 8. Public Access (`public:*`)
- `public:search` - Public search functionality
- `public:view` - View public information
- `public:view_temple` - View temple details

#### 9. Reports (`report:*`)
- `report:view`, `report:generate`, `report:export`

#### 10. Audit (`audit:*`)
- `audit:view`, `audit:export`

---

## Managing Users & Roles

### Prerequisites
- Must have `system:manage_users` OR `system:manage_roles` permission
- Super Admin bypasses all checks

### 1. Assign Role to User

**Endpoint:** `POST /api/v1/admin/rbac/user/assign-role`

**Request:**
```json
{
  "user_id": "UA0005",
  "role_id": "BH_VIEW",
  "expires_days": 365,
  "is_active": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Role 'BH_VIEW' assigned to user 'public_user'",
  "data": {
    "user_id": "UA0005",
    "username": "public_user",
    "role_id": "BH_VIEW",
    "role_name": "Bhikku Viewer",
    "is_active": true,
    "expires_date": "2026-11-14T18:30:00"
  }
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/admin/rbac/user/assign-role" \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=YOUR_TOKEN" \
  -d '{
    "user_id": "UA0005",
    "role_id": "BH_VIEW",
    "expires_days": null,
    "is_active": true
  }'
```

### 2. Revoke Role from User

**Endpoint:** `POST /api/v1/admin/rbac/user/revoke-role`

**Request:**
```json
{
  "user_id": "UA0005",
  "role_id": "BH_VIEW"
}
```

### 3. Add User to Group (Department)

**Endpoint:** `POST /api/v1/admin/rbac/user/assign-group`

**Request:**
```json
{
  "user_id": "UA0005",
  "group_id": 1
}
```

### 4. Override User Permission

**Endpoint:** `POST /api/v1/admin/rbac/user/override-permission`

**Request:**
```json
{
  "user_id": "UA0005",
  "permission_id": 15,
  "granted": true,
  "expires_days": 30,
  "is_active": true
}
```

**Use Cases:**
- Grant temporary elevated access
- Deny specific permission even if role allows it
- Handle exceptions without creating new roles

### 5. Get User's Complete RBAC Context

**Endpoint:** `GET /api/v1/admin/rbac/user/{user_id}/context`

**Response:**
```json
{
  "user_id": "UA0005",
  "username": "public_user",
  "email": "public@example.com",
  "is_active": true,
  "roles": [
    {
      "ro_role_id": "BH_VIEW",
      "ro_role_name": "Bhikku Viewer",
      "ro_level": "VIEWER",
      "department": "Bhikku Management",
      "assigned_date": "2025-11-14T18:30:00",
      "expires_date": null,
      "days_until_expiry": null
    }
  ],
  "groups": [
    {
      "group_id": 1,
      "group_name": "Bhikku Management",
      "group_type": "DEPARTMENT"
    }
  ],
  "permissions": [
    "bhikku:read",
    "public:view"
  ],
  "permission_overrides": [],
  "is_super_admin": false,
  "is_admin": false,
  "can_manage_users": false
}
```

### 6. List All Users with RBAC Summary

**Endpoint:** `GET /api/v1/admin/rbac/users/list?skip=0&limit=50`

---

## API Endpoints

### Authentication Required
All RBAC management endpoints require authentication via HTTP-only cookies.

### Available Endpoints

| Method | Endpoint | Required Permission | Description |
|--------|----------|-------------------|-------------|
| POST | `/api/v1/admin/rbac/user/assign-role` | `system:manage_users` OR `system:manage_roles` | Assign role to user |
| POST | `/api/v1/admin/rbac/user/revoke-role` | `system:manage_users` OR `system:manage_roles` | Revoke role from user |
| POST | `/api/v1/admin/rbac/user/assign-group` | `system:manage_users` OR `system:manage_groups` | Add user to group |
| POST | `/api/v1/admin/rbac/user/remove-group` | `system:manage_users` OR `system:manage_groups` | Remove user from group |
| POST | `/api/v1/admin/rbac/user/override-permission` | `system:manage_users` OR `system:manage_permissions` | Override user permission |
| POST | `/api/v1/admin/rbac/user/remove-permission-override` | `system:manage_users` OR `system:manage_permissions` | Remove permission override |
| GET | `/api/v1/admin/rbac/user/{user_id}/context` | `system:manage_users` OR `system:view_users` | Get user RBAC context |
| GET | `/api/v1/admin/rbac/users/list` | `system:manage_users` OR `system:view_users` | List all users |

### Protected Route Example

```python
from app.api.auth_dependencies import has_permission, has_any_permission

# Single permission required
@router.get("/bhikkus/list", dependencies=[has_permission("bhikku:read")])
def get_bhikku_list():
    # Only users with bhikku:read permission can access
    pass

# Any of the listed permissions
@router.post("/bhikkus/create", dependencies=[has_any_permission("bhikku:create", "bhikku:update")])
def create_bhikku():
    # Users with either permission can access
    pass
```

---

## Frontend Integration

### 1. Login & Cookie Management

```javascript
// Login request
const loginResponse = await fetch('http://api.dbagovlk.com/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include', // Important: Enables cookie handling
  body: JSON.stringify({
    ua_username: 'username',
    ua_password: 'password'
  })
});

const userData = await loginResponse.json();

// Store user context in app state
// Cookies are automatically managed by browser
```

### 2. Using User Context for UI Control

```javascript
// Check permissions
const canCreateBhikku = userData.permissions.includes('bhikku:create');
const canManageUsers = userData.can_manage_users;
const isSuperAdmin = userData.is_super_admin;

// Render UI based on permissions
{canCreateBhikku && <button>Add New Bhikku</button>}
{canManageUsers && <Link to="/admin/users">Manage Users</Link>}

// Check resource-specific permissions
const bhikkuPermissions = userData.permission_map.bhikku || [];
const canReadBhikku = bhikkuPermissions.includes('read');
const canUpdateBhikku = bhikkuPermissions.includes('update');
```

### 3. Making Authenticated Requests

```javascript
// All subsequent requests automatically include cookies
const response = await fetch('http://api.dbagovlk.com/api/v1/bhikkus/list', {
  method: 'GET',
  credentials: 'include' // Sends cookies automatically
});

// Handle 403 Forbidden (insufficient permissions)
if (response.status === 403) {
  showError('You do not have permission to access this resource');
}
```

### 4. Role-Based Navigation

```javascript
const navigation = [
  {
    label: 'Dashboard',
    path: '/dashboard',
    permission: null // Everyone can see
  },
  {
    label: 'Bhikku Management',
    path: '/bhikkus',
    permission: 'bhikku:read',
    children: [
      { label: 'View Bhikkus', path: '/bhikkus/list', permission: 'bhikku:read' },
      { label: 'Add Bhikku', path: '/bhikkus/create', permission: 'bhikku:create' }
    ]
  },
  {
    label: 'User Management',
    path: '/admin/users',
    permission: 'system:manage_users',
    adminOnly: true
  }
];

// Filter navigation based on user permissions
const allowedNav = navigation.filter(item => {
  if (!item.permission) return true;
  if (item.adminOnly && !userData.is_admin) return false;
  return userData.permissions.includes(item.permission);
});
```

---

## Best Practices

### 1. Security
- ✅ Always use HTTPS in production
- ✅ Never expose JWT tokens in localStorage (we use HTTP-only cookies)
- ✅ Implement proper CORS configuration
- ✅ Validate permissions on both frontend and backend
- ✅ Use principle of least privilege

### 2. Permission Design
- ✅ Use granular permissions (resource:action format)
- ✅ Group related permissions into roles
- ✅ Avoid creating too many roles
- ✅ Use user overrides for exceptions only

### 3. Role Management
- ✅ Set expiration dates for temporary access
- ✅ Regular audit of user permissions
- ✅ Deactivate instead of delete (maintains audit trail)
- ✅ Document role changes in audit logs

### 4. Frontend Implementation
- ✅ Hide UI elements user cannot access
- ✅ Handle 403 errors gracefully
- ✅ Show clear error messages
- ✅ Implement loading states during permission checks

---

## Troubleshooting

### Common Issues

**1. User cannot access protected route despite having role**

Check:
- Is the role active? (`ur_is_active = true`)
- Has the role expired? (`ur_expires_date`)
- Does the role have the required permission?
- Is there a user override denying the permission?

**2. Cookies not being sent**

Frontend must use:
```javascript
fetch(url, { credentials: 'include' })
```

Backend CORS must allow:
```python
BACKEND_CORS_ORIGINS = "https://frontend.com"
COOKIE_SAMESITE = "none"
COOKIE_SECURE = true
```

**3. Permission denied for super admin**

Super admins bypass all permission checks. If denied:
- Check if `is_super_admin` flag is set correctly
- Verify user has role with `ro_level = 'SUPER_ADMIN'`

---

## Database Schema

### Key Tables
- `user_accounts` - User information
- `roles` - Role definitions
- `groups` - Department/group definitions
- `permissions` - Permission definitions
- `user_roles` - User-role assignments
- `user_groups` - User-group memberships
- `user_permissions` - User permission overrides
- `role_permissions` - Role-permission mappings

---

## Contact & Support

For questions or issues with the RBAC system:
- Check audit logs: `/api/v1/admin/audit-logs`
- Review user context: `/api/v1/admin/rbac/user/{user_id}/context`
- Contact system administrator

---

**Last Updated:** November 15, 2025  
**Version:** 1.0.0  
**System:** DBA HRMS - Digital Buddhist Archive
