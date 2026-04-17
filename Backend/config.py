# config.py - 项目配置唯一管理/导出入口
"""
配置文件 - 从环境变量读取配置
作用：集中管理所有配置项，便于修改和维护
与其他文件的关系：db.py会读取这里的DATABASE_URL
"""
import os
from dotenv import load_dotenv

# AI辅助生成整体框架：Doubao-Seed-1.8, 2026-1-31

# 加载.env文件中的配置
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
load_dotenv(env_path, override=True)

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 120))

# AI接口配置
AI_API_URL = os.getenv("AI_API_URL")
AI_API_TOKEN = os.getenv("AI_API_TOKEN")
AI_MODEL = os.getenv("AI_MODEL")

# COZE接口配置
COZE_API_BASE = os.getenv("COZE_API_BASE", "https://api.coze.cn")
COZE_API_TOKEN = os.getenv("COZE_API_TOKEN")
COZE_BOT_ID = os.getenv("COZE_BOT_ID")

# 智谱AI接口配置
ZHIPU_API_BASE = os.getenv("ZHIPU_API_BASE", "https://open.bigmodel.cn/api/paas/v4")
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
ZHIPU_ASSISTANT_ID = os.getenv("ZHIPU_ASSISTANT_ID")
ZHIPU_ASSISTANT_MODEL = os.getenv("ZHIPU_ASSISTANT_MODEL", "glm-4-assistant")
ZHIPU_CHAT_MODEL = os.getenv("ZHIPU_CHAT_MODEL", "glm-5")

# 百度语音合成配置
BAIDU_TTS_ACCESS_TOKEN = os.getenv("BAIDU_TTS_ACCESS_TOKEN")
BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")
BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")

# 五大物理类别
PHYSICS_CATEGORIES = ["力学", "声学", "磁学", "光学", "热学"]

# 对话记忆配置
CHAT_MEMORY_MAX_LENGTH = 20

# 物理题库
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# 服务配置
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
