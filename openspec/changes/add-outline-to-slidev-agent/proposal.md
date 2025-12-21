# Change: 添加需求大纲转Slidev PPT的Agent系统

## Why

用户需要一个能够将自然语言需求转化为演示文稿（PPT）的智能系统。传统的PPT制作流程繁琐且耗时，通过AI驱动的Agent系统可以大幅提升效率。该系统将支持迭代式的需求细化，并利用Gemini 3 Pro生成高质量的React组件，最终转换为Slidev格式的PPT。

## What Changes

### 核心功能
- **需求输入模块**：Web界面接收用户的自然语言需求描述
- **大纲生成引擎**：将需求拆分成结构化的Markdown大纲模板
- **人机交互循环**：用户可以审核、增补和修改大纲，形成迭代优化
- **React组件生成**：调用Gemini 3 Pro API根据确定的大纲生成React组件
- **页面分解器**：将生成的React组件分解为独立的页面单元
- **Slidev转换器**：将分解后的页面转换为Slidev兼容的Markdown格式

### 技术栈
- 前端：React + TypeScript + TailwindCSS
- 后端：Python FastAPI
- AI集成：Google Gemini 3 Pro API
- 输出格式：Slidev Markdown

## Impact

- Affected specs: 
  - `specs/outline-generation/spec.md` (新增)
  - `specs/react-generation/spec.md` (新增)
  - `specs/slidev-conversion/spec.md` (新增)
  - `specs/web-interface/spec.md` (新增)
- Affected code:
  - `src/api/` - 后端API服务
  - `src/frontend/` - React前端应用
  - `src/agents/` - Agent核心逻辑
  - `src/converters/` - 格式转换器