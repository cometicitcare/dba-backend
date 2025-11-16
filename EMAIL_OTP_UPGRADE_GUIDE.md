# Industry-Level Email and OTP Service Upgrade Guide

## Overview

This upgrade transforms your email and OTP services from basic implementations to production-grade, enterprise-level services with the following improvements:

## Key Improvements

### Email Service V2 (`email_service_v2.py`)

**Problems Solved:**

- ✅ **Blocking SMTP calls** → Async email sending with thread pool executor
- ✅ **No connection pooling** → SMTP connection pool (5 connections)
- ✅ **Server slowdowns** → Non-blocking operations with background tasks
- ✅ **No rate limiting** → Token bucket rate limiter (100/hour global, 5/hour per recipient)
- ✅ **Poor error handling** → Circuit breaker pattern prevents cascading failures
- ✅ **No retry logic** → Exponential backoff retry with configurable attempts
- ✅ **No monitoring** → Comprehensive metrics tracking

**Features:**

- Connection pooling for SMTP connections
- Rate limiting to prevent abuse
- Circuit breaker pattern for fault tolerance
- Async and sync email sending options
- Template caching with LRU cache
- Detailed metrics and monitoring
- Exponential backoff retry logic
- SSL/TLS security enhancements

### OTP Service V2 (`otp_service_v2.py`)

**Problems Solved:**

- ✅ **In-memory storage** → Redis-backed storage for production scalability
- ✅ **Not production-ready** → Automatic failover to in-memory if Redis unavailable
- ✅ **No rate limiting** → Hourly and daily rate limits per user
- ✅ **Security issues** → OTP hashing (SHA-256) instead of plain text storage
- ✅ **No audit trail** → Comprehensive logging with IP/user agent tracking
- ✅ **No persistence** → Redis with TTL for automatic cleanup

**Features:**

- Redis-based storage with connection pooling
- Automatic fallback to in-memory storage
- OTP hashing for security
- Rate limiting (5 requests/hour, 10/day per user)
- Brute-force protection (max 3 attempts)
- IP address and user agent logging
- Multi-channel support (email, SMS, both)
- Automatic expiration and cleanup

### Background Task Service (`background_tasks.py`)

**Features:**

- Async task queue for non-blocking operations
- Worker thread pool (5 workers by default)
- Automatic retry with exponential backoff
- Task status tracking
- Graceful shutdown
- Metrics and monitoring

## Migration Steps

### 1. Install Required Dependencies

```bash
pip install redis==5.0.1 hiredis==2.3.2
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Update Environment Variables

Add these to your `.env` file:

```bash
# OTP Configuration (Enhanced)
OTP_EXPIRE_MINUTES=10
OTP_LENGTH=6
OTP_MAX_ATTEMPTS=3
OTP_MAX_REQUESTS_PER_HOUR=5
OTP_MAX_REQUESTS_PER_DAY=10

# Redis Configuration (for production OTP storage)
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0
```

### 3. Setup Redis (Production)

#### Option 1: Docker (Development/Testing)

```bash
docker run -d --name redis-otp \
  -p 6379:6379 \
  redis:7-alpine redis-server --requirepass your_redis_password
```

#### Option 2: Railway (Production)

1. Go to Railway dashboard
2. Click "New" → "Database" → "Add Redis"
3. Copy the connection details to your `.env`:
   - `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
4. Set `REDIS_ENABLED=true`

#### Option 3: Redis Cloud (Managed Service)

1. Sign up at https://redis.com/try-free/
2. Create a new database
3. Copy connection details to `.env`

### 4. Update Service Imports

Replace old imports with new ones in your existing code:

**Before:**

```python
from app.services.email_service import email_service
from app.services.password_reset_service import password_reset_service
```

**After:**

```python
# Use V2 services (backward compatible)
from app.services.email_service_v2 import email_service
from app.services.password_reset_service_v2 import password_reset_service
```

**OR** keep your existing imports - the old files can import from V2:

Update `app/services/email_service.py`:

```python
# Redirect to V2 for backward compatibility
from app.services.email_service_v2 import email_service_v2 as email_service
```

### 5. Update Password Reset Endpoints (if needed)

The new service returns additional information:

```python
success, message, delivery_info = password_reset_service.initiate_password_reset(
    user_id=user.id,
    user_email=user.email,
    user_name=user.name,
    user_phone=user.phone,  # Optional
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent"),
    async_send=True  # Async by default
)

# delivery_info contains:
# {
#     "email": bool,
#     "sms": bool,
#     "email_task_id": str (if async),
#     "delivery_channel": str,
#     "async": bool
# }
```

## Testing

### 1. Test Email Service

```python
from app.services.email_service_v2 import email_service_v2

# Test sync send
success = email_service_v2.send_email(
    to_email="test@example.com",
    subject="Test Email",
    html_content="<h1>Test</h1>",
    plain_text="Test"
)

# Test async send
import asyncio
success = await email_service_v2.send_email_async(
    to_email="test@example.com",
    subject="Test Async Email",
    html_content="<h1>Test Async</h1>"
)

# Check metrics
metrics = email_service_v2.get_metrics()
print(metrics)
```

### 2. Test OTP Service

```python
from app.services.otp_service_v2 import otp_service_v2

# Generate OTP
success, message, otp = otp_service_v2.generate_otp(
    user_id="123",
    user_identifier="user@example.com",
    delivery_channel="email",
    ip_address="127.0.0.1"
)

print(f"OTP: {otp}")

# Validate OTP
valid, message, metadata = otp_service_v2.validate_otp(
    user_id="123",
    otp=otp
)

# Check metrics
metrics = otp_service_v2.get_metrics()
print(f"Storage type: {metrics['storage_type']}")  # 'redis' or 'memory'
```

### 3. Test Background Tasks

```python
from app.services.background_tasks import send_email_async

# Send email asynchronously
task_id = send_email_async(
    to_email="test@example.com",
    subject="Async Test",
    html_content="<h1>Async</h1>"
)

# Check task status
from app.services.background_tasks import background_task_service
status = background_task_service.get_task_status(task_id)
print(status)
```

## Monitoring and Metrics

### Get Service Metrics

```python
from app.services.password_reset_service_v2 import password_reset_service_v2

metrics = password_reset_service_v2.get_service_metrics()

# Returns:
# {
#     "email_service": {
#         "emails_sent": 100,
#         "emails_failed": 2,
#         "total_retry_attempts": 5,
#         "rate_limited": 3,
#         "circuit_breaker_trips": 0
#     },
#     "otp_service": {
#         "otps_generated": 50,
#         "otps_validated": 45,
#         "otps_failed": 2,
#         "rate_limited": 3,
#         "storage_type": "redis"
#     },
#     "background_tasks": {
#         "tasks_submitted": 100,
#         "tasks_completed": 98,
#         "tasks_failed": 1,
#         "tasks_retried": 2,
#         "queue_size": 0,
#         "total_tasks": 100
#     }
# }
```

## Performance Improvements

### Before (Old Service)

- Blocking SMTP calls: ~2-5 seconds per email
- No connection pooling: New connection for each email
- In-memory OTP: Lost on server restart
- No rate limiting: Vulnerable to abuse
- Server slowdowns during email bursts

### After (V2 Service)

- Async email: <50ms response time (queued)
- Connection pooling: Reuse connections
- Redis OTP: Persistent and scalable
- Rate limiting: Protected from abuse
- No server slowdowns: Background processing

## Rollback Plan

If you need to rollback:

1. Keep the old service files
2. Change imports back to original
3. Set `REDIS_ENABLED=false` in `.env`
4. Restart the service

The new services are designed to be backward compatible.

## Production Checklist

- [ ] Redis installed and configured
- [ ] Environment variables updated
- [ ] Dependencies installed (`redis`, `hiredis`)
- [ ] Email service tested
- [ ] OTP service tested with Redis
- [ ] Rate limits configured appropriately
- [ ] Monitoring/metrics dashboard setup
- [ ] Backup strategy for Redis (if using)
- [ ] Log aggregation configured
- [ ] Alert thresholds defined

## Security Enhancements

1. **OTP Hashing**: OTPs stored as SHA-256 hashes
2. **Rate Limiting**: Prevents brute-force attacks
3. **IP Logging**: Tracks OTP requests by IP
4. **Circuit Breaker**: Prevents service overload
5. **SSL/TLS**: Enhanced SMTP security
6. **Attempt Limits**: Max 3 OTP validation attempts

## Scaling Considerations

### Current Implementation (Development/Small Scale)

- In-memory task queue
- Thread pool executor (10 workers)
- Single Redis instance

### Production Scale-Up Options

1. **Replace background tasks** with Celery + Redis/RabbitMQ
2. **Redis Cluster** for high availability
3. **Email service provider** (SendGrid, AWS SES) instead of SMTP
4. **Distributed rate limiting** with Redis
5. **Horizontal scaling** with load balancer

## Troubleshooting

### Redis Connection Issues

```python
# Check if Redis is connected
from app.services.otp_service_v2 import otp_service_v2
metrics = otp_service_v2.get_metrics()
print(f"Storage: {metrics['storage_type']}")  # Should be 'redis'
```

If showing 'memory', check:

- Redis server is running
- Credentials are correct
- Network connectivity
- Firewall rules

### Email Not Sending

```python
# Check circuit breaker state
from app.services.email_service_v2 import email_service_v2
# Circuit breaker will open after 5 consecutive failures
```

### Rate Limit Issues

Adjust in `.env`:

```bash
OTP_MAX_REQUESTS_PER_HOUR=10  # Increase if needed
OTP_MAX_REQUESTS_PER_DAY=20
```

## Support

For issues or questions:

1. Check logs for detailed error messages
2. Review metrics for service health
3. Verify environment configuration
4. Test Redis connectivity
5. Check SMTP credentials

## Next Steps

After successful migration:

1. Monitor metrics for first 24 hours
2. Adjust rate limits based on usage
3. Set up Redis backup/persistence
4. Consider email provider migration (SendGrid/SES)
5. Implement Celery for production scale
