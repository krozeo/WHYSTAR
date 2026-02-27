# config.py - 项目配置唯一管理/导出入口，业务代码仅导入此文件
import os
from dotenv import load_dotenv

# 加载.env文件中的配置（核心：自动读取根目录.env，无需指定路径）
load_dotenv(override=True)  # override=True：覆盖系统环境变量，确保读取本地.env

# -------------------------- 从.env读取并导出 动态配置（敏感/环境相关）--------------------------
# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")  # 直接复用你的完整连接串

# -------------------------- JWT配置 --------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("请在.env中配置SECRET_KEY！")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))


# AI接口配置
AI_API_URL = os.getenv("AI_API_URL")
AI_API_TOKEN = os.getenv("AI_API_TOKEN")
AI_MODEL = os.getenv("AI_MODEL")

# 服务配置
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))

# -------------------------- 导出 项目通用常量（硬编码抽离，多人合并后统一修改）--------------------------
# 核心：五大物理类别（抽离为常量，所有业务代码均导入此常量，避免硬编码字符串）
PHYSICS_CATEGORIES = ["力学", "声学", "磁学", "光学", "热学"]

# 对话记忆配置（后续拓展用，提前抽离，适配多人合并）
CHAT_MEMORY_MAX_LENGTH = 20  # 对话记忆最大条数，超过自动截断最早记录

#       物理题库
"""
配置文件 - 从环境变量读取配置
作用：集中管理所有配置项，便于修改和维护
与其他文件的关系：db.py会读取这里的DATABASE_URL
"""

# 其他配置项
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"