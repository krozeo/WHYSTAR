from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

# -------------------------- 请求模型 --------------------------
# 注册请求
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    password_confirm: str = Field(..., description="确认密码")
    password_question: str = Field(..., description="密保问题")
    password_answer: str = Field(..., description="密保答案")

# 登录请求（适配OAuth2）
class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

# 获取密保问题请求（无需登录）
class PasswordQuestionRequest(BaseModel):
    username: str = Field(..., description="用户名")

# 修改密码请求（需要登录）
class ChangePassword(BaseModel):
    password_answer: str = Field(..., description="密保答案")
    new_password: str = Field(..., min_length=6, description="新密码")

# 修改用户名请求（需要登录）
class ChangeUsername(BaseModel):
    new_username: str = Field(..., min_length=3, max_length=50, description="新用户名")

# -------------------------- 响应模型 --------------------------
# Token响应
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime  # Token过期时间
    id: UUID

# 用户信息响应
class UserResponse(BaseModel):
    id: UUID
    username: str
    total_points: int

    class Config:
        from_attributes = True

# 密保问题响应
class PasswordQuestionResponse(BaseModel):
    username: str
    password_question: str
