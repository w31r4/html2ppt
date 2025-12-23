# Change: Migrate Frontend from React to Streamlit

## Why

当前 React + TypeScript 前端技术栈对项目维护者造成负担。维护者不熟悉 React 生态，导致前端迭代效率低下。采用 Python 全栈方案（Streamlit）可以显著降低维护成本，使开发者能够专注于核心业务逻辑。

## What Changes

- **BREAKING**: 移除现有 React 前端应用 (`frontend/`)
- 新增 Streamlit 应用作为主界面 (`streamlit_app/`)
- 将 Vue 预览组件重构为独立的轻量级 Vite 服务 (`vue-preview-service/`)
- Streamlit 通过 iframe 嵌入 Vue 预览服务
- 调整 Docker Compose 编排以支持三服务架构
- **保留**: 后端 FastAPI 服务不变，Streamlit 作为 API 客户端

## Impact

- Affected specs: `web-interface`
- Affected code:
  - 移除: `frontend/` 整个目录
  - 新增: `streamlit_app/` 目录
  - 新增: `vue-preview-service/` 目录（精简版 Vite 服务，仅包含 VuePreview 组件）
  - 修改: `docker-compose.yml`
  - 修改: `README.md`

## Risk Assessment

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Streamlit 编辑器功能弱于 CodeMirror | 中 | 使用 st_ace 或 streamlit-code-editor 组件 |
| iframe 跨域问题 | 低 | 同一 docker-compose 网络，CORS 配置 |
| 首次加载性能 | 中 | Vue Preview 服务可延迟加载 |
| 部署复杂度增加（3服务 vs 2服务） | 低 | Docker Compose 统一管理 |

## Alternatives Considered

1. **保持 React 前端** - 不解决维护者技能缺口问题
2. **移除 Vue 预览功能** - 降低产品差异化价值
3. **使用 Gradio 替代 Streamlit** - Streamlit 生态更成熟，组件更丰富