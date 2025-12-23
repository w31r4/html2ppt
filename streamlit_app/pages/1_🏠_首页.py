"""Home page - requirement input."""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import submit_requirements, APIError

st.set_page_config(
    page_title="首页 - HTML2PPT",
    page_icon="🏠",
    layout="centered",
)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Header
st.markdown(
    """
<div style="text-align: center; padding: 2rem 0;">
    <h1>✨ AI演示文稿生成器</h1>
    <p style="color: #666; font-size: 1.1rem;">
        描述您的演示需求，AI将为您生成专业的Slidev演示文稿。<br>
        支持大纲编辑、实时预览和一键导出。
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# Input form
with st.form("requirement_form"):
    st.subheader("📝 需求描述")

    requirement = st.text_area(
        "请描述您的演示文稿需求",
        height=200,
        max_chars=10000,
        placeholder="例如：为我的产品发布会制作一个演示文稿，包括产品介绍、核心功能、竞争优势和定价方案...",
        help="详细描述您的演示文稿需求，包括主题、内容要点、风格偏好等",
    )

    # Character counter
    st.caption(f"{len(requirement)} / 10000 字符")

    submitted = st.form_submit_button("🚀 生成演示大纲", use_container_width=True, type="primary")

    if submitted:
        if not requirement.strip():
            st.error("请输入需求描述")
        else:
            with st.spinner("正在生成大纲..."):
                try:
                    response = submit_requirements(requirement.strip())
                    st.session_state.session_id = response["session_id"]
                    st.success("大纲生成成功！")
                    st.switch_page("pages/2_📝_大纲编辑.py")
                except APIError as e:
                    st.error(f"生成失败: {e.detail}")
                except Exception as e:
                    st.error(f"网络错误: {str(e)}")

# Features section
st.divider()
st.subheader("🌟 功能特性")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
    <div style="background: #f0f9ff; padding: 1.5rem; border-radius: 8px; text-align: center;">
        <div style="font-size: 2rem;">📝</div>
        <h4>智能大纲</h4>
        <p style="color: #666; font-size: 0.9rem;">AI自动分析需求，生成结构化的演示大纲</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
    <div style="background: #f0fdf4; padding: 1.5rem; border-radius: 8px; text-align: center;">
        <div style="font-size: 2rem;">✏️</div>
        <h4>自由编辑</h4>
        <p style="color: #666; font-size: 0.9rem;">支持Markdown编辑，随时调整演示内容</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
    <div style="background: #faf5ff; padding: 1.5rem; border-radius: 8px; text-align: center;">
        <div style="font-size: 2rem;">🎨</div>
        <h4>Slidev导出</h4>
        <p style="color: #666; font-size: 0.9rem;">一键导出Slidev格式，支持自定义主题</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
