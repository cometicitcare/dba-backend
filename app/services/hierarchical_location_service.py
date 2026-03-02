"""
Hierarchical Location Service
Provides cascading location data based on parent selections
Province → District → Divisional Secretariat → GN Division & Sasanarakshaka Bala Mandala
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import distinct

from app.models.province import Province
from app.models.district import District
from app.models.divisional_secretariat import DivisionalSecretariat
from app.models.grama_niladhari import GramaNiladhari
from app.models.sasanarakshaka_bm import SasanarakshakaBM


class HierarchicalLocationService:
    """Service for handling hierarchical location filtering"""

    def get_all_provinces(self, db: Session) -> List[Dict[str, str]]:
        """Get all provinces"""
        provinces = db.query(Province).filter(
            Province.pr_is_deleted.is_(False)
        ).order_by(Province.pr_prcode).all()
        
        return [
            {
                "code": p.pr_prcode,
                "name": p.pr_prname,
                "sinhala_name": p.pr_prname_si or ""
            }
            for p in provinces
        ]

    def get_districts_by_province(
        self, 
        db: Session, 
        province_code: str
    ) -> List[Dict[str, str]]:
        """Get districts in a specific province"""
        districts = db.query(District).filter(
            District.dd_prcode == province_code,
            District.dd_is_deleted.is_(False)
        ).order_by(District.dd_dcode).all()
        
        return [
            {
                "code": d.dd_dcode,
                "name": d.dd_dname,
                "province": d.dd_prcode
            }
            for d in districts
        ]

    def get_divisional_secretariats_by_district(
        self, 
        db: Session, 
        district_code: str
    ) -> List[Dict[str, str]]:
        """Get divisional secretariats in a specific district"""
        dvsecs = db.query(DivisionalSecretariat).filter(
            DivisionalSecretariat.dv_dcode == district_code,
            DivisionalSecretariat.dv_is_deleted.is_(False)
        ).order_by(DivisionalSecretariat.dv_dvcode).all()
        
        return [
            {
                "code": dv.dv_dvcode,
                "name": dv.dv_dvname,
                "district": dv.dv_dcode
            }
            for dv in dvsecs
        ]

    def get_gn_divisions_by_divisional_secretariat(
        self, 
        db: Session, 
        divisional_secretariat_code: str
    ) -> List[Dict[str, str]]:
        """Get GN divisions under a specific divisional secretariat"""
        # Note: GN division table might use different column names
        # Adjust based on actual schema
        gn_divs = db.query(GramaNiladhari).filter(
            GramaNiladhari.gn_dv_code == divisional_secretariat_code,
            GramaNiladhari.gn_is_deleted.is_(False)
        ).order_by(GramaNiladhari.gn_gndiv_code).all()
        
        return [
            {
                "code": gn.gn_gndiv_code,
                "name": gn.gn_gndiv_name,
                "divisional_secretariat": gn.gn_dv_code
            }
            for gn in gn_divs
        ]

    def get_ssbm_by_divisional_secretariat(
        self, 
        db: Session, 
        divisional_secretariat_code: str
    ) -> List[Dict[str, str]]:
        """
        Get Sasanarakshaka Bala Mandala (SSBM) under a specific divisional secretariat
        SSBM has relationship to divisional secretariat
        """
        ssbms = db.query(SasanarakshakaBM).filter(
            SasanarakshakaBM.sr_dv_code == divisional_secretariat_code,
            SasanarakshakaBM.sr_is_deleted.is_(False)
        ).order_by(SasanarakshakaBM.sr_ssbmcode).all()
        
        return [
            {
                "code": ssbm.sr_ssbmcode,
                "name": ssbm.sr_ssbmname,
                "divisional_secretariat": ssbm.sr_dv_code
            }
            for ssbm in ssbms
        ]

    def get_complete_hierarchy(
        self, 
        db: Session, 
        province_code: Optional[str] = None,
        district_code: Optional[str] = None,
        divisional_secretariat_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get complete location hierarchy based on selections
        Smart cascade: if province selected, return only its districts
                       if district selected, return only its divisional secretariats
                       if divisional secretariat selected, return GN + SSBM
        """
        result = {
            "provinces": [],
            "districts": [],
            "divisional_secretariats": [],
            "gn_divisions": [],
            "ssbm": []
        }

        # Always include provinces
        result["provinces"] = self.get_all_provinces(db)

        # If province selected, get its districts
        if province_code:
            result["districts"] = self.get_districts_by_province(db, province_code)
        else:
            # Get all districts if no province filter
            all_districts = db.query(District).filter(
                District.dd_is_deleted.is_(False)
            ).all()
            result["districts"] = [
                {
                    "code": d.dd_dcode,
                    "name": d.dd_dname,
                    "province": d.dd_prcode
                }
                for d in all_districts
            ]

        # If district selected, get its divisional secretariats
        if district_code:
            result["divisional_secretariats"] = (
                self.get_divisional_secretariats_by_district(db, district_code)
            )
        elif province_code:
            # Get all divisional secretariats in the province
            dvsecs = db.query(DivisionalSecretariat).join(
                District, 
                DivisionalSecretariat.dv_dcode == District.dd_dcode
            ).filter(
                District.dd_prcode == province_code,
                DivisionalSecretariat.dv_is_deleted.is_(False),
                District.dd_is_deleted.is_(False)
            ).all()
            result["divisional_secretariats"] = [
                {
                    "code": dv.dv_dvcode,
                    "name": dv.dv_dvname,
                    "district": dv.dv_dcode
                }
                for dv in dvsecs
            ]

        # If divisional secretariat selected, get GN divisions and SSBM
        if divisional_secretariat_code:
            result["gn_divisions"] = (
                self.get_gn_divisions_by_divisional_secretariat(
                    db, divisional_secretariat_code
                )
            )
            result["ssbm"] = (
                self.get_ssbm_by_divisional_secretariat(
                    db, divisional_secretariat_code
                )
            )

        return result
