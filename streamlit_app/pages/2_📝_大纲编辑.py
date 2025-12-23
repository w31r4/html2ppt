"""Outline editing page."""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_ace import st_ace
from api_client import get_outline, update_outline, add_supplement, confirm_outline, APIError

st.set_page_config(
    page_title="大纲编辑 - HTML2PPT",
    page_icon="📝",
    layout="wide",
)

# Check session
if "session_id" not in st.session_state or not st.session_state.session_id:
    st.warning("请先提交需求")
    if st.button("返回首页"):
        st.switch_page("pages/1_🏠_首页.py")
    st.stop()

session_id = st.session_state.session_id

# Initialize outline state
if "outline" not in st.session_state:
    st.session_state.outline = ""
if "original_outline" not in st.session_state:
    st.session_state.original_outline = ""


# Load outline
@st.cache_data(ttl=60)
def load_outline(sid: str) -> dict:
    return get_outline(sid)


try:
    outline_data = load_outline(session_id)
    if not st.session_state.outline:
        st.session_state.outline = outline_data.get("outline", "")
        st.session_state.original_outline = st.session_state.outline
except APIError as e:
    st.error(f"加载大纲失败: {e.detail}")
    st.stop()

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📝 编辑大纲")
    st.caption("审核并编辑生成的演示大纲，确认后开始生成幻灯片")

with col2:
    # Action buttons
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("💾 保存", use_container_width=True):
            try:
                update_outline(session_id, st.session_state.outline)
                st.session_state.original_outline = st.session_state.outline
                st.success("保存成功")
            except APIError as e:
                st.error(f"保存失败: {e.detail}")

    with btn_col2:
        if st.button("✅ 确认生成", type="primary", use_container_width=True):
            try:
                # Save first if changed
                if st.session_state.outline != st.session_state.original_outline:
                    update_outline(session_id, st.session_state.outline)
                confirm_outline(session_id)
                st.switch_page("pages/3_⏳_生成中.py")
            except APIError as e:
                st.error(f"确认失败: {e.detail}")

# Supplement section
with st.expander("➕ 补充需求", expanded=False):
    supplement_text = st.text_area("添加更多需求细节", placeholder="添加更多需求细节，AI将重新生成大纲...", height=100)
    if st.button("🔄 重新生成", disabled=not supplement_text.strip()):
        with st.spinner("重新生成中..."):
            try:
                response = add_supplement(session_id, supplement_text.strip())
                st.session_state.outline = response.get("outline", "")
                st.session_state.original_outline = st.session_state.outline
                # Clear cache to reload
                load_outline.clear()
                st.success("重新生成成功")
                st.rerun()
            except APIError as e:
                st.error(f"重新生成失败: {e.detail}")

# Editor and Preview
editor_col, preview_col = st.columns([1, 1])

with editor_col:
    st.subheader("编辑器")

    # Check if outline changed
    has_changes = st.session_state.outline != st.session_state.original_outline
    if has_changes:
        st.caption("⚠️ 未保存的更改")

    # Ace editor
    edited_outline = st_ace(
        value=st.session_state.outline,
        language="markdown",
        theme="github",
        height=500,
        key="outline_editor",
        auto_update=True,
    )

    if edited_outline != st.session_state.outline:
        st.session_state.outline = edited_outline

with preview_col:
    st.subheader("预览")
    st.markdown(st.session_state.outline)

# Tips
st.divider()
st.subheader("📖 编辑提示")
tips_col1, tips_col2 = st.columns(2)
with tips_col1:
    st.markdown(
        """
    - 使用 `#` 设置演示主题
    - 使用 `##` 或 `###` 设置章节标题
    - 使用 `-` 或 `*` 添加要点列表
    """
    )
with tips_col2:
    st.markdown(
        """
    - 每个章节将转换为一张幻灯片
    - 支持 Markdown 语法
    - 确认后将开始生成最终的 Slidev 演示文稿
    """
    )
