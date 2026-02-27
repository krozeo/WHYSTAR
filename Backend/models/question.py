"""
题目数据模型 - 定义physics_questions表的结构
作用：将数据库表映射为Python类，便于操作
与其他文件的关系：
  1. service层通过这个类查询和操作题目数据
  2. 继承自db.py中的BaseModel
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from db import BaseModel  # 导入数据库基类

class PhysicsQuestion(BaseModel):
    """
    物理题目表模型
    对应数据库中的physics_questions表
    每个属性对应表中的一列
    """
    __tablename__ = "physics_questions"  # 指定表名
    
    # 表字段定义
    question_id = Column(Integer, primary_key=True, autoincrement=True)  # 主键，自增
    category = Column(String(50), nullable=False)  # 题目类别，不能为空
    question_text = Column(Text, nullable=False)  # 题目内容，文本类型
    options = Column(JSON, nullable=False)  # 选项，JSON格式存储
    correct_answer = Column(String(10), nullable=False)  # 正确答案
    explanation = Column(Text, nullable=False)  # 答案解析
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 创建时间
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # 更新时间
    
    def __repr__(self):
        """对象的字符串表示，便于调试"""
        return f"<Question {self.question_id}: {self.category}>"