## ADDED Requirements

### Requirement: 多LLM后端支持
系统 SHALL 支持多种LLM后端，包括OpenAI兼容API和Google Gemini。

#### Scenario: OpenAI兼容端点配置
- **WHEN** 用户选择OpenAI兼容后端
- **THEN** 系统应支持配置自定义base_url
- **AND** 支持vLLM、Ollama、Azure OpenAI等OpenAI兼容服务
- **AND** 支持第三方代理如OpenRouter

#### Scenario: Gemini API配置
- **WHEN** 用户选择Gemini后端
- **THEN** 系统应使用Google Generative AI API
- **AND** 支持配置API密钥和模型名称

#### Scenario: API密钥配置
- **WHEN** 系统启动时
- **THEN** 应从环境变量或配置文件读取LLM配置
- **AND** 验证配置有效性

#### Scenario: API调用失败重试
- **WHEN** LLM API调用失败
- **THEN** 系统应按指数退避策略重试最多3次
- **AND** 超过重试次数后向用户报告错误

#### Scenario: API限流处理
- **WHEN** 收到API限流响应
- **THEN** 系统应暂停请求并在指定时间后重试
- **AND** 向用户显示等待状态

#### Scenario: 运行时切换后端
- **WHEN** 用户在设置中修改LLM配置
- **THEN** 系统应动态切换到新的后端
- **AND** 无需重启应用

### Requirement: 大纲到React组件转换
系统 SHALL 根据确认的大纲生成对应的React组件代码。

#### Scenario: 单页面组件生成
- **WHEN** 处理大纲中的一个章节
- **THEN** 应生成一个独立的React函数组件
- **AND** 组件应包含该章节的所有内容要点

#### Scenario: 组件样式生成
- **WHEN** 生成React组件时
- **THEN** 应同时生成TailwindCSS样式类
- **AND** 样式应适合演示文稿展示

#### Scenario: 组件代码规范
- **WHEN** 生成React组件代码
- **THEN** 代码应使用TypeScript语法
- **AND** 遵循React函数组件最佳实践
- **AND** 包含必要的类型定义

### Requirement: 生成进度跟踪
系统 SHALL 提供React组件生成的实时进度反馈。

#### Scenario: 显示生成进度
- **WHEN** 组件生成过程中
- **THEN** 应显示当前正在生成的章节
- **AND** 显示总体完成百分比

#### Scenario: 生成完成通知
- **WHEN** 所有组件生成完成
- **THEN** 应通知用户并显示生成结果摘要
- **AND** 允许用户预览生成的组件

### Requirement: 生成结果验证
系统 SHALL 验证生成的React组件代码的有效性。

#### Scenario: 语法验证
- **WHEN** 组件代码生成完成
- **THEN** 系统应验证TypeScript/JSX语法正确性
- **AND** 报告任何语法错误

#### Scenario: 自动修复尝试
- **WHEN** 检测到可修复的代码问题
- **THEN** 系统应尝试自动修复
- **AND** 记录修复操作日志

### Requirement: 组件预览功能
系统 SHALL 提供生成组件的实时预览能力。

#### Scenario: 单组件预览
- **WHEN** 用户选择预览某个组件
- **THEN** 系统应渲染该组件并显示效果
- **AND** 支持响应式预览尺寸调整

#### Scenario: 全部slides预览
- **WHEN** 用户选择预览全部slides
- **THEN** 系统应按顺序展示所有生成的组件
- **AND** 支持slide间导航