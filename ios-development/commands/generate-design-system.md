---
name: generate-design-system
description: 基于 Apple HIG Design Token 标准生成 SwiftUI Design System 代码。
---

# Generate Design System

基于 Apple HIG Design Token 标准生成 SwiftUI Design System 代码。

## 触发时机

- 新项目初始化时（由 `/project-kickoff` 调用）
- 现有项目需要添加 Design System 时（单独调用）

## 流程

### 1. 确认项目路径

询问用户或自动检测：
- 当前目录是否为 Xcode 项目根目录？
- 如果不是，询问项目路径

### 2. 选择主题配置

询问用户：选择预设主题或自定义？

**预设主题**：
- **sporty**：高饱和度蓝色（H=210, chromaPeak=0.30）- 适合运动、活力类 App
- **diet**：温和绿色（H=145, chromaPeak=0.18）- 适合健康、饮食类 App
- **minimalist**：低饱和度灰色（H=260, chromaPeak=0.10）- 适合工具、效率类 App
- **custom**：用户自定义（询问 primaryHue, chromaPeak 等参数）

### 3. 选择目标平台

询问用户：
- iOS only
- macOS only
- iOS + macOS（生成平台适配代码）

### 4. 调用 generate-design-system skill

传递参数：
- 主题配置（theme: sporty/diet/minimalist/custom）
- 目标平台（platform: iOS/macOS/both）
- 项目路径

### 5. 生成文件结构

```
[ProjectName]/DesignSystem/
├── DesignSystem.swift          // 主文件（Spacing, CornerRadius, Shadow）
├── Colors+Tokens.swift         // 语义颜色（基于 OKLCH 生成）
├── Typography+Tokens.swift     // 字体样式（iOS/macOS Dynamic Type）
└── Components/                 // 可选：基础组件
    ├── DSButton.swift
    ├── DSCard.swift
    └── DSTextField.swift
```

### 6. 询问是否生成基础组件

询问用户：是否生成基础组件（DSButton, DSCard, DSTextField）？

如果选 Yes：
- 生成使用 Design Token 的基础组件
- 每个组件包含多个 variant（primary, secondary, tertiary 等）

### 7. 输出总结

```
✅ Design System 已生成

生成文件：
- [ProjectName]/DesignSystem/DesignSystem.swift
- [ProjectName]/DesignSystem/Colors+Tokens.swift
- [ProjectName]/DesignSystem/Typography+Tokens.swift
- [ProjectName]/DesignSystem/Components/ (3 个组件)

下一步：
1. 在 Xcode 中将 DesignSystem/ 文件夹添加到项目
2. 在 Views 中使用 `AppSpacing.md`, `Color.appPrimary` 等 Token
3. 运行 `/ui-review` 检查现有代码的 Token 合规性
```

## 原则

1. **不硬编码**：生成的代码不包含任何硬编码的数值
2. **平台适配**：iOS 和 macOS 使用不同的字号、间距、触摸目标
3. **可扩展**：用户可以基于生成的代码添加更多 Token
