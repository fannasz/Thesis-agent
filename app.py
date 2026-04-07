import streamlit as st
import os
from agent import run_agent

st.set_page_config(page_title="論文搜尋 Agent", page_icon="📚")

os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

st.title("📖 論文搜尋 Agent")

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
