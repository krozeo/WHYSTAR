"""
用户答题统计表 - 记录每个用户的答题详细统计
作用：快速查询用户的答题总数、正确数、各方向正确率
为什么要新建这个表？
  1. 避免每次统计都去扫描user_question_progress表
  2. 提高查询性能
  3. 方便展示个人中心的各种统计指标
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from db import Base

# AI辅助生成：Deepseek-v3.2（网页端，2月）
class UserStats(Base):
    __tablename__ = "user_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    
    total_answered = Column(Integer, default=0) 
    total_correct = Column(Integer, default=0)

    acoustics_answered = Column(Integer, default=0)
    acoustics_correct = Column(Integer, default=0)
    
    thermodynamics_answered = Column(Integer, default=0)
    thermodynamics_correct = Column(Integer, default=0)
    
    mechanics_answered = Column(Integer, default=0) 
    mechanics_correct = Column(Integer, default=0)
    
    electromagnetism_answered = Column(Integer, default=0) 
    electromagnetism_correct = Column(Integer, default=0) 
    
    optics_answered = Column(Integer, default=0)
    optics_correct = Column(Integer, default=0)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserStats user:{self.user_id} total:{self.total_answered}>"