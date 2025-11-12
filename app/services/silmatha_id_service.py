from __future__ import annotations

from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.models.bhikku import Bhikku
from app.models.bhikku_certification import BhikkuCertification
from app.models.vihara import ViharaData
from app.schemas.silmatha_id import (
    DeclarationWithDate,
    SilmathaIDAcharyaInfo,
    SilmathaIDApplicantInfo,
    SilmathaIDCardData,
)


class SilmathaIDService:
    """Prepare ID card data for Silmatha (br_cat == CAT01) records."""

    SILMATHA_CATEGORY = "CAT01"

    def get_id_card_details(self, db: Session, *, regn: str) -> SilmathaIDCardData:
        lookup_key = regn.strip() if isinstance(regn, str) else ""
        if not lookup_key:
            raise ValueError("Registration number is required.")

        bhikku = (
            db.query(Bhikku)
            .filter(
                Bhikku.br_regn == lookup_key,
                Bhikku.br_is_deleted.is_(False),
            )
            .first()
        )
        if not bhikku:
            raise ValueError("Silmatha record not found.")

        category = (bhikku.br_cat or "").strip().upper()
        if category != self.SILMATHA_CATEGORY:
            raise ValueError("Registration number does not belong to a Silmatha (CAT01).")

        acharya = self._get_bhikku_by_regn(db, bhikku.br_mahanaacharyacd)
        acharya_residence = self._get_vihara_details(db, acharya.br_livtemple) if acharya else None

        silmatha_residence = self._get_vihara_details(db, bhikku.br_livtemple)

        certificate_exists = self._has_certificate(db, lookup_key)

        acharya_info = SilmathaIDAcharyaInfo(
            full_name=self._prefer_name(acharya),
            residence=self._format_location(
                acharya_residence.get("name") if acharya_residence else None,
                acharya_residence.get("address") if acharya_residence else None,
            ),
            phone_number=acharya.br_mobile if acharya else None,
            date_of_robing=acharya.br_mahanadate if acharya else None,
            date_registered=acharya.br_reqstdate if acharya else None,
            registration_number=acharya.br_regn if acharya else bhikku.br_mahanaacharyacd,
        )

        applicant_info = SilmathaIDApplicantInfo(
            full_name=bhikku.br_mahananame or bhikku.br_gihiname,
            aramaya_address=self._format_location(
                silmatha_residence.get("name") if silmatha_residence else None,
                silmatha_residence.get("address") if silmatha_residence else None,
            ),
            date_registered=bhikku.br_reqstdate,
            registration_number=bhikku.br_regn,
            certificate_copy_attached=certificate_exists,
            date_of_birth=bhikku.br_dofb,
            national_id=None,
            date_of_robing=bhikku.br_mahanadate,
            lay_name=bhikku.br_gihiname,
            birth_certificate_attached=None,
            highest_education=None,
            guardian_name=bhikku.br_fathrname,
            guardian_address=bhikku.br_fathrsaddrs,
            guardian_phone_number=bhikku.br_fathrsmobile,
            permanent_residence=self._format_location(
                silmatha_residence.get("name") if silmatha_residence else None,
                silmatha_residence.get("address") if silmatha_residence else None,
                bhikku.br_fathrsaddrs,
            ),
            left_thumbprint_url=None,
            applicant_image_url=None,
            application_date=bhikku.br_effctdate or bhikku.br_reqstdate,
            acharya_declaration=DeclarationWithDate(
                phone_number=acharya.br_mobile if acharya else None,
            ),
            grama_niladari_declaration=DeclarationWithDate(),
            devotional_secretariat_declaration=DeclarationWithDate(
                phone_number=bhikku.br_mobile,
            ),
        )

        return SilmathaIDCardData(
            form_id=bhikku.br_regn,
            district=bhikku.br_district,
            acharya=acharya_info,
            applicant=applicant_info,
        )

    @staticmethod
    def _get_bhikku_by_regn(db: Session, regn: Optional[str]) -> Optional[Bhikku]:
        if not regn:
            return None
        return (
            db.query(Bhikku)
            .filter(
                Bhikku.br_regn == regn,
                Bhikku.br_is_deleted.is_(False),
            )
            .first()
        )

    @staticmethod
    def _get_vihara_details(
        db: Session, vihara_code: Optional[str]
    ) -> Optional[Dict[str, Optional[str]]]:
        if not vihara_code:
            return None

        vihara = (
            db.query(ViharaData)
            .filter(
                ViharaData.vh_trn == vihara_code,
                ViharaData.vh_is_deleted.is_(False),
            )
            .first()
        )
        if not vihara:
            return None

        return {
            "name": vihara.vh_vname,
            "address": vihara.vh_addrs,
            "phone": vihara.vh_mobile,
        }

    @staticmethod
    def _format_location(*parts: Optional[str]) -> Optional[str]:
        meaningful = [
            part.strip()
            for part in parts
            if isinstance(part, str) and part.strip()
        ]
        if not meaningful:
            return None
        return ", ".join(dict.fromkeys(meaningful))

    @staticmethod
    def _prefer_name(record: Optional[Bhikku]) -> Optional[str]:
        if not record:
            return None
        return record.br_mahananame or record.br_gihiname

    @staticmethod
    def _has_certificate(db: Session, regn: str) -> bool:
        exists = (
            db.query(BhikkuCertification)
            .filter(
                BhikkuCertification.bc_regno == regn,
                BhikkuCertification.bc_is_deleted.is_(False),
            )
            .first()
        )
        return exists is not None


silmatha_id_service = SilmathaIDService()

