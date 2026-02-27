"""
用户业务逻辑层 - 处理所有用户相关的业务
作用：用户积分管理、统计计算、个人信息查询
与其他文件的关系：
  1. 被api/user.py调用
  2. 调用models中的User和UserStats类
  3. 被question_service.py调用（答题时更新积分）
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime, timedelta

from models.user import User
from models.user_stats import UserStats
from models.user_progress import UserQuestionProgress
from models.question import PhysicsQuestion

class UserService:
    
    # 方向名称映射（用于统计）
    DIRECTION_MAP = {
        "声学": "acoustics",
        "热学": "thermodynamics",
        "力学": "mechanics",
        "电磁学": "electromagnetism",
        "光学": "optics"
    }
    
    @staticmethod
    def create_user(
        username: str,
        password: str,
        password_question: Optional[str],
        password_answer: Optional[str],
        db: Session,
    ) -> Dict[str, Any]:
        """
        创建新用户
        流程：
          1. 检查用户名是否已存在
          2. 生成UUID
          3. 密码加密（实际应用中应该使用bcrypt等加密）
          4. 创建用户记录
          5. 创建对应的统计记录
        """
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return {"error": "用户名已存在"}
        
        # 生成UUID
        user_id = str(uuid.uuid4())

        if not password_question or not password_answer:
            return {"error": "密保问题和答案不能为空"}

        try:
            hashed_password = User.get_password_hash(password)
        except ValueError:
            return {"error": "密码处理失败。请重启服务后重试；若仍失败请检查密码哈希依赖环境"}

        # 创建用户
        new_user = User(
            id=user_id,
            username=username,
            password=hashed_password,
            password_question=password_question,
            password_answer=password_answer,
            total_points=0
        )
        db.add(new_user)
        
        # 创建对应的统计记录
        new_stats = UserStats(
            user_id=user_id
        )
        db.add(new_stats)
        
        db.commit()
        db.refresh(new_user)
        
        return {
            "user_id": user_id,
            "username": username,
            "total_points": 0,
            "message": "用户创建成功"
        }
    
    @staticmethod
    def add_points(user_id: str, db: Session, points: int = 1) -> Dict[str, Any]:
        """
        给用户增加积分
        调用时机：用户答对题目时调用
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "用户不存在"}
        
        # 增加积分
        user.total_points += points
        db.commit()
        db.refresh(user)
        
        return {
            "user_id": user_id,
            "username": user.username,
            "total_points": user.total_points,
            "added_points": points,
            "message": f"积分增加{points}分"
        }
    
    @staticmethod
    def deduct_points(user_id: str, points: int, db: Session) -> Dict[str, Any]:
        """
        扣除用户积分
        调用时机：用户兑换物品时调用
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "用户不存在"}
        
        if user.total_points < points:
            return {"error": f"积分不足，当前积分：{user.total_points}，需要：{points}"}
        
        # 扣除积分
        user.total_points -= points
        db.commit()
        db.refresh(user)
        
        return {
            "user_id": user_id,
            "username": user.username,
            "total_points": user.total_points,
            "deducted_points": points,
            "message": f"积分扣除{points}分"
        }
    
    @staticmethod
    def get_user_profile(user_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """
        获取用户个人信息
        包含：基本信息、积分、答题统计、各方向正确率
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # 获取统计信息
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        
        # 如果没有统计记录，创建一个
        if not stats:
            stats = UserStats(user_id=user_id)
            db.add(stats)
            db.commit()
            db.refresh(stats)
        
        # 计算总体正确率
        overall_accuracy = 0
        if stats.total_answered > 0:
            overall_accuracy = round(stats.total_correct / stats.total_answered * 100, 1)
        
        # 计算各方向正确率
        direction_stats = {}
        for ch_name, en_name in UserService.DIRECTION_MAP.items():
            answered = getattr(stats, f"{en_name}_answered", 0)
            correct = getattr(stats, f"{en_name}_correct", 0)
            accuracy = round(correct / answered * 100, 1) if answered > 0 else 0
            
            direction_stats[en_name] = {
                "name": ch_name,
                "answered": answered,
                "correct": correct,
                "accuracy": accuracy
            }
        
        # 获取最近的答题记录
        recent_answers = db.query(
            UserQuestionProgress,
            PhysicsQuestion.category,
            PhysicsQuestion.question_text
        ).join(
            PhysicsQuestion, 
            UserQuestionProgress.question_id == PhysicsQuestion.question_id
        ).filter(
            UserQuestionProgress.user_id == user_id
        ).order_by(
            UserQuestionProgress.last_updated.desc()
        ).limit(10).all()
        
        recent_list = []
        for progress, category, question_text in recent_answers:
            # 截取题目文本
            short_text = question_text[:30] + "..." if len(question_text) > 30 else question_text
            
            # 计算时间差
            time_ago = UserService._time_ago(progress.last_updated)
            
            recent_list.append({
                "question_id": progress.question_id,
                "category": category,
                "question_text": short_text,
                "is_correct": progress.is_correct,
                "time_ago": time_ago
            })
        
        # 获取当前排名（口径与排行榜一致：按 total_correct 降序，其次 total_points 降序）
        rows = (
            db.query(User.id)
            .join(UserStats, UserStats.user_id == User.id)
            .order_by(UserStats.total_correct.desc(), User.total_points.desc())
            .all()
        )
        rank = 0
        for i, (uid,) in enumerate(rows, 1):
            if str(uid) == str(user_id):
                rank = i
                break

        return {
            "user_id": str(user.id),
            "username": user.username,
            "total_points": user.total_points,
            "rank": rank
        }
    
    @staticmethod
    def update_answer_stats(user_id: str, question_id: int, is_correct: bool, db: Session):
        """
        更新用户答题统计
        调用时机：用户提交答案后自动调用
        这是积分系统的核心方法
        """
        # 获取题目信息
        question = db.query(PhysicsQuestion).filter(
            PhysicsQuestion.question_id == question_id
        ).first()
        
        if not question:
            return
        
        # 获取用户统计记录
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if not stats:
            stats = UserStats(user_id=user_id)
            db.add(stats)
            db.flush()
        
        # 更新总体统计
        stats.total_answered += 1
        if is_correct:
            stats.total_correct += 1
        
        # 更新对应方向的统计
        direction = question.category
        en_direction = UserService.DIRECTION_MAP.get(direction)
        
        if en_direction:
            # 更新答题数
            answered_field = f"{en_direction}_answered"
            setattr(stats, answered_field, getattr(stats, answered_field) + 1)
            
            # 更新正确数
            if is_correct:
                correct_field = f"{en_direction}_correct"
                setattr(stats, correct_field, getattr(stats, correct_field) + 1)
        
        db.commit()
    
    @staticmethod
    def _time_ago(dt) -> str:
        """计算时间间隔的友好显示"""
        from datetime import datetime, timezone
        if not dt:
            return "未知时间"
        
        now = datetime.now(timezone.utc)
        diff = now - dt
        
        if diff.days > 365:
            return f"{diff.days // 365}年前"
        elif diff.days > 30:
            return f"{diff.days // 30}个月前"
        elif diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}小时前"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}分钟前"
        else:
            return "刚刚"
    
    @staticmethod
    def get_leaderboard(db: Session, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取排行榜
        口径：按答对题目数量（total_correct）降序排序
        """
        rows = (
            db.query(User, UserStats)
            .join(UserStats, UserStats.user_id == User.id)
            .order_by(UserStats.total_correct.desc(), User.total_points.desc())
            .limit(limit)
            .all()
        )
        
        result = []
        for rank, (user, stats) in enumerate(rows, 1):
            result.append({
                "rank": rank,
                "username": user.username,
                "total_correct": stats.total_correct,
                "total_answered": stats.total_answered,
                "total_points": user.total_points
            })
        
        return result