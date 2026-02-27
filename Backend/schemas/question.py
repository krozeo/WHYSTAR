"""
数据验证模型 - 使用Pydantic验证请求和响应数据
作用：
  1. 验证客户端发送的数据是否合法
  2. 定义API响应的数据结构
  3. 自动生成API文档
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional


# 答题请求模型
class AnswerRequest(BaseModel):
    """客户端提交答案时的请求数据结构"""

    question_id: int
    user_answer: str = Field(..., description="用户选择的答案内容")
    user_id: Optional[str] = "1"

    @validator('user_answer')
    def extract_letter(cls, v):
        """
        自动从提交内容中提取第一个字母并转为大写
        兼容：'A', 'a', 'A.', 'A: 内容', '选项A' 等格式
        """
        import re
        # 寻找第一个出现的 A-D/a-d 字母
        match = re.search(r'[A-Da-d]', v)
        if match:
            return match.group(0).upper()
        raise ValueError('无法从答案中识别出合法的选项字母 (A-D)')


# 答题响应模型
class AnswerResponse(BaseModel):
    """服务器返回答题结果的响应数据结构"""

    is_correct: bool
    correct_answer: str
    explanation: str
    next_question_id: Optional[int] = None


# 题目信息模型
class QuestionInfo(BaseModel):
    """题目信息（不含答案）"""

    question_id: int
    category: str
    question_text: str
    options: Dict[str, str]


# 开始答题响应模型
class QuizStartResponse(BaseModel):
    """开始答题的响应"""

    question: QuestionInfo
    total_count: int
    current_index: int = 1
