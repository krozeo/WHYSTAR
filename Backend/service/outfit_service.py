from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.outfit import Outfit
from models.user_outfit import UserOutfit
from models.user import User


class OutfitService:
    @staticmethod
    def list_outfits(db: Session) -> List[Dict[str, object]]:
        outfits = db.query(Outfit).order_by(Outfit.id).all()
        return [
            {
                "id": outfit.id,
                "name": outfit.name,
                "price": outfit.price,
            }
            for outfit in outfits
        ]

    @staticmethod
    def list_user_outfits(user_id: str, db: Session) -> List[Dict[str, object]]:
        rows = (
            db.query(UserOutfit, Outfit)
            .join(Outfit, UserOutfit.outfit_id == Outfit.id)
            .filter(UserOutfit.user_id == user_id)
            .order_by(Outfit.id)
            .all()
        )
        return [
            {
                "id": outfit.id,
                "name": outfit.name,
                "price": outfit.price,
                "is_equipped": user_outfit.is_equipped,
            }
            for user_outfit, outfit in rows
        ]

    @staticmethod
    def redeem_outfit(user_id: str, outfit_id: int, db: Session) -> Dict[str, object]:
        outfit = db.query(Outfit).filter(Outfit.id == outfit_id).first()
        if not outfit:
            return {"error": "物品不存在"}

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "用户不存在"}

        existing = db.query(UserOutfit).filter(
            and_(UserOutfit.user_id == user_id, UserOutfit.outfit_id == outfit_id)
        ).first()
        if existing:
            return {"error": "已兑换该物品"}

        price = outfit.price or 0
        if user.total_points < price:
            return {"error": "积分不足"}

        user.total_points -= price
        db.add(UserOutfit(user_id=user_id, outfit_id=outfit_id, is_equipped=False))
        db.commit()

        return {
            "user_id": user_id,
            "outfit_id": outfit_id,
            "remaining_points": user.total_points,
        }

    @staticmethod
    def equip_outfit(user_id: str, outfit_id: int, db: Session) -> Dict[str, object]:
        record = db.query(UserOutfit).filter(
            and_(UserOutfit.user_id == user_id, UserOutfit.outfit_id == outfit_id)
        ).first()
        if not record:
            return {"error": "未拥有该物品"}

        db.query(UserOutfit).filter(UserOutfit.user_id == user_id).update(
            {"is_equipped": False}
        )
        record.is_equipped = True
        db.commit()

        return {"user_id": user_id, "outfit_id": outfit_id}

    @staticmethod
    def get_current_outfit(user_id: str, db: Session) -> Optional[Dict[str, object]]:
        row = (
            db.query(UserOutfit, Outfit)
            .join(Outfit, UserOutfit.outfit_id == Outfit.id)
            .filter(
                and_(UserOutfit.user_id == user_id, UserOutfit.is_equipped == True)
            )
            .first()
        )
        if not row:
            return None

        user_outfit, outfit = row
        return {
            "id": outfit.id,
            "name": outfit.name,
            "price": outfit.price,
            "is_equipped": user_outfit.is_equipped,
        }
