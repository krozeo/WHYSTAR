# api/chat_memory.py - 最终正确版：用flag_modified标记JSONB变更，解决500错误
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
# 导入SQLAlchemy官方标记工具（专门用于JSON/JSONB字段）
from sqlalchemy.orm.attributes import flag_modified
from core.deps import get_db
from core.ai_api import call_ai, clean_text
from models.chat import UserStoryChat
from models.story import NovelStory
from config import PHYSICS_CATEGORIES

router = APIRouter(prefix="/chat-memory", tags=["对话记忆核心模块（最终正确版）"])

# -------------------------- 初始化基础记忆 --------------------------
def init_base_memory(db: Session, user_id: int, category: str) -> UserStoryChat:
    story = db.query(NovelStory).filter(NovelStory.category == category).first()
    if not story:
        raise HTTPException(status_code=404, detail=f"【{category}】类别无故事信息～")
    if not story.prompt or not story.story_content:
        raise HTTPException(status_code=400, detail=f"【{category}】类别故事的提示词/剧情为空～")
    
    base_memory = [
        {"role": "system", "content": story.prompt},
        {"role": "user", "content": story.story_content}
    ]
    
    chat_record = db.query(UserStoryChat).filter(
        UserStoryChat.user_id == user_id,
        UserStoryChat.category == category
    ).first()
    if not chat_record:
        chat_record = UserStoryChat(user_id=user_id, category=category, chat_memory=base_memory)
        db.add(chat_record)
    else:
        chat_record.chat_memory = base_memory
        # 标记字段变更
        flag_modified(chat_record, 'chat_memory')
    
    db.commit()
    db.refresh(chat_record)
    return chat_record

# -------------------------- 1. 查询对话记忆 --------------------------
@router.get("/get", summary="查询完整记忆")
def get_chat_memory(
    user_id: str = Query(..., description="用户ID（UUID字符串）"),
    category: str = Query(..., description=f"故事类别：{PHYSICS_CATEGORIES}"),
    db: Session = Depends(get_db)
):
    if category not in PHYSICS_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"类别仅支持：{PHYSICS_CATEGORIES}")
    
    chat_record = db.query(UserStoryChat).filter(
        UserStoryChat.user_id == user_id,
        UserStoryChat.category == category
    ).first()
    if not chat_record:
        raise HTTPException(status_code=404, detail="暂无记忆，请先调用/restart～")
    
    display_chat = chat_record.chat_memory[2:] if len(chat_record.chat_memory) > 2 else []
    return {"code": 200, "data": {
        "chat_memory": chat_record.chat_memory,
        "display_chat": display_chat,
        "memory_length": len(chat_record.chat_memory)
    }}

# -------------------------- 2. 追加对话（核心：flag_modified标记JSONB变更）--------------------------
@router.post("/append", summary="用户选择→AI推进（无500错误）")
def append_chat_memory(
    user_id: str = Body(..., description="用户ID（UUID字符串）"),
    category: str = Body(..., description=f"故事类别：{PHYSICS_CATEGORIES}"),
    user_msg: str = Body(..., description="用户选择（如“选A”）"),
    db: Session = Depends(get_db)
):
    # 基础校验
    if category not in PHYSICS_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"类别仅支持：{PHYSICS_CATEGORIES}")
    clean_input = clean_text(user_msg)
    if not clean_input:
        raise HTTPException(status_code=400, detail="用户选择不可为空～")
    
    # 查记忆
    chat_record = db.query(UserStoryChat).filter(
        UserStoryChat.user_id == user_id,
        UserStoryChat.category == category
    ).first()
    if not chat_record:
        raise HTTPException(status_code=404, detail="暂无记忆，请先调用/restart～")
    
    # 保存原始记忆（回滚用）
    original_memory = chat_record.chat_memory.copy()
    
    try:
        # 1. 追加用户消息
        chat_record.chat_memory.append({"role": "user", "content": clean_input})
        # 🔴 正确标记：告诉SQLAlchemy chat_memory字段已修改
        flag_modified(chat_record, 'chat_memory')
        
        # 2. 调用AI
        ai_reply = call_ai(chat_memory=chat_record.chat_memory)
        
        # 3. 追加AI回复
        chat_record.chat_memory.append({"role": "assistant", "content": ai_reply})
        # 🔴 再次标记
        flag_modified(chat_record, 'chat_memory')
        
        # 4. 提交更新（此时数据库会真正保存）
        db.commit()
        db.refresh(chat_record)
    except Exception as e:
        # 出错回滚
        chat_record.chat_memory = original_memory
        flag_modified(chat_record, 'chat_memory')
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail=f"处理失败：{str(e)}，记忆已回滚～"
        )
    
    display_chat = chat_record.chat_memory[2:]
    return {"code": 200, "data": {
        "user_input": clean_input,
        "ai_reply": ai_reply,
        "chat_memory": chat_record.chat_memory,
        "display_chat": display_chat,
        "memory_length": len(chat_record.chat_memory)
    }}

# -------------------------- 3. 重新开始 --------------------------
@router.post("/restart", summary="重新生成场景1")
def restart_chat_memory(
    user_id: str = Body(..., description="用户ID（UUID字符串）"),
    category: str = Body(..., description=f"故事类别：{PHYSICS_CATEGORIES}"),
    db: Session = Depends(get_db)
):
    if category not in PHYSICS_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"类别仅支持：{PHYSICS_CATEGORIES}")
    
    # 初始化基础记忆
    chat_record = init_base_memory(db, user_id, category)
    
    try:
        # 调用AI生成场景1
        ai_scene1 = call_ai(chat_memory=chat_record.chat_memory)
        # 追加场景1
        chat_record.chat_memory.append({"role": "assistant", "content": ai_scene1})
        # 标记变更
        flag_modified(chat_record, 'chat_memory')
        db.commit()
        db.refresh(chat_record)
    except Exception as e:
        # 出错删除基础记忆
        db.delete(chat_record)
        db.commit()
        raise HTTPException(
            status_code=503,
            detail=f"AI调用失败：{str(e)}，已清除基础记忆～"
        )
    
    display_chat = chat_record.chat_memory[2:]
    return {"code": 200, "msg": "场景1生成成功", "data": {
        "ai_scene1": ai_scene1,
        "chat_memory": chat_record.chat_memory,
        "display_chat": display_chat,
        "memory_length": len(chat_record.chat_memory)
    }}

# -------------------------- 4. 清除单类别记忆 --------------------------
@router.put("/clear", summary="清除类别记忆")
def clear_chat_memory(
    user_id: int = Query(..., description="用户ID"),
    category: str = Query(..., description=f"故事类别：{PHYSICS_CATEGORIES}"),
    db: Session = Depends(get_db)
):
    if category not in PHYSICS_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"类别仅支持：{PHYSICS_CATEGORIES}")
    
    chat_record = db.query(UserStoryChat).filter(
        UserStoryChat.user_id == user_id,
        UserStoryChat.category == category
    ).first()
    if not chat_record:
        raise HTTPException(status_code=404, detail="暂无记忆～")
    
    db.delete(chat_record)
    db.commit()
    return {"code": 200, "msg": "记忆已清除～", "data": {
        "chat_memory": [],
        "memory_length": 0
    }}

# -------------------------- 5. 清除所有记忆 --------------------------
@router.put("/clear-all", summary="清除所有记忆")
def clear_all_chat_memory(
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    memories = db.query(UserStoryChat).filter(UserStoryChat.user_id == user_id).all()
    if not memories:
        raise HTTPException(status_code=404, detail="暂无记忆～")
    
    for m in memories:
        db.delete(m)
    db.commit()
    return {"code": 200, "msg": "所有记忆已清除～", "data": {"memory_count": len(memories)}}