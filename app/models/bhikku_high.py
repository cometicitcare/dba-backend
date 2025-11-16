# app/models/bhikku_high.py
from sqlalchemy import Boolean, Column, Date, Integer, String, TIMESTAMP, text
from sqlalchemy.orm import relationship, foreign, remote
from sqlalchemy.sql import func

from app.db.base import Base


class BhikkuHighRegist(Base):
    __tablename__ = "bhikku_high_regist"

    bhr_id = Column(Integer, primary_key=True, index=True)
    bhr_regn = Column(String(12), nullable=False, index=True)
    bhr_samanera_serial_no = Column(String(20))
    bhr_reqstdate = Column(Date, nullable=False)
    bhr_remarks = Column(String(100))
    bhr_currstat = Column(String(5), nullable=False)
    bhr_parshawaya = Column(String(10), nullable=False)
    bhr_livtemple = Column(String(10), nullable=False)
    bhr_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    bhr_is_deleted = Column(Boolean, server_default=text("false"))
    bhr_created_at = Column(TIMESTAMP, server_default=func.now())
    bhr_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    bhr_created_by = Column(String(25))
    bhr_updated_by = Column(String(25))
    bhr_version_number = Column(Integer, server_default=text("1"))
    bhr_cc_code = Column(String(5))
    bhr_candidate_regn = Column(String(12))
    bhr_higher_ordination_place = Column(String(10))
    bhr_higher_ordination_date = Column(Date)
    bhr_karmacharya_name = Column(String(12))
    bhr_upaddhyaya_name = Column(String(12))
    bhr_assumed_name = Column(String(50))
    bhr_residence_higher_ordination_trn = Column(String(10))
    bhr_residence_permanent_trn = Column(String(10))
    bhr_declaration_residence_address = Column(String(10))
    bhr_tutors_tutor_regn = Column(String(200))
    bhr_presiding_bhikshu_regn = Column(String(200))
    bhr_declaration_date = Column(Date)
    bhr_updated_by = Column(String(25))
    bhr_version_number = Column(Integer, server_default=text("1"))
    
    # Relationships for foreign keys
    # Bhikku relationships
    candidate_rel = relationship(
        "Bhikku",
        primaryjoin="foreign(BhikkuHighRegist.bhr_candidate_regn) == remote(Bhikku.br_regn)",
        viewonly=True,
        lazy="joined"
    )
    tutors_tutor_rel = relationship(
        "Bhikku",
        primaryjoin="foreign(BhikkuHighRegist.bhr_tutors_tutor_regn) == remote(Bhikku.br_regn)",
        viewonly=True,
        lazy="joined"
    )
    presiding_bhikshu_rel = relationship(
        "Bhikku",
        primaryjoin="foreign(BhikkuHighRegist.bhr_presiding_bhikshu_regn) == remote(Bhikku.br_regn)",
        viewonly=True,
        lazy="joined"
    )
    
    # Status relationship
    status_rel = relationship(
        "StatusData",
        primaryjoin="foreign(BhikkuHighRegist.bhr_currstat) == StatusData.st_statcd",
        viewonly=True,
        lazy="joined"
    )
    
    # Parshawaya relationship
    parshawaya_rel = relationship(
        "ParshawaData",
        primaryjoin="foreign(BhikkuHighRegist.bhr_parshawaya) == ParshawaData.pr_prn",
        viewonly=True,
        lazy="joined"
    )
    
    # Vihara/Temple relationships
    livtemple_rel = relationship(
        "ViharaData",
        primaryjoin="foreign(BhikkuHighRegist.bhr_livtemple) == ViharaData.vh_trn",
        viewonly=True,
        lazy="joined"
    )
    residence_higher_ordination_rel = relationship(
        "ViharaData",
        primaryjoin="foreign(BhikkuHighRegist.bhr_residence_higher_ordination_trn) == ViharaData.vh_trn",
        viewonly=True,
        lazy="joined"
    )
    residence_permanent_rel = relationship(
        "ViharaData",
        primaryjoin="foreign(BhikkuHighRegist.bhr_residence_permanent_trn) == ViharaData.vh_trn",
        viewonly=True,
        lazy="joined"
    )

