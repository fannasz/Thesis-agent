import time
import anthropic
import json
from tools import execute_tool

TOOLS = [
    {
        "name": "search_thesis",
        "description": "搜尋台灣博碩士論文，輸入關鍵字回傳相關論文列表",
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "搜尋關鍵字"},
                "year_from": {"type": "integer", "description": "起始年份"},
                "degree": {"type": "string", "enum": ["master", "doctor"]}
            },
            "required": ["keyword"]
        }
    }
]

SYSTEM_PROMPT = """
你是一位專業的學術文獻助理。
當使用者提出研究問題時：
1. 拆解出適合的關鍵字（可以中英文都試）
2. 呼叫 search_thesis 搜尋
3. 篩選最相關的 5-8 篇
4. 用繁體中文整理成結構化摘要

每篇論文格式：
**【序號】標題**
- 作者：XXX | 年份：XXXX | 引用次數：XX
- 來源：期刊或會議名稱
- 核心論點：1-2 句話說明這篇研究在做什麼
- DOI：連結（如有）
"""

def run_agent(user_query: str, progress_callback=None) -> str:
    client = anthropic.Anthropic() 
    messages = [{"role": "user", "content": user_query}]

    for _ in range(8):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if progress_callback:
                        progress_callback(f"🔍 搜尋關鍵字：{block.input.get('keyword', '')}")
                    result = execute_tool(block.name, block.input)
                    time.sleep(1) 
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        else:
            return "".join(
                b.text for b in response.content if hasattr(b, "text")
            )

    return "超過最大次數，請嘗試更具體的問題。"
