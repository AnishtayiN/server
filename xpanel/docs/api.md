# XPanel API Documentation

## Base URL

```
http://localhost:8080/api/v1
```

## Authentication

All API endpoints (except login) require JWT authentication.

### Get Access Token

```bash
curl -X POST "http://localhost:8080/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include in request headers:
```bash
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Authentication Endpoints

### Login

**POST** `/auth/login`

Get access token for authentication.

**Parameters:**
- `username` (form field): Admin username
- `password` (form field): Admin password

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## User Management

### List Users

**GET** `/users`

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100)
- `status_filter` (string, optional): Filter by status (active, expired, disabled, traffic_exhausted)
- `protocol_filter` (string, optional): Filter by protocol

**Response:**
```json
[
  {
    "id": 1,
    "username": "user1",
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "protocol": "vmess",
    "status": "active",
    "traffic_limit_gb": 100,
    "ip_limit": 0,
    "expiry_date": "2024-12-31T23:59:59Z",
    "traffic_used_bytes": 5368709120,
    "connection_count": 5,
    "last_connected": "2024-01-15T10:30:00Z",
    "notes": "Premium user",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### Get User

**GET** `/users/{user_id}`

**Response:** Single user object

### Create User

**POST** `/users`

**Request Body:**
```json
{
  "username": "newuser",
  "protocol": "vmess",
  "traffic_limit_gb": 50,
  "ip_limit": 2,
  "expiry_days": 30,
  "notes": "Test user",
  "config": {
    "port": 443,
    "network": "ws",
    "security": "tls"
  }
}
```

**Response:** Created user object

### Update User

**PUT** `/users/{user_id}`

**Request Body:**
```json
{
  "username": "updateduser",
  "traffic_limit_gb": 100,
  "status": "active"
}
```

**Response:** Updated user object

### Delete User

**DELETE** `/users/{user_id}`

**Response:** 204 No Content

### Get User Subscription

**GET** `/users/{user_id}/subscription`

**Response:**
```json
{
  "user_id": 1,
  "username": "user1",
  "subscription_url": "http://server:8080/api/v1/subscription/uuid-here",
  "protocol": "vmess"
}
```

---

## Inbound Management

### List Inbounds

**GET** `/inbounds`

**Query Parameters:**
- `skip` (int, optional): Pagination offset
- `limit` (int, optional): Page size

**Response:**
```json
[
  {
    "id": 1,
    "tag": "vmess-inbound",
    "protocol": "vmess",
    "port": 443,
    "listen": "0.0.0.0",
    "settings": {},
    "stream_settings": {},
    "sniffing": {"enabled": true, "destOverride": ["http", "tls"]},
    "enabled": true,
    "total_traffic_gb": 0,
    "traffic_used_bytes": 1073741824,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T00:00:00Z"
  }
]
```

### Get Inbound

**GET** `/inbounds/{inbound_id}`

### Create Inbound

**POST** `/inbounds`

**Request Body:**
```json
{
  "tag": "vless-inbound",
  "protocol": "vless",
  "port": 8443,
  "listen": "0.0.0.0",
  "settings": {},
  "stream_settings": {
    "security": "reality",
    "realitySettings": {}
  },
  "total_traffic_gb": 0
}
```

### Update Inbound

**PUT** `/inbounds/{inbound_id}`

### Delete Inbound

**DELETE** `/inbounds/{inbound_id}`

### Toggle Inbound

**POST** `/inbounds/{inbound_id}/toggle`

Enable or disable an inbound.

---

## Statistics & Monitoring

### Server Statistics

**GET** `/stats/server`

**Response:**
```json
{
  "cpu_usage": 25.5,
  "memory_usage": 45.2,
  "memory_total": 4294967296,
  "disk_usage": 35.8,
  "disk_total": 107374182400,
  "uptime": 1704067200,
  "xray_running": true,
  "active_connections": 15,
  "total_users": 50,
  "active_users": 42
}
```

### Traffic Statistics

**GET** `/stats/traffic`

**Response:**
```json
[
  {
    "user_id": 1,
    "username": "user1",
    "traffic_used_bytes": 5368709120,
    "traffic_limit_bytes": 107374182400,
    "upload_bytes": 2684354560,
    "download_bytes": 2684354560,
    "percentage_used": 5.0
  }
]
```

### User Statistics

**GET** `/stats/user/{user_id}`

**Response:**
```json
{
  "user_id": 1,
  "username": "user1",
  "protocol": "vmess",
  "status": "active",
  "traffic_used_bytes": 5368709120,
  "traffic_used_gb": 5.0,
  "traffic_limit_bytes": 107374182400,
  "traffic_limit_gb": 100,
  "percentage_used": 5.0,
  "connection_count": 5,
  "last_connected": "2024-01-15T10:30:00Z",
  "expiry_date": "2024-12-31T23:59:59Z",
  "days_remaining": 350
}
```

### System Logs

**GET** `/logs/system`

**Query Parameters:**
- `limit` (int, optional): Number of logs to retrieve (default: 50)

### Xray Status

**GET** `/xray/status`

**Response:**
```json
{
  "active": true,
  "status": "● xray.service - Xray Service\n   Active: active (running)..."
}
```

### Restart Xray

**POST** `/xray/restart`

**Response:**
```json
{
  "status": "success",
  "message": "Xray restarted successfully"
}
```

---

## Admin Management

### Get Current Admin

**GET** `/admins/me`

### Update Current Admin

**PUT** `/admins/me`

**Request Body:**
```json
{
  "username": "newadmin",
  "email": "admin@example.com",
  "password": "newpassword123"
}
```

### Create Admin (Super Admin Only)

**POST** `/admins`

---

## Error Responses

All errors return JSON with this format:

```json
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes

- `200`: Success
- `201`: Created
- `204`: No Content (successful deletion)
- `400`: Bad Request
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `500`: Internal Server Error

---

## Rate Limiting

API requests are rate-limited to prevent abuse:
- 100 requests per minute per IP
- 1000 requests per hour per user

Exceeding limits returns `429 Too Many Requests`.

---

## Examples

### Complete Workflow

```bash
# 1. Login and get token
TOKEN=$(curl -s -X POST "http://localhost:8080/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# 2. Create a user
curl -X POST "http://localhost:8080/api/v1/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "protocol": "vmess",
    "traffic_limit_gb": 50,
    "expiry_days": 30
  }'

# 3. List all users
curl "http://localhost:8080/api/v1/users" \
  -H "Authorization: Bearer $TOKEN"

# 4. Get server stats
curl "http://localhost:8080/api/v1/stats/server" \
  -H "Authorization: Bearer $TOKEN"
```

---

⚠️ **LEGAL DISCLAIMER**: Use API responsibly and in compliance with all applicable laws.
