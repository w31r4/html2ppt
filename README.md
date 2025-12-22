# HTML2PPT

🎯 AI驱动的演示文稿生成器 - 将需求描述转换为精美的Slidev演示文稿

## ✨ 功能特性

- **智能大纲生成** - AI自动分析需求，生成包含视觉建议和动画效果的结构化大纲
- **人工审核编辑** - 支持Markdown编辑器实时调整大纲内容
- **Vue组件生成** - 自动生成带动画效果的Vue组件（.vue + `<style scoped>`）
- **Slidev格式导出** - 一键导出兼容Slidev的Markdown演示文稿
- **组件打包导出** - 可下载包含slides.md与components/*.vue的zip
- **多LLM后端支持** - 支持OpenAI、Google Gemini、Azure OpenAI等

## 🛠️ 技术栈

**后端**
- Python 3.12+
- FastAPI - 高性能API框架
- LangGraph - LLM工作流编排
- LangChain - LLM集成

**前端**
- React 18 + TypeScript（支持预览Vue组件）
- Vite 6 - 构建工具
- TailwindCSS - 样式框架
- CodeMirror - Markdown编辑器

## 📦 快速开始

### 🐳 Docker 一键部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/your-username/html2ppt.git
cd html2ppt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 LLM API Key

# 3. 一键启动
docker compose up -d

# 4. 访问服务
# 打开浏览器访问 http://localhost:8912
```

**常用命令：**

```bash
# 查看日志
docker compose logs -f

# 停止服务
docker compose down

# 重新构建并启动
docker compose up -d --build

# 查看数据卷
docker volume ls | grep html2ppt
```

---

### 手动安装

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/html2ppt.git
cd html2ppt
```

#### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置你的API密钥：

```env
# =============================================================================
# 基础配置
# =============================================================================

# 选择LLM提供商: openai, azure_openai, gemini
HTML2PPT_LLM_PROVIDER=openai

# API密钥
HTML2PPT_LLM_API_KEY=sk-your-api-key-here

# 模型名称
HTML2PPT_LLM_MODEL=gpt-4o

# =============================================================================
# 自定义端点配置（可选）
# =============================================================================

# 自定义API端点URL（支持任何OpenAI兼容的服务）
# 取消注释并填写你的端点URL
# HTML2PPT_LLM_BASE_URL=https://your-custom-endpoint.com/v1

# 常见自定义端点示例:
#   - vLLM:      http://localhost:8000/v1
#   - Ollama:    http://localhost:11434/v1
#   - OpenRouter: https://openrouter.ai/api/v1
#   - 硅基流动:   https://api.siliconflow.cn/v1
#   - 月之暗面:   https://api.moonshot.cn/v1
#   - DeepSeek:  https://api.deepseek.com/v1
#   - 通义千问:   https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 自定义端点配置示例

**使用硅基流动 (SiliconFlow):**
```env
HTML2PPT_LLM_PROVIDER=openai
HTML2PPT_LLM_BASE_URL=https://api.siliconflow.cn/v1
HTML2PPT_LLM_API_KEY=sk-your-siliconflow-key
HTML2PPT_LLM_MODEL=Qwen/Qwen2.5-72B-Instruct
```

**使用 OpenRouter:**
```env
HTML2PPT_LLM_PROVIDER=openai
HTML2PPT_LLM_BASE_URL=https://openrouter.ai/api/v1
HTML2PPT_LLM_API_KEY=sk-or-your-openrouter-key
HTML2PPT_LLM_MODEL=anthropic/claude-3.5-sonnet
```

**使用本地 Ollama:**
```env
HTML2PPT_LLM_PROVIDER=openai
HTML2PPT_LLM_BASE_URL=http://localhost:11434/v1
HTML2PPT_LLM_API_KEY=ollama
HTML2PPT_LLM_MODEL=llama3.2
```

#### 3. 安装后端依赖

```bash
# 推荐使用 uv 包管理器
uv sync

# 或使用 pip
pip install -e .
```

#### 4. 安装前端依赖

```bash
cd frontend
npm install
```

#### 5. 启动服务

**启动后端服务：**

```bash
# 使用 uvicorn
uvicorn src.html2ppt.api.app:app --reload --port 8000

# 或使用 python
python main.py
```

**启动前端开发服务器：**

```bash
cd frontend
npm run dev
```

访问 http://localhost:3000 开始使用。

## 🎮 使用流程

1. **输入需求** - 在首页描述你的演示文稿需求
2. **审核大纲** - AI生成大纲后，可以编辑调整内容
3. **确认生成** - 确认大纲后开始生成Vue组件和Slidev格式
4. **导出使用** - 下载slides.md或组件包，在Slidev项目中使用

## 📁 项目结构

```
html2ppt/
├── src/html2ppt/           # 后端源码
│   ├── agents/             # LangGraph工作流
│   │   ├── workflow.py     # 主工作流定义
│   │   ├── state.py        # 状态管理
│   │   ├── prompts.py      # LLM提示词模板
│   │   └── llm_factory.py  # LLM工厂类
│   ├── api/                # FastAPI接口
│   │   ├── app.py          # 应用入口
│   │   └── routes/         # API路由
│   └── config/             # 配置管理
├── frontend/               # 前端源码
│   ├── src/
│   │   ├── pages/          # 页面组件
│   │   ├── components/     # 通用组件
│   │   └── api/            # API客户端
│   └── ...
└── openspec/               # 项目规范文档
```

## 🔧 API端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/requirements` | 提交需求，创建会话 |
| GET | `/api/outline/{session_id}` | 获取生成的大纲 |
| PUT | `/api/outline/{session_id}` | 更新大纲内容 |
| POST | `/api/outline/{session_id}/confirm` | 确认大纲，开始生成 |
| GET | `/api/generation/{session_id}/status` | 获取生成状态 |
| GET | `/api/result/{session_id}` | 获取生成结果 |
| GET | `/api/export/{session_id}` | 导出slides.md |
| GET | `/api/export/{session_id}?include_components=true` | 导出slides.md与components/*.vue的zip |
| GET/PUT | `/api/settings/llm` | LLM配置管理 |

## 🎨 生成的大纲格式

```markdown
# 演示文稿主题

---

### Page 1: 封面页

*   **标题**: 主标题文字
*   **副标题**: 副标题或演讲者信息
*   **视觉建议**:
    *   **背景**: 使用深蓝色渐变背景
    *   **核心图片**: 主题相关的3D图标
    *   **布局**: 标题居中偏左
*   **动画效果**:
    *   主标题使用"淡入"效果
    *   副标题延迟后"从下方滑入"

---

### Page 2: 内容页
...
```

## 🎬 动画说明

- Slidev内动画使用`v-click/v-clicks`控制顺序
- 视觉动画在Vue组件内通过`<style scoped>`定义（预览页可静态/近似展示，Slidev中效果完整）

## ▶️ 与 Slidev 配合使用（详细）

本项目会输出两类产物：
- `slides.md`：主文稿
- `components/*.vue`：每页对应的Vue组件（可选导出zip）

### 方式 A：新建 Slidev 项目并替换

1. 创建新项目：
```bash
npm init slidev@latest
cd <your-slidev-project>
```

2. 将生成的 `slides.md` 覆盖到项目根目录：
```
<your-slidev-project>/slides.md
```

3. 将生成的 `.vue` 组件放入 Slidev 默认组件目录：
```
<your-slidev-project>/components/
```

4. 启动 Slidev：
```bash
npm install
npm run dev
```

Slidev 会自动注册 `components/` 下的组件，你在 `slides.md` 里写的 `<ComponentName />` 会自动生效。

### 方式 B：使用导出的组件包

如果你下载的是 zip 包（包含 `slides.md` 和 `components/*.vue`），直接解压后：
```
slides.md
components/
```
把它们复制到你的 Slidev 项目根目录即可。

### 目录结构示例

```
my-slidev/
├── slides.md
├── components/
│   ├── IntroSlide.vue
│   ├── MarketSlide.vue
│   └── SummarySlide.vue
└── package.json
```

### 前置约定

- 组件名需与 `slides.md` 中的标签一致（系统已保证）
- 组件使用 `Vue 3 SFC` 格式
- 动画建议通过 `v-click/v-clicks` 控制顺序，并在组件内定义 `@keyframes`

### 常见调整

- **主题**：修改 `slides.md` 全局 frontmatter，例如：
```markdown
---
theme: default
title: My Deck
---
```
- **单页布局**：在单页前加入 frontmatter：
```markdown
---
layout: cover
class: text-center
---
```
- **组件路径**：默认 `components/` 即可自动注册，无需手动 `import`

## 🔌 支持的LLM后端

| 提供商 | 推荐模型 | 特点 | 配置 |
|--------|----------|------|------|
| OpenAI | **GPT-5.2** ⭐, GPT-4o | 最先进的通用模型，强大的推理能力 | `OPENAI_API_KEY` |
| Google Gemini | **Gemini 3 Flash** ⭐, Gemini 3 Pro | 性价比最高，在多项基准测试中超越GPT-5.2 | `GOOGLE_API_KEY` |
| Anthropic | **Claude Opus 4.5** ⭐, Claude Sonnet 4.5 | 最佳代码生成能力，响应速度快 | `ANTHROPIC_API_KEY` |
| Azure OpenAI | GPT-5.2, GPT-4o | 企业级部署 | `AZURE_OPENAI_*` |
| 自定义端点 | Llama 3.3 70B, DeepSeek等 | 本地部署/开源模型 | `OPENAI_API_BASE` |

### 💡 模型选择建议

- **追求最佳效果**: Claude Opus 4.5 或 GPT-5.2
- **追求性价比**: Gemini 3 Flash（与Pro级模型效果相近，成本更低）
- **代码生成任务**: Claude Opus 4.5（在代码生成测试中表现最佳）
- **本地部署**: Llama 3.3 70B（开源，支持Ollama/vLLM）

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
