from __future__ import annotations

from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.district import District
from app.models.divisional_secretariat import DivisionalSecretariat
from app.models.province import Province
from app.schemas.location import (
    DistrictNode,
    DivisionalSecretariatNode,
    ProvinceNode,
)


class LocationService:
    """Helpers to build nested province → district → divisional secretariat data."""

    def get_location_hierarchy(self, db: Session) -> List[ProvinceNode]:
        provinces = (
            db.query(Province)
            .filter(Province.cp_is_deleted.is_(False))
            .order_by(Province.cp_name, Province.cp_code)
            .all()
        )

        districts = (
            db.query(District)
            .filter(District.dd_is_deleted.is_(False))
            .order_by(District.dd_prcode, District.dd_dname)
            .all()
        )

        divisional_secretariats = (
            db.query(DivisionalSecretariat)
            .filter(DivisionalSecretariat.dv_is_deleted.is_(False))
            .order_by(DivisionalSecretariat.dv_distrcd, DivisionalSecretariat.dv_dvname)
            .all()
        )

        province_map: Dict[str, ProvinceNode] = {}
        for province in provinces:
            province_map[province.cp_code] = ProvinceNode(
                cp_id=province.cp_id,
                cp_code=province.cp_code,
                cp_name=province.cp_name,
                districts=[],
            )

        district_map: Dict[str, DistrictNode] = {}
        for district in districts:
            province_node = province_map.get(district.dd_prcode)
            if not province_node:
                continue

            district_node = DistrictNode(
                dd_id=district.dd_id,
                dd_dcode=district.dd_dcode,
                dd_dname=district.dd_dname,
                dd_prcode=district.dd_prcode,
                divisional_secretariats=[],
            )

            province_node.districts.append(district_node)
            district_map[district.dd_dcode] = district_node

        for division in divisional_secretariats:
            district_node = district_map.get(division.dv_distrcd)
            if not district_node:
                continue

            district_node.divisional_secretariats.append(
                DivisionalSecretariatNode(
                    dv_id=division.dv_id,
                    dv_dvcode=division.dv_dvcode,
                    dv_distrcd=division.dv_distrcd,
                    dv_dvname=division.dv_dvname,
                )
            )

        return list(province_map.values())


location_service = LocationService()
