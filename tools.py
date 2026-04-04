import requests
import json

def search_thesis(keyword: str,
                  year_from: int = None,
                  degree: str = None,
                  size: int = 10) -> dict:

    params = {
        "search": keyword,
        "per-page": size,
    }

    if year_from:
        params["filter"] = f"publication_year:>{year_from}"

    try:
        res = requests.get(
            "https://api.openalex.org/works",
            params=params,
            timeout=15,
            headers={"User-Agent": "thesis-agent/1.0"}
        )
        res.raise_for_status()
        data = res.json()

        papers = []
        for item in data.get("results", []):
            authors = [
                a["author"]["display_name"]
                for a in item.get("authorships", [])[:3]
            ]

            papers.append({
                "title":     item.get("display_name") or item.get("title", "（無標題）"),
                "authors":   "、".join(authors) if authors else "未知",
                "year":      item.get("publication_year", ""),
                "abstract":  (item.get("abstract_inverted_index") and "（有摘要）") or "（無摘要）",
                "citations": item.get("cited_by_count", 0),
                "doi":       item.get("doi", "")
            })

        return {"total": data.get("meta", {}).get("count", 0), "papers": papers}

    except requests.exceptions.Timeout:
        return {"error": "請求逾時，請稍後再試"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP 錯誤：{e}"}
    except Exception as e:
        return {"error": str(e)}


def execute_tool(name: str, inputs: dict) -> str:
    if name == "search_thesis":
        result = search_thesis(**inputs)
    else:
        result = {"error": f"未知工具：{name}"}
    return json.dumps(result, ensure_ascii=False)