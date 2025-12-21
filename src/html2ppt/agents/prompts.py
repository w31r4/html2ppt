"""Prompt templates for LLM agents."""

OUTLINE_GENERATION_PROMPT = """你是一位专业的演示文稿设计师和动画专家。根据用户的需求描述，生成一份包含视觉建议和动画效果的详细Markdown大纲。

## 需求描述

{requirement}

{supplement_section}

## 大纲格式要求

每一页（Slide）必须包含以下结构：

### Page N: 页面标题

*   **标题**: 该页的主标题
*   **副标题**: (可选) 副标题或口号
*   **核心内容**:
    *   主要内容要点，使用列表形式
    *   每个要点可以包含加粗的关键词
*   **视觉建议**:
    *   **背景**: 描述背景的颜色、纹理或图片建议
    *   **核心图片/图示**: 描述应该使用什么样的图片或图示
    *   **布局**: 描述元素的排列方式
    *   **图片链接**: (可选) 如果有具体图片URL可以提供
*   **动画效果**:
    *   描述元素的出现顺序和动画类型（淡入、飞入、缩放等）
    *   可以分步骤描述复杂的动画序列

---

## 示例格式

```markdown
# 演示文稿主题

---

### Page 1: 封面页

*   **标题**: 主标题文字
*   **副标题**: 副标题或演讲者信息
*   **视觉建议**:
    *   **背景**: 使用深蓝色渐变背景，配合抽象的科技感粒子效果
    *   **核心图片**: 在右侧放置主题相关的3D图标或插画
    *   **布局**: 标题居中偏左，图片占据右侧1/3区域
*   **动画效果**:
    *   主标题使用"淡入"效果，持续0.5秒
    *   副标题延迟0.3秒后"从下方滑入"
    *   背景粒子持续缓慢漂浮动画

---

### Page 2: 问题引入

*   **标题**: 我们面临的挑战
*   **核心内容**:
    *   以一个设问开场引起观众思考
    *   列出3-4个核心痛点：
        1.  **痛点一**: 具体描述
        2.  **痛点二**: 具体描述
        3.  **痛点三**: 具体描述
*   **视觉建议**:
    *   **背景**: 浅灰色纯色背景，保持专业感
    *   **核心图示**: 使用图标列表形式，每个痛点配一个相关的红色警告图标
    *   **布局**: 左侧放置一个大的问号图标，右侧是痛点列表
*   **动画效果**:
    *   标题首先"淡入"
    *   问号图标"缩放弹入"
    *   三个痛点依次"从右侧滑入"，间隔0.2秒
    *   每个痛点出现时，对应图标闪烁高亮

---

### Page 3: 解决方案

*   **标题**: 我们的解决方案
*   **核心内容**:
    *   **一句话定义**: 简洁有力的方案描述
    *   **核心价值**: 列出3个核心优势
    *   **生动比喻**: 用一个形象的比喻帮助理解
*   **视觉建议**:
    *   **背景**: 渐变从左侧深蓝到右侧浅蓝
    *   **核心图示**: 中央放置一个发光的解决方案图标或产品截图
    *   **布局**: 采用"英雄布局"，图片居中，文字环绕
*   **动画效果**:
    *   整页使用"推入"转场效果
    *   核心图示"缩放渐入"并伴随光晕效果
    *   优势列表使用"打字机"效果逐字显示

<!-- speaker notes
这里可以添加演讲者备注，包含更详细的讲解要点
-->
```

## 生成要求

1. **结构完整**: 每页必须包含标题、核心内容、视觉建议和动画效果四个部分
2. **视觉具体**: 视觉建议要具体可执行，包括颜色、布局、图片类型
3. **动画详细**: 动画效果要描述清晰，包括动画类型、时长、顺序
4. **专业设计**: 遵循专业PPT设计原则，注意视觉层次和信息传达
5. **页面分隔**: 使用 `---` 分隔每一页
6. **控制数量**: 根据内容复杂度，控制在5-10页之间
7. **直接输出**: 只输出Markdown格式的大纲，不要添加额外解释

"""

VUE_COMPONENT_PROMPT = """你是一位专业的Vue前端开发工程师和动画专家。根据提供的演示文稿页面设计，生成一个包含动画效果的Vue SFC组件。

## 页面设计

{slide_content}

{visual_suggestions}

{animation_effects}

{speaker_notes_section}

## 组件要求

1. **技术栈**: Vue 3 SFC + UnoCSS (兼容Tailwind类)
2. **尺寸**: 组件应适合16:9的幻灯片展示 (宽1920px, 高1080px 或等比缩放)
3. **动画**: 使用Slidev内置 `v-click`/`v-clicks` 指令表达顺序，并结合CSS动画类做入场效果
4. **背景**: 根据视觉建议实现渐变、图片或纯色背景
5. **样式**: 若使用自定义动画类，必须在 `<style scoped>` 内定义对应 `@keyframes`
6. **简洁脚本**: 尽量避免`<script>`，如需使用只写`<script setup>`且不引入外部依赖

## 动画实现规则

- 使用 `v-click` 或 `v-clicks` 控制逐步出现顺序
- 为需要入场的元素加动画类（例如 `anim-fade-in`, `anim-slide-up`）
- 使用 `style="animation-delay: 200ms"` 做时间错位
- 动画类必须在 `<style scoped>` 中定义，包含 `animation-fill-mode: both`
- 循环动画（如 `anim-float`, `anim-pulse`, `anim-wave`, `anim-breathe`）适合装饰元素，不依赖 `v-click`

## 动画建议映射（固定）

- **淡入 / 渐显** → `anim-fade-in`
- **从下方滑入 / 上滑** → `anim-slide-up`
- **从上方滑入 / 下滑** → `anim-slide-down`
- **从左侧滑入 / 右滑** → `anim-slide-in-left`
- **从右侧滑入 / 左滑 / 推入** → `anim-slide-in-right`
- **飞入 / 掠入** → `anim-fly-in`
- **缩放弹入 / 放大出现** → `anim-scale-in`
- **缩小出现 / 收缩出现** → `anim-scale-down`
- **浮动 / 漂浮** → `anim-float`
- **闪烁 / 脉冲高亮** → `anim-pulse`
- **打字机** → `anim-typewriter`
- **翻转入场** → `anim-flip-in`
- **模糊渐清** → `anim-blur-in`
- **弹跳 / 弹入** → `anim-bounce-in`
- **抖动 / 震动** → `anim-shake`
- **旋转入场 / 旋转** → `anim-rotate-in`
- **波浪 / 起伏** → `anim-wave`
- **呼吸 / 缩放呼吸** → `anim-breathe`

当“动画建议”字段包含上述关键词时，必须使用对应动画类；没有明确关键词时选择最接近的类。

## 示例组件

```vue
<template>
  <div class="relative flex flex-col items-center justify-center h-full overflow-hidden">
    <div class="absolute inset-0 bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900"></div>

    <div class="relative z-10 text-center px-16">
      <h1 class="text-6xl font-bold text-white mb-6 anim-fade-in" v-click>
        用 Go 构建 AI Agent 的"瑞士军刀"
      </h1>
      <p class="text-2xl text-blue-200 anim-slide-up" style="animation-delay: 200ms" v-click>
        深入解析模型上下文协议 (MCP)
      </p>
      <p class="text-xl text-blue-300 mt-8 anim-slide-up" style="animation-delay: 400ms" v-click>
        演讲者：张三
      </p>
    </div>
  </div>
</template>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.anim-fade-in {
  animation: fade-in 600ms ease-out both;
}

.anim-slide-up {
  animation: slide-up 600ms ease-out both;
}
</style>
```

## 动画类定义示例（可复用，放入 `<style scoped>`）

```css
@keyframes slide-down {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slide-in-left {
  from { opacity: 0; transform: translateX(-24px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes slide-in-right {
  from { opacity: 0; transform: translateX(24px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes fly-in {
  from { opacity: 0; transform: translateY(-36px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scale-in {
  from { opacity: 0; transform: scale(0.92); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes scale-down {
  from { opacity: 0; transform: scale(1.06); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@keyframes typewriter {
  from { width: 0; }
  to { width: 100%; }
}

@keyframes bounce-in {
  0% { opacity: 0; transform: scale(0.9); }
  60% { opacity: 1; transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-6px); }
  40% { transform: translateX(6px); }
  60% { transform: translateX(-4px); }
  80% { transform: translateX(4px); }
}

@keyframes rotate-in {
  from { opacity: 0; transform: rotate(-10deg); }
  to { opacity: 1; transform: rotate(0deg); }
}

@keyframes wave {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.03); }
}

@keyframes flip-in {
  from { opacity: 0; transform: rotateX(70deg); }
  to { opacity: 1; transform: rotateX(0deg); }
}

@keyframes blur-in {
  from { opacity: 0; filter: blur(8px); }
  to { opacity: 1; filter: blur(0); }
}

.anim-slide-down { animation: slide-down 600ms ease-out both; }
.anim-slide-in-left { animation: slide-in-left 600ms ease-out both; }
.anim-slide-in-right { animation: slide-in-right 600ms ease-out both; }
.anim-fly-in { animation: fly-in 650ms ease-out both; }
.anim-scale-in { animation: scale-in 520ms ease-out both; }
.anim-scale-down { animation: scale-down 520ms ease-out both; }
.anim-float { animation: float 3s ease-in-out infinite; }
.anim-pulse { animation: pulse 1.4s ease-in-out infinite; }
.anim-typewriter { 
  animation: typewriter 1.2s steps(20, end) both; 
  overflow: hidden; 
  white-space: nowrap; 
}
.anim-bounce-in { animation: bounce-in 700ms ease-out both; }
.anim-shake { animation: shake 600ms ease-in-out both; }
.anim-rotate-in { animation: rotate-in 600ms ease-out both; transform-origin: center; }
.anim-wave { animation: wave 2.6s ease-in-out infinite; }
.anim-breathe { animation: breathe 2.4s ease-in-out infinite; }
.anim-flip-in { animation: flip-in 520ms ease-out both; transform-origin: center; }
.anim-blur-in { animation: blur-in 650ms ease-out both; }
</style>
```

## 生成要求

1. **完整代码**: 输出完整的Vue SFC代码
2. **无外部依赖**: 不要引入第三方库或图片资源
3. **动画落地**: 所有动画类必须有对应CSS定义
4. **可运行**: 确保`<template>`语法正确
5. **无额外解释**: 只输出代码，不添加任何解释性文字
"""


def get_outline_prompt(requirement: str, supplement: str | None = None) -> str:
    """Generate outline prompt with requirement and optional supplement.

    Args:
        requirement: User requirement text
        supplement: Optional additional requirements

    Returns:
        Formatted prompt string
    """
    supplement_section = ""
    if supplement:
        supplement_section = f"""## 补充需求

{supplement}
"""

    return OUTLINE_GENERATION_PROMPT.format(
        requirement=requirement,
        supplement_section=supplement_section,
    )


def get_vue_prompt(
    section_title: str,
    section_points: list[str] | None = None,
    speaker_notes: str | None = None,
    visual_suggestions: dict | None = None,
    animation_effects: dict | None = None,
    raw_content: str | None = None,
) -> str:
    """Generate Vue component prompt for a section with rich formatting.

    Args:
        section_title: Section title
        section_points: List of bullet points (optional if raw_content provided)
        speaker_notes: Optional speaker notes
        visual_suggestions: Visual design suggestions dict
        animation_effects: Animation effects dict
        raw_content: Raw markdown content for this section

    Returns:
        Formatted prompt string
    """
    # Build slide content section
    if raw_content:
        slide_content = f"### 原始内容\n\n{raw_content}"
    else:
        points_text = "\n".join(f"- {point}" for point in (section_points or []))
        slide_content = f"### 标题: {section_title}\n\n### 内容要点:\n{points_text}"

    # Build visual suggestions section
    visual_section = ""
    if visual_suggestions:
        visual_parts = ["### 视觉建议"]
        if visual_suggestions.get("background"):
            visual_parts.append(f"- **背景**: {visual_suggestions['background']}")
        if visual_suggestions.get("core_image"):
            visual_parts.append(f"- **核心图示**: {visual_suggestions['core_image']}")
        if visual_suggestions.get("layout"):
            visual_parts.append(f"- **布局**: {visual_suggestions['layout']}")
        if visual_suggestions.get("image_url"):
            visual_parts.append(f"- **图片链接**: {visual_suggestions['image_url']}")
        visual_section = "\n".join(visual_parts)

    # Build animation effects section
    animation_section = ""
    if animation_effects:
        animation_parts = ["### 动画效果"]
        if animation_effects.get("elements"):
            for elem in animation_effects["elements"]:
                animation_parts.append(f"- {elem}")
        elif animation_effects.get("description"):
            animation_parts.append(animation_effects["description"])
        animation_section = "\n".join(animation_parts)

    # Build speaker notes section
    speaker_notes_section = ""
    if speaker_notes:
        speaker_notes_section = f"### 演讲者备注\n\n{speaker_notes}"

    return VUE_COMPONENT_PROMPT.format(
        slide_content=slide_content,
        visual_suggestions=visual_section or "(无特定视觉建议)",
        animation_effects=animation_section or "(使用默认动画)",
        speaker_notes_section=speaker_notes_section,
    )
