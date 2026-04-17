# db.py - 数据库连接配置
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

# AI辅助生成整体框架：Doubao-Seed-1.8, 2026-1-31

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=False)

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def get_db():
    """
    数据库会话依赖函数
    作用：为每个请求提供独立的数据库会话，请求结束后自动关闭
    使用方式：在FastAPI的路由函数参数中使用Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()