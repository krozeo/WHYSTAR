from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from db import Base


class UserOutfit(Base):
    __tablename__ = "user_outfits"

    user_id = Column(String(255), ForeignKey("users.id"), primary_key=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), primary_key=True)
    is_equipped = Column(Boolean, default=False)
