"""
题目数据模型 - 定义physics_questions表的结构
作用：将数据库表映射为Python类，便于操作
与其他文件的关系：
  1. service层通过这个类查询和操作题目数据
  2. 继承自db.py中的BaseModel
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from db import Base

class PhysicsQuestion(Base):
    """
    物理题目表模型
    对应数据库中的physics_questions表
    每个属性对应表中的一列
    """
    __tablename__ = "physics_questions"
    
    question_id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(String(10), nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        """对象的字符串表示，便于调试"""
        return f"<Question {self.question_id}: {self.category}>"