"""
用户进度模型 - 记录用户答题情况
作用：跟踪每个用户的答题历史和正确率
"""
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey,Index, String
from sqlalchemy.sql import func
from db import BaseModel

class UserQuestionProgress(BaseModel):
    __tablename__ = "user_question_progress"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)  # 用户ID（UUID字符串），建立索引提高查询速度
    question_id = Column(Integer, ForeignKey('physics_questions.question_id'), nullable=False)  # 外键关联题目
    is_correct = Column(Boolean, default=False)  # 是否答对
    is_completed = Column(Boolean, default=True)  # 是否完成
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # 最后更新时间
    
    # 添加复合索引，提高查询性能
    __table_args__ = (
        Index('idx_user_question', 'user_id', 'question_id', unique=True),
        Index('idx_user_stats', 'user_id', 'is_correct', 'last_updated'),
    )

    def __repr__(self):
        return f"<Progress user:{self.user_id} question:{self.question_id}>"