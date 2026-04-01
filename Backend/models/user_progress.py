"""
用户进度模型 - 记录用户答题情况
作用：跟踪每个用户的答题历史和正确率
"""
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey,Index, String
from sqlalchemy.sql import func
from db import Base

class UserQuestionProgress(Base):
    __tablename__ = "user_question_progress"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    question_id = Column(Integer, ForeignKey('physics_questions.question_id'), nullable=False)
    is_correct = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_user_question', 'user_id', 'question_id', unique=True),
        Index('idx_user_stats', 'user_id', 'is_correct', 'last_updated'),
    )

    def __repr__(self):
        return f"<Progress user:{self.user_id} question:{self.question_id}>"