# PyTest/test_stage_e_temp_integration.py
"""
Stage E Integration Tests
Tests for TEMP record handling after merging development_dev_branch:
- Test *_is_transferred flags in TEMP tables
- Test is_temporary_record flags in main tables
- Test TEMP record creation and tracking
"""
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.database import get_db
from app.models.temporary_vihara import TemporaryVihara
from app.models.vihara import ViharaData
from app.models.temporary_bhikku import TemporaryBhikku
from app.models.bhikku import Bhikku
from app.models.temporary_silmatha import TemporarySilmatha
from app.models.silmatha_regist import SilmathaRegist
from app.models.temporary_arama import TemporaryArama
from app.models.arama import AramaData


@pytest.fixture(scope="function")
def db_session() -> Session:
    """Create an in-memory SQLite database for testing"""
    # Use SQLite for testing to avoid needing PostgreSQL
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


class TestTemporaryViharaFlags:
    """Test temporary_vihara table transfer flags and main table integration"""
    
    def test_temporary_vihara_has_transfer_flag(self, db_session: Session):
        """Verify temporary_vihara model has tv_is_transferred column"""
        # Create a temporary vihara record
        temp_vihara = TemporaryVihara(
            tv_name="Test Temple",
            tv_address="Test Address",
            tv_province="WP",
            tv_district="DC001",
            tv_is_transferred=False,  # Initially not transferred
        )
        db_session.add(temp_vihara)
        db_session.commit()
        
        # Retrieve and verify
        retrieved = db_session.query(TemporaryVihara).filter_by(tv_name="Test Temple").first()
        assert retrieved is not None
        assert retrieved.tv_is_transferred == False
        assert hasattr(retrieved, 'tv_is_transferred'), "tv_is_transferred flag missing!"
    
    def test_temporary_vihara_transfer_flag_update(self, db_session: Session):
        """Verify tv_is_transferred can be marked as transferred"""
        temp_vihara = TemporaryVihara(
            tv_name="Test Temple 2",
            tv_address="Test Address 2",
            tv_is_transferred=False,
        )
        db_session.add(temp_vihara)
        db_session.commit()
        tv_id = temp_vihara.tv_id
        
        # Mark as transferred
        temp_vihara.tv_is_transferred = True
        db_session.commit()
        
        # Verify update
        retrieved = db_session.query(TemporaryVihara).filter_by(tv_id=tv_id).first()
        assert retrieved.tv_is_transferred == True
    
    def test_vihara_main_table_has_temp_flag(self, db_session: Session):
        """Verify vihaddata (main vihara table) has is_temporary_record column"""
        vihara = ViharaData(
            vh_trn="VH001",
            vh_vname="Main Temple",
            vh_is_temporary_record=True,  # Mark as from temporary table
            vh_bgndate=None,  # Required field
            vh_fmlycnt=0,
            vh_ssbmcode="",
            vh_syojakarmrs="",
            vh_syojakarmdate=None,
            vh_landownrship="",
            vh_pralename="",
            vh_pralesigdate=None,
            vh_bacgrecmn="",
            vh_bacgrcmdate=None,
            vh_minissecrsigdate=None,
            vh_ssbmsigdate=None,
        )
        db_session.add(vihara)
        db_session.commit()
        
        # Retrieve and verify
        retrieved = db_session.query(ViharaData).filter_by(vh_trn="VH001").first()
        assert retrieved is not None
        assert retrieved.vh_is_temporary_record == True
        assert hasattr(retrieved, 'vh_is_temporary_record'), "vh_is_temporary_record flag missing!"


class TestTemporaryBhikkuFlags:
    """Test temporary_bhikku table transfer flags and main table integration"""
    
    def test_temporary_bhikku_has_transfer_flag(self, db_session: Session):
        """Verify temporary_bhikku model has tb_is_transferred column"""
        temp_bhikku = TemporaryBhikku(
            tb_name="Test Bhikku",
            tb_contact_number="0771234567",
            tb_is_transferred=False,  # Initially not transferred
        )
        db_session.add(temp_bhikku)
        db_session.commit()
        
        # Retrieve and verify
        retrieved = db_session.query(TemporaryBhikku).filter_by(tb_name="Test Bhikku").first()
        assert retrieved is not None
        assert retrieved.tb_is_transferred == False
        assert hasattr(retrieved, 'tb_is_transferred'), "tb_is_transferred flag missing!"
    
    def test_bhikku_main_table_has_temp_flag(self, db_session: Session):
        """Verify bhikku_regist (main bhikku table) has is_temporary_record column"""
        from datetime import date
        
        bhikku = Bhikku(
            br_regn="BH001",
            br_reqstdate=date(2026, 1, 1),
            br_gihiname="Test Bhikku Name",
            br_dofb=date(1970, 1, 1),
            br_currstat="A",  # Active status
            br_parshawaya="WP",  # Western Province
            br_is_temporary_record=True,  # Mark as from temporary table
        )
        db_session.add(bhikku)
        db_session.commit()
        
        # Retrieve and verify
        retrieved = db_session.query(Bhikku).filter_by(br_regn="BH001").first()
        assert retrieved is not None
        assert retrieved.br_is_temporary_record == True
        assert hasattr(retrieved, 'br_is_temporary_record'), "br_is_temporary_record flag missing!"


class TestTemporarySilmathaFlags:
    """Verify existing Silmatha integration still works"""
    
    def test_silmatha_has_temp_flag(self, db_session: Session):
        """Verify silmatha_regist has is_temporary_record flag"""
        from datetime import date
        
        silmatha = SilmathaRegist(
            sil_regn="SIL001",
            sil_reqstdate=date(2026, 1, 1),
            sil_gihiname="Test Silmatha",
            sil_dofb=date(1970, 1, 1),
            sil_currstat="A",
            sil_is_temporary_record=True,
        )
        db_session.add(silmatha)
        db_session.commit()
        
        # Retrieve and verify
        retrieved = db_session.query(SilmathaRegist).filter_by(sil_regn="SIL001").first()
        assert retrieved is not None
        assert retrieved.sil_is_temporary_record == True


class TestTemporaryAramaFlags:
    """Verify existing Arama integration still works"""
    
    def test_arama_has_temp_flag(self, db_session: Session):
        """Verify aramadata has is_temporary_record flag"""
        arama = AramaData(
            ar_trn="AR001",
            ar_name="Test Arama",
            ar_is_temporary_record=True,
        )
        db_session.add(arama)
        db_session.commit()
        
        # Retrieve and verify
        retrieved = db_session.query(AramaData).filter_by(ar_trn="AR001").first()
        assert retrieved is not None
        assert retrieved.ar_is_temporary_record == True


class TestAllEntitiesConsistency:
    """Test that all 4 entity types follow consistent TEMP handling pattern"""
    
    def test_all_temp_tables_have_transfer_flags(self):
        """Verify all temporary tables have *_is_transferred columns"""
        # These should all pass model-level inspection
        temp_vihara = TemporaryVihara(tv_name="Test")
        temp_bhikku = TemporaryBhikku(tb_name="Test")
        temp_silmatha = TemporarySilmatha(ts_gihiname="Test")
        temp_arama = TemporaryArama(ta_name="Test")
        
        # Check attributes
        assert hasattr(temp_vihara, 'tv_is_transferred')
        assert hasattr(temp_bhikku, 'tb_is_transferred')
        assert hasattr(temp_silmatha, 'ts_is_transferred')
        assert hasattr(temp_arama, 'ta_is_transferred')
    
    def test_all_main_tables_have_temp_flags(self):
        """Verify main tables have is_temporary_record columns"""
        # These should all have the flag
        assert hasattr(ViharaData, 'vh_is_temporary_record')
        assert hasattr(Bhikku, 'br_is_temporary_record')
        assert hasattr(SilmathaRegist, 'sil_is_temporary_record')
        assert hasattr(AramaData, 'ar_is_temporary_record')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
