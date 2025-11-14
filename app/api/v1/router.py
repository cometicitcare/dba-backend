# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.routes import (
    audit_log,
    auth,
    bank_branches,
    banks,
    beneficiary_data,
    bhikku_category,
    bhikku_certification,
    bhikku_high,
    bhikku_id_cards,
    bhikku_nikaya_data,
    bhikku_parshawa_data,
    bhikkus,
    bhikku_summary,
    bhikku_workflow,
    certificate_changes,
    certificates,
    city,
    dashboard,
    district,
    divisional_secretariat,
    gramasewaka,
    health,
    location_hierarchy,
    nilame,
    payment_methods,
    province,
    religion,
    roles,
    status,
    vihara_data,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(bhikkus.router, prefix="/bhikkus", tags=["Bhikkus"])
api_router.include_router(
    bhikku_workflow.router,
    prefix="/bhikkus/workflow",
    tags=["Bhikku Workflow"],
)
api_router.include_router(bhikku_high.router, prefix="/bhikkus-high", tags=["Bhikku High"])
api_router.include_router(
    bhikku_id_cards.router,
    prefix="/bhikku-id-cards",
    tags=["Bhikku ID Cards"],
)
api_router.include_router(
    bhikku_certification.router,
    prefix="/bhikkus-certifications",
    tags=["Bhikku Certification"],
)
api_router.include_router(
    certificates.router,
    prefix="/certificates",
    tags=["Certificates"],
)
api_router.include_router(
    certificate_changes.router,
    prefix="/certificate-changes",
    tags=["Certificate Changes"],
)
api_router.include_router(
    banks.router,
    prefix="/banks",
    tags=["Banks"],
)
api_router.include_router(
    bank_branches.router,
    prefix="/bank-branches",
    tags=["Bank Branches"],
)
api_router.include_router(
    payment_methods.router,
    prefix="/payment-methods",
    tags=["Payment Methods"],
)
api_router.include_router(
    bhikku_summary.router,
    prefix="/bhikkus-summary",
    tags=["Bhikku Summary"],
)
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(nilame.router, prefix="/nilame", tags=["Nilame"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(
    vihara_data.router,
    prefix="/vihara-data",
)
api_router.include_router(beneficiary_data.router, prefix="/beneficiary-data")
api_router.include_router(
    bhikku_parshawa_data.router,
    prefix="/bhikku-parshawa-data",
    tags=["Bhikku Parshawa Data"],
)
api_router.include_router(
    bhikku_nikaya_data.router,
    prefix="/bhikku-nikaya-data",
    tags=["Bhikku Nikaya Data"],
)
api_router.include_router(city.router, prefix="/city", tags=["City"])
api_router.include_router(
    gramasewaka.router, prefix="/gramasewaka", tags=["Gramasewaka Management"]
)
api_router.include_router(
    bhikku_category.router, prefix="/bhikku-category", tags=["Bhikku Category"]
)
api_router.include_router(district.router, prefix="/district", tags=["District"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(
    audit_log.router, prefix="/audit-log", tags=["Audit Log"]
)
api_router.include_router(
    religion.router, prefix="/religion", tags=["Religion"]
)
api_router.include_router(
    status.router, prefix="/status", tags=["Status"]
)
api_router.include_router(province.router, prefix="/province", tags=["Province"])
api_router.include_router(
    divisional_secretariat.router,
    prefix="/divisional-secretariat",
    tags=["Divisional Secretariat"],
)
api_router.include_router(
    location_hierarchy.router,
    prefix="/locations",
)
