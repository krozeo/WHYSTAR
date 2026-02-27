# core/ai_api.py - 修复所有AI调用错误，主动抛异常，严格校验返回
import requests
import re
from config import AI_API_TOKEN, AI_MODEL  # 仅导入2个核心配置

# 火山豆包官方固定API地址（确认无误，保留）
VOLC_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

# 输入清洗函数：移除不可见控制字符，避免JSON解析错误（保留原有逻辑）
def clean_text(text):
    return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)

def call_ai(chat_memory: list) -> str:
    """
    调用火山豆包模型（修复后）
    :param chat_memory: 对话记忆列表
    :return: 豆包模型清洗后的回复内容
    :raise Exception: 配置错误/接口调用/解析失败时主动抛异常，供上层事务捕获
    """
    # 1. 配置校验（失败主动抛异常，而非返回字符串）
    if not AI_API_TOKEN or not AI_MODEL:
        raise Exception("AI配置未完善，请在.env中填写有效的AI_API_TOKEN和AI_MODEL")

    # 2. 清洗记忆中的所有内容（保留原有核心逻辑）
    cleaned_memory = []
    for msg in chat_memory:
        cleaned_memory.append({
            "role": msg["role"],
            "content": clean_text(msg["content"])
        })

    # 3. 构造火山豆包请求体（保留原有格式）
    req_data = {
        "model": AI_MODEL,
        "messages": cleaned_memory,
        "temperature": 0.7
    }

    # 4. 请求头（保留原有格式）
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_TOKEN}"
    }

    res = None  # 提前初始化res，避免except中未定义
    try:
        # 5. 调用火山接口（分离requests.post和json解析，单独捕获连接错误）
        response = requests.post(VOLC_API_URL, headers=headers, json=req_data, timeout=30)
        res = response.json()  # 单独解析，捕获JSON解析错误

        # 新增：校验火山API返回状态码（核心修复，避免解析错误）
        if response.status_code != 200:
            error_msg = res.get("error", {}).get("message", f"服务端错误，状态码：{response.status_code}")
            raise Exception(f"火山API返回错误：{error_msg}")

        # 6. 解析返回结果（保留原有逻辑）
        ai_answer = res["choices"][0]["message"]["content"]
        clean_answer = clean_text(ai_answer)
        return clean_answer

    except requests.exceptions.ConnectionError as e:
        # 捕获网络连接错误（如地址/端口错误、网络不通）
        raise Exception(f"网络连接失败：{str(e)}，请检查API地址和服务器网络")
    except requests.exceptions.Timeout as e:
        # 捕获请求超时错误
        raise Exception(f"接口请求超时：{str(e)}，请稍后重试")
    except KeyError as e:
        # 捕获返回格式错误（如无choices、message字段）
        raise Exception(f"AI返回格式解析失败：缺失{str(e)}字段，原始返回：{res if res else '无数据'}")
    except Exception as e:
        # 捕获其他所有错误
        error_info = str(e)
        volc_raw = res if res else "接口无返回数据"
        print(f"火山豆包调用失败：{error_info} | 火山原始返回：{volc_raw}")
        raise Exception(f"AI调用失败：{error_info[:60]}，请检查配置或稍后再试")