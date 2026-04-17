from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import config
from core.deps import create_access_token, get_current_user, get_db
from models.user import User
from schemas.auth import (
    ChangePassword,
    ChangeUsername,
    PasswordQuestionResponse,
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["用户认证（登录/注册/改密码/改用户名）"])
templates = Jinja2Templates(directory="templates")

# AI辅助生成整体框架：Doubao-Seed-1.8, 2026-2-12
# -------------------------- 页面路由 --------------------------
@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    """渲染登录页面"""
    return templates.TemplateResponse("login.html", {"request": request})

# -------------------------- 1. 注册接口 --------------------------
@router.post("/register", response_model=UserResponse, summary="用户注册")
def register(user: UserRegister, db: Session = Depends(get_db)):
    # 1. 校验用户名是否重复
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )
    # 2. 校验两次密码是否一致
    if user.password != user.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="两次输入的密码不一致"
        )
    # 3. 哈希密码+创建用户
    hashed_password = User.get_password_hash(user.password)
    new_user = User(
        username=user.username,
        password=hashed_password,
        password_question=user.password_question,
        password_answer=user.password_answer
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# -------------------------- 2. 登录接口 --------------------------
@router.post("/login", response_model=Token, summary="用户登录（返回JWT Token）")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    # 1. 查询用户
    db_user = db.query(User).filter(User.username == user.username).first()
    # 2. 校验用户名/密码
    if not db_user or not db_user.verify_password_and_migrate(user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    db.commit()

    # 3. 生成Token
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, 
        expires_delta=access_token_expires
    )
    # 4. 写入 Cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=int(access_token_expires.total_seconds()),
    )

    # 5. 返回Token+过期时间
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": datetime.utcnow() + access_token_expires,
        "id": db_user.id
    }

# -------------------------- 3. 获取密保问题 --------------------------
@router.get("/password-question", response_model=PasswordQuestionResponse, summary="获取密保问题（改密码前调用）")
def get_password_question(username: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return {"username": username, "password_question": db_user.password_question}

# -------------------------- 4. 修改密码 --------------------------
@router.post("/change-password", response_model=UserResponse, summary="修改密码（需登录）")
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 校验密保答案
    if current_user.password_answer != data.password_answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密保答案错误"
        )
    # 2. 哈希新密码并更新
    current_user.password = User.get_password_hash(data.new_password)
    db.commit()
    db.refresh(current_user)
    return current_user

# -------------------------- 5. 修改用户名 --------------------------
@router.post("/change-username", response_model=UserResponse, summary="修改用户名（需登录）")
def change_username(
    data: ChangeUsername,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 校验新用户名是否被其他用户占用
    existing_user = db.query(User).filter(
        User.username == data.new_username,
        User.username != current_user.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新用户名已被占用"
        )
    # 2. 更新用户名
    current_user.username = data.new_username
    db.commit()
    db.refresh(current_user)
    return current_user
