"""
用户数据验证模型 - 使用Pydantic验证请求和响应数据
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# 创建用户请求
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    password_question: Optional[str] = Field(None, description="密码找回问题")
    password_answer: Optional[str] = Field(None, description="密码找回答案")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v

    @validator('password')
    def password_max_72_bytes(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('密码过长，请缩短密码或减少特殊字符/表情')
        return v

# 积分操作请求
class PointsRequest(BaseModel):
    user_id: str
    points: int = Field(1, ge=1, le=100)
    reason: Optional[str] = "答题奖励"

# 方向统计
class DirectionStat(BaseModel):
    name: str
    answered: int
    correct: int
    accuracy: float

# 近期答题记录
class RecentAnswer(BaseModel):
    question_id: int
    category: str
    question_text: str
    is_correct: bool
    time_ago: str

# 排行榜项
class LeaderboardItem(BaseModel):
    rank: int
    username: str
    total_points: int

# 用户个人信息
class UserProfile(BaseModel):
    user_id: str
    username: str
    total_points: int
    created_at: datetime
    stats: Dict[str, Any]
    recent_answers: List[RecentAnswer]
    leaderboard: List[LeaderboardItem]