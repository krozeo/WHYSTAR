from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

# 注册请求
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    password_confirm: str = Field(..., description="确认密码")
    password_question: str = Field(..., description="密保问题")
    password_answer: str = Field(..., description="密保答案")

# 登录请求
class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

# 获取密保问题请求
class PasswordQuestionRequest(BaseModel):
    username: str = Field(..., description="用户名")

# 修改密码请求
class ChangePassword(BaseModel):
    password_answer: str = Field(..., description="密保答案")
    new_password: str = Field(..., min_length=6, description="新密码")

# 修改用户名请求
class ChangeUsername(BaseModel):
    new_username: str = Field(..., min_length=3, max_length=50, description="新用户名")

# Token响应
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
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
