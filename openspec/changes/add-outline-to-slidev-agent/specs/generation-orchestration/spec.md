## ADDED Requirements

### Requirement: 按页并发生成
系统 SHALL 支持按页并发生成Vue组件与Slidev内容。

#### Scenario: 并发生成组件
- **WHEN** 大纲确认进入生成阶段
- **THEN** 系统应按页并发生成Vue组件
- **AND** 并发度应可配置

#### Scenario: 并发生成Markdown片段
- **WHEN** 生成slides内容
- **THEN** 系统应按页并发生成Markdown片段
- **AND** 支持按序组装最终`slides.md`

### Requirement: 增量结果回传
系统 SHALL 支持增量结果回传与展示。

#### Scenario: 分页结果获取
- **WHEN** 用户请求生成结果
- **THEN** 系统应允许返回已完成页面的组件与Markdown片段
- **AND** 标注各页完成状态

#### Scenario: 进度计算
- **WHEN** 按页生成进行中
- **THEN** 进度应基于已完成页面占比计算
- **AND** 总进度应包含Markdown组装阶段

### Requirement: 失败处理与重试
系统 SHALL 提供单页失败处理与重试机制。

#### Scenario: 单页失败
- **WHEN** 某页生成失败
- **THEN** 系统应记录失败原因
- **AND** 允许重试该页生成

#### Scenario: 失败降级
- **WHEN** 多次重试仍失败
- **THEN** 系统应提供占位内容以继续组装
- **AND** 向用户提示失败页面
