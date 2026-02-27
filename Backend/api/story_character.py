from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from core.deps import get_db
from models.story import NovelStory
from models.character import NovelCharacter
from config import PHYSICS_CATEGORIES  # 导入统一常量，做参数校验

router = APIRouter(prefix="/story-character", tags=["故事&角色模块"])

# 按类别查询故事（核心，AI对话获取prompt）
@router.get("/get-story", summary="按类别查询故事信息")
def get_story_by_category(
    category: str = Query(..., description=f"故事类别，仅支持：{PHYSICS_CATEGORIES}"),
    db: Session = Depends(get_db)
):
    if category not in PHYSICS_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"类别仅支持：{PHYSICS_CATEGORIES}")
    story = db.query(NovelStory).filter(NovelStory.category == category).first()
    if not story:
        raise HTTPException(status_code=404, detail="该类别故事不存在")
    return {"code": 200, "data": {
        "category": story.category,
        "story_intro": story.story_intro,
        "prompt": story.prompt,
        "story_content": story.story_content
    }}

# 按类别查询角色
@router.get("/get-character", summary="按类别查询角色信息")
def get_character_by_category(
    category: str = Query(..., description=f"故事类别，仅支持：{PHYSICS_CATEGORIES}"),
    db: Session = Depends(get_db)
):
    if category not in PHYSICS_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"类别仅支持：{PHYSICS_CATEGORIES}")
    characters = db.query(NovelCharacter).filter(NovelCharacter.category == category).all()
    if not characters:
        raise HTTPException(status_code=404, detail="该类别暂无角色")
    return {"code": 200, "data": [{
        "name": c.name,
        "character_intro": c.character_intro,
        "category": c.category
    } for c in characters]}

# 故事+角色联表查询（核心，AI对话一次性获取基础数据）
@router.get("/get-story-character", summary="按类别联表查询故事+角色信息")
def get_story_character(
    category: str = Query(..., description=f"故事类别，仅支持：{PHYSICS_CATEGORIES}"),
    db: Session = Depends(get_db)
):
    if category not in PHYSICS_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"类别仅支持：{PHYSICS_CATEGORIES}")
    # 联表查询
    results = db.query(NovelStory, NovelCharacter).join(
        NovelCharacter, NovelStory.category == NovelCharacter.category
    ).filter(NovelStory.category == category).all()
    
    if not results:
        raise HTTPException(status_code=404, detail="该类别无故事或角色信息")
    
    # 按故事类别整理所有角色（支持多个角色）
    story = results[0][0]  # 同一类别下故事唯一，取第一条的故事信息
    characters = [
        {
            "name": char.name,
            "intro": char.character_intro
        }
        for (s, char) in results  # 遍历所有结果，收集该类别的所有角色
    ]
    
    return {"code": 200, "data": {
        "category": category,
        "story": {
            "intro": story.story_intro,
            "prompt": story.prompt
        },
        "characters": characters  # 改为复数characters，返回角色列表
    }}