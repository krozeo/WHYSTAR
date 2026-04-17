# api/chat_memory.py - 最终正确版：用flag_modified标记JSONB变更，解决500错误
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
# 导入SQLAlchemy官方标记工具（专门用于JSON/JSONB字段）
from sqlalchemy.orm.attributes import flag_modified
from typing import Optional
from core.deps import get_db
from core.ai_api import call_ai, call_coze, call_zhipu_assistant, stream_zhipu_assistant, clean_text
from models.chat import UserStoryChat
from models.story import NovelStory
from config import PHYSICS_CATEGORIES, BAIDU_TTS_ACCESS_TOKEN, BAIDU_API_KEY, BAIDU_SECRET_KEY
import json
import requests
import time

_BAIDU_TOKEN_CACHE = {"token": None, "expires_at": 0}

def get_baidu_access_token() -> str:
    if BAIDU_TTS_ACCESS_TOKEN:
        return BAIDU_TTS_ACCESS_TOKEN

    if not BAIDU_API_KEY or not BAIDU_SECRET_KEY:
        raise Exception("缺少百度语音合成配置，请填写 BAIDU_TTS_ACCESS_TOKEN 或 BAIDU_API_KEY/BAIDU_SECRET_KEY")

    now = time.time()
    if _BAIDU_TOKEN_CACHE["token"] and _BAIDU_TOKEN_CACHE["expires_at"] > now:
        return _BAIDU_TOKEN_CACHE["token"]

    token_res = requests.post(
        "https://aip.baidubce.com/oauth/2.0/token",
        data={
            "grant_type": "client_credentials",
            "client_id": BAIDU_API_KEY,
            "client_secret": BAIDU_SECRET_KEY
        },
        timeout=15
    )
    token_data = token_res.json()
    access_token = token_data.get("access_token")
    if token_res.status_code != 200 or not access_token:
        err_msg = token_data.get("error_description") or token_data.get("error") or "获取百度Access Token失败"
        raise Exception(err_msg)

    expires_in = int(token_data.get("expires_in", 0))
    _BAIDU_TOKEN_CACHE["token"] = access_token
    _BAIDU_TOKEN_CACHE["expires_at"] = now + max(0, expires_in - 60)
    return access_token

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

# -------------------------- 2. 追加对话--------------------------
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
    
    # 保存原始记忆
    original_memory = chat_record.chat_memory.copy()
    
    try:
        # 1. 追加用户消息
        chat_record.chat_memory.append({"role": "user", "content": clean_input})
        flag_modified(chat_record, 'chat_memory')
        
        # 2. 调用AI
        ai_reply = call_ai(chat_memory=chat_record.chat_memory)
        
        # 3. 追加AI回复
        chat_record.chat_memory.append({"role": "assistant", "content": ai_reply})
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

@router.post("/coze-chat", summary="Coze智能体对话")
def coze_chat(
    user_id: str = Body(..., description="用户ID"),
    message: str = Body(..., description="用户消息"),
    conversation_id: Optional[str] = Body(None, description="会话ID（可选）")
):
    clean_input = clean_text(message)
    if not clean_input:
        raise HTTPException(status_code=400, detail="用户消息不可为空～")

    try:
        result = call_coze(
            user_id=str(user_id),
            message=clean_input,
            conversation_id=conversation_id
        )
        return {"code": 200, "data": result}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Coze调用失败：{str(e)}")

@router.post("/zhipu-chat", summary="智谱AI智能体对话")
def zhipu_chat(
    request: Request,
    user_id: str = Body(..., description="用户ID"),
    message: str = Body(..., description="用户消息"),
    conversation_id: Optional[str] = Body(None, description="会话ID（可选）"),
    stream: bool = Body(False, description="是否启用流式输出（SSE）"),
    history: Optional[list] = Body(None, description="对话历史（可选，用于fallback到chat/completions）")
):
    clean_input = clean_text(message)
    if not clean_input:
        raise HTTPException(status_code=400, detail="用户消息不可为空～")

    try:
        accept = request.headers.get("accept", "")
        use_stream = stream or ("text/event-stream" in accept)
        if use_stream:
            def event_generator():
                for event in stream_zhipu_assistant(
                    user_id=str(user_id),
                    message=clean_input,
                    conversation_id=conversation_id,
                    history=history
                ):
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )

        result = call_zhipu_assistant(user_id=str(user_id), message=clean_input, conversation_id=conversation_id)
        return {"code": 200, "data": result}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"智谱AI调用失败：{str(e)}")

@router.post("/tts", summary="百度语音合成（返回音频流）")
def tts_synthesize(
    text: str = Body(..., description="要朗读的文本"),
    user_id: Optional[str] = Body(None, description="用户ID（可选）")
):
    clean_input = clean_text(text)
    if not clean_input:
        raise HTTPException(status_code=400, detail="朗读文本不可为空～")

    try:
        token = get_baidu_access_token()
        cuid = f"whyplanet-{user_id}" if user_id else "whyplanet-server"
        tts_res = requests.get(
            "https://tsn.baidu.com/text2audio",
            params={
                "tex": clean_input,
                "tok": token,
                "cuid": cuid,
                "ctp": 1,
                "lan": "zh",
                "per": 6205,
                "aue": 3
            },
            timeout=30
        )

        content_type = (tts_res.headers.get("content-type") or "").lower()
        if content_type.startswith("audio/"):
            return StreamingResponse(iter([tts_res.content]), media_type=content_type or "audio/mp3")

        err_msg = "语音合成失败"
        try:
            err_json = tts_res.json()
            err_msg = err_json.get("err_msg") or err_json.get("error_description") or err_msg
        except Exception:
            if tts_res.text:
                err_msg = tts_res.text
        raise HTTPException(status_code=503, detail=err_msg)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"语音合成失败：{str(e)}")

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
