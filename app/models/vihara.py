from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.sql import expression

from app.db.base import Base


class ViharaData(Base):
    __tablename__ = "vihaddata"

    vh_id = Column(Integer, primary_key=True, index=True)
    vh_trn = Column(String(10), nullable=False, index=True, unique=True)
    vh_vname = Column(String(200))
    vh_addrs = Column(String(200))
    vh_mobile = Column(String(10), nullable=False)
    vh_whtapp = Column(String(10), nullable=False)
    vh_email = Column(String(200), nullable=False, index=True, unique=True)
    vh_typ = Column(String(10), nullable=False)
    vh_gndiv = Column(String(10), nullable=False)
    vh_fmlycnt = Column(Integer)
    vh_bgndate = Column(Date)
    vh_ownercd = Column(String(12), nullable=False)
    vh_parshawa = Column(String(10), nullable=False)
    vh_ssbmcode = Column(String(10))
    vh_syojakarmakrs = Column(String(100))
    vh_syojakarmdate = Column(Date)
    vh_landownrship = Column(String(150))
    vh_pralename = Column(String(50))
    vh_pralesigdate = Column(Date)
    vh_bacgrecmn = Column(String(100))
    vh_bacgrcmdate = Column(Date)
    vh_minissecrsigdate = Column(Date)
    vh_minissecrmrks = Column(String(200))
    vh_ssbmsigdate = Column(Date)
    vh_version = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    vh_is_deleted = Column(Boolean, nullable=False, server_default=expression.false())
    vh_created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    vh_updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    vh_created_by = Column(String(25))
    vh_updated_by = Column(String(25))
    vh_version_number = Column(Integer, nullable=False, server_default="1")
