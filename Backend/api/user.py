"""
用户API接口层 - 处理用户相关的HTTP请求
作用：
  1. 定义用户相关路由
  2. 接收HTTP请求
  3. 调用UserService处理业务
  4. 返回JSON或HTML响应
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from db import get_db
from service.user_service import UserService
from schemas.user import UserCreate, UserProfile, PointsRequest, LeaderboardItem
from models.user import User
from core.deps import get_current_user_page

router = APIRouter(prefix="/user", tags=["用户中心"])
templates = Jinja2Templates(directory="templates")

# ========== 页面路由 ==========

@router.get("/profile/{user_id}", response_class=HTMLResponse)
async def profile_page(request: Request, user_id: str, db: Session = Depends(get_db)):
    """
    个人信息页面
    访问地址：http://localhost:8000/user/profile/{user_id}
    """
    # 检查登录状态
    try:
        current_user = get_current_user_page(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login", status_code=302)

    profile = UserService.get_user_profile(user_id, db)
    if not profile:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "用户不存在"
        })
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile": profile
    })

@router.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard_page(request: Request, db: Session = Depends(get_db)):
    # 检查登录状态
    try:
        current_user = get_current_user_page(request, db)
    except HTTPException:
        return RedirectResponse(url="/auth/login", status_code=302)
    """
    积分排行榜页面
    访问地址：http://localhost:8000/user/leaderboard
    """
    leaderboard = UserService.get_leaderboard(db, limit=50)
    return templates.TemplateResponse("leaderboard.html", {
        "request": request,
        "leaderboard": leaderboard
    })

# ========== API接口 ==========

@router.post("/api/create")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    result = UserService.create_user(
        username=user_data.username,
        password=user_data.password,
        password_question=user_data.password_question,
        password_answer=user_data.password_answer,
        db=db,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "data": result}

@router.get("/api/profile/{user_id}")
async def get_profile(user_id: str, db: Session = Depends(get_db)):
    """获取用户个人信息（JSON格式）"""
    profile = UserService.get_user_profile(user_id, db)
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"success": True, "data": profile}

@router.post("/api/points/add")
async def add_points(
    user_id: str = Query(...),
    points: int = Query(1, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    增加用户积分
    主要用于管理员操作或特殊奖励
    """
    result = UserService.add_points(user_id, db, points)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {"success": True, "data": result}

@router.post("/api/points/deduct")
async def deduct_points(
    user_id: str = Query(...),
    points: int = Query(..., ge=1),
    reason: str = Query("兑换物品"),
    db: Session = Depends(get_db)
):
    """
    扣除用户积分
    用于兑换物品
    """
    result = UserService.deduct_points(user_id, points, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # 这里可以添加兑换记录日志
    return {
        "success": True, 
        "data": {
            **result,
            "reason": reason
        }
    }

@router.get("/api/leaderboard")
async def get_leaderboard(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取积分排行榜"""
    leaderboard = UserService.get_leaderboard(db, limit)
    return {"success": True, "data": leaderboard}

@router.get("/api/points/{user_id}")
async def get_points(user_id: str, db: Session = Depends(get_db)):
    """查询用户当前积分"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "success": True,
        "data": {
            "user_id": user.id,
            "username": user.username,
            "total_points": user.total_points
        }
    }