from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class SMSTestRequest(BaseModel):
    recipient: str
    message: Optional[str] = "Test message from DBA HRMS"


@router.post("/send-test-sms", status_code=status.HTTP_200_OK)
async def send_test_sms(request: SMSTestRequest, x_sms_test_key: Optional[str] = Header(None)):
    """Dev-only endpoint to send a test SMS.

    - Requires header `X-SMS-TEST-KEY` to match `SMS_TEST_KEY` in environment.
    - Intended for local/integration testing only. Do NOT enable in public deployments.
    """
    # Simple authorization for safety
    if not settings.SMS_TEST_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="SMS test key not configured on server",
        )

    if x_sms_test_key is None or x_sms_test_key != settings.SMS_TEST_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid test key")

    # Ensure sms service is available
    try:
        from app.services.sms_service import sms_service
    except Exception as e:
        logger.error(f"SMS service import failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SMS service unavailable")

    # Send (sms_service will respect SMS_ENABLED and token config)
    sent = sms_service.send_sms(recipient=request.recipient, message=request.message)

    if not sent:
        logger.error(f"Failed to send test SMS to {request.recipient}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send SMS")

    return {"success": True, "recipient": request.recipient}
