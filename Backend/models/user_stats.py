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
from db import BaseModel

class UserStats(BaseModel):
    __tablename__ = "user_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    
    # 总体统计
    total_answered = Column(Integer, default=0)  # 总答题数
    total_correct = Column(Integer, default=0)   # 总正确数
    
    # 各方向统计（5个方向）
    acoustics_answered = Column(Integer, default=0)   # 声学答题数
    acoustics_correct = Column(Integer, default=0)    # 声学正确数
    
    thermodynamics_answered = Column(Integer, default=0)  # 热学答题数
    thermodynamics_correct = Column(Integer, default=0)   # 热学正确数
    
    mechanics_answered = Column(Integer, default=0)  # 力学答题数
    mechanics_correct = Column(Integer, default=0)   # 力学正确数
    
    electromagnetism_answered = Column(Integer, default=0)  # 电磁学答题数
    electromagnetism_correct = Column(Integer, default=0)   # 电磁学正确数
    
    optics_answered = Column(Integer, default=0)  # 光学答题数
    optics_correct = Column(Integer, default=0)   # 光学正确数
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserStats user:{self.user_id} total:{self.total_answered}>"