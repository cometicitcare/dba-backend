# app/services/audit_service.py
from __future__ import annotations

import json
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Iterable, Optional
from uuid import uuid4

from fastapi.encoders import jsonable_encoder
from sqlalchemy import event, inspect
from sqlalchemy.orm import Mapper, Session

from app.db.session import SessionLocal
from app.models.audit_log import AuditLog


@dataclass(slots=True)
class AuditContext:
    transaction_id: str
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    route: Optional[str]
    method: Optional[str]


class AuditService:
    def __init__(self) -> None:
        self._context_var: ContextVar[AuditContext | None] = ContextVar(
            "audit_context", default=None
        )

    # ------------------------------------------------------------------ #
    # Request Context Helpers
    # ------------------------------------------------------------------ #
    def begin_request(
        self,
        *,
        user_id: Optional[str],
        session_id: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str],
        route: Optional[str],
        method: Optional[str],
        transaction_id: Optional[str] = None,
    ):
        context = AuditContext(
            transaction_id=transaction_id or str(uuid4()),
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            route=route,
            method=method,
        )
        token = self._context_var.set(context)
        return token, context.transaction_id

    def end_request(self, token) -> None:
        try:
            self._context_var.reset(token)
        except (ValueError, LookupError):
            # Already cleared or never set; ignore quietly
            pass

    def get_context(self) -> Optional[AuditContext]:
        return self._context_var.get()

    # ------------------------------------------------------------------ #
    # Logging helpers
    # ------------------------------------------------------------------ #
    def log_api_call(
        self,
        db: Session,
        *,
        status_code: int,
        response_payload: Optional[dict[str, Any]] = None,
    ) -> None:
        context = self.get_context()
        if not context:
            return

        operation = self._infer_operation_from_method(context.method)
        response_data = None
        if response_payload is not None:
            try:
                response_data = jsonable_encoder(response_payload)
            except TypeError:
                # Fallback: ensure serialization does not fail
                response_data = json.loads(json.dumps(response_payload, default=str))

        entry = AuditLog(
            al_table_name="__api_call__",
            al_record_id=context.route or "unknown",
            al_operation=operation,
            al_old_values=None,
            al_new_values={"status_code": status_code, "response": response_data},
            al_changed_fields=None,
            al_user_id=context.user_id,
            al_session_id=context.session_id,
            al_ip_address=context.ip_address,
            al_user_agent=context.user_agent,
            al_transaction_id=context.transaction_id,
        )
        db.add(entry)
        db.commit()

    # ------------------------------------------------------------------ #
    # SQLAlchemy instrumentation
    # ------------------------------------------------------------------ #
    def _collect_instance_payload(
        self,
        mapper: Mapper,
        instance: Any,
        *,
        columns: Optional[Iterable[str]] = None,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for attr in mapper.column_attrs:
            key = attr.key
            if columns and key not in columns:
                continue
            value = getattr(instance, key, None)
            result[key] = self._serialize_value(value)
        return result

    def _serialize_value(self, value: Any) -> Any:
        try:
            return jsonable_encoder(value)
        except TypeError:
            return json.loads(json.dumps(value, default=str))

    def _infer_operation_from_method(self, method: Optional[str]) -> str:
        if not method:
            return "READ"
        mapping = {
            "GET": "READ",
            "HEAD": "READ",
            "OPTIONS": "READ",
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE",
        }
        return mapping.get(method.upper(), "READ")


audit_service = AuditService()


# ---------------------------------------------------------------------- #
# SQLAlchemy session hooks for automatic audit capture
# ---------------------------------------------------------------------- #
def _is_audit_model(instance: Any) -> bool:
    return isinstance(instance, AuditLog)


def _collect_update_changes(instance) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    state = inspect(instance)
    mapper = state.mapper
    old_values: dict[str, Any] = {}
    new_values: dict[str, Any] = {}
    changed_fields: list[str] = []

    for attr in mapper.column_attrs:
        hist = state.attrs[attr.key].history
        if not hist.has_changes():
            continue
        # Skip primary key modifications to avoid redundant records
        if attr.key in mapper.primary_key:
            continue

        old_val = hist.deleted[0] if hist.deleted else None
        new_val = hist.added[0] if hist.added else getattr(instance, attr.key, None)
        old_values[attr.key] = audit_service._serialize_value(old_val)
        new_values[attr.key] = audit_service._serialize_value(new_val)
        changed_fields.append(attr.key)

    return old_values, new_values, changed_fields


def _get_record_id(instance) -> str:
    state = inspect(instance)
    if state.identity:
        if len(state.identity) == 1:
            return str(state.identity[0])
        return ":".join(str(item) for item in state.identity)

    # For instances without identity yet (e.g., before flush without PK),
    # fall back to primary key attribute values if available.
    mapper = state.mapper
    pk_values = []
    for pk_col in mapper.primary_key:
        value = getattr(instance, pk_col.name, None)
        pk_values.append(str(value) if value is not None else "None")
    return ":".join(pk_values) if pk_values else "pending"


@event.listens_for(SessionLocal, "before_flush")
def capture_audit_events(session: Session, flush_context, instances):
    if session.info.get("skip_audit", False):
        return

    entries: list[dict[str, Any]] = session.info.setdefault("_audit_entries", [])
    context = audit_service.get_context()

    # Handle new objects (CREATE)
    for instance in session.new:
        if _is_audit_model(instance):
            continue
        mapper = inspect(instance).mapper
        new_values = audit_service._collect_instance_payload(mapper, instance)
        entries.append(
            {
                "instance": instance,
                "operation": "CREATE",
                "table_name": mapper.local_table.name,
                "record_id": None,  # Filled after flush when PK is available
                "old_values": None,
                "new_values": new_values,
                "changed_fields": list(new_values.keys()),
                "user_id": context.user_id if context else None,
                "session_id": context.session_id if context else None,
                "ip_address": context.ip_address if context else None,
                "user_agent": context.user_agent if context else None,
                "transaction_id": context.transaction_id if context else None,
            }
        )

    # Handle updated objects (UPDATE)
    for instance in session.dirty:
        if _is_audit_model(instance):
            continue
        state = inspect(instance)
        if not state.persistent or not state.has_identity:
            continue

        old_values, new_values, changed_fields = _collect_update_changes(instance)
        if not changed_fields:
            continue

        mapper = state.mapper
        entries.append(
            {
                "instance": instance,
                "operation": "UPDATE",
                "table_name": mapper.local_table.name,
                "record_id": _get_record_id(instance),
                "old_values": old_values,
                "new_values": new_values,
                "changed_fields": changed_fields,
                "user_id": context.user_id if context else None,
                "session_id": context.session_id if context else None,
                "ip_address": context.ip_address if context else None,
                "user_agent": context.user_agent if context else None,
                "transaction_id": context.transaction_id if context else None,
            }
        )

    # Handle deletions (DELETE)
    for instance in session.deleted:
        if _is_audit_model(instance):
            continue
        state = inspect(instance)
        mapper = state.mapper
        old_values = audit_service._collect_instance_payload(mapper, instance)
        entries.append(
            {
                "instance": instance,
                "operation": "DELETE",
                "table_name": mapper.local_table.name,
                "record_id": _get_record_id(instance),
                "old_values": old_values,
                "new_values": None,
                "changed_fields": list(old_values.keys()),
                "user_id": context.user_id if context else None,
                "session_id": context.session_id if context else None,
                "ip_address": context.ip_address if context else None,
                "user_agent": context.user_agent if context else None,
                "transaction_id": context.transaction_id if context else None,
            }
        )


@event.listens_for(SessionLocal, "after_flush")
def persist_audit_events(session: Session, flush_context):
    entries = session.info.pop("_audit_entries", [])
    if not entries:
        return

    session.info["skip_audit"] = True
    try:
        for entry in entries:
            instance = entry.get("instance")
            if instance is not None and entry.get("record_id") in (None, "pending"):
                entry["record_id"] = _get_record_id(instance)

            session.add(
                AuditLog(
                    al_table_name=entry["table_name"],
                    al_record_id=str(entry["record_id"] or "unknown"),
                    al_operation=entry["operation"],
                    al_old_values=entry["old_values"],
                    al_new_values=entry["new_values"],
                    al_changed_fields=entry["changed_fields"],
                    al_user_id=entry["user_id"],
                    al_session_id=entry["session_id"],
                    al_ip_address=entry["ip_address"],
                    al_user_agent=entry["user_agent"],
                    al_transaction_id=entry["transaction_id"],
                )
            )
    finally:
        session.info["skip_audit"] = False
