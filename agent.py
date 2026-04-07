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

## 搜尋策略
- 第一輪用中文關鍵字搜尋
- 第二輪用對應的英文關鍵字搜尋
- 如果結果少於 5 篇，換不同關鍵字再搜一次
- 最多搜尋 2 輪

## 篩選標準
1. 標題或摘要直接提到使用者的研究主題
2. 優先選引用次數較高的論文
4. 排除明顯不相關的論文

## 每篇論文輸出格式
**【序號】標題**
- 作者：XXX | 年份：XXXX | 引用次數：XX
- 來源：期刊或會議名稱
- 核心論點：1-2 句話說明這篇研究在做什麼
- 相關性：說明與使用者研究問題的具體關聯
- 關鍵字：抓取論文提供的keywords，沒有提供關鍵字則標示「無」
- DOI：連結（如有）

## 最後加上文獻整體分析
- 尚未被充分研究的缺口
- 建議延伸閱讀的方向

## 規則
- 所有論文必須來自 search_thesis 工具的實際結果
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
