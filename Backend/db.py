# db.py - 数据库连接配置（极简，核心配置从config.py导入）
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL  # 仅导入config.py，无硬编码

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=False)  # echo=True可开启SQL打印，调试用

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类 - 所有数据模型都要继承这个类
# IMPORTANT: 项目里必须只使用同一个 Base，否则会出现 ForeignKey 找不到目标表等问题
Base = declarative_base()
BaseModel = Base

def get_db():
    """
    数据库会话依赖函数
    作用：为每个请求提供独立的数据库会话，请求结束后自动关闭
    使用方式：在FastAPI的路由函数参数中使用 Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db  # 将db对象提供给请求处理函数使用
    finally:
        db.close()  # 请求结束后关闭连接