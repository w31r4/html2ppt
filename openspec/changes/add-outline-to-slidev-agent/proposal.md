# Change: 添加需求大纲转Slidev PPT的Agent系统（Vue原生输出）

## Why

用户需要一个能够将自然语言需求转化为演示文稿（PPT）的智能系统。传统的PPT制作流程繁琐且耗时，通过AI驱动的Agent系统可以大幅提升效率。该系统将支持迭代式的需求细化，并直接生成原生Slidev所需的`slides.md`和Vue组件（`.vue`），同时前端可直接预览Vue组件。

## What Changes

### 核心功能
- **需求输入模块**：Web界面接收用户的自然语言需求描述
- **大纲生成引擎**：将需求拆分成结构化的Markdown大纲模板
- **人机交互循环**：用户可以审核、增补和修改大纲，形成迭代优化
- **Vue组件生成**：调用LLM根据确定的大纲生成Vue SFC组件（`.vue`）
- **Slidev内容生成**：按页生成Slidev Markdown片段并增量拼装`slides.md`
- **前端预览**：前端渲染生成的Vue组件并预览Slidev内容
- **异步并发生成**：按页并发生成组件与Markdown，减少等待时间

### 技术栈
- 前端：React + TypeScript + TailwindCSS（预览Vue组件）
- 后端：Python FastAPI
- AI集成：Google Gemini 3 Pro API
- 输出格式：Slidev Markdown + Vue SFC

## Impact

- Affected specs:
  - `specs/outline-generation/spec.md` (更新确认流程)
  - `specs/vue-generation/spec.md` (新增)
  - `specs/slidev-conversion/spec.md` (更新为原生Slidev输出)
  - `specs/generation-orchestration/spec.md` (新增)
  - `specs/web-interface/spec.md` (更新预览与轮询)
- Affected code:
  - `src/api/` - 后端API服务
  - `src/frontend/` - React前端应用
  - `src/agents/` - Agent核心逻辑与状态机
  - `src/converters/` - 格式转换器
