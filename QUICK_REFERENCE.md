# Quick Reference - Email & OTP Services V2

## 🚀 Quick Setup (30 seconds)

```bash
# 1. Install dependencies
pip install redis hiredis

# 2. Start Redis (Docker)
docker run -d --name redis-otp -p 6379:6379 redis:7-alpine

# 3. Add to .env
echo "REDIS_ENABLED=true" >> .env

# 4. Test
python test_email_otp_services.py
```

## 📧 Email Service

### Send Email (Async - Recommended)

```python
from app.services.email_service_v2 import email_service

# Async (non-blocking)
success = await email_service.send_email_async(
    to_email="user@example.com",
    subject="Welcome",
    html_content="<h1>Hello</h1>",
    plain_text="Hello"
)
```

### Send Email (Sync)

```python
success = email_service.send_email(
    to_email="user@example.com",
    subject="Welcome",
    html_content="<h1>Hello</h1>"
)
```

### Check Metrics

```python
metrics = email_service.get_metrics()
# {
#   "emails_sent": 100,
#   "emails_failed": 2,
#   "rate_limited": 1,
#   ...
# }
```

## 🔐 OTP Service

### Generate OTP

```python
from app.services.otp_service_v2 import otp_service

success, message, otp = otp_service.generate_otp(
    user_id="123",
    user_identifier="user@example.com",
    delivery_channel="email",
    ip_address="127.0.0.1"
)

print(f"OTP: {otp}")  # "123456"
```

### Validate OTP

```python
valid, message, metadata = otp_service.validate_otp(
    user_id="123",
    otp="123456"
)

if valid:
    print("OTP is valid!")
```

### Check Status

```python
status = otp_service.get_otp_status("123")
# {
#   "has_otp": True,
#   "time_remaining_minutes": 8.5,
#   "attempts_remaining": 3,
#   "is_expired": False
# }
```

### Check Metrics

```python
metrics = otp_service.get_metrics()
# {
#   "storage_type": "redis",  # or "memory"
#   "otps_generated": 50,
#   "otps_validated": 45,
#   ...
# }
```

## 📝 Background Tasks

### Send Email via Background Task

```python
from app.services.background_tasks import send_email_async

task_id = send_email_async(
    to_email="user@example.com",
    subject="Async Email",
    html_content="<h1>Hello</h1>"
)

# Check status
from app.services.background_tasks import background_task_service
status = background_task_service.get_task_status(task_id)
```

### Custom Background Task

```python
def my_task(x, y):
    return x + y

task_id = background_task_service.submit_task(
    task_name="add_numbers",
    func=my_task,
    x=5,
    y=3,
    max_retries=3
)
```

## 🔄 Password Reset (Complete Flow)

```python
from app.services.password_reset_service_v2 import password_reset_service

# 1. Initiate reset
success, message, info = password_reset_service.initiate_password_reset(
    user_id=user.id,
    user_email=user.email,
    user_name=user.name,
    user_phone=user.phone,  # Optional
    ip_address=request.client.host,
    async_send=True  # Send email async
)

# 2. User receives OTP via email
# 3. Validate OTP
valid, message, metadata = password_reset_service.validate_otp_for_reset(
    user_id=user.id,
    otp="123456"
)

# 4. Complete reset (if valid)
if valid:
    success, msg = password_reset_service.complete_password_reset(
        user_id=user.id,
        new_password="new_secure_password"
    )
```

## 📊 Monitoring

### All Service Metrics

```python
metrics = password_reset_service.get_service_metrics()
# {
#   "email_service": {...},
#   "otp_service": {...},
#   "background_tasks": {...}
# }
```

## ⚙️ Configuration (.env)

```bash
# SMTP
SMTP_SERVER=mail.smtp2go.com
SMTP_PORT=2525
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password

# OTP
OTP_EXPIRE_MINUTES=10
OTP_LENGTH=6
OTP_MAX_ATTEMPTS=3
OTP_MAX_REQUESTS_PER_HOUR=5
OTP_MAX_REQUESTS_PER_DAY=10

# Redis
REDIS_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

## 🔧 Troubleshooting

### Redis not connecting?

```python
# Check storage type
from app.services.otp_service_v2 import otp_service
metrics = otp_service.get_metrics()
print(metrics['storage_type'])  # Should be "redis"

# If "memory", check:
# 1. Redis is running: redis-cli ping
# 2. Credentials in .env are correct
# 3. REDIS_ENABLED=true
```

### Email not sending?

```python
# Check circuit breaker
from app.services.email_service_v2 import email_service
metrics = email_service.get_metrics()
print(metrics)  # Check 'circuit_breaker_trips'

# Test sync send
success = email_service.send_email(
    to_email="test@example.com",
    subject="Test",
    html_content="<h1>Test</h1>"
)
print(success)
```

### Rate limited?

```python
# Adjust in .env
OTP_MAX_REQUESTS_PER_HOUR=10  # Increase
OTP_MAX_REQUESTS_PER_DAY=20
```

## 🎯 Best Practices

1. **Use async email sending** for better performance
2. **Enable Redis** for production OTP storage
3. **Monitor metrics** regularly
4. **Adjust rate limits** based on usage
5. **Set up alerts** for failures/circuit breaker trips
6. **Log IP addresses** for OTP requests (security)
7. **Use background tasks** for non-critical operations

## 📚 Documentation

- `EMAIL_OTP_UPGRADE_GUIDE.md` - Full upgrade guide
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `test_email_otp_services.py` - Test all features
- `.env.email-otp-example` - Configuration examples

## 🆘 Common Commands

```bash
# Test everything
python test_email_otp_services.py

# Install dependencies
pip install -r requirements.txt

# Start Redis (Docker)
docker run -d --name redis-otp -p 6379:6379 redis:7-alpine

# Check Redis
redis-cli ping

# View logs
tail -f logs/app.log

# Run installation script
./install_email_otp_upgrade.sh
```

## ✅ Success Indicators

- ✓ Storage type: "redis" (not "memory")
- ✓ Email service circuit breaker: "CLOSED"
- ✓ Background task queue_size: low
- ✓ Emails sending in <50ms (async)
- ✓ OTPs generating and validating successfully
- ✓ Rate limiting preventing abuse

---

**Need Help?** See `EMAIL_OTP_UPGRADE_GUIDE.md` for detailed documentation.
