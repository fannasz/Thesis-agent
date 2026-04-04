import streamlit as st
import os
from agent import run_agent

st.set_page_config(page_title="論文搜尋 Agent", page_icon="📚")

with st.sidebar:
    st.markdown("## ⚙️ 設定")
    api_key = st.text_input("Anthropic API Key", type="password")
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key

st.title("論文搜尋 Agent")

query = st.text_area("輸入研究問題", height=100,
                     placeholder="例如：社會階層對人工智慧態度的影響")

if st.button("搜尋", type="primary"):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.error("請先在左側輸入 API Key")
    elif not query.strip():
        st.warning("請輸入研究問題")
    else:
        status = st.empty()

        def update(msg):
            status.info(msg)

        with st.spinner(""):
            result = run_agent(query, progress_callback=update)

        status.empty()
        st.markdown(result)
        st.download_button("⬇️ 下載結果", data=result,
                           file_name="論文搜尋.md", mime="text/markdown")