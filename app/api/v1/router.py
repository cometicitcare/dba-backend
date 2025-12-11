# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.routes import (
    arama_data,
    audit_log,
    auth,
    bank_branches,
    banks,
    beneficiary_data,
    bhikku_category,
    bhikku_certification,
    bhikku_high,
    bhikku_id_card,
    bhikku_nikaya_data,
    bhikku_parshawa_data,
    bhikkus,
    qr_search,
    bhikku_summary,
    certificate_changes,
    certificates,
    city,
    dashboard,
    debug,
    devala_data,
    direct_bhikku_high,
    district,
    divisional_secretariat,
    gramasewaka,
    health,
    location_hierarchy,
    nilame,
    objections,
    objection_types,
    payment_methods,
    province,
    reprint,
    rbac_admin,
    religion,
    roles,
    status,
    silmatha_id,
    silmatha_id_card,
    silmatha_regist,
    vihara_data,
)
from app.api.v1 import auth_sms_test

api_router = APIRouter()

# ============================================================================
# HEALTH & STATUS
# ============================================================================
api_router.include_router(
    health.router, 
    tags=["🏥 Health & Status"]
)

# ============================================================================
# QR SEARCH (public)
# ============================================================================
api_router.include_router(
    qr_search.router,
    tags=["🔍 QR Search"]
)

# ============================================================================
# AUTHENTICATION & AUTHORIZATION
# ============================================================================
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["🔐 Authentication & Authorization"]
)
api_router.include_router(
    auth_sms_test.router, 
    prefix="/auth", 
    tags=["🔐 Authentication & Authorization"]
)

# ============================================================================
# DBA-HRMS: BHIKKU REGISTRATION
# ============================================================================
api_router.include_router(
    bhikkus.router, 
    prefix="/bhikkus", 
    tags=["👤 DBA-HRMS: Bhikku Registration"]
)
api_router.include_router(
    bhikku_high.router, 
    prefix="/bhikkus-high", 
    tags=["👤 DBA-HRMS: Bhikku Registration"]
)
api_router.include_router(
    direct_bhikku_high.router, 
    prefix="/direct-bhikku-high", 
    tags=["👤 DBA-HRMS: Direct High Bhikku Registration"]
)
api_router.include_router(
    bhikku_summary.router,
    prefix="/bhikkus-summary",
    tags=["👤 DBA-HRMS: Bhikku Registration"]
)

# ============================================================================
# DBA-HRMS: BHIKKU ID CARD
# ============================================================================
api_router.include_router(
    bhikku_id_card.router,
    prefix="/bhikku-id-card",
    tags=["🪪 DBA-HRMS: Bhikku ID Card"]
)

# ============================================================================
# DBA-HRMS: REPRINT REQUESTS (Central)
# ============================================================================
api_router.include_router(
    reprint.router,
    prefix="/reprint",
    tags=["📜 Reprint Requests"]
)

# ============================================================================
# DBA-HRMS: CERTIFICATIONS & DOCUMENTS
# ============================================================================
api_router.include_router(
    bhikku_certification.router,
    prefix="/bhikkus-certifications",
    tags=["📜 DBA-HRMS: Certifications & Documents"]
)
api_router.include_router(
    certificates.router,
    prefix="/certificates",
    tags=["📜 DBA-HRMS: Certifications & Documents"]
)
api_router.include_router(
    certificate_changes.router,
    prefix="/certificate-changes",
    tags=["📜 DBA-HRMS: Certifications & Documents"]
)

# ============================================================================
# SILMATHA MANAGEMENT
# ============================================================================
api_router.include_router(
    silmatha_id.router,
    prefix="/silmatha-id",
    tags=["🕉️ Silmatha Management"]
)
api_router.include_router(
    silmatha_id_card.router,
    prefix="/silmatha-id-card",
    tags=["🕉️ Silmatha Management"]
)
api_router.include_router(
    silmatha_regist.router,
    prefix="/silmatha-regist",
    tags=["🕉️ Silmatha Management"]
)

# ============================================================================
# VIHARA & RELIGIOUS DATA
# ============================================================================
api_router.include_router(
    vihara_data.router,
    prefix="/vihara-data",
    tags=["🏛️ Vihara & Religious Data"]
)
api_router.include_router(
    arama_data.router,
    prefix="/arama-data",
    tags=["🏛️ Vihara & Religious Data"]
)
api_router.include_router(
    devala_data.router,
    prefix="/devala-data",
    tags=["🏛️ Vihara & Religious Data"]
)
api_router.include_router(
    bhikku_parshawa_data.router,
    prefix="/bhikku-parshawa-data",
    tags=["🏛️ Vihara & Religious Data"]
)
api_router.include_router(
    bhikku_nikaya_data.router,
    prefix="/bhikku-nikaya-data",
    tags=["🏛️ Vihara & Religious Data"]
)
api_router.include_router(
    religion.router, 
    prefix="/religion", 
    tags=["🏛️ Vihara & Religious Data"]
)
api_router.include_router(
    nilame.router, 
    prefix="/nilame", 
    tags=["🏛️ Vihara & Religious Data"]
)
api_router.include_router(
    objections.router,
    prefix="/objections",
    tags=["🏛️ Vihara & Religious Data"]
)
api_router.include_router(
    objection_types.router,
    prefix="/objections",
    tags=["🏛️ Vihara & Religious Data"]
)

# ============================================================================
# MASTER DATA MANAGEMENT
# ============================================================================
api_router.include_router(
    banks.router,
    prefix="/banks",
    tags=["📊 Master Data Management"]
)
api_router.include_router(
    bank_branches.router,
    prefix="/bank-branches",
    tags=["📊 Master Data Management"]
)
api_router.include_router(
    payment_methods.router,
    prefix="/payment-methods",
    tags=["📊 Master Data Management"]
)
api_router.include_router(
    beneficiary_data.router, 
    prefix="/beneficiary-data",
    tags=["📊 Master Data Management"]
)
api_router.include_router(
    bhikku_category.router, 
    prefix="/bhikku-category", 
    tags=["📊 Master Data Management"]
)
api_router.include_router(
    status.router, 
    prefix="/status", 
    tags=["📊 Master Data Management"]
)

# ============================================================================
# LOCATION MANAGEMENT
# ============================================================================
api_router.include_router(
    province.router, 
    prefix="/province", 
    tags=["📍 Location Management"]
)
api_router.include_router(
    district.router, 
    prefix="/district", 
    tags=["📍 Location Management"]
)
api_router.include_router(
    city.router, 
    prefix="/city", 
    tags=["📍 Location Management"]
)
api_router.include_router(
    divisional_secretariat.router,
    prefix="/divisional-secretariat",
    tags=["📍 Location Management"]
)
api_router.include_router(
    gramasewaka.router, 
    prefix="/gramasewaka", 
    tags=["📍 Location Management"]
)
api_router.include_router(
    location_hierarchy.router,
    prefix="/locations",
    tags=["📍 Location Management"]
)

# ============================================================================
# USER & ROLE MANAGEMENT (RBAC)
# ============================================================================
api_router.include_router(
    rbac_admin.router,
    prefix="/admin",
    tags=["👥 User & Role Management"]
)
api_router.include_router(
    roles.router, 
    prefix="/roles", 
    tags=["👥 User & Role Management"]
)

# ============================================================================
# DASHBOARD & REPORTS
# ============================================================================
api_router.include_router(
    dashboard.router, 
    prefix="/dashboard", 
    tags=["📈 Dashboard & Reports"]
)

# ============================================================================
# AUDIT & MONITORING
# ============================================================================
api_router.include_router(
    audit_log.router, 
    prefix="/audit-log", 
    tags=["🔍 Audit & Monitoring"]
)

# ============================================================================
# SYSTEM & DEBUG
# ============================================================================
api_router.include_router(
    debug.router, 
    tags=["🛠️ System & Debug"]
)
