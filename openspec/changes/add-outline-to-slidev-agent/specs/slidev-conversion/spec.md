## ADDED Requirements

### Requirement: React组件分解
系统 SHALL 将生成的React组件代码分解为独立的页面单元。

#### Scenario: 识别组件边界
- **WHEN** 处理生成的React代码
- **THEN** 系统应识别每个独立的函数组件
- **AND** 提取组件的内容和样式

#### Scenario: 提取组件元数据
- **WHEN** 分解组件时
- **THEN** 应提取组件名称、props定义和JSX结构
- **AND** 保留组件间的顺序关系

### Requirement: Slidev Markdown格式转换
系统 SHALL 将分解后的React组件转换为Slidev兼容的Markdown格式。

#### Scenario: 生成slide分隔符
- **WHEN** 转换多个组件为slides
- **THEN** 每个slide之间应使用三个短横线分隔
- **AND** 第一个slide前不需要分隔符

#### Scenario: 转换JSX到Markdown
- **WHEN** 处理JSX内容
- **THEN** 应将标题元素转换为Markdown标题
- **AND** 将列表元素转换为Markdown列表
- **AND** 将文本内容保留为纯文本

#### Scenario: 样式转换处理
- **WHEN** 处理TailwindCSS样式
- **THEN** 应转换为Slidev支持的内联样式或UnoCSS类
- **AND** 保留布局和排版效果

### Requirement: Slidev Frontmatter生成
系统 SHALL 为生成的slides添加适当的Slidev frontmatter配置。

#### Scenario: 全局frontmatter
- **WHEN** 生成slides.md文件
- **THEN** 文件开头应包含全局frontmatter配置
- **AND** 配置应包含theme、title等基本信息

#### Scenario: 单页frontmatter
- **WHEN** 某个slide需要特殊布局或配置
- **THEN** 该slide应有独立的frontmatter块
- **AND** 支持layout、class等常用属性

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

### Requirement: Slidev项目输出
系统 SHALL 输出完整可运行的Slidev项目结构。

#### Scenario: 生成slides.md主文件
- **WHEN** 转换完成
- **THEN** 应生成包含所有slides的slides.md文件
- **AND** 文件应可直接被Slidev解析

#### Scenario: 导出下载功能
- **WHEN** 用户请求导出
- **THEN** 系统应提供slides.md文件下载
- **AND** 可选择包含package.json等项目配置文件

#### Scenario: Slidev预览集成
- **WHEN** 用户请求在线预览
- **THEN** 系统应启动Slidev开发服务器
- **AND** 提供预览链接给用户