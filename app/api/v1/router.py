# app/api/v1/router.py
from fastapi import APIRouter

import app.api.v1.routes.arama_data as arama_data
import app.api.v1.routes.audit_log as audit_log
import app.api.v1.routes.auth as auth
import app.api.v1.routes.bank_branches as bank_branches
import app.api.v1.routes.banks as banks
import app.api.v1.routes.beneficiary_data as beneficiary_data
import app.api.v1.routes.bhikku_category as bhikku_category
import app.api.v1.routes.bhikku_certification as bhikku_certification
import app.api.v1.routes.bhikku_high as bhikku_high
import app.api.v1.routes.bhikku_id_card as bhikku_id_card
import app.api.v1.routes.bhikku_nikaya_data as bhikku_nikaya_data
import app.api.v1.routes.bhikku_parshawa_data as bhikku_parshawa_data
import app.api.v1.routes.bhikkus as bhikkus
import app.api.v1.routes.qr_search as qr_search
import app.api.v1.routes.bhikku_summary as bhikku_summary
import app.api.v1.routes.certificate_changes as certificate_changes
import app.api.v1.routes.certificates as certificates
import app.api.v1.routes.city as city
import app.api.v1.routes.dashboard as dashboard
import app.api.v1.routes.debug as debug
import app.api.v1.routes.devala_data as devala_data
import app.api.v1.routes.direct_bhikku_high as direct_bhikku_high
import app.api.v1.routes.district as district
import app.api.v1.routes.divisional_secretariat as divisional_secretariat
import app.api.v1.routes.gramasewaka as gramasewaka
import app.api.v1.routes.health as health
import app.api.v1.routes.location_hierarchy as location_hierarchy
import app.api.v1.routes.nilame as nilame
import app.api.v1.routes.objections as objections
import app.api.v1.routes.objection_types as objection_types
import app.api.v1.routes.payment_methods as payment_methods
import app.api.v1.routes.province as province
import app.api.v1.routes.reprint as reprint
import app.api.v1.routes.reprint_search as reprint_search
import app.api.v1.routes.rbac_admin as rbac_admin
import app.api.v1.routes.nikaya_manage as nikaya_manage
import app.api.v1.routes.religion as religion
import app.api.v1.routes.roles as roles
import app.api.v1.routes.sasanarakshaka as sasanarakshaka
import app.api.v1.routes.sasanarakshana_regist as sasanarakshana_regist
import app.api.v1.routes.dayakasaba_regist as dayakasaba_regist
import app.api.v1.routes.gov_officers as gov_officers
import app.api.v1.routes.status as status
import app.api.v1.routes.silmatha_id as silmatha_id
import app.api.v1.routes.silmatha_id_card as silmatha_id_card
import app.api.v1.routes.silmatha_regist as silmatha_regist
import app.api.v1.routes.temporary_arama as temporary_arama
import app.api.v1.routes.temporary_bhikku as temporary_bhikku
import app.api.v1.routes.temporary_devala as temporary_devala
import app.api.v1.routes.temporary_silmatha as temporary_silmatha
import app.api.v1.routes.temporary_vihara as temporary_vihara
import app.api.v1.routes.vihara_data as vihara_data
import app.api.v1.routes.vihara_user_report as vihara_user_report
import app.api.v1.routes.viharanga as viharanga
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
# REPRINT SEARCH
# ============================================================================
api_router.include_router(
    reprint_search.router,
    tags=["🔄 Reprint Search"]
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
# DBA-HRMS: TEMPORARY BHIKKU
# ============================================================================
api_router.include_router(
    temporary_bhikku.router,
    prefix="/temporary-bhikku",
    tags=["👤 DBA-HRMS: Temporary Bhikku"]
)

# ============================================================================
# DBA-HRMS: TEMPORARY VIHARA
# ============================================================================
api_router.include_router(
    temporary_vihara.router,
    prefix="/temporary-vihara",
    tags=["🏛️ DBA-HRMS: Temporary Vihara"]
)

# ============================================================================
# DBA-HRMS: TEMPORARY ARAMA
# ============================================================================
api_router.include_router(
    temporary_arama.router,
    prefix="/temporary-arama",
    tags=["🏛️ DBA-HRMS: Temporary Arama"]
)

# ============================================================================
# DBA-HRMS: TEMPORARY DEVALA
# ============================================================================
api_router.include_router(
    temporary_devala.router,
    prefix="/temporary-devala",
    tags=["🏛️ DBA-HRMS: Temporary Devala"]
)

# ============================================================================
# DBA-HRMS: TEMPORARY SILMATHA
# ============================================================================
api_router.include_router(
    temporary_silmatha.router,
    prefix="/temporary-silmatha",
    tags=["👩 DBA-HRMS: Temporary Silmatha"]
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
    vihara_user_report.router,
    prefix="/vihara-user-report",
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
    nikaya_manage.router,
    prefix="/nikaya-manage",
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
    sasanarakshaka.router,
    prefix="/sasanarakshaka",
    tags=["📊 Master Data Management"]
)
api_router.include_router(
    sasanarakshana_regist.router,
    prefix="/sasanarakshana-regist-manage",
    tags=["📊 Master Data Management"]
)
api_router.include_router(
    dayakasaba_regist.router,
    prefix="/dayakasaba-regist-manage",
    tags=["📊 Master Data Management"]
)
api_router.include_router(
    gov_officers.router,
    prefix="/gov-officers",
    tags=["📊 Master Data Management"]
)
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
    viharanga.router, 
    prefix="/viharanga", 
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
    prefix="/location-hierarchy",
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
