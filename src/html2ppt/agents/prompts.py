"""Prompt templates for LLM agents."""

OUTLINE_GENERATION_PROMPT = """你是一位专业的演示文稿设计师。根据用户的需求描述，生成一份结构清晰的Markdown大纲。

## 需求描述

{requirement}

{supplement_section}

## 大纲格式要求

1. 使用一级标题(#)作为演示文稿主题
2. 使用二级标题(##)作为各个章节
3. 使用无序列表(-)列出每个章节的要点
4. 每个章节包含1-5个要点
5. 大纲层级不超过3级
6. 可选添加speaker notes块

## 示例格式

```markdown
# 演示文稿主题

## 第一章：开篇
- 背景介绍
- 核心问题引入
- 本次演讲目标

## 第二章：主要内容
- 关键概念解释
- 案例分析
- 数据支撑

## 第三章：总结
- 核心要点回顾
- 行动建议
- Q&A

<!-- speaker notes
这里是演讲者备注
-->
```

## 生成要求

- 直接输出Markdown格式的大纲
- 不要添加任何解释性文字
- 确保内容与用户需求相关
- 控制在3-7个章节之间
"""

REACT_COMPONENT_PROMPT = """你是一位专业的React前端开发工程师。根据提供的演示文稿章节内容，生成一个用于Slidev展示的React组件。

## 章节信息

标题: {section_title}
要点:
{section_points}

{speaker_notes_section}

## 组件要求

1. 使用TypeScript + React函数组件
2. 使用TailwindCSS进行样式设计
3. 组件应适合16:9的幻灯片展示
4. 保持简洁清晰的视觉层次
5. 组件名称使用PascalCase，基于章节标题

## 示例组件

```tsx
import React from 'react';

interface SlideProps {{
  className?: string;
}}

const IntroductionSlide: React.FC<SlideProps> = ({{ className = '' }}) => {{
  return (
    <div className={{`flex flex-col items-center justify-center h-full p-8 ${{className}}`}}>
      <h1 className="text-4xl font-bold text-gray-800 mb-6">
        章节标题
      </h1>
      <ul className="text-xl text-gray-600 space-y-4">
        <li className="flex items-center">
          <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
          要点一
        </li>
        <li className="flex items-center">
          <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
          要点二
        </li>
      </ul>
    </div>
  );
}};

export default IntroductionSlide;
```

## 生成要求

- 只输出完整的TypeScript React组件代码
- 不要添加任何解释性文字
- 确保代码语法正确
- 使用现代React最佳实践
"""

SLIDEV_CONVERSION_PROMPT = """将以下React组件转换为Slidev兼容的Markdown格式。

## React组件代码

```tsx
{react_code}
```

## 转换规则

1. 提取组件中的标题，转换为Markdown标题
2. 提取列表项，转换为Markdown列表
3. 保留文本内容
4. TailwindCSS类转换为UnoCSS或内联样式
5. 添加适当的Slidev frontmatter

## 示例输出

```markdown
---
layout: default
---

# 章节标题

- 要点一
- 要点二
- 要点三

<style>
.slidev-layout {{
  @apply flex flex-col items-center justify-center;
}}
</style>
```

## 生成要求

- 直接输出Slidev Markdown格式
- 不要包含```markdown代码块包裹
- 确保格式与Slidev兼容
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


def get_react_prompt(
    section_title: str,
    section_points: list[str],
    speaker_notes: str | None = None,
) -> str:
    """Generate React component prompt for a section.

    Args:
        section_title: Section title
        section_points: List of bullet points
        speaker_notes: Optional speaker notes

    Returns:
        Formatted prompt string
    """
    points_text = "\n".join(f"- {point}" for point in section_points)

    speaker_notes_section = ""
    if speaker_notes:
        speaker_notes_section = f"""## 演讲者备注

{speaker_notes}
"""

    return REACT_COMPONENT_PROMPT.format(
        section_title=section_title,
        section_points=points_text,
        speaker_notes_section=speaker_notes_section,
    )


def get_slidev_prompt(react_code: str) -> str:
    """Generate Slidev conversion prompt.

    Args:
        react_code: React component code

    Returns:
        Formatted prompt string
    """
    return SLIDEV_CONVERSION_PROMPT.format(react_code=react_code)
