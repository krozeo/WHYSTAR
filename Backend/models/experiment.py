from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from db import Base

class PhysicsExperiment(Base):
    """
    物理实验表模型
    对应数据库中的physics_experiments表
    """
    __tablename__ = "physics_experiments"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="实验ID")
    title = Column(String(100), nullable=False, comment="实验标题")
    category = Column(String(50), nullable=False, index=True, comment="实验分类（如：光学、力学）")
    description = Column(Text, nullable=True, comment="实验简介")
    content_path = Column(String(255), nullable=False, comment="HTML文件路径")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<PhysicsExperiment {self.title} ({self.category})>"
