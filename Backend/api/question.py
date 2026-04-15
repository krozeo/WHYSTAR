"""
API接口层 - 处理HTTP请求和响应
作用：
  1. 定义API路由（URL路径）
  2. 接收HTTP请求
  3. 调用业务逻辑层处理
  4. 返回HTTP响应
与其他文件的关系：
  1. 被main.py导入并注册
  2. 调用service层处理业务
  3. 使用schemas验证数据
  4. 使用templates渲染HTML页面
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from core.deps import get_current_user, get_db  # 导入认证和数据库依赖
from models.user import User # 导入用户模型
from service.question_service import QuestionService  # 导入业务逻辑
from schemas.question import AnswerRequest, AnswerResponse, QuizStartResponse  # 导入数据验证模型

# 创建路由器 - 管理所有/question开头的路由
# AI辅助生成：Deepseek-v3.2（网页端，1月）
router = APIRouter(prefix="/question", tags=["物理题库模块"])

# 配置模板引擎 - 用于渲染HTML页面
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request, db: Session = Depends(get_db)):
    # 检查登录状态（首页 /info 不需要登录，但题库页面需要）
    from core.deps import get_current_user_page
    from fastapi.responses import RedirectResponse
    from fastapi import HTTPException

    try:
        _ = get_current_user_page(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login", status_code=302)
    """
    主页：显示5个物理学方向供选择
    请求方式：GET
    访问地址：http://localhost:8000/question/
    参数：request - FastAPI的请求对象，db - 数据库会话
    返回：HTML页面
    """
    directions = QuestionService.get_directions(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "directions": directions
    })

@router.get("/quiz/{category_id}", response_class=HTMLResponse)
async def quiz_page(request: Request, category_id: str, db: Session = Depends(get_db)):
    # 检查登录状态
    from core.deps import get_current_user_page
    from fastapi.responses import RedirectResponse
    from fastapi import HTTPException

    try:
        _ = get_current_user_page(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login", status_code=302)
    """
    答题页面：显示题目和答题界面
    请求方式：GET
    访问地址：http://localhost:8000/question/quiz/{方向ID}
    参数：category_id - 方向ID
    返回：HTML页面
    """
    # 方向ID到中文名称的映射
    direction_map = {
        "acoustics": "声学",
        "thermodynamics": "热学", 
        "mechanics": "力学",
        "electromagnetism": "电磁学",
        "optics": "光学"
    }
    display_category = direction_map.get(category_id, category_id)
    return templates.TemplateResponse("quiz.html", {
        "request": request,
        "category": display_category,
        "category_id": category_id
    })

@router.get("/api/directions")
async def get_directions(db: Session = Depends(get_db)):
    """
    获取所有物理学方向（API接口）
    请求方式：GET
    访问地址：http://localhost:8000/question/api/directions
    返回：JSON格式的方向列表
    """
    directions = QuestionService.get_directions(db)
    return {"success": True, "data": directions, "message": "获取方向成功"}

@router.get("/api/start/{category_id}", response_model=QuizStartResponse)
async def start_quiz(
    category_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    开始答题
    """
    direction_map = {
        "acoustics": "声学",
        "thermodynamics": "热学",
        "mechanics": "力学",
        "electromagnetism": "电磁学",
        "optics": "光学"
    }
    chinese_category = direction_map.get(category_id, category_id)
    result = QuestionService.start_quiz(chinese_category, str(current_user.id), db)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@router.get("/api/question/{question_id}")
async def get_question(question_id: int, db: Session = Depends(get_db)):
    """获取题目信息"""
    question = QuestionService.get_question(question_id, db)
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return {"success": True, "data": question, "message": "获取题目成功"}

@router.post("/api/submit", response_model=AnswerResponse)
async def submit_answer(
    data: AnswerRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """提交答案"""
    result = QuestionService.submit_answer(data.question_id, data.user_answer, str(current_user.id), db)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/api/next/{current_id}/{category_id}")
async def get_next_question(current_id: int, category_id: str, db: Session = Depends(get_db)):
    """获取下一题"""
    direction_map = {
        "acoustics": "声学",
        "thermodynamics": "热学",
        "mechanics": "力学",
        "electromagnetism": "电磁学",
        "optics": "光学"
    }
    chinese_category = direction_map.get(category_id, category_id)
    next_question = QuestionService.get_next_question(current_id, chinese_category, db)
    
    if not next_question:
        return {"success": True, "data": None, "message": "已是最后一题"}
    
    return {"success": True, "data": next_question, "message": "获取下一题成功"}