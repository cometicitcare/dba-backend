# app/services/main_bhikku_service.py
from __future__ import annotations

from typing import Optional, Any

from sqlalchemy.orm import Session

from app.models.main_bhikku import MainBhikku
from app.models.nikaya import NikayaData
from app.models.parshawadata import ParshawaData
from app.repositories.main_bhikku_repo import main_bhikku_repo


def _serialize_bhikku(bhikku) -> Optional[dict[str, Any]]:
    if not bhikku:
        return None
    return {
        "regn": bhikku.br_regn,
        "gihiname": getattr(bhikku, "br_gihiname", None),
        "mahananame": getattr(bhikku, "br_mahanayaka_name", None) or getattr(bhikku, "br_mahananame", None),
        "address": getattr(bhikku, "br_fathrsaddrs", None),
        "current_status": getattr(bhikku, "br_currstat", None),
    }


class MainBhikkuService:

    # ------------------------------------------------------------------ #
    # SET PARSHAWA MAHANAYAKA                                             #
    # ------------------------------------------------------------------ #

    def set_parshawa_mahanayaka(
        self,
        db: Session,
        *,
        mb_nikaya_cd: str,
        mb_parshawa_cd: str,
        br_regn: str,
        mb_start_date=None,
        mb_remarks: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Assign a new Parshawa Mahanayaka.
        Deactivates any currently-active record for the same nikaya+parshawa
        before creating the new appointment.
        """
        # Validate nikaya
        nikaya = (
            db.query(NikayaData)
            .filter(NikayaData.nk_nkn == mb_nikaya_cd, NikayaData.nk_is_deleted.is_(False))
            .first()
        )
        if not nikaya:
            raise ValueError(f"Nikaya '{mb_nikaya_cd}' not found.")

        # Validate parshawa (must belong to the nikaya)
        parshawa = (
            db.query(ParshawaData)
            .filter(
                ParshawaData.pr_prn == mb_parshawa_cd,
                ParshawaData.pr_nikayacd == mb_nikaya_cd,
                ParshawaData.pr_is_deleted.is_(False),
            )
            .first()
        )
        if not parshawa:
            raise ValueError(
                f"Parshawa '{mb_parshawa_cd}' not found under nikaya '{mb_nikaya_cd}'."
            )

        # Validate bhikku exists (import lazily to avoid circular imports)
        from app.models.bhikku import Bhikku
        bhikku = (
            db.query(Bhikku)
            .filter(Bhikku.br_regn == br_regn, Bhikku.br_is_deleted.is_(False))
            .first()
        )
        if not bhikku:
            raise ValueError(f"Bhikku with registration '{br_regn}' not found.")

        # Deactivate existing active appointment
        main_bhikku_repo.deactivate_existing(
            db,
            nikaya_cd=mb_nikaya_cd,
            parshawa_cd=mb_parshawa_cd,
            mb_type="PARSHAWA_MAHANAYAKA",
            actor_id=actor_id,
        )

        # Create new appointment
        record = main_bhikku_repo.create(
            db,
            mb_type="PARSHAWA_MAHANAYAKA",
            nikaya_cd=mb_nikaya_cd,
            parshawa_cd=mb_parshawa_cd,
            bhikku_regn=br_regn,
            start_date=mb_start_date,
            remarks=mb_remarks,
            actor_id=actor_id,
        )

        # Also update denormalized pr_nayakahimi on parshawa table
        parshawa.pr_nayakahimi = br_regn
        db.commit()
        db.refresh(record)

        return {
            "record": record,
            "bhikku": _serialize_bhikku(bhikku),
            "nikaya": {"code": nikaya.nk_nkn, "name": nikaya.nk_nname},
            "parshawa": {"code": parshawa.pr_prn, "name": parshawa.pr_pname},
        }

    # ------------------------------------------------------------------ #
    # SET NIKAYA MAHANAYAKA                                               #
    # ------------------------------------------------------------------ #

    def set_nikaya_mahanayaka(
        self,
        db: Session,
        *,
        mb_nikaya_cd: str,
        br_regn: str,
        mb_start_date=None,
        mb_remarks: Optional[str] = None,
        actor_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Assign a new Nikaya Mahanayaka.
        Deactivates any currently-active record for the same nikaya
        before creating the new appointment.
        """
        nikaya = (
            db.query(NikayaData)
            .filter(NikayaData.nk_nkn == mb_nikaya_cd, NikayaData.nk_is_deleted.is_(False))
            .first()
        )
        if not nikaya:
            raise ValueError(f"Nikaya '{mb_nikaya_cd}' not found.")

        from app.models.bhikku import Bhikku
        bhikku = (
            db.query(Bhikku)
            .filter(Bhikku.br_regn == br_regn, Bhikku.br_is_deleted.is_(False))
            .first()
        )
        if not bhikku:
            raise ValueError(f"Bhikku with registration '{br_regn}' not found.")

        main_bhikku_repo.deactivate_existing(
            db,
            nikaya_cd=mb_nikaya_cd,
            parshawa_cd=None,
            mb_type="NIKAYA_MAHANAYAKA",
            actor_id=actor_id,
        )

        record = main_bhikku_repo.create(
            db,
            mb_type="NIKAYA_MAHANAYAKA",
            nikaya_cd=mb_nikaya_cd,
            parshawa_cd=None,
            bhikku_regn=br_regn,
            start_date=mb_start_date,
            remarks=mb_remarks,
            actor_id=actor_id,
        )

        # Also update denormalized nk_nahimicd on nikaya table
        nikaya.nk_nahimicd = br_regn
        db.commit()
        db.refresh(record)

        return {
            "record": record,
            "bhikku": _serialize_bhikku(bhikku),
            "nikaya": {"code": nikaya.nk_nkn, "name": nikaya.nk_nname},
            "parshawa": None,
        }


main_bhikku_service = MainBhikkuService()
