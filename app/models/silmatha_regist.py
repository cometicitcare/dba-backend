# app/models/silmatha_regist.py
from sqlalchemy import Boolean, Column, Integer, String, Date, TIMESTAMP, text, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class SilmathaRegist(Base):
    __tablename__ = "silmatha_regist"

    br_id = Column(Integer, primary_key=True, index=True)
    br_regn = Column(String(20), unique=True, nullable=False, index=True)
    br_reqstdate = Column(Date, nullable=False)

    br_birthpls = Column(String(50))
    br_province = Column(String(50), ForeignKey("cmm_province.cp_code", onupdate="CASCADE", ondelete="SET NULL"))
    br_district = Column(String(50), ForeignKey("cmm_districtdata.dd_dcode", onupdate="CASCADE", ondelete="SET NULL"))
    br_korale = Column(String(50))
    br_pattu = Column(String(50))
    br_division = Column(String(50), ForeignKey("cmm_dvsec.dv_dvcode", onupdate="CASCADE", ondelete="SET NULL"))
    br_vilage = Column(String(50))
    br_gndiv = Column(String(10), ForeignKey("cmm_gndata.gn_gnc", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)

    br_gihiname = Column(String(50))
    br_dofb = Column(Date)
    br_fathrname = Column(String(50))
    br_remarks = Column(String(100))

    br_currstat = Column(String(5), ForeignKey("statusdata.st_statcd", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    br_effctdate = Column(Date)
    br_residence_at_declaration = Column(String(200))
    br_declaration_date = Column(Date)

    br_parshawaya = Column(String(10), nullable=False)
    br_nikaya = Column(String(10))
    br_livtemple = Column(String(10), nullable=True)
    br_mahanatemple = Column(String(10), ForeignKey("vihaddata.vh_trn", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    br_mahanaacharyacd = Column(String(12), ForeignKey("bhikku_regist.br_regn", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    br_multi_mahanaacharyacd = Column(String(200))
    br_mahananame = Column(String(50))
    br_mahanadate = Column(Date)
    br_mahanayaka_name = Column(String(200))
    br_mahanayaka_address = Column(String(200))
    br_viharadhipathi = Column(String(12), ForeignKey("bhikku_regist.br_regn", onupdate="CASCADE", ondelete="SET NULL"))
    br_cat = Column(String(5), ForeignKey("cmm_cat.cc_code", onupdate="CASCADE", ondelete="SET NULL"))

    br_mobile = Column(String(10))
    br_email = Column(String(50))
    br_fathrsaddrs = Column(String(200))
    br_fathrsmobile = Column(String(10))

    br_upasampada_serial_no = Column(String(20))
    br_robing_tutor_residence = Column(String(10), ForeignKey("vihaddata.vh_trn", onupdate="CASCADE", ondelete="SET NULL"))
    br_robing_after_residence_temple = Column(String(10), ForeignKey("vihaddata.vh_trn", onupdate="CASCADE", ondelete="SET NULL"))

    br_version = Column(TIMESTAMP, nullable=False, server_default=func.now())
    br_is_deleted = Column(Boolean, server_default=text("false"))
    br_created_at = Column(TIMESTAMP, server_default=func.now())
    br_updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    br_created_by = Column(String(25))
    br_updated_by = Column(String(25))
    br_version_number = Column(Integer, server_default=text("1"))
