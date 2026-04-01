"""
项目主入口
作用：
  1. 创建FastAPI应用实例，整合两个模块
  2. 配置CORS、模板等全局设置
  3. 创建数据库表（如果不存在）
  4. 注册所有路由
  5. 提供统一的服务启动入口
与其他文件的关系：
  1. 导入config.py中的统一配置
  2. 导入路由
  3. 调用db.py创建数据库表
  4. 作为程序的唯一启动点
"""

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import os

# 导入 JWT 验证依赖
try:
    from core.deps import get_current_user
    from models.user import User
    HAS_AUTH_MODULE = True
except ImportError:
    HAS_AUTH_MODULE = False

# 导入统一配置
from config import SERVER_HOST, SERVER_PORT, DEBUG

# 导入数据库相关（物理题库模块需要）
try:
    from db import BaseModel, engine
    # 显式导入所有模型以确保 SQLAlchemy 能识别所有表（解决 NoReferencedTableError）
    from models.user import User
    from models.user_stats import UserStats
    from models.user_progress import UserQuestionProgress
    from models.question import PhysicsQuestion
    from models.experiment import PhysicsExperiment
    from models.outfit import Outfit
    from models.user_outfit import UserOutfit

    HAS_PHYSICS_MODULE = True
except ImportError:
    print("⚠️  物理题库模块的数据库配置未找到，仅加载AI对话模块")
    HAS_PHYSICS_MODULE = False

# ==================== 第一步：创建FastAPI应用实例 ====================
app = FastAPI(
    title="AI对话与物理题库整合系统",
    description="基于AI的小说对话系统 + 五大物理学方向在线答题系统",
    version="2.0.0",
    docs_url=None,  # 禁用默认的docs
    redoc_url=None  # 禁用默认的redoc
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    return response

# 自定义Swagger UI配置，解决国内CDN访问问题
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
    )

# ==================== 第二步：配置跨域（前端对接必备）====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境替换为指定前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 第三步：创建数据库表（物理题库模块）====================
if HAS_PHYSICS_MODULE:
    try:
        # 这会根据models中定义的类，在数据库中创建对应的表
        BaseModel.metadata.create_all(bind=engine)
        print("✅ 物理题库数据库表创建完成")
    except Exception as e:
        print(f"⚠️  数据库表创建失败: {e}")
        print("   物理题库模块可能无法正常工作")

# ==================== 第四步：配置模板目录（物理题库模块需要）====================
templates_dir = "templates"
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)
print(f"✅ 模板目录配置完成: {templates_dir}")

# 静态目录
# 1. 获取 main.py 所在目录 (Backend/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 2. 获取 Backend 的父级目录，即项目根目录 (WhyStar/)
root_dir = os.path.dirname(current_dir)
# 3. 拼接得到项目根目录下的 static 文件夹路径 (WhyStar/static)
static_dir = os.path.join(root_dir, "static")

if not os.path.exists(static_dir):
    # 如果找不到根目录下的static，尝试使用当前目录下的static (仅作为备选)
    static_dir = os.path.join(current_dir, "static")

print(f"✅ 静态资源目录已配置: {static_dir}")
os.makedirs(os.path.join(static_dir, "experiments"), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ==================== 第五步：导入并注册所有模块路由 ====================
# 注意：这里使用try-except确保单个模块缺失不会影响整体运行

# AI对话模块路由
try:
    from api import story_character, chat_memory
    app.include_router(story_character.router, prefix="/api", tags=["AI对话模块"])
    app.include_router(chat_memory.router, prefix="/api", tags=["AI记忆模块"])
    print("✅ AI对话模块路由注册完成")
except ImportError as e:
    print(f"⚠️  AI对话模块导入失败: {e}")
    print("   AI对话功能将不可用")

# 用户中心模块路由
try:
    from api.user import router as user_router
    from api.auth import router as auth_router
    app.include_router(user_router)
    app.include_router(auth_router)
    print("✅ 用户中心与认证模块路由注册完成")
except ImportError as e:
    print(f"⚠️  用户中心或认证模块导入失败: {e}")

# 物理题库模块路由
try:
    from api.question import router as question_router
    app.include_router(question_router)
    print("✅ 物理题库模块路由注册完成")
except ImportError as e:
    print(f"⚠️  物理题库模块导入失败: {e}")
    print("   物理题库功能将不可用")

try:
    from api.experiment import router as experiment_router
    app.include_router(experiment_router)
    print("✅ 物理实验模块路由注册完成")
except ImportError as e:
    print(f"⚠️  物理实验模块导入失败: {e}")

# 虚拟物品兑换模块路由
try:
    from api.outfit import router as outfit_router
    app.include_router(outfit_router)
    print("✅ 虚拟物品兑换模块路由注册完成")
except ImportError as e:
    print(f"⚠️  虚拟物品兑换模块导入失败: {e}")

# ==================== 第六步：定义全局路由 ====================

@app.get("/", summary="系统主页")
async def root():
    """
    系统根路径
    返回：重定向到系统信息页面
    """
    return RedirectResponse(url="/info")


@app.get("/register", include_in_schema=False)
async def register_page_redirect():
    return RedirectResponse(url="/auth/login")

if HAS_AUTH_MODULE:
    @app.get("/api/me", summary="获取当前登录用户信息", tags=["用户中心"])
    async def get_me(current_user: User = Depends(get_current_user)):
        """
        验证登录状态并返回当前用户信息
        Header 需包含: Authorization: Bearer <Token>
        """
        return {
            "success": True,
            "data": {
                "id": current_user.id,
                "username": current_user.username,
                "total_points": current_user.total_points
            }
        }

@app.get("/info", summary="系统信息")
async def system_info():
    """
    获取系统信息和模块状态
    返回：系统版本、模块状态、可用功能等
    """
    modules_status = {
        "ai_dialogue": {
            "available": "story_character" in globals() and "chat_memory" in globals(),
            "endpoints": ["/api/story", "/api/chat"]
        },
        "physics_quiz": {
            "available": "question_router" in globals(),
            "endpoints": ["/question/", "/question/api/"]
        }
    }

    return {
        "code": 200,
        "message": "AI对话与物理题库整合系统运行正常",
        "system": {
            "name": "AI对话与物理题库整合系统",
            "version": "2.0.0",
            "description": "基于AI的小说对话系统 + 五大物理学方向在线答题系统"
        },
        "modules": modules_status,
        "docs": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "系统信息": "/info",
            "服务健康检查": "/health",
            "物理题库主页": "/question/",
            "AI对话API": "/api/",
            "API文档": "/docs"
        },
        "server": f"http://{SERVER_HOST}:{SERVER_PORT}"
    }

@app.get("/health", summary="服务健康检查")
async def health_check():
    """
    服务健康检查接口
    用于监控服务状态和负载均衡健康检查
    """
    health_status = {
        "status": "healthy",
        "services": {}
    }

    # 检查AI对话模块
    try:
        from api import story_character
        health_status["services"]["ai_dialogue"] = "available"
    except ImportError:
        health_status["services"]["ai_dialogue"] = "unavailable"

    # 检查物理题库模块
    try:
        from api.question import router
        health_status["services"]["physics_quiz"] = "available"
    except ImportError:
        health_status["services"]["physics_quiz"] = "unavailable"

    # 检查数据库连接（如果物理题库模块存在）
    if HAS_PHYSICS_MODULE:
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            health_status["services"]["database"] = "connected"
        except Exception as e:
            health_status["services"]["database"] = f"error: {str(e)}"
            health_status["status"] = "degraded"

    return health_status

@app.get("/modules", summary="可用模块列表")
async def list_modules():
    """
    列出所有可用模块和功能
    返回：模块信息和访问路径
    """
    modules = []

    # AI对话模块
    try:
        from api import story_character
        modules.append({
            "name": "AI对话系统",
            "description": "基于AI的小说对话与记忆管理系统",
            "endpoints": [
                {"path": "/api/story", "description": "故事角色管理"},
                {"path": "/api/chat", "description": "对话与记忆管理"}
            ],
            "status": "available"
        })
    except ImportError:
        modules.append({
            "name": "AI对话系统",
            "description": "基于AI的小说对话与记忆管理系统",
            "status": "unavailable",
            "note": "模块未找到或导入失败"
        })

    # 物理题库模块
    try:
        from api.question import router
        modules.append({
            "name": "物理题库系统",
            "description": "五大物理学方向在线答题系统",
            "endpoints": [
                {"path": "/question/", "description": "物理题库主页"},
                {"path": "/question/quiz/{方向}", "description": "开始答题"},
                {"path": "/question/api/", "description": "题库API"}
            ],
            "status": "available"
        })
    except ImportError:
        modules.append({
            "name": "物理题库系统",
            "description": "五大物理学方向在线答题系统",
            "status": "unavailable",
            "note": "模块未找到或导入失败"
        })

    return {
        "code": 200,
        "modules": modules,
        "total": len([m for m in modules if m["status"] == "available"]),
        "message": f"共找到 {len(modules)} 个模块"
    }

# ==================== 第七步：启动服务 ====================
if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*50)
    print("🚀 AI对话与物理题库整合系统")
    print("="*50)
    print(f"📡 服务地址: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"📚 API文档: http://{SERVER_HOST}:{SERVER_PORT}/docs")
    print(f"📊 系统信息: http://{SERVER_HOST}:{SERVER_PORT}/info")
    print(f"❤️  健康检查: http://{SERVER_HOST}:{SERVER_PORT}/health")
    print(f"🎯 物理题库: http://{SERVER_HOST}:{SERVER_PORT}/question/")
    print("="*50)
    print("按下 Ctrl+C 停止服务")
    print("="*50 + "\n")

    # 启动服务
    uvicorn.run(
        "main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=DEBUG,  # 根据配置决定是否启用热重载
        log_level="info" if DEBUG else "warning"
    )
