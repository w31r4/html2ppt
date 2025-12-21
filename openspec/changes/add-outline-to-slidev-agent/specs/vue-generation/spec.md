## ADDED Requirements

### Requirement: Vue SFC组件生成
系统 SHALL 根据确认的大纲生成对应的Vue SFC组件。

#### Scenario: 单页面组件生成
- **WHEN** 处理大纲中的一个章节
- **THEN** 应生成一个独立的Vue组件
- **AND** 组件内容覆盖该章节的核心要点与视觉建议

#### Scenario: 组件结构规范
- **WHEN** 生成Vue SFC代码
- **THEN** 应包含`<template>`与`<script setup>`块
- **AND** 可选包含`<style>`或使用UnoCSS类

### Requirement: 组件命名与文件输出
系统 SHALL 为每个页面生成稳定的组件名并输出`.vue`文件。

#### Scenario: 组件命名规则
- **WHEN** 基于章节标题生成组件名
- **THEN** 应输出PascalCase名称
- **AND** 遇到非法字符时自动清理与回退

#### Scenario: 文件输出路径
- **WHEN** 组件生成完成
- **THEN** 应输出为`.vue`文件
- **AND** 可按Slidev约定放置在`components/`目录

### Requirement: Slidev兼容样式与指令
系统 SHALL 生成与Slidev兼容的样式与指令。

#### Scenario: UnoCSS/Tailwind类支持
- **WHEN** 生成样式类
- **THEN** 应使用Slidev默认支持的UnoCSS类
- **AND** 保持布局与排版稳定

#### Scenario: 动画指令生成
- **WHEN** 需要展示动画
- **THEN** 应使用Slidev支持的`v-click`或相关指令
- **AND** 避免依赖运行期自定义动画库

### Requirement: 生成结果验证
系统 SHALL 验证生成的Vue SFC代码有效性。

#### Scenario: SFC语法验证
- **WHEN** 组件生成完成
- **THEN** 应验证SFC语法正确性
- **AND** 报告任何语法错误

#### Scenario: 自动修复尝试
- **WHEN** 检测到可修复的代码问题
- **THEN** 系统应尝试自动修复
- **AND** 记录修复操作日志
