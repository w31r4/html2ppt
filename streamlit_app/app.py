"""Streamlit app main entry point."""

import streamlit as st

st.set_page_config(
    page_title="HTML2PPT - AI演示文稿生成器",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .feature-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.title("✨ HTML2PPT")
    st.markdown("AI驱动的演示文稿生成器")
    st.divider()

    # Show current session if exists
    if "session_id" in st.session_state and st.session_state.session_id:
        st.info(f"当前会话: {st.session_state.session_id[:8]}...")
        if st.button("清除会话", use_container_width=True):
            st.session_state.session_id = None
            st.rerun()

# Main content - redirect to home page
st.switch_page("pages/1_🏠_首页.py")
