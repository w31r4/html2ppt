"""Result page with Slidev preview."""

import streamlit as st
import streamlit.components.v1 as st_components
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import get_result, get_export_url, APIError

st.set_page_config(
    page_title="结果 - HTML2PPT",
    page_icon="🎉",
    layout="wide",
)

# Slidev Preview Service URL
VUE_PREVIEW_URL = os.getenv("VUE_PREVIEW_URL", "http://localhost:5173")


def normalize_preview_url(url: str) -> str:
    if not url:
        return "/preview/"
    return url if url.endswith("/") else f"{url}/"

# Check session
if "session_id" not in st.session_state or not st.session_state.session_id:
    st.warning("请先提交需求")
    if st.button("返回首页"):
        st.switch_page("pages/1_🏠_首页.py")
    st.stop()

session_id = st.session_state.session_id


# Load result
@st.cache_data(ttl=300)
def load_result(sid: str) -> dict:
    return get_result(sid)


try:
    result = load_result(session_id)
except APIError as e:
    st.error(f"加载结果失败: {e.detail}")
    if st.button("返回首页"):
        st.switch_page("pages/1_🏠_首页.py")
    st.stop()

slides_md = result.get("slides_md", "")
component_list = result.get("components", [])
slides = result.get("slides", [])

# Header
col1, col2 = st.columns([2, 1])
with col1:
    st.title("🎉 生成结果")
    st.caption("您的Slidev演示文稿已准备就绪")

with col2:
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        # Download slides.md
        st.download_button(
            label="📥 下载 slides.md",
            data=slides_md,
            file_name=f"slides-{session_id[:8]}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with btn_col2:
        # Download zip link
        st.link_button(
            label="📦 下载组件包",
            url=get_export_url(session_id, include_components=True),
            use_container_width=True,
        )

# Tabs
tab_preview, tab_markdown, tab_components = st.tabs(["👁️ 预览", "📄 Markdown", "🧩 Vue组件"])

with tab_preview:
    st.subheader("幻灯片预览")

    if not slides_md.strip():
        st.info("没有可预览的幻灯片")
    else:
        component_map = {comp.get("name"): comp.get("code", "") for comp in component_list}
        preview_url = normalize_preview_url(VUE_PREVIEW_URL)
        payload = {
            "type": "preview-code",
            "code": slides_md,
        }
        if component_map:
            payload["components"] = component_map

        payload_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

        st_components.html(
            f"""
        <iframe
            id="preview-frame"
            src="{preview_url}"
            width="100%"
            height="600"
            style="border: 1px solid #ddd; border-radius: 8px;"
            frameborder="0"
        ></iframe>
        <script>
          const payload = {payload_json};
          const frame = document.getElementById('preview-frame');
          const sendPayload = () => {{
            if (!frame || !frame.contentWindow) return;
            frame.contentWindow.postMessage(payload, "*");
          }};
          frame.addEventListener('load', sendPayload);
          setTimeout(sendPayload, 500);
        </script>
        """,
            height=620,
        )

with tab_markdown:
    st.subheader("Slidev Markdown")

    # Copy button
    if st.button("📋 复制到剪贴板"):
        st.code(slides_md, language="markdown")
        st.info("请手动复制上面的代码（Streamlit 不支持自动复制到剪贴板）")

    # Display code
    st.code(slides_md, language="markdown", line_numbers=True)

with tab_components:
    st.subheader("Vue 组件")

    if not component_list:
        st.info("没有生成的Vue组件")
    else:
        # Component selector
        component_names = [comp.get("name", f"Component {i}") for i, comp in enumerate(component_list)]
        selected_component = st.selectbox("选择组件", component_names)

        # Find selected component
        selected_idx = component_names.index(selected_component)
        component = component_list[selected_idx]

        st.markdown(f"**{component.get('name', 'Component')}.vue**")
        st.code(component.get("code", ""), language="vue", line_numbers=True)

# Usage instructions
st.divider()
st.subheader("📖 使用说明")

steps = [
    ("1", "下载 slides.md 文件"),
    ("2", "创建Slidev项目：`npm init slidev@latest`"),
    ("3", "将 slides.md 内容替换到项目的 slides.md 文件中"),
    ("4", "将生成的 .vue 组件放到项目的 components/ 目录中"),
    ("5", "运行开发服务器：`npm run dev`"),
]

for num, text in steps:
    st.markdown(
        f"""
    <div style="display: flex; align-items: center; margin: 0.5rem 0;">
        <div style="background: #3b82f6; color: white; width: 24px; height: 24px; 
                    border-radius: 50%; display: flex; align-items: center; 
                    justify-content: center; margin-right: 12px; font-size: 12px;">
            {num}
        </div>
        <span>{text}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

# New presentation button
st.divider()
if st.button("✨ 创建新的演示文稿", use_container_width=True):
    st.session_state.session_id = None
    st.session_state.outline = ""
    st.session_state.original_outline = ""
    st.switch_page("pages/1_🏠_首页.py")
