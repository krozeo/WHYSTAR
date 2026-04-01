"""
业务逻辑层 - 处理核心业务逻辑
作用：将API层的HTTP处理与数据层的数据操作分离
与其他文件的关系：
  1. 被api/question.py调用
  2. 调用models中的类操作数据库
  3. 返回的数据会被schemas验证
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional,Dict, Any, List,Union
from service.user_service import UserService 
from models.user import User
from models.question import PhysicsQuestion
from models.user_progress import UserQuestionProgress

class QuestionService:
    """物理题库业务逻辑类"""
    
    # 5个物理学方向配置
    DIRECTIONS = {
        "acoustics": {"name": "声学", "description": "声音的产生、传播、接收和效应"},
        "thermodynamics": {"name": "热学", "description": "热力学定律、热传导、物态变化"},
        "mechanics": {"name": "力学", "description": "经典力学、运动学、动力学、静力学"},
        "electromagnetism": {"name": "电磁学", "description": "电场、磁场、电磁感应、电磁波"},
        "optics": {"name": "光学", "description": "几何光学、物理光学、光的本性"}
    }
    
    @staticmethod
    def get_directions(db: Session) -> List[Dict[str, Any]]:
        """
        获取所有物理学方向及题目数量
        参数：db - 数据库会话
        返回：方向列表，每个方向包含id、name、description、question_count
        """
        result = []
        for direction_id, info in QuestionService.DIRECTIONS.items():
            # 查询该方向的题目数量
            count = db.query(func.count(PhysicsQuestion.question_id)).filter(
                PhysicsQuestion.category == info["name"]
            ).scalar() or 0
            
            result.append({
                "id": direction_id,
                "name": info["name"],
                "description": info["description"],
                "question_count": count
            })
        
        return result
    
    @staticmethod
    def start_quiz(category: str, user_id: str, db: Session) -> Dict[str, Any]:
        """开始答题：获取该方向的第一道题"""
        questions = db.query(PhysicsQuestion).filter(
            PhysicsQuestion.category == category
        ).order_by(PhysicsQuestion.question_id).all()
        
        if not questions:
            return {"error": f"{category} 方向暂无题目"}
        
        total_count = len(questions)
        first_question = questions[0]
        
        # 处理options格式
        options = first_question.options
        
        # 如果是列表格式，转换为字典格式
        if isinstance(options, list):
            processed_options = {}
            for i, option in enumerate(options):
                # 尝试提取选项字母
                if isinstance(option, str) and len(option) > 2:
                    if '. ' in option:
                        key = option.split('. ')[0].strip()
                        value = option.split('. ')[1].strip()
                    elif ': ' in option:
                        key = option.split(': ')[0].strip()
                        value = option.split(': ')[1].strip()
                    else:
                        # 默认使用A, B, C, D作为键
                        key = chr(65 + i)
                        value = option.strip()
                    processed_options[key] = value
                else:
                    # 无法解析，使用默认处理
                    key = chr(65 + i)
                    processed_options[key] = str(option)
            options = processed_options
        
        # 确保options是字典格式
        if not isinstance(options, dict):
            options = {}
        
        # 构建题目信息
        question_info = {
            "question_id": first_question.question_id,
            "category": first_question.category,
            "question_text": first_question.question_text,
            "options": options  # 使用处理后的options
        }
        
        return {
            "question": question_info,
            "total_count": total_count,
            "current_index": 1
        }
    
    @staticmethod
    def get_question(question_id: int, db: Session) -> Union[Dict[str, Any], None]:
        """根据ID获取题目"""
        question = db.query(PhysicsQuestion).filter(
            PhysicsQuestion.question_id == question_id
        ).first()
        
        if not question:
            return None
        
        # 处理options格式
        options = question.options
        if isinstance(options, list):
            processed_options = {}
            for i, option in enumerate(options):
                if isinstance(option, str) and len(option) > 2:
                    if '. ' in option:
                        key = option.split('. ')[0].strip()
                        value = option.split('. ')[1].strip()
                    elif ': ' in option:
                        key = option.split(': ')[0].strip()
                        value = option.split(': ')[1].strip()
                    else:
                        key = chr(65 + i)
                        value = option.strip()
                    processed_options[key] = value
                else:
                    key = chr(65 + i)
                    processed_options[key] = str(option)
            options = processed_options
        
        if not isinstance(options, dict):
            options = {}
        
        return {
            "question_id": question.question_id,
            "category": question.category,
            "question_text": question.question_text,
            "options": options
        }
    
    @staticmethod
    def has_answered_question(user_id: str, question_id: int, db: Session) -> bool:
        """检查用户是否已经回答过该题目"""
        return db.query(UserQuestionProgress).filter(
            and_(
                UserQuestionProgress.user_id == user_id,
                UserQuestionProgress.question_id == question_id
            )
        ).first() is not None

    @staticmethod
    def update_answer(user_id: str, question_id: int, user_answer: str, db: Session) -> Dict[str, Any]:
        """更新已有的答题记录"""
        progress = db.query(UserQuestionProgress).filter(
            and_(
                UserQuestionProgress.user_id == user_id,
                UserQuestionProgress.question_id == question_id
            )
        ).first()
        
        question = db.query(PhysicsQuestion).filter(
            PhysicsQuestion.question_id == question_id
        ).first()
        
        if not question or not progress:
            return {"error": "记录不存在"}
            
        is_correct = user_answer.upper() == question.correct_answer.upper()
        
        # 更新进度记录
        progress.is_correct = is_correct
        db.commit()
        
        # 同步更新统计信息
        UserService.update_answer_stats(user_id, question_id, is_correct, db)
        
        # 查找下一题
        next_question = db.query(PhysicsQuestion).filter(
            and_(
                PhysicsQuestion.category == question.category,
                PhysicsQuestion.question_id > question_id
            )
        ).order_by(PhysicsQuestion.question_id).first()
        
        return {
            "is_correct": is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "next_question_id": next_question.question_id if next_question else None,
            "message": "已更新之前的回答"
        }
    
    @staticmethod
    def submit_answer(
        question_id: int, 
        user_answer: str, 
        user_id: str, 
        db: Session
    ) -> Dict[str, Any]:
        """提交答案并返回解析"""
         # 检查是否已经回答过
        if QuestionService.has_answered_question(user_id, question_id, db):
            return QuestionService.update_answer(user_id, question_id, user_answer, db)
        
        #获取题目
        question = db.query(PhysicsQuestion).filter(
            PhysicsQuestion.question_id == question_id
        ).first()
        
        if not question:
            return {"error": "题目不存在"}
        
        # 检查答案（忽略大小写）
        is_correct = user_answer.upper() == question.correct_answer.upper()

        # 记录答题进度
        progress = UserQuestionProgress(
            user_id=user_id,
            question_id=question_id,
            is_correct=is_correct,
            is_completed=True
        )
        db.add(progress)

        if is_correct:
            # 1. 增加用户积分
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.total_points += 1
                print(f"✅ 用户 {user.username} 答对题目，获得1积分，当前总积分：{user.total_points}")
            
            # 2. 更新答题统计
            UserService.update_answer_stats(user_id, question_id, True, db)
        else:
            # 答错也要更新统计
            UserService.update_answer_stats(user_id, question_id, False, db)
        # ========================
        

        db.commit()
        
        # 查找同一方向的下一个题目
        next_question = db.query(PhysicsQuestion).filter(
            and_(
                PhysicsQuestion.category == question.category,
                PhysicsQuestion.question_id > question_id
            )
        ).order_by(PhysicsQuestion.question_id).first()
        
        return {
            "is_correct": is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "next_question_id": next_question.question_id if next_question else None
        }
    
    @staticmethod
    def get_next_question(current_id: int, category: str, db: Session) -> Optional[Dict[str, Any]]:
        """
        获取当前题目的下一题
        参数：
          current_id - 当前题目ID
          category - 题目类别（中文）
          db - 数据库会话
        返回：下一题的信息，没有则返回None
        """
        # 查询同一类别中ID大于当前ID的第一道题
        next_question = db.query(PhysicsQuestion).filter(
            and_(
                PhysicsQuestion.category == category,
                PhysicsQuestion.question_id > current_id
            )
        ).order_by(PhysicsQuestion.question_id).first()
        
        if not next_question:
            return None
        
        # 处理options格式
        options = QuestionService._process_options(next_question.options)
        
        return {
            "question_id": next_question.question_id,
            "category": next_question.category,
            "question_text": next_question.question_text,
            "options": options
        }
    
    @staticmethod
    def _process_options(options_data: Any) -> Dict[str, str]:
        """
        处理options字段格式的辅助方法
        将列表格式 ["A. 内容", "B. 内容"] 转换为字典格式 {"A": "内容", "B": "内容"}
        """
        # 如果已经是字典格式，直接返回
        if isinstance(options_data, dict):
            return options_data
        
        # 如果是列表格式，转换为字典
        if isinstance(options_data, list):
            processed_options = {}
            for i, option in enumerate(options_data):
                if isinstance(option, str) and len(option) > 2:
                    # 处理 "A. 内容" 或 "A: 内容" 格式
                    if '. ' in option:
                        key = option.split('. ')[0].strip()
                        value = option.split('. ')[1].strip()
                    elif ': ' in option:
                        key = option.split(': ')[0].strip()
                        value = option.split(': ')[1].strip()
                    elif '、' in option:
                        key = option.split('、')[0].strip()
                        value = option.split('、')[1].strip()
                    else:
                        # 无法解析，使用默认处理
                        key = chr(65 + i)  # 65是'A'的ASCII码
                        value = option.strip()
                    processed_options[key] = value
                else:
                    # 非字符串或长度不足，使用默认处理
                    key = chr(65 + i)
                    processed_options[key] = str(option)
            return processed_options
        
        # 其他格式，返回空字典
        return {}
    
    @staticmethod
    def get_user_stats(user_id: int, db: Session) -> Dict[str, Any]:
        """获取用户答题统计"""
        total_answered = db.query(func.count(UserQuestionProgress.id)).filter(
            UserQuestionProgress.user_id == user_id
        ).scalar() or 0
        
        correct_answered = db.query(func.count(UserQuestionProgress.id)).filter(
            and_(
                UserQuestionProgress.user_id == user_id,
                UserQuestionProgress.is_correct == True
            )
        ).scalar() or 0
        
        accuracy = correct_answered / total_answered * 100 if total_answered > 0 else 0
        
        return {
            "total_answered": total_answered,
            "correct_answered": correct_answered,
            "accuracy": round(accuracy, 1)
        }