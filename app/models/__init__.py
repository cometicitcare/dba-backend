# Import all models here to ensure they're registered with SQLAlchemy
# This is important for Alembic migrations to detect all models

from app.models.user import UserAccount, LoginHistory
from app.models.roles import Role
from app.models.group import Group
from app.models.permissions import Permission
from app.models.user_roles import UserRole
from app.models.user_group import UserGroup
from app.models.role_permissions import RolePermission
from app.models.user_permission import UserPermission

# Geographic/Location models
from app.models.province import Province
from app.models.district import District
from app.models.city import City
from app.models.divisional_secretariat import DivisionalSecretariat
from app.models.gramasewaka import Gramasewaka

# # Bhikku/Monk models
# from app.models.bhikku import Bhikku
# from app.models.bhikku_high import BhikkuHighRegist
# from app.models.bhikku_summary import BhikkuSummary
# from app.models.bhikku_category import BhikkuCategory
# from app.models.bhikku_certification import BhikkuCertification
# from app.models.bhikku_id_card import BhikkuIDCard

# # Temple/Vihara models
# from app.models.vihara import Vihara
# from app.models.nikaya import Nikaya
# from app.models.nilame import Nilame
# from app.models.parshawadata import ParshawaData
# from app.models.silmatha_id_card import SilmathaIDCard

# # Certificate models
# from app.models.certificate import Certificate
# from app.models.certificate_change import CertificateChange

# # Other models
# from app.models.bank import Bank
# from app.models.bank_branch import BankBranch
# from app.models.beneficiary import Beneficiary
# from app.models.payment_method import PaymentMethod
# from app.models.religion import Religion
# from app.models.status import Status
# from app.models.audit_log import AuditLog

__all__ = [
    # Auth & RBAC
    "UserAccount",
    "LoginHistory",
    "Role",
    "Group",
    "Permission",
    "UserRole",
    "UserGroup",
    "RolePermission",
    "UserPermission",
    # Geographic
    "Province",
    "District",
    "City",
    "DivisionalSecretariat",
    "Gramasewaka",
    # # Bhikku
    # "Bhikku",
    # "BhikkuHigh",
    # "BhikkuSummary",
    # "BhikkuCategory",
    # "BhikkuCertification",
    # "BhikkuIDCard",
    # # Vihara
    # "Vihara",
    # "Nikaya",
    # "Nilame",
    # "ParshawaData",
    # "SilmathaIDCard",
    # # Certificates
    # "Certificate",
    # "CertificateChange",
    # # Other
    # "Bank",
    # "BankBranch",
    # "Beneficiary",
    # "PaymentMethod",
    # "Religion",
    # "Status",
    # "AuditLog",
]
