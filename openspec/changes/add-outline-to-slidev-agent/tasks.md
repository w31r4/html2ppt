# 实现任务清单

## 1. 项目基础设施

- [x] 1.1 更新pyproject.toml添加必要依赖（FastAPI, uvicorn, pydantic, langgraph, langchain, langchain-openai, langchain-google-genai等）
- [x] 1.2 创建项目目录结构（src/api, src/agents, src/converters, src/frontend）
- [x] 1.3 配置环境变量管理（.env文件和配置加载）
- [x] 1.4 设置日志系统
- [x] 1.5 创建LLM配置schema（支持多后端）

## 2. 后端API服务

- [x] 2.1 创建FastAPI应用入口（src/api/main.py）
- [x] 2.2 实现需求提交API端点（POST /api/requirements）
- [x] 2.3 实现大纲获取API端点（GET /api/outline/{session_id}）
- [x] 2.4 实现大纲更新API端点（PUT /api/outline/{session_id}）
- [x] 2.5 实现大纲确认API端点（POST /api/outline/{session_id}/confirm）
- [x] 2.6 实现生成状态API端点（GET /api/generation/{session_id}/status）
- [x] 2.7 实现结果获取API端点（GET /api/result/{session_id}）
- [x] 2.8 实现导出下载API端点（GET /api/export/{session_id}）
- [x] 2.9 实现LLM配置API端点（GET/PUT /api/settings/llm）
- [x] 2.10 配置CORS和API文档

## 3. LangGraph工作流

### 3.1 状态定义和图构建
- [x] 3.1.1 定义工作流状态Schema（src/agents/state.py）
- [x] 3.1.2 创建LangGraph StateGraph骨架（src/agents/workflow.py）
- [x] 3.1.3 实现节点间状态传递逻辑
- [x] 3.1.4 配置interrupt_before人工审核断点

### 3.2 大纲生成节点
- [x] 3.2.1 实现大纲生成节点函数
- [x] 3.2.2 设计大纲生成Prompt模板
- [x] 3.2.3 实现需求解析和大纲结构化逻辑
- [x] 3.2.4 实现大纲模板格式验证
- [x] 3.2.5 实现增补需求合并逻辑

### 3.3 React生成节点
- [x] 3.3.1 实现React生成节点函数
- [x] 3.3.2 设计React组件生成Prompt模板
- [x] 3.3.3 实现大纲到组件的映射逻辑
- [x] 3.3.4 实现生成代码验证
- [ ] 3.3.5 实现代码自动修复逻辑

### 3.4 Slidev转换节点
- [x] 3.4.1 实现Slidev转换节点函数
- [x] 3.4.2 实现React组件解析器
- [x] 3.4.3 实现JSX到Markdown转换器
- [x] 3.4.4 实现Slidev frontmatter生成器
- [x] 3.4.5 实现slides.md文件生成

## 4. 多LLM后端集成

- [x] 4.1 创建LLM工厂类（src/agents/llm_factory.py）
- [x] 4.2 实现OpenAI兼容后端支持（支持自定义base_url）
- [x] 4.3 实现Gemini后端支持
- [x] 4.4 实现API密钥验证
- [x] 4.5 实现请求重试和限流处理
- [x] 4.6 实现运行时后端切换
- [ ] 4.7 实现流式响应处理（用于进度显示）

## 5. 格式转换器

- [x] 5.1 实现Markdown大纲解析器（src/converters/outline_parser.py）- 集成在state.py中
- [x] 5.2 实现React组件分解器（src/converters/component_splitter.py）- 集成在workflow.py中
- [x] 5.3 实现Slidev格式转换器（src/converters/slidev_converter.py）- 集成在workflow.py中
- [ ] 5.4 实现项目打包器（生成完整Slidev项目zip）

## 6. 前端界面

### 6.1 项目设置
- [x] 6.1.1 初始化React + TypeScript + Vite项目（frontend/）
- [x] 6.1.2 配置TailwindCSS
- [x] 6.1.3 配置API客户端（axios封装）
- [x] 6.1.4 设置路由（React Router）

### 6.2 页面组件
- [x] 6.2.1 实现首页/需求输入页面
- [x] 6.2.2 实现大纲编辑页面（集成Markdown编辑器）
- [x] 6.2.3 实现生成进度页面
- [x] 6.2.4 实现结果预览页面
- [x] 6.2.5 实现设置页面（API密钥配置）

### 6.3 通用组件
- [x] 6.3.1 实现Markdown编辑器组件（使用CodeMirror）
- [x] 6.3.2 实现进度指示器组件
- [x] 6.3.3 实现Slides预览组件
- [x] 6.3.4 实现代码查看器组件
- [x] 6.3.5 实现导出按钮组件

## 7. 测试

- [ ] 7.1 编写Agent单元测试
- [ ] 7.2 编写API端点集成测试
- [ ] 7.3 编写转换器单元测试
- [ ] 7.4 编写前端组件测试

## 8. 文档和部署

- [ ] 8.1 更新README.md使用说明
- [ ] 8.2 编写API文档
- [ ] 8.3 创建Docker配置文件
- [ ] 8.4 编写部署指南