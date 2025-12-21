## ADDED Requirements

### Requirement: Slidev Markdown生成
系统 SHALL 生成Slidev兼容的Markdown内容。

#### Scenario: 生成slide分隔符
- **WHEN** 生成多个slides
- **THEN** 每个slide之间应使用三个短横线分隔
- **AND** 第一个slide前不需要分隔符

#### Scenario: 全局与单页frontmatter
- **WHEN** 生成`slides.md`
- **THEN** 文件开头应包含全局frontmatter
- **AND** 需要特殊布局时为单页生成frontmatter

### Requirement: Vue组件引用
系统 SHALL 在Slidev Markdown中引用生成的Vue组件。

#### Scenario: 组件引用注入
- **WHEN** 某页包含复杂布局或交互
- **THEN** slides内容应包含对应的`<ComponentName />`标签
- **AND** 组件名与生成的`.vue`文件保持一致

#### Scenario: 组件目录约定
- **WHEN** 输出`.vue`文件
- **THEN** 应使用Slidev默认的`components/`目录
- **AND** 组件应可被Slidev自动注册

### Requirement: Slidev语法兼容性
系统生成的Markdown SHALL 完全兼容Slidev语法规范。

#### Scenario: 代码块处理
- **WHEN** 内容包含代码展示
- **THEN** 应使用Slidev支持的代码块语法
- **AND** 支持代码高亮和行号

#### Scenario: 图片和媒体处理
- **WHEN** 内容包含图片引用
- **THEN** 应使用Slidev支持的图片语法
- **AND** 支持图片尺寸和位置配置

#### Scenario: 动画和过渡效果
- **WHEN** 生成slides
- **THEN** 应支持基本的v-click动画指令
- **AND** 支持slide过渡效果配置

### Requirement: 输出与导出
系统 SHALL 输出完整可运行的Slidev内容。

#### Scenario: 生成slides.md主文件
- **WHEN** 生成完成
- **THEN** 应输出包含所有slides的`slides.md`
- **AND** 文件可直接被Slidev解析

#### Scenario: 生成Vue组件文件
- **WHEN** 组件生成完成
- **THEN** 应输出对应的`.vue`文件
- **AND** 可与`slides.md`配合直接运行

#### Scenario: 导出下载功能
- **WHEN** 用户请求导出
- **THEN** 系统应提供`slides.md`与`.vue`文件下载
- **AND** 可选择包含项目配置文件
