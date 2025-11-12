from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.bhikku import Bhikku
from app.models.nikaya import NikayaData
from app.models.parshawadata import ParshawaData
from app.models.status import StatusData
from app.models.vihara import ViharaData
from app.repositories.bhikku_id_repo import bhikku_id_repo
from app.schemas.bhikku_id import (
    BhikkuIDBirthDetails,
    BhikkuIDCardData,
    BhikkuIDDeclaration,
    BhikkuIDDeclarationDetail,
    BhikkuIDDeclarations,
    BhikkuIDDocuments,
    BhikkuIDHigherOrdination,
    BhikkuIDOrdinationDetails,
    BhikkuIDReferences,
)


class BhikkuIDService:
    """Aggregate helper that prepares Bhikku ID card payloads."""

    def __init__(self) -> None:
        self._id_lookup_query = text(
            """
            SELECT idn, stat, reqstdate, printdate, issuedate, mahanaacharyacd,
                   archadrs, achambl, achamhndate, acharegdt, mahananame, vname,
                   addrs, regn, dofb, mahanadate, gihiname, fathrdetails
            FROM bikkudtls_id_alllist
            WHERE regn = :regn
            LIMIT 1
            """
        )

    def get_id_card_details(self, db: Session, *, regn: str) -> BhikkuIDCardData:
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
            raise ValueError("Bhikku record not found.")

        id_meta = self._fetch_id_card_meta(db, lookup_key)

        status_descr = self._resolve_status_description(db, bhikku.br_currstat)
        parshawa_name, nikaya_name = self._resolve_parshawa_and_nikaya(
            db, bhikku.br_parshawaya
        )
        robe_location = self._resolve_vihara(db, bhikku.br_mahanatemple)
        residence = self._resolve_vihara(db, bhikku.br_livtemple)

        acharya_record = self._get_bhikku(db, bhikku.br_mahanaacharyacd)
        acharya_name = self._prefer_name(acharya_record) or id_meta.get("achambl")

        chief_incumbent_name: Optional[str] = None
        chief_incumbent_address: Optional[str] = None
        if residence:
            chief_incumbent_address = residence.get("address")
            owner_regn = residence.get("owner_regn")
            chief_incumbent = self._get_bhikku(db, owner_regn)
            chief_incumbent_name = self._prefer_name(chief_incumbent)

        permanent_residence = self._build_address_string(
            residence.get("name") if residence else None,
            residence.get("address") if residence else None,
        )

        ordination_place = self._build_address_string(
            robe_location.get("name") if robe_location else None,
            robe_location.get("address") if robe_location else None,
        )

        higher_name = id_meta.get("mahananame") or bhikku.br_mahananame

        payload = BhikkuIDCardData(
            form_no=id_meta.get("idn") or bhikku.br_regn,
            divisional_secretariat=bhikku.br_division,
            district=bhikku.br_district,
            declaration=BhikkuIDDeclaration(
                full_bhikku_name=higher_name,
                title_or_post=status_descr,
            ),
            birth_certificate=BhikkuIDBirthDetails(
                lay_name=id_meta.get("gihiname") or bhikku.br_gihiname,
                date_of_birth=id_meta.get("dofb") or bhikku.br_dofb,
                place_of_birth=bhikku.br_birthpls,
            ),
            ordination=BhikkuIDOrdinationDetails(
                date_of_robing=id_meta.get("reqstdate") or bhikku.br_reqstdate,
                place_of_robing=ordination_place,
                nikaya=nikaya_name,
                parshawaya=parshawa_name,
            ),
            higher_ordination=BhikkuIDHigherOrdination(
                samanera_reg_no=bhikku.br_regn,
                upasampada_reg_no=bhikku.br_upasampada_serial_no,
                higher_ordination_date=id_meta.get("mahanadate") or bhikku.br_mahanadate,
            ),
            higher_ordination_name=higher_name,
            permanent_residence=permanent_residence or bhikku.br_fathrsaddrs,
            documents=BhikkuIDDocuments(),
            references=BhikkuIDReferences(
                acharya_name=acharya_name,
                chief_incumbent_name=chief_incumbent_name,
                chief_incumbent_address=chief_incumbent_address,
            ),
            declarations=BhikkuIDDeclarations(
                acharya_declaration=BhikkuIDDeclarationDetail(
                    phone_number=acharya_record.br_mobile if acharya_record else None,
                ),
                grama_niladari_declaration=BhikkuIDDeclarationDetail(),
                devotional_secretariat_declaration=BhikkuIDDeclarationDetail(
                    phone_number=bhikku.br_mobile,
                ),
            ),
        )

        self._enrich_with_card_details(db, payload, bhikku, acharya_record)
        return payload

    def _fetch_id_card_meta(self, db: Session, regn: str) -> Dict[str, Any]:
        result = db.execute(self._id_lookup_query, {"regn": regn}).mappings().first()
        return dict(result) if result else {}

    def _resolve_status_description(
        self, db: Session, status_code: Optional[str]
    ) -> Optional[str]:
        if not status_code:
            return None
        status = (
            db.query(StatusData)
            .filter(
                StatusData.st_statcd == status_code,
                StatusData.st_is_deleted.is_(False),
            )
            .first()
        )
        return status.st_descr if status else None

    def _resolve_parshawa_and_nikaya(
        self, db: Session, parshawa_code: Optional[str]
    ) -> tuple[Optional[str], Optional[str]]:
        if not parshawa_code:
            return (None, None)

        parshawa = (
            db.query(ParshawaData)
            .filter(
                ParshawaData.pr_prn == parshawa_code,
                ParshawaData.pr_is_deleted.is_(False),
            )
            .first()
        )
        if not parshawa:
            return (None, None)

        nikaya_name: Optional[str] = None
        if parshawa.pr_nikayacd:
            nikaya = (
                db.query(NikayaData)
                .filter(
                    NikayaData.nk_nkn == parshawa.pr_nikayacd,
                    NikayaData.nk_is_deleted.is_(False),
                )
                .first()
            )
            if nikaya:
                nikaya_name = nikaya.nk_nname

        return (parshawa.pr_pname, nikaya_name)

    def _resolve_vihara(
        self, db: Session, vihara_code: Optional[str]
    ) -> Optional[Dict[str, Any]]:
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
            "owner_regn": vihara.vh_ownercd,
        }

    @staticmethod
    def _build_address_string(*parts: Optional[str]) -> Optional[str]:
        meaningful = [part.strip() for part in parts if isinstance(part, str) and part.strip()]
        if not meaningful:
            return None
        return ", ".join(meaningful)

    def _enrich_with_card_details(
        self,
        db: Session,
        payload: BhikkuIDCardData,
        bhikku: Bhikku,
        acharya: Optional[Bhikku],
    ) -> None:
        extra = bhikku_id_repo.get_by_regn(db, bhikku.br_regn)
        if not extra:
            return

        if extra.bic_national_id:
            payload.national_id = extra.bic_national_id

        if extra.bic_left_thumbprint_url:
            payload.documents.left_thumbprint_url = extra.bic_left_thumbprint_url

        if extra.bic_applicant_image_url:
            payload.documents.applicant_image_url = extra.bic_applicant_image_url

        decls = payload.declarations

        if extra.bic_acharya_phone:
            decls.acharya_declaration.phone_number = extra.bic_acharya_phone
        elif not decls.acharya_declaration.phone_number and acharya:
            decls.acharya_declaration.phone_number = acharya.br_mobile

        if extra.bic_acharya_approved is not None:
            decls.acharya_declaration.approved = extra.bic_acharya_approved
        if extra.bic_acharya_date:
            decls.acharya_declaration.date = extra.bic_acharya_date

        if extra.bic_grama_niladari_phone:
            decls.grama_niladari_declaration.phone_number = extra.bic_grama_niladari_phone
        if extra.bic_grama_niladari_approved is not None:
            decls.grama_niladari_declaration.approved = extra.bic_grama_niladari_approved
        if extra.bic_grama_niladari_date:
            decls.grama_niladari_declaration.date = extra.bic_grama_niladari_date

        if extra.bic_devotional_secretariat_phone:
            decls.devotional_secretariat_declaration.phone_number = (
                extra.bic_devotional_secretariat_phone
            )
        if extra.bic_devotional_secretariat_approved is not None:
            decls.devotional_secretariat_declaration.approved = (
                extra.bic_devotional_secretariat_approved
            )
        if extra.bic_devotional_secretariat_date:
            decls.devotional_secretariat_declaration.date = (
                extra.bic_devotional_secretariat_date
            )

    def _get_bhikku(self, db: Session, regn: Optional[str]) -> Optional[Bhikku]:
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
    def _prefer_name(record: Optional[Bhikku]) -> Optional[str]:
        if not record:
            return None
        return record.br_mahananame or record.br_gihiname


bhikku_id_service = BhikkuIDService()

