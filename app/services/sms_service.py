"""
SMS Service Module

Sends short SMS messages via text.lk (or similar) using HTTP API.
Provides a simple template loader for plain-text SMS templates located in
`app/templates/<name>.txt`.

Notes:
- Uses `httpx` existing in requirements.
- Keeps messages short (trims to `SMS_MAX_LENGTH` characters).
- Uses bearer token from config, and `SMS_ENABLED` flag.
"""
from pathlib import Path
import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    def __init__(self):
        self.api_url = settings.SMS_API_URL
        self.bearer_token = settings.SMS_BEARER_TOKEN
        self.default_sender = settings.SMS_DEFAULT_SENDER_ID
        self.max_length = settings.SMS_MAX_LENGTH
        self.enabled = settings.SMS_ENABLED

    def load_template(self, template_name: str, **kwargs) -> str:
        """Load a plain text SMS template and substitute {{key}} placeholders."""
        try:
            template_path = Path(__file__).parent.parent / "templates" / f"{template_name}.txt"
            if not template_path.exists():
                logger.error(f"SMS template not found: {template_path}")
                return ""

            content = template_path.read_text(encoding="utf-8")
            for key, value in kwargs.items():
                placeholder = f"{{{{{key}}}}}"
                content = content.replace(placeholder, str(value))

            # Ensure message is short
            if len(content) > self.max_length:
                logger.warning("SMS message exceeds max length; truncating")
                content = content[: self.max_length - 3].rstrip() + "..."

            return content

        except Exception as e:
            logger.error(f"Failed to load SMS template {template_name}: {e}")
            return ""

    def send_sms(self, recipient: str, message: str, sender_id: Optional[str] = None) -> dict:
        """Send SMS via provider API.

        Returns a small result dict with a `success` boolean and a few provider
        response fields (kept minimal to avoid leaking secrets). The dict is
        truthy when `success` is True so existing callers that test the value
        in boolean context keep working.
        """
        if not self.enabled:
            logger.info("SMS sending is disabled in configuration")
            return False

        if not self.bearer_token:
            logger.error("No SMS bearer token configured; cannot send SMS")
            return False

        # Ensure recipient is in expected format (provider expects country code, e.g., 9471...)
        payload = {
            "recipient": recipient,
            "sender_id": sender_id or self.default_sender,
            "type": "plain",
            "message": message,
        }

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(self.api_url, json=payload, headers=headers)

            # Try to parse provider JSON response but fall back to text
            provider_payload = None
            try:
                provider_payload = resp.json()
            except Exception:
                provider_payload = {"raw": resp.text}

            result = {
                "success": 200 <= resp.status_code < 300,
                "status_code": resp.status_code,
            }

            # Pull a few useful fields if present in provider response
            if isinstance(provider_payload, dict):
                # Common fields returned by providers: uid/to/from/status/cost/sms_count
                for k in ("uid", "to", "from", "status", "cost", "sms_count"):
                    if k in provider_payload:
                        result[k] = provider_payload[k]
                # Include a short provider message if present
                if "message" in provider_payload and not result.get("message"):
                    result["message"] = str(provider_payload.get("message"))
            else:
                result["provider_text"] = str(provider_payload)

            if result["success"]:
                logger.info(f"SMS sent to {recipient} (status={resp.status_code})")
                return result

            # Non-2xx responses
            logger.error(f"Failed to send SMS to {recipient}: {resp.status_code} {resp.text}")
            return result

        except Exception as e:
            logger.error(f"Exception when sending SMS to {recipient}: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
sms_service = SMSService()
