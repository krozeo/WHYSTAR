from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from db import Base
from models.story import NovelStory

class NovelCharacter(Base):
    __tablename__ = "novel_character"
    __table_args__ = {"comment": "小说角色表（name主键，外键关联故事类别）"}

    name = Column(String(50), primary_key=True, comment="角色姓名（主键）")
    character_intro = Column(Text, nullable=False, comment="角色简介")
    category = Column(String(20), ForeignKey("novel_story.category", ondelete="RESTRICT"), 
                      nullable=False, comment="所属类别（关联novel_story）")
    
    # ORM关联关系（方便联表查询）
    story = relationship("NovelStory", backref="characters")