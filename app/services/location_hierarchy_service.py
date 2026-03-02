"""
Location Hierarchy Service
Provides location data with human-readable names and codes for cascading filters
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.province import Province
from app.models.district import District
from app.models.divisional_secretariat import DivisionalSecretariat
from app.models.gramasewaka import Gramasewaka
from app.models.sasanarakshaka import SasanarakshakaBalaMandalaya


class LocationHierarchyService:
    """Service for managing location hierarchy with cascading support"""
    
    @staticmethod
    def get_provinces(db: Session) -> List[Dict[str, str]]:
        """
        Get all provinces with human-readable names
        Returns: [{"code": "WP", "name": "Western Province"}, ...]
        """
        provinces = db.query(Province).filter(Province.pr_is_deleted == False).order_by(Province.pr_pcode).all()
        return [
            {
                "code": p.pr_pcode,
                "name": p.pr_pname or p.pr_pcode
            }
            for p in provinces
        ]
    
    @staticmethod
    def get_districts_by_province(db: Session, province_code: str) -> List[Dict[str, str]]:
        """
        Get districts for a specific province with names and codes
        Args: province_code (e.g., "WP")
        Returns: [{"code": "DC001", "name": "කොළඹ (Colombo)"}, ...]
        """
        districts = (
            db.query(District)
            .filter(
                District.dd_prcode == province_code,
                District.dd_is_deleted == False
            )
            .order_by(District.dd_dcode)
            .all()
        )
        return [
            {
                "code": d.dd_dcode,
                "name": d.dd_dname or d.dd_dcode  # e.g., "කොළඹ (Colombo)"
            }
            for d in districts
        ]
    
    @staticmethod
    def get_divisional_secretariats_by_district(db: Session, district_code: str) -> List[Dict[str, str]]:
        """
        Get divisional secretariats for a specific district
        Args: district_code (e.g., "DC001")
        Returns: [{"code": "DV0001", "name": "Colombo North", ...}, ...]
        """
        dvs = (
            db.query(DivisionalSecretariat)
            .filter(
                DivisionalSecretariat.dv_distrcd == district_code,
                DivisionalSecretariat.dv_is_deleted == False
            )
            .order_by(DivisionalSecretariat.dv_dvcode)
            .all()
        )
        return [
            {
                "code": dv.dv_dvcode,
                "name": dv.dv_dvname or dv.dv_dvcode
            }
            for dv in dvs
        ]
    
    @staticmethod
    def get_gn_divisions_by_divisional_secretariat(
        db: Session, 
        divisional_secretariat_code: str
    ) -> List[Dict[str, str]]:
        """
        Get GN divisions for a specific divisional secretariat
        Args: divisional_secretariat_code (e.g., "DV0001")
        Returns: [{"code": "GN001", "name": "Colombo North - GN 01"}, ...]
        """
        gns = (
            db.query(Gramasewaka)
            .filter(
                Gramasewaka.gn_dvcode == divisional_secretariat_code,
                Gramasewaka.gn_is_deleted == False
            )
            .order_by(Gramasewaka.gn_gnc)
            .all()
        )
        return [
            {
                "code": gn.gn_gnc,
                "name": gn.gn_gnname or gn.gn_gnc
            }
            for gn in gns
        ]
    
    @staticmethod
    def get_sasanarakshaka_bala_mandalas_by_divisional_secretariat(
        db: Session, 
        divisional_secretariat_code: str
    ) -> List[Dict[str, str]]:
        """
        Get Sasanarakshaka Bala Mandalas for a specific divisional secretariat
        Args: divisional_secretariat_code (e.g., "DV0001")
        Returns: [{"code": "SR001", "name": "Colombo North SSBM"}, ...]
        """
        sbms = (
            db.query(SasanarakshakaBalaMandalaya)
            .filter(
                SasanarakshakaBalaMandalaya.sr_dvcd == divisional_secretariat_code,
                SasanarakshakaBalaMandalaya.sr_is_deleted == False
            )
            .order_by(SasanarakshakaBalaMandalaya.sr_ssbmcode)
            .all()
        )
        return [
            {
                "code": sbm.sr_ssbmcode,
                "name": sbm.sr_ssbname or sbm.sr_ssbmcode
            }
            for sbm in sbms
        ]

    @staticmethod
    def get_sasanarakshaka_bala_mandalas_by_district(
        db: Session,
        district_code: str
    ) -> List[Dict[str, str]]:
        """
        Get all Sasanarakshaka Bala Mandalas in a district (across all its DVs)
        Args: district_code (e.g., "DC001")
        Returns: [{"code": "SR001", "name": "Colombo North SSBM"}, ...]
        """
        sbms = (
            db.query(SasanarakshakaBalaMandalaya)
            .join(
                DivisionalSecretariat,
                SasanarakshakaBalaMandalaya.sr_dvcd == DivisionalSecretariat.dv_dvcode
            )
            .filter(
                DivisionalSecretariat.dv_distrcd == district_code,
                DivisionalSecretariat.dv_is_deleted == False,
                SasanarakshakaBalaMandalaya.sr_is_deleted == False
            )
            .order_by(SasanarakshakaBalaMandalaya.sr_ssbmcode)
            .all()
        )
        return [
            {
                "code": sbm.sr_ssbmcode,
                "name": sbm.sr_ssbname or sbm.sr_ssbmcode
            }
            for sbm in sbms
        ]
    
    @staticmethod
    def get_full_hierarchy(db: Session) -> Dict[str, Any]:
        """
        Get complete location hierarchy for frontend cascading filters
        Returns: {
            "provinces": [...],
            "districtsByProvince": {
                "WP": [...],
                "CP": [...]
            },
            "dvsByDistrict": {
                "DC001": [...],
                "DC003": [...]
            },
            ...
        }
        """
        provinces = LocationHierarchyService.get_provinces(db)
        
        # Build district mapping for each province
        districts_by_province = {}
        all_districts = db.query(District).filter(District.dd_is_deleted == False).all()
        
        for district in all_districts:
            pcode = district.dd_prcode
            if pcode not in districts_by_province:
                districts_by_province[pcode] = []
            districts_by_province[pcode].append({
                "code": district.dd_dcode,
                "name": district.dd_dname or district.dd_dcode
            })
        
        # Build DV mapping for each district
        dvs_by_district = {}
        all_dvs = db.query(DivisionalSecretariat).filter(DivisionalSecretariat.dv_is_deleted == False).all()
        
        for dv in all_dvs:
            dcode = dv.dv_distrcd
            if dcode not in dvs_by_district:
                dvs_by_district[dcode] = []
            dvs_by_district[dcode].append({
                "code": dv.dv_dvcode,
                "name": dv.dv_dvname or dv.dv_dvcode
            })
        
        # Build GN mapping for each DV
        gns_by_dv = {}
        all_gns = db.query(Gramasewaka).filter(Gramasewaka.gn_is_deleted == False).all()
        
        for gn in all_gns:
            dvcode = gn.gn_dvcode
            if dvcode not in gns_by_dv:
                gns_by_dv[dvcode] = []
            gns_by_dv[dvcode].append({
                "code": gn.gn_gnc,
                "name": gn.gn_gnname or gn.gn_gnc
            })
        
        # Build SSBM mapping for each DV
        sbms_by_dv = {}
        all_sbms = db.query(SasanarakshakaBalaMandalaya).filter(SasanarakshakaBalaMandalaya.sr_is_deleted == False).all()
        
        for sbm in all_sbms:
            dvcode = sbm.sr_dvcd
            if dvcode not in sbms_by_dv:
                sbms_by_dv[dvcode] = []
            sbms_by_dv[dvcode].append({
                "code": sbm.sr_ssbmcode,
                "name": sbm.sr_ssbname or sbm.sr_ssbmcode
            })
        
        return {
            "provinces": provinces,
            "districtsByProvince": districts_by_province,
            "dvsByDistrict": dvs_by_district,
            "gnsByDv": gns_by_dv,
            "sbmsByDv": sbms_by_dv
        }
    
    @staticmethod
    def convert_name_to_code(
        db: Session,
        location_type: str,
        name: str,
        context_code: Optional[str] = None
    ) -> Optional[str]:
        """
        Convert human-readable location name to code
        Args:
            location_type: "province", "district", "dv", "gn", "sbm"
            name: Human-readable name
            context_code: Optional code of parent level (e.g., province code for district)
        Returns: Code or None if not found
        """
        if location_type == "province":
            result = db.query(Province).filter(
                Province.pr_pname.ilike(f"%{name}%"),
                Province.pr_is_deleted == False
            ).first()
            return result.pr_pcode if result else None
        
        elif location_type == "district":
            query = db.query(District).filter(
                District.dd_dname.ilike(f"%{name}%"),
                District.dd_is_deleted == False
            )
            if context_code:  # Filter by province if provided
                query = query.filter(District.dd_prcode == context_code)
            result = query.first()
            return result.dd_dcode if result else None
        
        elif location_type == "dv":
            query = db.query(DivisionalSecretariat).filter(
                DivisionalSecretariat.dv_dvname.ilike(f"%{name}%"),
                DivisionalSecretariat.dv_is_deleted == False
            )
            if context_code:  # Filter by district if provided
                query = query.filter(DivisionalSecretariat.dv_dcode == context_code)
            result = query.first()
            return result.dv_dvcode if result else None
        
        elif location_type == "gn":
            query = db.query(Gramasewaka).filter(
                Gramasewaka.gn_gnname.ilike(f"%{name}%"),
                Gramasewaka.gn_is_deleted == False
            )
            if context_code:  # Filter by DV if provided
                query = query.filter(Gramasewaka.gn_dvcode == context_code)
            result = query.first()
            return result.gn_gnc if result else None
        
        elif location_type == "sbm":
            query = db.query(SasanarakshakaBalaMandalaya).filter(
                SasanarakshakaBalaMandalaya.sr_ssbname.ilike(f"%{name}%"),
                SasanarakshakaBalaMandalaya.sr_is_deleted == False
            )
            if context_code:  # Filter by DV if provided
                query = query.filter(SasanarakshakaBalaMandalaya.sr_dvcd == context_code)
            result = query.first()
            return result.sr_ssbmcode if result else None
        
        return None
