# app/api/v1/routes/vihara_user_report.py
"""
Vihara Data-Entry User Activity Report
---------------------------------------
Provides per-user statistics for all users holding the VIHA_DATA role:
  • Total login sessions and cumulative working time (from login_history)
  • Record counts inserted / updated in vihara-related tables (from audit_log)
Supports optional date-range filtering.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, case, func, literal
from sqlalchemy.orm import Session

from app.api.auth_dependencies import has_any_permission, is_super_admin
from app.api.auth_middleware import get_current_user
from app.api.deps import get_db
from app.models.audit_log import AuditLog
from app.models.roles import Role
from app.models.user import LoginHistory, UserAccount
from app.models.user_roles import UserRole

router = APIRouter()  # Tags defined in router.py

# Tables that vihara data-entry users work with
VIHARA_TABLES = ("vihaddata", "temporary_vihara")


# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------
class RecordStats(BaseModel):
    """Counts per operation type."""
    created: int = 0
    updated: int = 0
    deleted: int = 0
    total: int = 0


class LoginStats(BaseModel):
    """Login / working-time statistics."""
    total_sessions: int = 0
    total_working_minutes: float = 0
    first_login: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserReport(BaseModel):
    """Per-user report entry."""
    user_id: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    user_status: Optional[str] = None
    vihara_records: RecordStats = Field(default_factory=RecordStats)
    temp_vihara_records: RecordStats = Field(default_factory=RecordStats)
    all_records: RecordStats = Field(default_factory=RecordStats)
    login_stats: LoginStats = Field(default_factory=LoginStats)


class ViharaUserReportResponse(BaseModel):
    status: str
    message: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    total_users: int = 0
    data: list[UserReport] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _record_stats_from_rows(rows) -> RecordStats:
    """Collapse rows of (operation, count) into a RecordStats."""
    stats = RecordStats()
    for op, cnt in rows:
        op_upper = (op or "").upper()
        if op_upper == "CREATE":
            stats.created += cnt
        elif op_upper == "UPDATE":
            stats.updated += cnt
        elif op_upper == "DELETE":
            stats.deleted += cnt
    stats.total = stats.created + stats.updated + stats.deleted
    return stats


def _get_vihara_data_entry_users(db: Session):
    """Return all active users with the VIHA_DATA role."""
    now = datetime.utcnow()
    return (
        db.query(UserAccount)
        .join(UserRole, UserRole.ur_user_id == UserAccount.ua_user_id)
        .filter(
            UserRole.ur_role_id == "VIHA_DATA",
            UserRole.ur_is_active.is_(True),
            (UserRole.ur_expires_date.is_(None) | (UserRole.ur_expires_date > now)),
            UserAccount.ua_is_deleted.is_(False),
        )
        .all()
    )


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.get(
    "/report",
    response_model=ViharaUserReportResponse,
    summary="Vihara data-entry user activity report",
)
def vihara_user_activity_report(
    date_from: Optional[date] = Query(None, description="Start date (inclusive)"),
    date_to: Optional[date] = Query(None, description="End date (inclusive)"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Returns an activity report for all **Vihara Data Entry** users:
    - How many vihara / temporary-vihara records they created, updated, deleted.
    - Login session count and cumulative working time.
    Filterable by date range.
    Only accessible by admins (VIHA_ADM) or super admins.
    """
    # ── Access check ──────────────────────────────────────────────────────
    if not is_super_admin(db, current_user):
        now = datetime.utcnow()
        admin_role = (
            db.query(UserRole)
            .filter(
                UserRole.ur_user_id == current_user.ua_user_id,
                UserRole.ur_role_id == "VIHA_ADM",
                UserRole.ur_is_active.is_(True),
                (UserRole.ur_expires_date.is_(None) | (UserRole.ur_expires_date > now)),
            )
            .first()
        )
        if not admin_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Only Vihara Admins or Super Admins can view this report.",
            )

    # ── Resolve date boundaries ───────────────────────────────────────────
    ts_from: Optional[datetime] = None
    ts_to: Optional[datetime] = None
    if date_from:
        ts_from = datetime.combine(date_from, datetime.min.time())
    if date_to:
        ts_to = datetime.combine(date_to, datetime.max.time())

    # ── Gather vihara data-entry users ────────────────────────────────────
    users = _get_vihara_data_entry_users(db)
    if not users:
        return ViharaUserReportResponse(
            status="success",
            message="No vihara data-entry users found.",
            date_from=date_from,
            date_to=date_to,
            total_users=0,
            data=[],
        )

    user_ids = [u.ua_user_id for u in users]

    # ── Audit log stats (record counts) ───────────────────────────────────
    audit_q = db.query(
        AuditLog.al_user_id,
        AuditLog.al_table_name,
        AuditLog.al_operation,
        func.count().label("cnt"),
    ).filter(
        AuditLog.al_user_id.in_(user_ids),
        AuditLog.al_table_name.in_(VIHARA_TABLES),
    )
    if ts_from:
        audit_q = audit_q.filter(AuditLog.al_timestamp >= ts_from)
    if ts_to:
        audit_q = audit_q.filter(AuditLog.al_timestamp <= ts_to)

    audit_rows = audit_q.group_by(
        AuditLog.al_user_id,
        AuditLog.al_table_name,
        AuditLog.al_operation,
    ).all()

    # Build a nested dict:  { user_id: { table: [(op, cnt), ...] } }
    audit_map: dict[str, dict[str, list]] = {}
    for uid, table, op, cnt in audit_rows:
        audit_map.setdefault(uid, {}).setdefault(table, []).append((op, cnt))

    # ── Login history stats ───────────────────────────────────────────────
    login_q = db.query(
        LoginHistory.lh_user_id,
        func.count().label("sessions"),
        func.sum(
            case(
                (
                    and_(
                        LoginHistory.lh_logout_time.isnot(None),
                        LoginHistory.lh_login_time.isnot(None),
                    ),
                    func.extract("epoch", LoginHistory.lh_logout_time)
                    - func.extract("epoch", LoginHistory.lh_login_time),
                ),
                else_=literal(0),
            )
        ).label("total_seconds"),
        func.min(LoginHistory.lh_login_time).label("first_login"),
        func.max(LoginHistory.lh_login_time).label("last_login"),
    ).filter(
        LoginHistory.lh_user_id.in_(user_ids),
        LoginHistory.lh_success.is_(True),
    )
    if ts_from:
        login_q = login_q.filter(LoginHistory.lh_login_time >= ts_from)
    if ts_to:
        login_q = login_q.filter(LoginHistory.lh_login_time <= ts_to)

    login_rows = login_q.group_by(LoginHistory.lh_user_id).all()

    login_map: dict[str, dict] = {}
    for uid, sessions, total_sec, first_l, last_l in login_rows:
        login_map[uid] = {
            "total_sessions": sessions or 0,
            "total_working_minutes": round((total_sec or 0) / 60, 1),
            "first_login": first_l,
            "last_login": last_l,
        }

    # ── Assemble response ─────────────────────────────────────────────────
    reports: list[UserReport] = []
    for u in users:
        uid = u.ua_user_id
        user_audit = audit_map.get(uid, {})

        vihara_stats = _record_stats_from_rows(user_audit.get("vihaddata", []))
        temp_stats = _record_stats_from_rows(user_audit.get("temporary_vihara", []))
        all_stats = RecordStats(
            created=vihara_stats.created + temp_stats.created,
            updated=vihara_stats.updated + temp_stats.updated,
            deleted=vihara_stats.deleted + temp_stats.deleted,
            total=vihara_stats.total + temp_stats.total,
        )

        login_info = login_map.get(uid, {})

        reports.append(
            UserReport(
                user_id=uid,
                username=u.ua_username,
                first_name=u.ua_first_name,
                last_name=u.ua_last_name,
                email=u.ua_email,
                user_status=u.ua_status,
                vihara_records=vihara_stats,
                temp_vihara_records=temp_stats,
                all_records=all_stats,
                login_stats=LoginStats(**login_info) if login_info else LoginStats(),
            )
        )

    # Sort by total records desc (most productive first)
    reports.sort(key=lambda r: r.all_records.total, reverse=True)

    return ViharaUserReportResponse(
        status="success",
        message=f"Activity report for {len(reports)} vihara data-entry user(s).",
        date_from=date_from,
        date_to=date_to,
        total_users=len(reports),
        data=reports,
    )
