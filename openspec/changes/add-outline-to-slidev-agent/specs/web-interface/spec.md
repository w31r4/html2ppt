## ADDED Requirements

### Requirement: 需求输入界面
系统 SHALL 提供直观的Web界面供用户输入演示文稿需求。

#### Scenario: 显示需求输入表单
- **WHEN** 用户访问应用首页
- **THEN** 应显示一个文本输入区域
- **AND** 提供示例需求和使用提示

#### Scenario: 需求提交交互
- **WHEN** 用户填写需求并点击提交
- **THEN** 应显示加载状态
- **AND** 禁用提交按钮防止重复提交

### Requirement: 大纲编辑界面
系统 SHALL 提供Markdown编辑器供用户编辑生成的大纲。

#### Scenario: 显示生成的大纲
- **WHEN** 大纲生成完成
- **THEN** 应在编辑器中显示Markdown格式的大纲
- **AND** 提供语法高亮

#### Scenario: 实时编辑功能
- **WHEN** 用户编辑大纲内容
- **THEN** 应实时保存更改
- **AND** 支持撤销和重做操作

#### Scenario: 大纲预览功能
- **WHEN** 用户编辑大纲时
- **THEN** 应提供实时Markdown预览面板
- **AND** 预览应与编辑同步更新

### Requirement: 需求增补界面
系统 SHALL 支持用户在大纲编辑阶段添加额外需求。

#### Scenario: 添加增补需求
- **WHEN** 用户想要添加新需求
- **THEN** 应提供额外的输入区域
- **AND** 支持选择是追加还是重新生成

#### Scenario: 增补确认流程
- **WHEN** 用户提交增补需求
- **THEN** 应调用大纲生成Agent重新处理
- **AND** 显示新生成的大纲供审核

### Requirement: 生成进度界面
系统 SHALL 提供清晰的生成进度展示。

#### Scenario: 显示生成阶段
- **WHEN** 用户确认大纲开始生成
- **THEN** 应显示当前所处的生成阶段
- **AND** 显示各阶段的完成状态

#### Scenario: 显示详细日志
- **WHEN** 生成过程中
- **THEN** 应提供可展开的详细日志面板
- **AND** 实时更新日志内容

#### Scenario: 轮询状态更新
- **WHEN** 生成进行中
- **THEN** 前端应通过轮询获取最新状态
- **AND** 轮询间隔应可配置

### Requirement: 结果预览界面
系统 SHALL 提供生成结果的预览功能。

#### Scenario: Slides预览模式
- **WHEN** 生成完成
- **THEN** 应显示slides的预览视图
- **AND** 支持slide间导航和全屏预览

#### Scenario: 代码查看模式
- **WHEN** 用户选择查看源码
- **THEN** 应显示生成的Slidev Markdown代码与Vue组件源码
- **AND** 提供语法高亮

#### Scenario: Vue组件预览
- **WHEN** 用户切换到组件预览
- **THEN** 应渲染生成的`.vue`组件
- **AND** 支持按页切换预览

### Requirement: 导出下载界面
系统 SHALL 提供便捷的导出和下载功能。

#### Scenario: 下载slides.md
- **WHEN** 用户点击下载按钮
- **THEN** 应下载生成的slides.md文件
- **AND** 文件名应包含项目名称

#### Scenario: 下载完整项目
- **WHEN** 用户选择下载完整项目
- **THEN** 应下载包含package.json等配置的zip文件
- **AND** 项目应可直接npm install && npm run dev运行

### Requirement: API密钥配置界面
系统 SHALL 提供Gemini API密钥的配置界面。

#### Scenario: 首次配置引导
- **WHEN** 用户首次使用且未配置API密钥
- **THEN** 应显示配置引导界面
- **AND** 提供获取API密钥的链接

#### Scenario: 密钥验证反馈
- **WHEN** 用户输入API密钥
- **THEN** 应验证密钥有效性
- **AND** 显示验证结果

### Requirement: 响应式设计
系统界面 SHALL 支持多种设备和屏幕尺寸。

#### Scenario: 桌面端布局
- **WHEN** 在桌面浏览器访问
- **THEN** 应显示多列布局
- **AND** 充分利用屏幕空间

#### Scenario: 移动端适配
- **WHEN** 在移动设备访问
- **THEN** 应切换为单列布局
- **AND** 保持功能可用性
