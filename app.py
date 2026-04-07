import streamlit as st
import os
from agent import run_agent

st.set_page_config(page_title="論文搜尋 Agent ouo")
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

query = st.text_area("輸入關鍵字", height=100,
                     placeholder="例如：社會階層、人工智慧態度")

if st.button("搜尋", type="primary"):
    if not query.strip():
        st.warning("請輸入研究問題")
    else:
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
                    "⬇️ 下載 Markdown",
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
                    "⬇️ 下載 Word",
                    data=buf,
                    file_name="論文搜尋.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
