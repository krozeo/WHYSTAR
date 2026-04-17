from sqlalchemy import Column, String, Text
from db import Base

# AI辅助生成整体框架：Doubao-Seed-1.8, 2026-1-31
class NovelStory(Base):
    __tablename__ = "novel_story"
    __table_args__ = {"comment": "小说剧情表"}

    category = Column(String(20), primary_key=True, comment="故事类别")
    story_content = Column(Text, nullable=False, comment="故事完整内容")
    story_intro = Column(Text, nullable=False, comment="故事简介")
    prompt = Column(Text, nullable=False, comment="AI对话提示词")