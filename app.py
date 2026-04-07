import streamlit as st
import os
from agent import run_agent

st.set_page_config(page_title="論文搜尋 Agent", page_icon="📚")

# 自動從 Secrets 讀取，不需要使用者輸入
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
            result = run_agent(query, progress_callback=update)

        status.empty()
st.markdown(result)

# 產生下載檔案
col1, col2, col3 = st.columns(3)

# Markdown 下載
with col1:
    st.download_button(
        "⬇️ 下載 Markdown",
        data=result,
        file_name="論文搜尋.md",
        mime="text/markdown"
    )

# Word 下載
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

# PDF 下載
with col3:
    from fpdf import FPDF
    from io import BytesIO

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("NotoSans", fname="NotoSansTC-Regular.ttf", uni=True)
    pdf.set_font("NotoSans", size=12)
    for line in result.split("\n"):
        pdf.multi_cell(0, 8, line)
    pdf_bytes = pdf.output()
    st.download_button(
        "⬇️ 下載 PDF",
        data=bytes(pdf_bytes),
        file_name="論文搜尋.pdf",
        mime="application/pdf"
    )
