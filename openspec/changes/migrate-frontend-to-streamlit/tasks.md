## 1. Vue Preview Service 搭建

- [ ] 1.1 创建 `vue-preview-service/` 目录结构
- [ ] 1.2 从 `frontend/src/components/VuePreview.tsx` 提取核心逻辑到 `vue-preview-service/src/VuePreview.ts`
- [ ] 1.3 创建 `vue-preview-service/index.html` 入口页面
- [ ] 1.4 创建 `vue-preview-service/package.json` (最小依赖: vue, @vue/compiler-sfc, @unocss/core, vite)
- [ ] 1.5 创建 `vue-preview-service/vite.config.ts`
- [ ] 1.6 实现 URL query parameter 解码和组件渲染逻辑
- [ ] 1.7 创建 `vue-preview-service/Dockerfile`
- [ ] 1.8 本地测试：`cd vue-preview-service && npm install && npm run dev`，验证组件渲染

## 2. Streamlit 应用搭建

- [ ] 2.1 创建 `streamlit_app/` 目录结构
- [ ] 2.2 添加 Streamlit 依赖到 `pyproject.toml`: streamlit, streamlit-ace, httpx
- [ ] 2.3 创建 `streamlit_app/app.py` 主入口
- [ ] 2.4 创建 `streamlit_app/pages/1_🏠_首页.py` - 需求输入页
- [ ] 2.5 创建 `streamlit_app/pages/2_📝_大纲编辑.py` - 使用 st_ace 编辑器
- [ ] 2.6 创建 `streamlit_app/pages/3_⏳_生成中.py` - 进度轮询页
- [ ] 2.7 创建 `streamlit_app/pages/4_🎉_结果.py` - 包含 iframe 预览嵌入
- [ ] 2.8 创建 `streamlit_app/pages/5_⚙️_设置.py` - LLM 配置页
- [ ] 2.9 创建 `streamlit_app/api_client.py` - FastAPI 客户端封装
- [ ] 2.10 创建 `streamlit_app/Dockerfile`
- [ ] 2.11 本地测试：`streamlit run streamlit_app/app.py`，验证页面导航

## 3. Nginx 配置更新

- [ ] 3.1 创建 `nginx/nginx.conf` 配置文件
- [ ] 3.2 配置路由规则：`/` → streamlit:8501, `/api/*` → backend:8000, `/preview/*` → vue-preview:5173
- [ ] 3.3 配置 WebSocket 代理（Streamlit 需要）
- [ ] 3.4 创建 `nginx/Dockerfile`

## 4. Docker Compose 更新

- [ ] 4.1 修改 `docker-compose.yml` 添加 vue-preview 服务
- [ ] 4.2 修改 `docker-compose.yml` 添加 streamlit 服务
- [ ] 4.3 修改 `docker-compose.yml` 替换 frontend 服务为 nginx
- [ ] 4.4 配置服务间网络和依赖关系
- [ ] 4.5 运行 `docker compose up --build` 验证完整流程

## 5. 功能验证

- [ ] 5.1 验证首页需求提交流程
- [ ] 5.2 验证大纲编辑和保存功能
- [ ] 5.3 验证增补需求重新生成功能
- [ ] 5.4 验证生成进度页轮询更新
- [ ] 5.5 验证结果页 Vue 组件预览（iframe 嵌入）
- [ ] 5.6 验证 slides.md 下载功能
- [ ] 5.7 验证组件包 zip 下载功能
- [ ] 5.8 验证 LLM 设置页保存功能

## 6. 清理与文档

- [ ] 6.1 更新 `README.md` 新架构说明
- [ ] 6.2 更新 `.env.example` 如有新环境变量
- [ ] 6.3 标记 `frontend/` 目录为废弃（不立即删除，保留一个版本周期）
- [ ] 6.4 更新 `.gitignore` 如有新的忽略规则