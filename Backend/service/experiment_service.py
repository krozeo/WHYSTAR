from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from models.experiment import PhysicsExperiment


class ExperimentService:
    @staticmethod
    def list_titles_by_category(db: Session, category: str) -> List[str]:
        rows = (
            db.query(PhysicsExperiment.title)
            .filter(PhysicsExperiment.category == category)
            .order_by(PhysicsExperiment.id)
            .all()
        )
        return [r[0] for r in rows]

    @staticmethod
    def get_content_path_by_category_title(db: Session, category: str, title: str) -> Optional[Dict[str, Any]]:
        it = (
            db.query(PhysicsExperiment)
            .filter(
                PhysicsExperiment.category == category,
                PhysicsExperiment.title == title,
            )
            .first()
        )
        if not it:
            return None
            
        relative_path = it.content_path            
        return {
            "content_url": f"/experiments-static/{relative_path}",
            "id": it.id,
            "title": it.title,
            "category": it.category,
        }
