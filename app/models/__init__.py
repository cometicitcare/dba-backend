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
from app.models.reprint_request import ReprintRequest

# Geographic/Location models
from app.models.province import Province
from app.models.district import District
from app.models.city import City
from app.models.divisional_secretariat import DivisionalSecretariat
from app.models.gramasewaka import Gramasewaka

# Branch models for location-based access control
from app.models.main_branch import MainBranch
from app.models.district_branch import DistrictBranch

# Bhikku/Monk models
from app.models.bhikku import Bhikku
from app.models.bhikku_regist_old import BhikkuRegistOld
from app.models.bhikku_high import BhikkuHighRegist
from app.models.direct_bhikku_high import DirectBhikkuHigh
from app.models.bhikku_summary import BhikkuSummary
from app.models.bhikku_category import BhikkuCategory
from app.models.bhikku_certification import BhikkuCertification
from app.models.bhikku_id_card import BhikkuIDCard

# Temple/Vihara models
from app.models.vihara import ViharaData
from app.models.temple_land import TempleLand
from app.models.resident_bhikkhu import ResidentBhikkhu
from app.models.vihara_land import ViharaLand
from app.models.nikaya import NikayaData
from app.models.parshawadata import ParshawaData
from app.models.arama import AramaData
from app.models.arama_land import AramaLand
from app.models.arama_resident_silmatha import AramaResidentSilmatha
from app.models.devala import DevalaData
from app.models.devala_land import DevalaLand
# from app.models.nilame import Nilame
from app.models.silmatha_regist import SilmathaRegist
from app.models.silmatha_id_card import SilmathaIDCard

# Objection model
from app.models.objection import Objection
from app.models.objection_type import ObjectionType

# Sasanaarakshana Registration
from app.models.sasanarakshana_regist import SasanarakshanaRegist
from app.models.sasanarakshaka import SasanarakshakaBalaMandalaya

# Other models
from app.models.status import StatusData
# from app.models.certificate import Certificate
# from app.models.certificate_change import CertificateChange
# from app.models.bank import Bank
# from app.models.bank_branch import BankBranch
# from app.models.beneficiary import Beneficiary
# from app.models.payment_method import PaymentMethod
# from app.models.religion import Religion
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
    "ReprintRequest",
    # Geographic
    "Province",
    "District",
    "City",
    "DivisionalSecretariat",
    "Gramasewaka",
    # Branches
    "MainBranch",
    "DistrictBranch",
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
