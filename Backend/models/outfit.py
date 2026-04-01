from sqlalchemy import Column, Integer, String
from db import Base


class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    price = Column(Integer, nullable=True)
