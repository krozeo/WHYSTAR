from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from db import Base
from models.story import NovelStory

# AI辅助生成整体框架：Doubao-Seed-1.8, 2026-1-31
class NovelCharacter(Base):
    __tablename__ = "novel_character"
    __table_args__ = {"comment": "小说角色表"}

    name = Column(String(50), primary_key=True, comment="角色姓名")
    character_intro = Column(Text, nullable=False, comment="角色简介")
    category = Column(String(20), ForeignKey("novel_story.category", ondelete="RESTRICT"), nullable=False, comment="所属类别")
    story = relationship("NovelStory", backref="characters")