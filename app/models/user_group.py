from sqlalchemy import String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from datetime import datetime

class UserGroup(Base):
    __tablename__ = "user_groups"

    user_id: Mapped[str] = mapped_column(String(10), ForeignKey("user_accounts.ua_user_id", ondelete="CASCADE"), primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.group_id", ondelete="CASCADE"), primary_key=True)
    created_by: Mapped[str] = mapped_column(String(50), nullable=True)
    updated_by: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    group = relationship("Group", back_populates="users")
    user = relationship("UserAccount", back_populates="groups")


    def __repr__(self):
        return f"<UserGroup(user_id={self.user_id}, group_id={self.group_id}, created_at={self.created_at})>"