"""Settings page for LLM configuration."""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import get_llm_settings, update_llm_settings, APIError

st.set_page_config(
    page_title="设置 - HTML2PPT",
    page_icon="⚙️",
    layout="centered",
)

# Provider options
PROVIDERS = [
    {"value": "openai", "label": "OpenAI / OpenAI兼容"},
    {"value": "gemini", "label": "Google Gemini"},
    {"value": "azure_openai", "label": "Azure OpenAI"},
]

PRESET_MODELS = {
    "openai": ["gpt-4o", "gpt-4o-mini", "o1", "o1-mini"],
    "gemini": [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ],
    "azure_openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
}


# Load settings
@st.cache_data(ttl=60)
def load_settings() -> dict:
    return get_llm_settings()


settings = load_settings()

# Header
st.title("⚙️ 设置")
st.caption("配置LLM后端和生成参数")

# Settings form
with st.form("settings_form"):
    # Provider
    provider_options = [p["value"] for p in PROVIDERS]
    provider_labels = [p["label"] for p in PROVIDERS]

    current_provider_idx = (
        provider_options.index(settings.get("provider", "openai"))
        if settings.get("provider") in provider_options
        else 0
    )

    provider = st.selectbox(
        "LLM 提供商",
        options=provider_options,
        format_func=lambda x: dict(zip(provider_options, provider_labels))[x],
        index=current_provider_idx,
    )

    # Model
    preset_models = PRESET_MODELS.get(provider, [])
    current_model = settings.get("model", "gpt-4o")

    model = st.text_input("模型", value=current_model, help="可直接输入模型名称；推荐使用 GPT-4o 或 Gemini 2.5 系列")

    # Preset model buttons
    if preset_models:
        st.caption("推荐模型：")
        cols = st.columns(len(preset_models))
        for i, m in enumerate(preset_models):
            with cols[i]:
                if st.form_submit_button(m, use_container_width=True):
                    model = m

    # Base URL
    base_url = st.text_input(
        "自定义API端点 (可选)",
        value=settings.get("base_url", ""),
        placeholder="例如: http://localhost:11434/v1 (Ollama)",
        help="留空使用官方API，或填写自定义端点如vLLM、Ollama、OpenRouter等",
    )

    # Temperature
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=settings.get("temperature", 0.7),
        step=0.1,
        help="较低值更精确，较高值更有创意",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("精确 (0)")
    with col2:
        st.caption("平衡 (0.7)")
    with col3:
        st.caption("创意 (2)")

    # Max tokens
    max_tokens = st.number_input(
        "最大Token数",
        min_value=256,
        max_value=32000,
        value=settings.get("max_tokens", 4096),
        step=256,
    )

    # Submit
    submitted = st.form_submit_button("💾 保存设置", use_container_width=True, type="primary")

    if submitted:
        new_settings = {
            "provider": provider,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if base_url.strip():
            new_settings["base_url"] = base_url.strip()

        try:
            update_llm_settings(new_settings)
            load_settings.clear()  # Clear cache
            st.success("✅ 设置已保存")
        except APIError as e:
            st.error(f"保存失败: {e.detail}")

# Info box
st.divider()
st.info(
    """
**提示**
- API密钥需要在服务器端的 `.env` 文件中配置
- 可使用自定义模型名称以兼容各类OpenAI兼容服务
- OpenAI兼容端点支持 vLLM、Ollama、OpenRouter 等方案
"""
)
