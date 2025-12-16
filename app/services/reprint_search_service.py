# app/services/reprint_search_service.py
"""
Service for unified reprint search across all entity types.
Searches: Bhikku, Silmatha, High Bhikku, Direct High Bhikku, Vihara, Arama, Devala
"""
from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.models.bhikku import Bhikku
from app.models.silmatha_regist import SilmathaRegist
from app.models.bhikku_high import BhikkuHighRegist
from app.models.direct_bhikku_high import DirectBhikkuHigh
from app.models.vihara import ViharaData
from app.models.arama import AramaData
from app.models.devala import DevalaData
from app.models.status import StatusData
from app.models.bhikku_category import BhikkuCategory
from app.schemas.reprint_search import ReprintSearchResultItem, QRStyleDetailItem


class ReprintSearchService:
    """Service for unified reprint search operations"""
    
    def search_all_entities(
        self,
        db: Session,
        registration_number: Optional[str] = None,
        name: Optional[str] = None,
        birth_date: Optional[date] = None,
        entity_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[ReprintSearchResultItem], int]:
        """
        Search across all entity types with optional filters.
        
        Returns:
            Tuple of (results, total_count)
        """
        results = []
        
        # If entity type is specified, search only that type
        if entity_type:
            if entity_type == "bhikku":
                results, total = self._search_bhikku(db, registration_number, name, birth_date, skip, limit)
            elif entity_type == "silmatha":
                results, total = self._search_silmatha(db, registration_number, name, birth_date, skip, limit)
            elif entity_type == "high_bhikku":
                results, total = self._search_high_bhikku(db, registration_number, name, birth_date, skip, limit)
            elif entity_type == "direct_high_bhikku":
                results, total = self._search_direct_high_bhikku(db, registration_number, name, birth_date, skip, limit)
            elif entity_type == "vihara":
                results, total = self._search_vihara(db, registration_number, name, birth_date, skip, limit)
            elif entity_type == "arama":
                results, total = self._search_arama(db, registration_number, name, birth_date, skip, limit)
            elif entity_type == "devala":
                results, total = self._search_devala(db, registration_number, name, birth_date, skip, limit)
            else:
                results, total = [], 0
        else:
            # Search all types and combine results
            all_results = []
            
            bhikku_results, _ = self._search_bhikku(db, registration_number, name, birth_date, 0, limit * 2)
            all_results.extend(bhikku_results)
            
            silmatha_results, _ = self._search_silmatha(db, registration_number, name, birth_date, 0, limit * 2)
            all_results.extend(silmatha_results)
            
            high_bhikku_results, _ = self._search_high_bhikku(db, registration_number, name, birth_date, 0, limit * 2)
            all_results.extend(high_bhikku_results)
            
            direct_high_results, _ = self._search_direct_high_bhikku(db, registration_number, name, birth_date, 0, limit * 2)
            all_results.extend(direct_high_results)
            
            vihara_results, _ = self._search_vihara(db, registration_number, name, birth_date, 0, limit * 2)
            all_results.extend(vihara_results)
            
            arama_results, _ = self._search_arama(db, registration_number, name, birth_date, 0, limit * 2)
            all_results.extend(arama_results)
            
            devala_results, _ = self._search_devala(db, registration_number, name, birth_date, 0, limit * 2)
            all_results.extend(devala_results)
            
            total = len(all_results)
            results = all_results[skip:skip + limit]
        
        return results, total
    
    def _search_bhikku(
        self,
        db: Session,
        registration_number: Optional[str],
        name: Optional[str],
        birth_date: Optional[date],
        skip: int,
        limit: int
    ) -> Tuple[List[ReprintSearchResultItem], int]:
        """Search Bhikku records"""
        query = db.query(Bhikku).filter(
            Bhikku.br_is_deleted == False,
            Bhikku.br_workflow_status == 'COMPLETED'
        )
        
        if registration_number:
            query = query.filter(Bhikku.br_regn.ilike(f"%{registration_number}%"))
        if name:
            query = query.filter(
                or_(
                    Bhikku.br_mahananame.ilike(f"%{name}%"),
                    Bhikku.br_gihiname.ilike(f"%{name}%")
                )
            )
        if birth_date:
            query = query.filter(Bhikku.br_dofb == birth_date)
        
        total = query.count()
        entities = query.offset(skip).limit(limit).all()
        
        results = []
        for entity in entities:
            # Get temple info
            temple_name = None
            temple_address = None
            if entity.br_livtemple:
                temple = db.query(ViharaData).filter(ViharaData.vh_trn == entity.br_livtemple).first()
                if temple:
                    temple_name = temple.vh_vname
                    temple_address = temple.vh_addrs
            
            # Get status
            status_text = entity.br_currstat
            if entity.br_currstat:
                status = db.query(StatusData).filter(StatusData.st_statcd == entity.br_currstat).first()
                if status:
                    status_text = status.st_descr
            
            results.append(ReprintSearchResultItem(
                entity_type="bhikku",
                registration_number=entity.br_regn,
                form_id=entity.br_form_id,
                ordained_name=entity.br_mahananame,
                birth_name=entity.br_gihiname,
                date_of_birth=entity.br_dofb,
                birth_place=entity.br_birthpls,
                mobile=entity.br_mobile,
                email=entity.br_email,
                temple_name=temple_name,
                temple_address=temple_address,
                current_status=status_text,
                workflow_status=entity.br_workflow_status,
                ordination_date=entity.br_mahanadate,
                request_date=entity.br_reqstdate
            ))
        
        return results, total
    
    def _search_silmatha(
        self,
        db: Session,
        registration_number: Optional[str],
        name: Optional[str],
        birth_date: Optional[date],
        skip: int,
        limit: int
    ) -> Tuple[List[ReprintSearchResultItem], int]:
        """Search Silmatha records"""
        query = db.query(SilmathaRegist).filter(
            SilmathaRegist.sil_is_deleted == False,
            SilmathaRegist.sil_workflow_status == 'COMPLETED'
        )
        
        if registration_number:
            query = query.filter(SilmathaRegist.sil_regn.ilike(f"%{registration_number}%"))
        if name:
            query = query.filter(
                or_(
                    SilmathaRegist.sil_mahananame.ilike(f"%{name}%"),
                    SilmathaRegist.sil_gihiname.ilike(f"%{name}%")
                )
            )
        if birth_date:
            query = query.filter(SilmathaRegist.sil_dofb == birth_date)
        
        total = query.count()
        entities = query.offset(skip).limit(limit).all()
        
        results = []
        for entity in entities:
            # Get arama info
            temple_name = None
            temple_address = None
            if entity.sil_mahanatemple:
                temple = db.query(AramaData).filter(AramaData.ar_trn == entity.sil_mahanatemple).first()
                if temple:
                    temple_name = temple.ar_vname
                    temple_address = temple.ar_addrs
            
            # Get status
            status_text = entity.sil_currstat
            if entity.sil_currstat:
                status = db.query(StatusData).filter(StatusData.st_statcd == entity.sil_currstat).first()
                if status:
                    status_text = status.st_descr
            
            results.append(ReprintSearchResultItem(
                entity_type="silmatha",
                registration_number=entity.sil_regn,
                form_id=entity.sil_form_id,
                ordained_name=entity.sil_mahananame,
                birth_name=entity.sil_gihiname,
                date_of_birth=entity.sil_dofb,
                birth_place=entity.sil_birthpls,
                mobile=entity.sil_mobile,
                email=entity.sil_email,
                temple_name=temple_name,
                temple_address=temple_address,
                current_status=status_text,
                workflow_status=entity.sil_workflow_status,
                ordination_date=entity.sil_mahanadate,
                request_date=entity.sil_reqstdate
            ))
        
        return results, total
    
    def _search_high_bhikku(
        self,
        db: Session,
        registration_number: Optional[str],
        name: Optional[str],
        birth_date: Optional[date],
        skip: int,
        limit: int
    ) -> Tuple[List[ReprintSearchResultItem], int]:
        """Search High Bhikku records"""
        from sqlalchemy.orm import lazyload
        
        query = db.query(BhikkuHighRegist).options(lazyload('*')).filter(
            BhikkuHighRegist.bhr_is_deleted == False,
            BhikkuHighRegist.bhr_workflow_status == 'COMPLETED'
        )
        
        if registration_number:
            query = query.filter(BhikkuHighRegist.bhr_regn.ilike(f"%{registration_number}%"))
        if name:
            # For high bhikku, search in assumed_name only if not null
            query = query.filter(
                and_(
                    BhikkuHighRegist.bhr_assumed_name.isnot(None),
                    BhikkuHighRegist.bhr_assumed_name.ilike(f"%{name}%")
                )
            )
        if birth_date:
            # High bhikku gets birth date from related bhikku record
            query = query.join(Bhikku, BhikkuHighRegist.bhr_candidate_regn == Bhikku.br_regn).filter(
                Bhikku.br_dofb == birth_date
            )
        
        total = query.count()
        entities = query.offset(skip).limit(limit).all()
        
        results = []
        for entity in entities:
            # Get bhikku info for names
            ordained_name = entity.bhr_assumed_name
            birth_name = None
            dob = None
            birth_place = None
            mobile = None
            email = None
            
            if entity.bhr_candidate_regn:
                bhikku = db.query(Bhikku).filter(Bhikku.br_regn == entity.bhr_candidate_regn).first()
                if bhikku:
                    birth_name = bhikku.br_gihiname
                    dob = bhikku.br_dofb
                    birth_place = bhikku.br_birthpls
                    mobile = bhikku.br_mobile
                    email = bhikku.br_email
            
            # Get temple info
            temple_name = None
            temple_address = None
            if entity.bhr_livtemple:
                temple = db.query(ViharaData).filter(ViharaData.vh_trn == entity.bhr_livtemple).first()
                if temple:
                    temple_name = temple.vh_vname
                    temple_address = temple.vh_addrs
            
            # Get status
            status_text = entity.bhr_currstat
            if entity.bhr_currstat:
                status = db.query(StatusData).filter(StatusData.st_statcd == entity.bhr_currstat).first()
                if status:
                    status_text = status.st_descr
            
            results.append(ReprintSearchResultItem(
                entity_type="high_bhikku",
                registration_number=entity.bhr_regn,
                form_id=entity.bhr_form_id,
                ordained_name=ordained_name,
                birth_name=birth_name,
                date_of_birth=dob,
                birth_place=birth_place,
                mobile=mobile,
                email=email,
                temple_name=temple_name,
                temple_address=temple_address,
                current_status=status_text,
                workflow_status=entity.bhr_workflow_status,
                ordination_date=entity.bhr_higher_ordination_date,
                request_date=entity.bhr_reqstdate
            ))
        
        return results, total
    
    def _search_direct_high_bhikku(
        self,
        db: Session,
        registration_number: Optional[str],
        name: Optional[str],
        birth_date: Optional[date],
        skip: int,
        limit: int
    ) -> Tuple[List[ReprintSearchResultItem], int]:
        """Search Direct High Bhikku records"""
        from sqlalchemy.orm import lazyload
        
        query = db.query(DirectBhikkuHigh).options(lazyload('*')).filter(
            DirectBhikkuHigh.dbh_is_deleted == False,
            DirectBhikkuHigh.dbh_workflow_status == 'COMPLETED'
        )
        
        if registration_number:
            query = query.filter(DirectBhikkuHigh.dbh_regn.ilike(f"%{registration_number}%"))
        if name:
            query = query.filter(
                or_(
                    DirectBhikkuHigh.dbh_mahananame.ilike(f"%{name}%"),
                    DirectBhikkuHigh.dbh_assumed_name.ilike(f"%{name}%"),
                    DirectBhikkuHigh.dbh_gihiname.ilike(f"%{name}%")
                )
            )
        if birth_date:
            query = query.filter(DirectBhikkuHigh.dbh_dofb == birth_date)
        
        total = query.count()
        entities = query.offset(skip).limit(limit).all()
        
        results = []
        for entity in entities:
            # Get temple info
            temple_name = None
            temple_address = None
            if entity.dbh_livtemple:
                temple = db.query(ViharaData).filter(ViharaData.vh_trn == entity.dbh_livtemple).first()
                if temple:
                    temple_name = temple.vh_vname
                    temple_address = temple.vh_addrs
            
            # Get status
            status_text = entity.dbh_currstat
            if entity.dbh_currstat:
                status = db.query(StatusData).filter(StatusData.st_statcd == entity.dbh_currstat).first()
                if status:
                    status_text = status.st_descr
            
            # Use assumed name if available, otherwise mahana name
            ordained_name = entity.dbh_assumed_name or entity.dbh_mahananame
            
            results.append(ReprintSearchResultItem(
                entity_type="direct_high_bhikku",
                registration_number=entity.dbh_regn,
                form_id=None,  # DirectBhikkuHigh doesn't have form_id field
                ordained_name=ordained_name,
                birth_name=entity.dbh_gihiname,
                date_of_birth=entity.dbh_dofb,
                birth_place=entity.dbh_birthpls,
                mobile=entity.dbh_mobile,
                email=entity.dbh_email,
                temple_name=temple_name,
                temple_address=temple_address,
                current_status=status_text,
                workflow_status=entity.dbh_workflow_status,
                ordination_date=entity.dbh_higher_ordination_date,
                request_date=entity.dbh_reqstdate
            ))
        
        return results, total
    
    def _search_vihara(
        self,
        db: Session,
        registration_number: Optional[str],
        name: Optional[str],
        birth_date: Optional[date],
        skip: int,
        limit: int
    ) -> Tuple[List[ReprintSearchResultItem], int]:
        """Search Vihara records"""
        query = db.query(ViharaData).filter(
            ViharaData.vh_is_deleted == False,
            ViharaData.vh_workflow_status == 'COMPLETED'
        )
        
        if registration_number:
            query = query.filter(ViharaData.vh_trn.ilike(f"%{registration_number}%"))
        if name:
            query = query.filter(ViharaData.vh_vname.ilike(f"%{name}%"))
        # birth_date filter doesn't apply to vihara
        
        total = query.count()
        entities = query.offset(skip).limit(limit).all()
        
        results = []
        for entity in entities:
            results.append(ReprintSearchResultItem(
                entity_type="vihara",
                registration_number=entity.vh_trn,
                form_id=entity.vh_form_id,
                ordained_name=entity.vh_vname,
                birth_name=None,
                date_of_birth=None,
                birth_place=None,
                mobile=entity.vh_mobile,
                email=entity.vh_email,
                temple_name=entity.vh_vname,
                temple_address=entity.vh_addrs,
                current_status=None,
                workflow_status=entity.vh_workflow_status,
                ordination_date=entity.vh_bgndate,  # Begin date
                request_date=None
            ))
        
        return results, total
    
    def _search_arama(
        self,
        db: Session,
        registration_number: Optional[str],
        name: Optional[str],
        birth_date: Optional[date],
        skip: int,
        limit: int
    ) -> Tuple[List[ReprintSearchResultItem], int]:
        """Search Arama records"""
        query = db.query(AramaData).filter(
            AramaData.ar_is_deleted == False,
            AramaData.ar_workflow_status == 'COMPLETED'
        )
        
        if registration_number:
            query = query.filter(AramaData.ar_trn.ilike(f"%{registration_number}%"))
        if name:
            query = query.filter(AramaData.ar_vname.ilike(f"%{name}%"))
        # birth_date filter doesn't apply to arama
        
        total = query.count()
        entities = query.offset(skip).limit(limit).all()
        
        results = []
        for entity in entities:
            results.append(ReprintSearchResultItem(
                entity_type="arama",
                registration_number=entity.ar_trn,
                form_id=entity.ar_form_id,
                ordained_name=entity.ar_vname,
                birth_name=None,
                date_of_birth=None,
                birth_place=None,
                mobile=entity.ar_mobile,
                email=entity.ar_email,
                temple_name=entity.ar_vname,
                temple_address=entity.ar_addrs,
                current_status=None,
                workflow_status=entity.ar_workflow_status,
                ordination_date=entity.ar_bgndate,  # Begin date
                request_date=None
            ))
        
        return results, total
    
    def _search_devala(
        self,
        db: Session,
        registration_number: Optional[str],
        name: Optional[str],
        birth_date: Optional[date],
        skip: int,
        limit: int
    ) -> Tuple[List[ReprintSearchResultItem], int]:
        """Search Devala records"""
        from sqlalchemy import func as sqlfunc
        
        # Build count query separately to avoid column issues
        count_query = db.query(sqlfunc.count(DevalaData.dv_id)).filter(
            DevalaData.dv_is_deleted == False,
            DevalaData.dv_workflow_status == 'COMPLETED'
        )
        
        if registration_number:
            count_query = count_query.filter(DevalaData.dv_trn.ilike(f"%{registration_number}%"))
        if name:
            count_query = count_query.filter(DevalaData.dv_vname.ilike(f"%{name}%"))
        
        total = count_query.scalar()
        
        # Query with specific columns only
        query = db.query(
            DevalaData.dv_trn,
            DevalaData.dv_vname,
            DevalaData.dv_addrs,
            DevalaData.dv_mobile,
            DevalaData.dv_email,
            DevalaData.dv_form_id,
            DevalaData.dv_workflow_status
        ).filter(
            DevalaData.dv_is_deleted == False,
            DevalaData.dv_workflow_status == 'COMPLETED'
        )
        
        if registration_number:
            query = query.filter(DevalaData.dv_trn.ilike(f"%{registration_number}%"))
        if name:
            query = query.filter(DevalaData.dv_vname.ilike(f"%{name}%"))
        
        entities = query.offset(skip).limit(limit).all()
        
        results = []
        for row in entities:
            # row is a tuple: (dv_trn, dv_vname, dv_addrs, dv_mobile, dv_email, dv_form_id, dv_workflow_status)
            results.append(ReprintSearchResultItem(
                entity_type="devala",
                registration_number=row[0],  # dv_trn
                form_id=row[5],  # dv_form_id
                ordained_name=row[1],  # dv_vname
                birth_name=None,
                date_of_birth=None,
                birth_place=None,
                mobile=row[3],  # dv_mobile
                email=row[4],  # dv_email
                temple_name=row[1],  # dv_vname
                temple_address=row[2],  # dv_addrs
                current_status=None,
                workflow_status=row[6],  # dv_workflow_status
                ordination_date=None,
                request_date=None
            ))
        
        return results, total
    
    def get_entity_detail(
        self,
        db: Session,
        entity_type: str,
        registration_number: str
    ) -> Optional[List[QRStyleDetailItem]]:
        """
        Get detailed information for a single entity in QR style format.
        Similar to QR search but for reprint purposes.
        """
        if entity_type == "bhikku":
            return self._get_bhikku_detail(db, registration_number)
        elif entity_type == "silmatha":
            return self._get_silmatha_detail(db, registration_number)
        elif entity_type == "high_bhikku":
            return self._get_high_bhikku_detail(db, registration_number)
        elif entity_type == "direct_high_bhikku":
            return self._get_direct_high_bhikku_detail(db, registration_number)
        elif entity_type == "vihara":
            return self._get_vihara_detail(db, registration_number)
        elif entity_type == "arama":
            return self._get_arama_detail(db, registration_number)
        elif entity_type == "devala":
            return self._get_devala_detail(db, registration_number)
        
        return None
    
    def _get_bhikku_detail(self, db: Session, regn: str) -> Optional[List[QRStyleDetailItem]]:
        """Get detailed Bhikku information"""
        entity = db.query(Bhikku).filter(Bhikku.br_regn == regn, Bhikku.br_is_deleted == False).first()
        if not entity:
            return None
        
        # Get temple info
        temple_info = None
        if entity.br_livtemple:
            temple = db.query(ViharaData).filter(ViharaData.vh_trn == entity.br_livtemple).first()
            if temple:
                temple_info = f"{temple.vh_vname}, {temple.vh_addrs}" if temple.vh_addrs else temple.vh_vname
        
        # Get status
        status_text = entity.br_currstat
        if entity.br_currstat:
            status = db.query(StatusData).filter(StatusData.st_statcd == entity.br_currstat).first()
            if status:
                status_text = status.st_descr
        
        # Get category
        category_text = entity.br_cat
        if entity.br_cat:
            category = db.query(BhikkuCategory).filter(BhikkuCategory.cc_code == entity.br_cat).first()
            if category:
                category_text = category.cc_catogry
        
        return [
            QRStyleDetailItem(titel="Entity Type", text="Bhikku"),
            QRStyleDetailItem(titel="Registration Number", text=entity.br_regn),
            QRStyleDetailItem(titel="Form ID", text=entity.br_form_id),
            QRStyleDetailItem(titel="Ordained Name", text=entity.br_mahananame),
            QRStyleDetailItem(titel="Birth Name", text=entity.br_gihiname),
            QRStyleDetailItem(titel="Date of Birth", text=str(entity.br_dofb) if entity.br_dofb else None),
            QRStyleDetailItem(titel="Birth Place", text=entity.br_birthpls),
            QRStyleDetailItem(titel="Contact Number", text=entity.br_mobile),
            QRStyleDetailItem(titel="Email", text=entity.br_email),
            QRStyleDetailItem(titel="Live Location", text=temple_info),
            QRStyleDetailItem(titel="Current Status", text=status_text),
            QRStyleDetailItem(titel="Category", text=category_text),
            QRStyleDetailItem(titel="Ordination Date", text=str(entity.br_mahanadate) if entity.br_mahanadate else None),
            QRStyleDetailItem(titel="Workflow Status", text=entity.br_workflow_status),
        ]
    
    def _get_silmatha_detail(self, db: Session, regn: str) -> Optional[List[QRStyleDetailItem]]:
        """Get detailed Silmatha information"""
        entity = db.query(SilmathaRegist).filter(SilmathaRegist.sil_regn == regn, SilmathaRegist.sil_is_deleted == False).first()
        if not entity:
            return None
        
        # Get arama info
        temple_info = None
        if entity.sil_mahanatemple:
            temple = db.query(AramaData).filter(AramaData.ar_trn == entity.sil_mahanatemple).first()
            if temple:
                temple_info = f"{temple.ar_vname}, {temple.ar_addrs}" if temple.ar_addrs else temple.ar_vname
        
        # Get status
        status_text = entity.sil_currstat
        if entity.sil_currstat:
            status = db.query(StatusData).filter(StatusData.st_statcd == entity.sil_currstat).first()
            if status:
                status_text = status.st_descr
        
        # Get category
        category_text = entity.sil_cat
        if entity.sil_cat:
            category = db.query(BhikkuCategory).filter(BhikkuCategory.cc_code == entity.sil_cat).first()
            if category:
                category_text = category.cc_catogry
        
        return [
            QRStyleDetailItem(titel="Entity Type", text="Silmatha"),
            QRStyleDetailItem(titel="Registration Number", text=entity.sil_regn),
            QRStyleDetailItem(titel="Form ID", text=entity.sil_form_id),
            QRStyleDetailItem(titel="Ordained Name", text=entity.sil_mahananame),
            QRStyleDetailItem(titel="Birth Name", text=entity.sil_gihiname),
            QRStyleDetailItem(titel="Date of Birth", text=str(entity.sil_dofb) if entity.sil_dofb else None),
            QRStyleDetailItem(titel="Birth Place", text=entity.sil_birthpls),
            QRStyleDetailItem(titel="Contact Number", text=entity.sil_mobile),
            QRStyleDetailItem(titel="Email", text=entity.sil_email),
            QRStyleDetailItem(titel="Arama Location", text=temple_info),
            QRStyleDetailItem(titel="Current Status", text=status_text),
            QRStyleDetailItem(titel="Category", text=category_text),
            QRStyleDetailItem(titel="Ordination Date", text=str(entity.sil_mahanadate) if entity.sil_mahanadate else None),
            QRStyleDetailItem(titel="Workflow Status", text=entity.sil_workflow_status),
        ]
    
    def _get_high_bhikku_detail(self, db: Session, regn: str) -> Optional[List[QRStyleDetailItem]]:
        """Get detailed High Bhikku information"""
        entity = db.query(BhikkuHighRegist).filter(BhikkuHighRegist.bhr_regn == regn, BhikkuHighRegist.bhr_is_deleted == False).first()
        if not entity:
            return None
        
        # Get bhikku info for additional details
        birth_name = None
        dob = None
        birth_place = None
        mobile = None
        email = None
        
        if entity.bhr_candidate_regn:
            bhikku = db.query(Bhikku).filter(Bhikku.br_regn == entity.bhr_candidate_regn).first()
            if bhikku:
                birth_name = bhikku.br_gihiname
                dob = bhikku.br_dofb
                birth_place = bhikku.br_birthpls
                mobile = bhikku.br_mobile
                email = bhikku.br_email
        
        # Get temple info
        temple_info = None
        if entity.bhr_livtemple:
            temple = db.query(ViharaData).filter(ViharaData.vh_trn == entity.bhr_livtemple).first()
            if temple:
                temple_info = f"{temple.vh_vname}, {temple.vh_addrs}" if temple.vh_addrs else temple.vh_vname
        
        # Get status
        status_text = entity.bhr_currstat
        if entity.bhr_currstat:
            status = db.query(StatusData).filter(StatusData.st_statcd == entity.bhr_currstat).first()
            if status:
                status_text = status.st_descr
        
        return [
            QRStyleDetailItem(titel="Entity Type", text="High Bhikku"),
            QRStyleDetailItem(titel="Registration Number", text=entity.bhr_regn),
            QRStyleDetailItem(titel="Form ID", text=entity.bhr_form_id),
            QRStyleDetailItem(titel="Assumed Name", text=entity.bhr_assumed_name),
            QRStyleDetailItem(titel="Birth Name", text=birth_name),
            QRStyleDetailItem(titel="Date of Birth", text=str(dob) if dob else None),
            QRStyleDetailItem(titel="Birth Place", text=birth_place),
            QRStyleDetailItem(titel="Contact Number", text=mobile),
            QRStyleDetailItem(titel="Email", text=email),
            QRStyleDetailItem(titel="Live Location", text=temple_info),
            QRStyleDetailItem(titel="Current Status", text=status_text),
            QRStyleDetailItem(titel="Higher Ordination Date", text=str(entity.bhr_higher_ordination_date) if entity.bhr_higher_ordination_date else None),
            QRStyleDetailItem(titel="Higher Ordination Place", text=entity.bhr_higher_ordination_place),
            QRStyleDetailItem(titel="Workflow Status", text=entity.bhr_workflow_status),
        ]
    
    def _get_direct_high_bhikku_detail(self, db: Session, regn: str) -> Optional[List[QRStyleDetailItem]]:
        """Get detailed Direct High Bhikku information"""
        entity = db.query(DirectBhikkuHigh).filter(DirectBhikkuHigh.dbh_regn == regn, DirectBhikkuHigh.dbh_is_deleted == False).first()
        if not entity:
            return None
        
        # Get temple info
        temple_info = None
        if entity.dbh_livtemple:
            temple = db.query(ViharaData).filter(ViharaData.vh_trn == entity.dbh_livtemple).first()
            if temple:
                temple_info = f"{temple.vh_vname}, {temple.vh_addrs}" if temple.vh_addrs else temple.vh_vname
        
        # Get status
        status_text = entity.dbh_currstat
        if entity.dbh_currstat:
            status = db.query(StatusData).filter(StatusData.st_statcd == entity.dbh_currstat).first()
            if status:
                status_text = status.st_descr
        
        # Get category
        category_text = entity.dbh_cat
        if entity.dbh_cat:
            category = db.query(BhikkuCategory).filter(BhikkuCategory.cc_code == entity.dbh_cat).first()
            if category:
                category_text = category.cc_catogry
        
        ordained_name = entity.dbh_assumed_name or entity.dbh_mahananame
        
        return [
            QRStyleDetailItem(titel="Entity Type", text="Direct High Bhikku"),
            QRStyleDetailItem(titel="Registration Number", text=entity.dbh_regn),
            QRStyleDetailItem(titel="Ordained Name", text=ordained_name),
            QRStyleDetailItem(titel="Birth Name", text=entity.dbh_gihiname),
            QRStyleDetailItem(titel="Date of Birth", text=str(entity.dbh_dofb) if entity.dbh_dofb else None),
            QRStyleDetailItem(titel="Birth Place", text=entity.dbh_birthpls),
            QRStyleDetailItem(titel="Contact Number", text=entity.dbh_mobile),
            QRStyleDetailItem(titel="Email", text=entity.dbh_email),
            QRStyleDetailItem(titel="Live Location", text=temple_info),
            QRStyleDetailItem(titel="Current Status", text=status_text),
            QRStyleDetailItem(titel="Category", text=category_text),
            QRStyleDetailItem(titel="Higher Ordination Date", text=str(entity.dbh_higher_ordination_date) if entity.dbh_higher_ordination_date else None),
            QRStyleDetailItem(titel="Higher Ordination Place", text=entity.dbh_higher_ordination_place),
            QRStyleDetailItem(titel="Workflow Status", text=entity.dbh_workflow_status),
        ]
    
    def _get_vihara_detail(self, db: Session, trn: str) -> Optional[List[QRStyleDetailItem]]:
        """Get detailed Vihara information"""
        entity = db.query(ViharaData).filter(ViharaData.vh_trn == trn, ViharaData.vh_is_deleted == False).first()
        if not entity:
            return None
        
        return [
            QRStyleDetailItem(titel="Entity Type", text="Vihara"),
            QRStyleDetailItem(titel="Registration Number (TRN)", text=entity.vh_trn),
            QRStyleDetailItem(titel="Form ID", text=entity.vh_form_id),
            QRStyleDetailItem(titel="Vihara Name", text=entity.vh_vname),
            QRStyleDetailItem(titel="Address", text=entity.vh_addrs),
            QRStyleDetailItem(titel="Contact Number", text=entity.vh_mobile),
            QRStyleDetailItem(titel="WhatsApp", text=entity.vh_whtapp),
            QRStyleDetailItem(titel="Email", text=entity.vh_email),
            QRStyleDetailItem(titel="Viharadhipathi Name", text=entity.vh_viharadhipathi_name),
            QRStyleDetailItem(titel="Province", text=entity.vh_province),
            QRStyleDetailItem(titel="District", text=entity.vh_district),
            QRStyleDetailItem(titel="Establishment Date", text=str(entity.vh_bgndate) if entity.vh_bgndate else None),
            QRStyleDetailItem(titel="Workflow Status", text=entity.vh_workflow_status),
        ]
    
    def _get_arama_detail(self, db: Session, trn: str) -> Optional[List[QRStyleDetailItem]]:
        """Get detailed Arama information"""
        entity = db.query(AramaData).filter(AramaData.ar_trn == trn, AramaData.ar_is_deleted == False).first()
        if not entity:
            return None
        
        return [
            QRStyleDetailItem(titel="Entity Type", text="Arama"),
            QRStyleDetailItem(titel="Registration Number (TRN)", text=entity.ar_trn),
            QRStyleDetailItem(titel="Form ID", text=entity.ar_form_id),
            QRStyleDetailItem(titel="Arama Name", text=entity.ar_vname),
            QRStyleDetailItem(titel="Address", text=entity.ar_addrs),
            QRStyleDetailItem(titel="Contact Number", text=entity.ar_mobile),
            QRStyleDetailItem(titel="WhatsApp", text=entity.ar_whtapp),
            QRStyleDetailItem(titel="Email", text=entity.ar_email),
            QRStyleDetailItem(titel="Aramadhipathi Name", text=entity.ar_viharadhipathi_name),
            QRStyleDetailItem(titel="Province", text=entity.ar_province),
            QRStyleDetailItem(titel="District", text=entity.ar_district),
            QRStyleDetailItem(titel="Establishment Date", text=str(entity.ar_bgndate) if entity.ar_bgndate else None),
            QRStyleDetailItem(titel="Workflow Status", text=entity.ar_workflow_status),
        ]
    
    def _get_devala_detail(self, db: Session, trn: str) -> Optional[List[QRStyleDetailItem]]:
        """Get detailed Devala information"""
        # Query only specific columns to avoid missing field errors
        result = db.query(
            DevalaData.dv_trn,
            DevalaData.dv_form_id,
            DevalaData.dv_vname,
            DevalaData.dv_addrs,
            DevalaData.dv_mobile,
            DevalaData.dv_whtapp,
            DevalaData.dv_email,
            DevalaData.dv_bgndate,
            DevalaData.dv_workflow_status
        ).filter(
            DevalaData.dv_trn == trn,
            DevalaData.dv_is_deleted == False
        ).first()
        
        if not result:
            return None
        
        return [
            QRStyleDetailItem(titel="Entity Type", text="Devala"),
            QRStyleDetailItem(titel="Registration Number (TRN)", text=result.dv_trn),
            QRStyleDetailItem(titel="Form ID", text=result.dv_form_id),
            QRStyleDetailItem(titel="Devala Name", text=result.dv_vname),
            QRStyleDetailItem(titel="Address", text=result.dv_addrs),
            QRStyleDetailItem(titel="Contact Number", text=result.dv_mobile),
            QRStyleDetailItem(titel="WhatsApp", text=result.dv_whtapp),
            QRStyleDetailItem(titel="Email", text=result.dv_email),
            QRStyleDetailItem(titel="Establishment Date", text=str(result.dv_bgndate) if result.dv_bgndate else None),
            QRStyleDetailItem(titel="Workflow Status", text=result.dv_workflow_status),
        ]


# Singleton instance
reprint_search_service = ReprintSearchService()
