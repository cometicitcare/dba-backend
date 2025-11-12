from sqlalchemy import Boolean, Column, Date, Integer, String, TIMESTAMP, text
from sqlalchemy.sql import func

from app.db.base import Base


class BhikkuIDCard(Base):
    __tablename__ = "bhikku_id_card"

    bic_id = Column(Integer, primary_key=True, index=True)
    bic_regn = Column(String(20), nullable=False, unique=True, index=True)
    bic_national_id = Column(String(20))
    bic_left_thumbprint_url = Column(String(255))
    bic_applicant_image_url = Column(String(255))
    bic_acharya_approved = Column(Boolean)
    bic_acharya_date = Column(Date)
    bic_grama_niladari_approved = Column(Boolean)
    bic_grama_niladari_date = Column(Date)
    bic_devotional_secretariat_approved = Column(Boolean)
    bic_devotional_secretariat_date = Column(Date)
    bic_created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    bic_updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    bic_is_deleted = Column(Boolean, nullable=False, server_default=text("false"))
    bic_acharya_phone = Column(String(20))
    bic_grama_niladari_phone = Column(String(20))
    bic_devotional_secretariat_phone = Column(String(20))

