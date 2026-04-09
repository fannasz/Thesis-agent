import streamlit as st
import os
from agent import run_agent
from datetime import datetime

st.set_page_config(page_title="論文搜尋 Agent ouo")
STATS_FILE = "stats.json"

def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    return {"total": 0, "daily": {}}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

def add_click():
    stats = load_stats()
    stats["total"] += 1
    today = datetime.now().strftime("%Y-%m-%d")
    stats["daily"][today] = stats["daily"].get(today, 0) + 1
    save_stats(stats)
    return stats
    
st.markdown("""
<style>
/* 對話輸入框加框線 */
textarea {
    border: 2px solid #2563EB !important;
    border-radius: 8px !important;
}

/* 聚焦時框線變深 */
textarea:focus {
    border: 2px solid #1E3A5F !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
}
</style>
""", unsafe_allow_html=True)

os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

st.title("論文搜尋 Agent ouo")

st.markdown("### 搜尋條件")
col_a, col_b, col_c = st.columns(3)

with col_a:
    keyword1 = st.text_input("第一順位",
                              placeholder="例如：人工智慧")
with col_b:
    keyword2 = st.text_input("第二順位",
                              placeholder="例如：台獨")
with col_c:
    keyword3 = st.text_input("第三順位",
                              placeholder="例如：社會階層")

if st.button("搜尋", type="primary"):
    if not keyword1.strip():
        st.warning("請至少填寫第一順位關鍵字")
    else:
        # 組合關鍵字，只加入有填寫的欄位
        keywords = [k for k in [keyword1, keyword2, keyword3] if k.strip()]
        combined_query = " ".join(keywords)

        # 告訴 Agent 搜尋邏輯
        query = f"""
請搜尋以下主題的論文：
- 第一順位（必須符合）：{keyword1}
{"- 第二順位（優先符合）：" + keyword2 if keyword2 else ""}
{"- 第三順位（額外篩選）：" + keyword3 if keyword3 else ""}

搜尋時以第一順位為主要關鍵字，
回傳的論文必須與第一順位相關，
有符合第二、第三順位的論文優先排在前面。
"""

        status = st.empty()

        def update(msg):
            status.info(msg)

        with st.spinner(""):
            try:
                result = run_agent(query, progress_callback=update)
            except Exception as e:
                result = f"⚠️ 發生錯誤：{str(e)}"

        status.empty()

        if result:
            st.markdown(result)

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    "下載 Markdown",
                    data=result,
                    file_name="論文搜尋.md",
                    mime="text/markdown"
                )

            with col2:
                from docx import Document
                from io import BytesIO

                doc = Document()
                doc.add_heading("論文搜尋結果", 0)
                for line in result.split("\n"):
                    doc.add_paragraph(line)
                buf = BytesIO()
                doc.save(buf)
                buf.seek(0)
                st.download_button(
                    "下載 Word",
                    data=buf,
                    file_name="論文搜尋.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
