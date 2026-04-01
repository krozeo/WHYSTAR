from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import PrimaryKeyConstraint
from db import Base
from models.story import NovelStory

class UserStoryChat(Base):
    __tablename__ = "user_story_chat"
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "category"),
        {"comment": "用户-故事对话记忆表"}
    )

    user_id = Column(String(255), nullable=False, comment="用户ID")
    category = Column(String(20), ForeignKey("novel_story.category", ondelete="RESTRICT"), nullable=False, comment=f"所属类别")
    chat_memory = Column(JSONB, nullable=False, default=[], comment="对话记忆内容")
    story = relationship("NovelStory", backref="chat_records")