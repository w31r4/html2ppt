"""Generation progress page."""

import streamlit as st
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import get_generation_status, APIError

st.set_page_config(
    page_title="生成中 - HTML2PPT",
    page_icon="⏳",
    layout="centered",
)

# Check session
if "session_id" not in st.session_state or not st.session_state.session_id:
    st.warning("请先提交需求")
    if st.button("返回首页"):
        st.switch_page("pages/1_🏠_首页.py")
    st.stop()

session_id = st.session_state.session_id

# Stage definitions
STAGES = [
    {"key": "outline_confirmed", "label": "大纲确认", "description": "大纲已确认，准备生成"},
    {"key": "vue_generating", "label": "生成Vue组件", "description": "正在为每个章节生成Vue组件..."},
    {"key": "vue_completed", "label": "Vue组件完成", "description": "所有组件已生成"},
    {"key": "slidev_assembling", "label": "组装Slidev", "description": "正在生成Slidev Markdown..."},
    {"key": "completed", "label": "生成完成", "description": "演示文稿已准备就绪"},
]

# Header
st.markdown(
    """
<div style="text-align: center; padding: 2rem 0;">
    <h1>⏳ 正在生成演示文稿</h1>
    <p style="color: #666;">AI正在为您创建精美的Slidev演示文稿，请稍候...</p>
</div>
""",
    unsafe_allow_html=True,
)

# Progress container
progress_container = st.container()
status_container = st.container()
error_container = st.container()


# Polling loop
def get_stage_index(stage: str) -> int:
    for i, s in enumerate(STAGES):
        if s["key"] == stage:
            return i
    return -1


def poll_status():
    """Poll for status updates."""
    try:
        status = get_generation_status(session_id)
        return status
    except APIError as e:
        return {"stage": "error", "progress": 0, "error": str(e.detail)}


# Create a placeholder for auto-refresh
placeholder = st.empty()

# Poll status
status = poll_status()
current_stage = status.get("stage", "")
progress = status.get("progress", 0)
error = status.get("error")

with progress_container:
    # Progress bar
    st.markdown("### 进度")
    progress_bar = st.progress(progress)
    st.caption(f"{int(progress * 100)}% 完成")

with status_container:
    st.markdown("### 生成阶段")

    current_index = get_stage_index(current_stage)

    for i, stage in enumerate(STAGES):
        if i < current_index:
            # Completed
            st.success(f"✅ **{stage['label']}** - {stage['description']}")
        elif i == current_index:
            # Current
            if current_stage == "completed":
                st.success(f"✅ **{stage['label']}** - {stage['description']}")
            elif current_stage == "error":
                st.error(f"❌ **错误** - 生成过程中出现问题")
            else:
                st.info(f"⏳ **{stage['label']}** - {stage['description']}")
        else:
            # Pending
            st.markdown(f"⏸️ **{stage['label']}** - {stage['description']}")

with error_container:
    if current_stage == "error" and error:
        st.error(f"生成失败: {error}")
        if st.button("返回首页重试"):
            st.session_state.session_id = None
            st.switch_page("pages/1_🏠_首页.py")

# Auto-redirect on completion
if current_stage == "completed":
    st.success("🎉 生成完成！正在跳转到结果页...")
    time.sleep(1.5)
    st.switch_page("pages/4_🎉_结果.py")
elif current_stage != "error":
    # Auto-refresh after 2 seconds
    st.markdown(
        """
    <script>
        setTimeout(function() {
            window.location.reload();
        }, 2000);
    </script>
    """,
        unsafe_allow_html=True,
    )

    # Fallback: use st.rerun with a delay
    time.sleep(2)
    st.rerun()

# Tips
st.divider()
st.caption("💡 生成过程可能需要1-2分钟，请耐心等待")
