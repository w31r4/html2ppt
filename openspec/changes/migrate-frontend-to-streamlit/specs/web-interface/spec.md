## MODIFIED Requirements

### Requirement: 大纲编辑界面
系统 SHALL 提供Markdown编辑器供用户编辑生成的大纲。

**实现变更**: 从 React CodeMirror 迁移到 Streamlit + streamlit-ace 组件。

#### Scenario: 显示生成的大纲
- **WHEN** 大纲生成完成
- **THEN** 应在 streamlit-ace 编辑器中显示Markdown格式的大纲
- **AND** 提供语法高亮

#### Scenario: 实时编辑功能
- **WHEN** 用户编辑大纲内容
- **THEN** 应通过 st.session_state 保存更改
- **AND** 提供保存按钮确认变更

#### Scenario: 大纲预览功能
- **WHEN** 用户编辑大纲时
- **THEN** 应提供 st.expander 可展开的 Markdown 预览面板
- **AND** 预览应在用户触发时更新

### Requirement: 结果预览界面
系统 SHALL 提供生成结果的预览功能。

**实现变更**: Vue 组件预览通过 iframe 嵌入独立的 Vue Preview Service。

#### Scenario: Slides预览模式
- **WHEN** 生成完成
- **THEN** 应显示 slides 的预览视图
- **AND** 通过 st.tabs 支持 slide 间导航

#### Scenario: 代码查看模式
- **WHEN** 用户选择查看源码
- **THEN** 应在 st.code 组件中显示生成的 Slidev Markdown 代码与 Vue 组件源码
- **AND** 提供语法高亮

#### Scenario: Vue组件预览
- **WHEN** 用户切换到组件预览
- **THEN** 应通过 st.components.v1.iframe 嵌入 Vue Preview Service
- **AND** 组件代码通过 URL 参数或 postMessage 传递给预览服务
- **AND** 支持按页切换预览

### Requirement: 响应式设计
系统界面 SHALL 支持多种设备和屏幕尺寸。

**实现变更**: Streamlit 原生响应式布局替代 TailwindCSS。

#### Scenario: 桌面端布局
- **WHEN** 在桌面浏览器访问
- **THEN** 应使用 st.columns 显示多列布局
- **AND** 充分利用屏幕空间

#### Scenario: 移动端适配
- **WHEN** 在移动设备访问
- **THEN** Streamlit 原生响应式自动切换为单列布局
- **AND** 保持功能可用性

## ADDED Requirements

### Requirement: Vue Preview Service
系统 SHALL 提供独立的 Vue 组件预览服务。

#### Scenario: 启动预览服务
- **WHEN** Docker Compose 启动时
- **THEN** Vue Preview Service 应在独立端口 (5173) 启动
- **AND** 通过 nginx 在 /preview/* 路径提供访问

#### Scenario: 接收组件代码
- **WHEN** Streamlit 前端请求预览 Vue 组件
- **THEN** 预览服务应通过 URL query parameter 或 postMessage 接收 base64 编码的 Vue SFC 代码
- **AND** 在浏览器端编译并渲染组件

#### Scenario: 渲染 Vue SFC
- **WHEN** 预览服务接收到 Vue SFC 代码
- **THEN** 应使用 @vue/compiler-sfc 在浏览器端编译组件
- **AND** 使用 Vue 3 runtime 渲染到页面
- **AND** 应用 UnoCSS 样式

#### Scenario: 处理渲染错误
- **WHEN** Vue 组件编译或渲染失败
- **THEN** 应在预览区域显示错误信息
- **AND** 不应导致整个预览服务崩溃

### Requirement: Streamlit 页面导航
系统 SHALL 提供清晰的多页面导航结构。

#### Scenario: 侧边栏导航
- **WHEN** 用户访问 Streamlit 应用
- **THEN** 应在侧边栏显示页面导航菜单
- **AND** 当前页面应高亮显示

#### Scenario: 页面间状态传递
- **WHEN** 用户在页面间导航
- **THEN** session_id 应通过 st.session_state 或 query params 保持
- **AND** 不应丢失当前工作会话

### Requirement: Nginx 统一路由
系统 SHALL 通过 Nginx 统一管理所有服务的访问入口。

#### Scenario: 路由分发
- **WHEN** 用户访问应用
- **THEN** Nginx 应根据路径前缀分发请求：
  - `/` → Streamlit 服务 (8501)
  - `/api/*` → FastAPI 后端 (8000)
  - `/preview/*` → Vue Preview Service (5173)

#### Scenario: 跨服务通信
- **WHEN** Streamlit 需要调用后端 API
- **THEN** 应通过 nginx 代理的 /api/* 路径访问
- **AND** 不应出现 CORS 问题