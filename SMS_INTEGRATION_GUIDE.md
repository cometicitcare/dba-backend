# SMS Integration Guide

This document summarizes the SMS/OTP integration added to the project (patterned after the existing email docs).
Keep this short and focused on configuration, files, and how to test safely.

## Overview

- Provider example: text.lk (HTTP API). The app uses a small `sms_service` wrapper that sends short plain-text messages via the provider's HTTP API.
- Purpose: deliver short OTPs (password reset) as a fallback/alternative to email. Messages are intentionally short to reduce cost.
- Important: do not commit bearer tokens or other secrets to the repo. Use environment variables or your secret store.

## Files added / changed

- Added: `app/services/sms_service.py` — simple HTTP client wrapper and template loader for plain SMS templates.
- Added: `app/templates/password_reset_sms.txt` — short OTP template used for password reset.
- Updated: `app/core/config.py` — new config values read from env:
  - `SMS_ENABLED` (bool)
  - `SMS_API_URL` (string)
  - `SMS_BEARER_TOKEN` (string)
  - `SMS_DEFAULT_SENDER_ID` (string)
  - `SMS_MAX_LENGTH` (int)
- Updated: `app/services/password_reset_service.py` — `initiate_password_reset(...)` now accepts `user_phone` and attempts to send OTP by SMS in addition to email. Function returns success when at least one channel delivered.
- Updated: `app/services/auth_service.py` — passes `user.ua_phone` into the password-reset initiation.
- Updated (example): top-level `env` file contains commented examples of the SMS env variables (placeholders only).

## Environment variables (set in host/CI, not in repo)

Required/Recommended (example names):

- SMS_ENABLED=true
- SMS_API_URL=https://app.text.lk/api/v3/sms/send
- SMS_BEARER_TOKEN=<your_bearer_token_here>
- SMS_DEFAULT_SENDER_ID=COMETICINSY
- SMS_MAX_LENGTH=160

Example (PowerShell):

```powershell
$env:SMS_ENABLED = "true"
$env:SMS_API_URL = "https://app.text.lk/api/v3/sms/send"
$env:SMS_BEARER_TOKEN = "<your_bearer_token_here>"
$env:SMS_DEFAULT_SENDER_ID = "COMETICINSY"
```

## Template

- `app/templates/password_reset_sms.txt` — content:

  `Your DBA HRMS OTP is {{otp}}. Valid for {{otp_expiry}} minute(s). Do not share this code.`

Template variables:
- `otp` — the 6-digit (configurable) OTP
- `otp_expiry` — expiry in minutes

The SMS loader will trim/truncate the message to `SMS_MAX_LENGTH` to avoid long messages and cost overruns.

## How it works (summary)

1. User requests password reset (existing flow).
2. The server generates an OTP (using `OTPManager`) and stores it in memory (see notes below about production storage).
3. The app attempts to send the OTP via email (existing email service) and — if `user.ua_phone` exists and `SMS_ENABLED` is true — via SMS using `sms_service`.
4. The OTP validation and reset logic is unchanged; SMS is a delivery channel, not an alternate verification mechanism.

## Sample provider payload (curl example)

Use environment variables or a secrets store; do not paste tokens into shared code.

Example payload (replace token with your secret):

```bash
curl -X POST https://app.text.lk/api/v3/sms/send \
  -H "Authorization: Bearer <YOUR_BEARER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"recipient":"9471xxxxxxx","sender_id":"COMETICINSY","type":"plain","message":"Your OTP is 123456"}'
```

The app's `sms_service` performs the same call using `httpx` and logs provider responses when non-2xx.

## Security & operational notes (short)

- Secrets: never commit `SMS_BEARER_TOKEN` to source control. Use env/secret manager.
- OTP storage: current implementation stores OTPs in memory (in `OTPManager._otp_store`) — this is fine for small dev setups, but not for multi-process production. For production use Redis (or a DB) so OTPs persist across processes and can be rate-limited.
- OTP hashing: for higher security, store OTP hashes rather than plaintext values.
- Rate limiting & throttling: implement per-user and global send quotas (suggest Redis). This prevents abuse and excessive cost.
- Message length: SMS messages are truncated to `SMS_MAX_LENGTH` (defaults to 160) to avoid multipart messages and higher costs.
- Logging: the service logs provider errors and responses (avoid logging OTP contents in persistent logs).

## Testing

- Locally: set `SMS_ENABLED=true` and `SMS_BEARER_TOKEN` to a valid token, ensure the test user has `ua_phone` set, then trigger the password-reset request. Check logs for delivery status.
- Unit tests: mock the `sms_service` client and assert correct payloads and truncation behavior.

## Next steps (recommended)

- Replace in-memory OTP store with Redis and add rate-limiting middleware for SMS endpoints.
- Replace plaintext OTP storage with hashed OTPs (bcrypt/HMAC) to avoid raw values in memory/logs.
- Add unit/integration tests for `sms_service` and password reset flows (success + failure branches).
- Add an authenticated admin/test-only route to send SMS for manual integration tests (protect with admin auth).

---

If you want, I can implement Redis-backed OTP storage and add tests next — tell me which one you want prioritized and I'll proceed.