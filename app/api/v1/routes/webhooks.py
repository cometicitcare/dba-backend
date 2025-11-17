from fastapi import APIRouter, Request, HTTPException, status
from typing import Any, Dict
import logging
from app.services.suppression_list import suppression_list
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/smtp2go")
async def smtp2go_webhook(request: Request) -> Dict[str, Any]:
    """
    SMTP2GO webhook handler with Bearer token authentication.

    Expected JSON example (simplified):
    {
      "events": [
        {"event": "bounce", "email": "user@example.com", "reason": "mailbox full"},
        {"event": "spam", "email": "user@example.com"},
        {"event": "blocked", "email": "user@example.com", "reason": "domain invalid"}
      ]
    }

    Authentication: Accepts token via:
    - Authorization: Bearer <token> header (SMTP2GO standard)
    - JSON body field "token" (fallback)

    We mark addresses in a temporary suppression list with TTL so transient
    inbox issues expire automatically.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON")

    # Optional shared-secret token check (header or body)
    expected = (settings.SMTP2GO_WEBHOOK_TOKEN or "").strip()
    if expected:
        # Check Authorization: Bearer header first (SMTP2GO standard)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            provided = auth_header[7:].strip()
        else:
            # Fallback to JSON body token field
            provided = (payload.get("token") or "").strip()
        
        if provided != expected:
            logger.warning(f"Webhook token validation failed from {request.client.host if request.client else 'unknown'}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    events = payload.get("events")
    if not isinstance(events, list):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing events array")

    suppressible = {"bounce", "blocked", "spam", "invalid", "dropped"}
    marked = 0
    for ev in events:
        if not isinstance(ev, dict):
            continue
        evt = str(ev.get("event") or ev.get("type") or "").lower()
        email = str(ev.get("email") or ev.get("recipient") or "").strip()
        reason = str(ev.get("reason") or ev.get("message") or evt)
        if evt in suppressible and email:
            suppression_list.mark(email, reason)
            marked += 1

    logger.info(f"SMTP2GO webhook processed: {len(events)} events, suppressed={marked}")
    # Best-effort prune expired entries occasionally
    try:
        pruned = suppression_list.prune()
        if pruned:
            logger.info(f"Suppression list pruned: {pruned} expired entries")
    except Exception:
        pass

    return {"ok": True, "suppressed": marked}
