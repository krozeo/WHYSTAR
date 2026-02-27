from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import PrimaryKeyConstraint
from db import Base
from models.story import NovelStory
from config import PHYSICS_CATEGORIES  # 导入统一常量，避免硬编码

class UserStoryChat(Base):
    __tablename__ = "user_story_chat"
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "category"),  # 联合主键：用户ID+category
        {"comment": "用户-故事对话记忆表（联合主键，JSONB存储记忆，清空即清除）"}
    )

    # 用户ID，UUID字符串，联合主键字段之一，对应具体用户
    user_id = Column(String(255), nullable=False, comment="用户ID（联合主键1，UUID字符串）")

    # 故事类别，字符串类型，联合主键字段之二
    # 外键关联到 NovelStory.category，只允许在 PHYSICS_CATEGORIES 中定义的类别
    category = Column(String(20), ForeignKey("novel_story.category", ondelete="RESTRICT"),
                      nullable=False, comment=f"所属类别（联合主键2，仅支持：{PHYSICS_CATEGORIES}）")

    # 对话记忆内容，按用户+类别维度存储的 JSONB 数组
    # 默认是空列表，清空该字段等价于清除该用户在该类别下的所有对话记忆
    chat_memory = Column(JSONB, nullable=False, default=[], comment="对话记忆内容，JSONB数组，清空=清除记忆")

    # ORM 关联关系：一条对话记录关联到一条故事记录
    story = relationship("NovelStory", backref="chat_records")