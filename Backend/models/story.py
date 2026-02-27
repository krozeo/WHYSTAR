from sqlalchemy import Column, String, Text
from db import Base

class NovelStory(Base):
    __tablename__ = "novel_story"
    __table_args__ = {"comment": "小说剧情表（5大物理类别，category主键）"}

    category = Column(String(20), primary_key=True, comment="故事类别（力学/声学/磁学/光学/热学，主键）")
    story_content = Column(Text, nullable=False, comment="故事完整内容")
    story_intro = Column(Text, nullable=False, comment="故事简介")
    prompt = Column(Text, nullable=False, comment="AI对话提示词")