import requests
import re
import json
import uuid
from config import (
    AI_API_TOKEN,
    AI_MODEL,
    COZE_API_BASE,
    COZE_API_TOKEN,
    COZE_BOT_ID,
    ZHIPU_API_BASE,
    ZHIPU_API_KEY,
    ZHIPU_ASSISTANT_ID,
    ZHIPU_ASSISTANT_MODEL,
    ZHIPU_CHAT_MODEL,
)

VOLC_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
COZE_CHAT_URL = f"{COZE_API_BASE.rstrip('/')}/v3/chat"

# AI辅助生成整体框架：Doubao-Seed-1.8, 2026-1-31
def clean_text(text):
    return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)

def call_ai(chat_memory: list) -> str:
    """
    调用火山豆包模型
    :param chat_memory: 对话记忆列表
    :return: 豆包模型清洗后的回复内容
    :raise Exception: 配置错误/接口调用/解析失败时主动抛异常，供上层事务捕获
    """
    # 1. 配置校验
    if not AI_API_TOKEN or not AI_MODEL:
        raise Exception("AI配置未完善，请在.env中填写有效的AI_API_TOKEN和AI_MODEL")

    # 2. 清洗记忆中的所有内容
    cleaned_memory = []
    for msg in chat_memory:
        cleaned_memory.append({
            "role": msg["role"],
            "content": clean_text(msg["content"])
        })

    # 3. 构造火山豆包请求体
    req_data = {
        "model": AI_MODEL,
        "messages": cleaned_memory,
        "temperature": 0.7
    }

    # 4. 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_TOKEN}"
    }

    res = None 
    try:
        # 5. 调用火山接口
        response = requests.post(VOLC_API_URL, headers=headers, json=req_data, timeout=30)
        res = response.json() 

        # 校验火山API返回状态码
        if response.status_code != 200:
            error_msg = res.get("error", {}).get("message", f"服务端错误，状态码：{response.status_code}")
            raise Exception(f"火山API返回错误：{error_msg}")

        # 6. 解析返回结果
        ai_answer = res["choices"][0]["message"]["content"]
        clean_answer = clean_text(ai_answer)
        return clean_answer

    except requests.exceptions.ConnectionError as e:
        # 捕获网络连接错误
        raise Exception(f"网络连接失败：{str(e)}，请检查API地址和服务器网络")
    except requests.exceptions.Timeout as e:
        # 捕获请求超时错误
        raise Exception(f"接口请求超时：{str(e)}，请稍后重试")
    except KeyError as e:
        # 捕获返回格式错误
        raise Exception(f"AI返回格式解析失败：缺失{str(e)}字段，原始返回：{res if res else '无数据'}")
    except Exception as e:
        # 捕获其他所有错误
        error_info = str(e)
        volc_raw = res if res else "接口无返回数据"
        print(f"火山豆包调用失败：{error_info} | 火山原始返回：{volc_raw}")
        raise Exception(f"AI调用失败：{error_info[:60]}，请检查配置或稍后再试")
    
def call_coze(user_id: str, message: str, conversation_id: str | None = None) -> dict:
    if not COZE_API_TOKEN or not COZE_BOT_ID:
        raise Exception("Coze配置未完善，请在.env中填写COZE_API_TOKEN和COZE_BOT_ID")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {COZE_API_TOKEN}"
    }

    payload = {
        "bot_id": COZE_BOT_ID,
        "user_id": user_id,
        "stream": True,
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": message,
                "content_type": "text"
            }
        ]
    }

    params = {}
    if conversation_id:
        params["conversation_id"] = conversation_id

    try:
        response = requests.post(
            COZE_CHAT_URL,
            headers=headers,
            params=params,
            json=payload,
            stream=True,
            timeout=60
        )
        
        if response.status_code != 200:
             raise Exception(f"Coze接口错误：{response.status_code} {response.text}")
    except Exception as e:
         raise Exception(f"请求Coze失败: {str(e)}")

    answer_chunks = []
    response_conversation_id = None
    last_event = None
    
    for raw_line in response.iter_lines():
        if not raw_line:
            continue
            
        if isinstance(raw_line, bytes):
            line = raw_line.decode("utf-8", errors="ignore").strip()
        else:
            line = str(raw_line).strip()
        
        if line.startswith("event:"):
            last_event = line.replace("event:", "", 1).strip()
            continue
            
        if line.startswith("data:"):
            data_str = line.replace("data:", "", 1).strip()
            if not data_str:
                continue
                
            try:
                data_obj = json.loads(data_str)
            except:
                continue

            # 捕获会话ID
            if not response_conversation_id:
                response_conversation_id = data_obj.get("conversation_id")

            # 捕获流式消息增量
            if last_event == "conversation.message.delta":
                content = data_obj.get("content", "")
                if content:
                    answer_chunks.append(content)
            
            # 捕获非流式或完整消息
            elif last_event == "conversation.message.completed":
                if data_obj.get("type") == "answer" and not answer_chunks:
                     content = data_obj.get("content", "")
                     if content:
                         answer_chunks.append(content)

    answer = "".join(answer_chunks).strip()
    if not answer:
         print(f"Coze无返回内容，最后一次事件: {last_event if 'last_event' in locals() else 'None'}")
         raise Exception("Coze返回内容为空")

    return {
        "answer": answer,
        "conversation_id": response_conversation_id
    }

def call_zhipu_assistant(user_id: str, message: str, conversation_id: str | None = None) -> dict:
    if not ZHIPU_API_KEY or not ZHIPU_ASSISTANT_ID:
        raise Exception("智谱AI配置未完善，请在.env中填写ZHIPU_API_KEY和ZHIPU_ASSISTANT_ID")

    clean_message = clean_text(message)
    if not clean_message:
        raise Exception("用户消息不可为空～")

    next_conversation_id = conversation_id or uuid.uuid4().hex
    request_id = uuid.uuid4().hex

    url = f"{ZHIPU_API_BASE.rstrip('/')}/assistant"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
    }
    payload = {
        "assistant_id": ZHIPU_ASSISTANT_ID,
        "model": ZHIPU_ASSISTANT_MODEL,
        "messages": [{"role": "user", "content": clean_message}],
        "conversation_id": next_conversation_id,
        "stream": False,
        "request_id": request_id,
        "user_id": f"user_{user_id}",
    }

    res = None
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        try:
            res = response.json()
        except Exception:
            res = None

        if response.status_code != 200:
            err_detail = ""
            if isinstance(res, dict):
                err_detail = res.get("error", {}).get("message") or res.get("message") or ""
            raise Exception(f"智谱AI接口错误：{response.status_code} {err_detail or response.text}")

        if not isinstance(res, dict):
            raise Exception("智谱AI返回格式解析失败：非JSON对象")

        choices = res.get("choices") or []
        if not choices:
            raise Exception("智谱AI返回格式解析失败：choices为空")

        msg = (choices[0] or {}).get("message") or {}
        answer = (msg.get("content") or msg.get("reasoning_content") or "").strip()
        if not answer:
            raise Exception("智谱AI返回内容为空")

        returned_conversation_id = res.get("conversation_id") or next_conversation_id
        return {"answer": answer, "conversation_id": returned_conversation_id}
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"网络连接失败：{str(e)}，请检查智谱AI地址和服务器网络")
    except requests.exceptions.Timeout as e:
        raise Exception(f"接口请求超时：{str(e)}，请稍后重试")
    except Exception as e:
        error_info = str(e)
        zhipu_raw = res if res else "接口无返回数据"
        print(f"智谱AI调用失败：{error_info} | 智谱原始返回：{zhipu_raw}")
        raise

def _is_zhipu_assistant_api_id(value: str | None) -> bool:
    if not value:
        return False
    return re.fullmatch(r"[0-9a-f]{24}", value) is not None

def stream_zhipu_chat_completions(messages: list, conversation_id: str | None = None):
    if not ZHIPU_API_KEY:
        raise Exception("智谱AI配置未完善，请在.env中填写ZHIPU_API_KEY")

    next_conversation_id = conversation_id or uuid.uuid4().hex
    url = f"{ZHIPU_API_BASE.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
    }
    payload = {
        "model": ZHIPU_CHAT_MODEL,
        "messages": messages,
        "stream": True,
        "temperature": 0.7,
    }

    res_text = None
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=(10, 300))
        if response.status_code != 200:
            res_text = response.text
            raise Exception(f"智谱AI接口错误：{response.status_code} {res_text}")

        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            line = raw_line.strip()
            if not line.startswith("data:"):
                continue

            data_str = line.replace("data:", "", 1).strip()
            if not data_str:
                continue
            if data_str == "[DONE]":
                yield {"done": True, "conversation_id": next_conversation_id}
                break

            try:
                data_obj = json.loads(data_str)
            except Exception:
                continue

            delta = ""
            try:
                choices = data_obj.get("choices") or []
                if choices:
                    choice0 = choices[0] or {}
                    delta_obj = choice0.get("delta") or {}
                    delta = delta_obj.get("content") or ""
                    if not delta:
                        msg_obj = choice0.get("message") or {}
                        delta = msg_obj.get("content") or ""
            except Exception:
                delta = ""

            if delta:
                yield {"delta": delta, "conversation_id": next_conversation_id}
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"网络连接失败：{str(e)}，请检查智谱AI地址和服务器网络")
    except requests.exceptions.Timeout as e:
        raise Exception(f"接口请求超时：{str(e)}，请稍后重试")
    except Exception as e:
        error_info = str(e)
        print(f"智谱AI流式调用失败：{error_info} | 智谱原始返回：{res_text if res_text else '无'}")
        raise

def stream_zhipu_assistant(user_id: str, message: str, conversation_id: str | None = None, history: list | None = None):
    if not ZHIPU_API_KEY or not ZHIPU_ASSISTANT_ID:
        raise Exception("智谱AI配置未完善，请在.env中填写ZHIPU_API_KEY和ZHIPU_ASSISTANT_ID")

    if not _is_zhipu_assistant_api_id(ZHIPU_ASSISTANT_ID):
        safe_history = history if isinstance(history, list) and history else [{"role": "user", "content": message}]
        yield from stream_zhipu_chat_completions(safe_history, conversation_id=conversation_id)
        return

    clean_message = clean_text(message)
    if not clean_message:
        raise Exception("用户消息不可为空～")

    next_conversation_id = conversation_id or uuid.uuid4().hex
    request_id = uuid.uuid4().hex

    url = f"{ZHIPU_API_BASE.rstrip('/')}/assistant"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
    }
    payload = {
        "assistant_id": ZHIPU_ASSISTANT_ID,
        "model": ZHIPU_ASSISTANT_MODEL,
        "messages": [{"role": "user", "content": clean_message}],
        "conversation_id": next_conversation_id,
        "stream": True,
        "request_id": request_id,
        "user_id": f"user_{user_id}",
    }

    res_text = None
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=(10, 300))
        if response.status_code != 200:
            res_text = response.text
            raise Exception(f"智谱AI接口错误：{response.status_code} {res_text}")

        response_conversation_id = next_conversation_id
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue

            line = raw_line.strip()
            if not line.startswith("data:"):
                continue

            data_str = line.replace("data:", "", 1).strip()
            if not data_str:
                continue
            if data_str == "[DONE]":
                yield {"done": True, "conversation_id": response_conversation_id}
                break

            try:
                data_obj = json.loads(data_str)
            except Exception:
                continue

            if isinstance(data_obj, dict):
                response_conversation_id = data_obj.get("conversation_id") or response_conversation_id

            delta = ""
            try:
                choices = data_obj.get("choices") or []
                if choices:
                    choice0 = choices[0] or {}
                    delta_obj = choice0.get("delta") or {}
                    delta = delta_obj.get("content") or ""
                    if not delta:
                        msg_obj = choice0.get("message") or {}
                        delta = msg_obj.get("content") or ""
            except Exception:
                delta = ""

            if delta:
                yield {"delta": delta, "conversation_id": response_conversation_id}
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"网络连接失败：{str(e)}，请检查智谱AI地址和服务器网络")
    except requests.exceptions.Timeout as e:
        raise Exception(f"接口请求超时：{str(e)}，请稍后重试")
    except Exception as e:
        error_info = str(e)
        print(f"智谱AI流式调用失败：{error_info} | 智谱原始返回：{res_text if res_text else '无'}")
        raise
