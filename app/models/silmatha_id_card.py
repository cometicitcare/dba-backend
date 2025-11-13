from sqlalchemy import Boolean, Column, Date, Integer, String, TIMESTAMP, text
from sqlalchemy.sql import func

from app.db.base import Base


class SilmathaIDCard(Base):
    __tablename__ = "silmatha_id_card"

    sic_id = Column(Integer, primary_key=True, index=True)
    sic_regn = Column(String(20), nullable=False, unique=True, index=True)
    sic_national_id = Column(String(20))
    sic_birth_certificate_attached = Column(Boolean)
    sic_left_thumbprint_url = Column(String(255))
    sic_applicant_image_url = Column(String(255))
    sic_acharya_approved = Column(Boolean)
    sic_acharya_date = Column(Date)
    sic_grama_niladari_approved = Column(Boolean)
    sic_grama_niladari_date = Column(Date)
    sic_devotional_secretariat_approved = Column(Boolean)
    sic_devotional_secretariat_date = Column(Date)
    sic_created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    sic_updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    sic_is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    sic_acharya_phone = Column(String(20))
    sic_grama_niladari_phone = Column(String(20))
    sic_devotional_secretariat_phone = Column(String(20))

