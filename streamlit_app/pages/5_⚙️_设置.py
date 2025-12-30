"""Settings page for backend configuration."""

import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import (
    APIError,
    get_llm_settings,
    get_reflection_settings,
    reset_reflection_settings,
    update_llm_settings,
    update_reflection_settings,
)

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


@st.cache_data(ttl=60)
def load_reflection() -> dict:
    return get_reflection_settings()


settings = load_settings()

# Header
st.title("⚙️ 设置")
st.caption("配置LLM后端和生成参数（含可选的反思审查）")

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

st.divider()
st.header("🔎 Reflection 审查（可选）")
st.caption("用于生成后逐页快速规则校验 + 可选 LLM 复核，必要时触发重写；默认关闭。")

try:
    reflection_settings = load_reflection()
except APIError as e:
    reflection_settings = None
    st.warning(f"无法读取 Reflection 设置: {e.detail}")

if reflection_settings:
    base = reflection_settings.get("base") or {}
    override = reflection_settings.get("override") or None
    effective = reflection_settings.get("effective") or {}
    overridden_fields = reflection_settings.get("overridden_fields") or []

    if override:
        st.info(f"当前存在运行时覆盖字段: {', '.join(overridden_fields) if overridden_fields else '(未知)'}")

    with st.form("reflection_form"):
        enabled = st.toggle("启用 Reflection 审查", value=bool(effective.get("enabled", False)))

        st.subheader("逐页审查")
        per_slide_max_rewrites = st.number_input(
            "逐页最大重写次数",
            min_value=0,
            max_value=5,
            value=int(effective.get("per_slide_max_rewrites", 2)),
            step=1,
            help="每页最多允许被打回并重写的次数；超过后降级保留最后版本并记录 warnings。",
        )

        enable_llm_review = st.toggle(
            "启用 LLM 复核（Judge）",
            value=bool(effective.get("enable_llm_review", True)),
        )
        evaluator_temperature = st.slider(
            "Judge Temperature",
            min_value=0.0,
            max_value=2.0,
            value=float(effective.get("evaluator_temperature", 0.1)),
            step=0.1,
        )

        st.subheader("静态规则")
        col1, col2 = st.columns(2)
        with col1:
            enable_rule_text_density = st.toggle(
                "文本密度限制",
                value=bool(effective.get("enable_rule_text_density", True)),
            )
            text_char_limit = st.number_input(
                "单页文本字符上限（估算）",
                min_value=0,
                max_value=5000,
                value=int(effective.get("text_char_limit", 900)),
                step=50,
                help="近似可见文本字符数上限（非渲染级统计）。",
            )
        with col2:
            enable_rule_point_density = st.toggle(
                "要点密度限制",
                value=bool(effective.get("enable_rule_point_density", True)),
            )
            max_points_per_slide = st.number_input(
                "单页要点数上限（估算）",
                min_value=0,
                max_value=20,
                value=int(effective.get("max_points_per_slide", 8)),
                step=1,
            )
            max_chars_per_point = st.number_input(
                "单个要点字符上限（估算）",
                min_value=0,
                max_value=1000,
                value=int(effective.get("max_chars_per_point", 120)),
                step=10,
            )

        enable_rule_root_container = st.toggle(
            "强化根容器结构约束（复用现有校验）",
            value=bool(effective.get("enable_rule_root_container", True)),
        )

        st.subheader("全局审查")
        enable_global_review = st.toggle(
            "启用全局审查（Deck-level）",
            value=bool(effective.get("enable_global_review", False)),
        )
        global_max_rewrite_passes = st.number_input(
            "全局最大重写轮次",
            min_value=0,
            max_value=3,
            value=int(effective.get("global_max_rewrite_passes", 1)),
            step=1,
        )

        saved = st.form_submit_button("💾 保存 Reflection 设置", use_container_width=True, type="primary")
        if saved:
            patch = {
                "enabled": enabled,
                "per_slide_max_rewrites": per_slide_max_rewrites,
                "enable_llm_review": enable_llm_review,
                "enable_rule_text_density": enable_rule_text_density,
                "text_char_limit": text_char_limit,
                "enable_rule_point_density": enable_rule_point_density,
                "max_points_per_slide": max_points_per_slide,
                "max_chars_per_point": max_chars_per_point,
                "enable_rule_root_container": enable_rule_root_container,
                "evaluator_temperature": evaluator_temperature,
                "enable_global_review": enable_global_review,
                "global_max_rewrite_passes": global_max_rewrite_passes,
            }

            try:
                update_reflection_settings(patch)
                load_reflection.clear()
                st.success("✅ Reflection 设置已保存（运行时覆盖）")
            except APIError as e:
                st.error(f"保存失败: {e.detail}")

    if st.button("🧹 清除运行时覆盖（恢复 env 默认）", use_container_width=True):
        try:
            reset_reflection_settings()
            load_reflection.clear()
            st.success("✅ 已清除运行时覆盖")
        except APIError as e:
            st.error(f"清除失败: {e.detail}")

# Info box
st.divider()
st.info(
    """
**提示**
- API 密钥需要在服务器端的 `.env` 文件中配置
- 可使用自定义模型名称以兼容各类 OpenAI 兼容服务
- OpenAI 兼容端点支持 vLLM、Ollama、OpenRouter 等方案
- Reflection 设置为运行时覆盖：重启服务后会恢复为 `.env` 默认值
"""
)
