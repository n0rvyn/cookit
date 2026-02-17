---
name: ui-review
description: iOS/SwiftUI 的 UI 与交互规范审查，用于模块完成后的质量检查。
---

# UI Review

iOS/SwiftUI 代码的 UI + UX 专项审查。在功能模块完成后手动触发。

## 触发时机

- 完成一个功能模块的 UI 开发后
- PR 前的最终检查
- 用户说"检查一下 UI"或"review 一下交互"

## 流程

### 1. 确定范围

询问用户或自动识别：
- 指定文件：检查指定的 View 文件
- 指定目录：检查目录下所有 `*View.swift`、`*Screen.swift`
- 无指定：检查本次变更涉及的 UI 文件

### 2. 读取检查清单

1. 读取 `~/.claude/docs/ios-ui-checklist.md` 获取代码合规检查项
2. 读取 `~/.claude/docs/ui-design-principles.md` §13 检查清单 和 §16 页面构成模板

### 3. 逐文件检查

对每个 UI 文件，检查以下维度：

---

## Part A: 视觉规范（代码验证）

#### A1. 间距与布局（增强：Token 检查）

- [ ] 间距值是否为 8pt 倍数？（4/8/16/24/32）
- [ ] 是否使用项目 Design System Token？（`AppSpacing.xs/sm/md/lg` 而非硬编码）
- [ ] 触摸目标是否 ≥ 44pt？
- [ ] 安全区域是否正确处理？

**Token 检查**：调用 `validate-design-tokens` skill 检查硬编码间距。

#### A2. 颜色合规性（色彩策略归 `/design-review`）
- [ ] 是否使用语义颜色？（`Color.primary` 而非 `Color.black`）
- [ ] 是否避免硬编码颜色？（`Color(hex:)` 应定义在 Design System）
- [ ] 自定义颜色是否有 light/dark 变体？
- [ ] 对比度风险：浅色文字是否用在浅色背景上？（如 `.secondary` on `.secondary`）
- [ ] 不只靠颜色：状态/错误是否同时有图标或文字？（红绿色盲无法区分纯色差异）
- [ ] 透明度陷阱：`.opacity()` 在深色模式下是否仍可见？

#### A3. 字体
- [ ] 是否使用动态字体？（`.font(.body)` 而非 `.font(.system(size:))`）
- [ ] 金额/数字是否使用 `.monospacedDigit()`？

#### A4. 无障碍
- [ ] 图标按钮是否有 `.accessibilityLabel()`？
- [ ] 装饰性图片是否标记 `.accessibilityHidden(true)`？

---

## Part B: 交互完整性（代码验证）

#### B1. 状态完整性
检查每个异步操作（网络请求、数据库查询）是否处理四态：

| 状态 | 代码特征 |
|------|---------|
| Loading | `ProgressView()` 或 loading 状态变量 |
| Success | 正常内容展示 |
| Error | 错误视图 + 明确下一步 |
| Empty | `ContentUnavailableView` 或空状态占位 |

**检查方法**：
```swift
// 找到 async 调用
Task { await fetchData() }

// 验证是否有对应的状态处理
@State private var isLoading = false
@State private var error: Error?
// 且在 View 中有条件渲染
```

**常见问题**：
- ❌ 只处理 success，无 loading/error/empty
- ❌ error 只 print，不显示给用户
- ❌ 空列表显示空白而非占位

#### B2. 错误可行动
检查错误提示是否包含下一步：

```swift
// ✅ 好：告诉用户怎么办
.alert("加载失败", isPresented: $showError) {
    Button("重试") { Task { await retry() } }
    Button("取消", role: .cancel) { }
} message: {
    Text("请检查网络连接后重试")
}

// ❌ 坏：只说失败，不说怎么办
.alert("错误", isPresented: $showError) {
    Button("确定") { }
}
```

**检查项**：
- [ ] 错误提示是否有重试选项（如果操作可重试）？
- [ ] 错误提示是否说明可能原因或下一步？
- [ ] 是否区分可恢复错误和不可恢复错误？

#### B3. 交互防护
检查是否防止重复触发：

```swift
// ✅ 好：提交时禁用按钮
Button("提交") { Task { await submit() } }
    .disabled(isSubmitting)

// ❌ 坏：无防护，可重复点击
Button("提交") { Task { await submit() } }
```

**检查项**：
- [ ] 提交类按钮是否有 `.disabled()` 防重复？
- [ ] 或是否有 loading 状态替换按钮？
- [ ] 破坏性操作是否有 `.confirmationDialog()` 确认？

#### B4. 表单校验时机
检查校验是否在合理时机：

```swift
// ✅ 好：失焦时校验 + 提交前校验
TextField("Email", text: $email)
    .onSubmit { validateEmail() }
    .onChange(of: email) { if !email.isEmpty { validateEmail() } }

// ❌ 坏：每输入一个字符就报错
TextField("Email", text: $email)
    .onChange(of: email) { validateEmail() } // 输入 "a" 就报 "邮箱格式错误"
```

**检查项**：
- [ ] 是否避免"输入即报错"？
- [ ] 提交时是否校验所有必填项？
- [ ] 错误提示是否贴近对应字段？

#### B5. 导航状态保持
检查返回后状态是否丢失：

```swift
// ✅ 好：使用 @State 或持久化
@State private var scrollPosition: Int?

// ❌ 坏：每次进入都重新加载，丢失滚动位置
.onAppear { loadData() } // 无条件重载
```

**检查项**：
- [ ] 列表滚动位置是否保持？
- [ ] 表单部分填写后返回再进入是否保留？
- [ ] 是否避免 `.onAppear` 无条件重载覆盖用户状态？

#### B6. SwiftUI 反模式

> 参考：`ios-ui-checklist.md` §10

**检查项**：
- [ ] 可交互元素是否使用 `Button` 而非 `.onTapGesture`？
  **代码检查**：搜索 `.onTapGesture`，检查作用对象是否应该是 Button。
- [ ] View 中的异步任务是否使用 `.task {}` 而非裸 `Task {}`？
  **代码检查**：搜索 `Task {` 或 `Task.init`（不含 .task modifier），检查是否在 View body/onAppear 中。
- [ ] 同一 View 上是否有多个 `.sheet()` modifier？
  **代码检查**：搜索 `.sheet(`，按 View struct 分组，>1 个则标记。
- [ ] 是否使用 `DispatchQueue.main.asyncAfter` 做 Sheet 切换？
  **代码检查**：搜索 `asyncAfter`，检查上下文是否是关闭一个 sheet 后打开另一个。
- [ ] 是否使用废弃 API？（NavigationView、.foregroundColor、GeometryReader 嵌套）
- [ ] (iOS 26 target) 是否对内容区域误用 `.glassEffect()`？
  **代码检查**：搜索 `.glassEffect(`，检查作用对象是否在 View body/List/ScrollView 的内容层。
- [ ] (iOS 26 target) 是否手动给 Glass 元素加 `.shadow()`？
  **代码检查**：搜索 `.shadow(`，检查前方是否有 `.glassEffect(`。
- [ ] (iOS 26 target) Sheet 是否使用了 `presentationBackground()`？
  **代码检查**：搜索 `presentationBackground`，在 iOS 26 target 上标记。

---

## Part C: 人工验证清单

以下项目 Claude 无法通过代码验证，需要人工运行后确认。根据代码分析生成针对性问题。

### C1. 任务流可完成性
基于代码分析识别的入口和流程，生成：

```
请人工验证以下任务流：
- [ ] 从 [入口A] 到 [目标B] 是否可顺利完成？
- [ ] 每一步的下一步操作是否明确？
- [ ] 是否有"死路"（无法返回或继续）？
```

### C2. 视觉层级
```
请人工验证：
- [ ] 页面主操作是否一眼可见？
- [ ] 主次按钮是否有明显区分？
- [ ] 信息层级是否清晰（标题 > 正文 > 辅助）？
```

### C3. 动画与过渡
```
请人工验证：
- [ ] 页面切换是否流畅？
- [ ] 是否有掉帧或卡顿？
- [ ] 动画是否有助于理解状态变化？
```

**代码检查提示**：if-else 视图切换需用 `Group {}` 包装后加 `.transition()` + `.animation()`。

### C4. 首屏体验
```
请人工验证：
- [ ] 冷启动后多久可以开始操作？
- [ ] 是否有骨架屏或占位减少等待感？
- [ ] 首屏加载失败时用户是否知道发生了什么？
```

---

## 4. 输出报告

```
## UI + UX Review Report

### 检查范围
- [文件列表]

### Part A: 视觉规范

#### 🔴 必须修复
- [file:line] 问题描述
  建议：具体修复方案

#### 🟡 建议修复
- [file:line] 问题描述
  建议：具体修复方案

### Part B: 交互完整性

#### 🔴 必须修复
- [file:line] 问题描述
  建议：具体修复方案
  验收：[可测试的验收标准]

#### 🟡 建议修复
- [file:line] 问题描述
  建议：具体修复方案

### Part C: 人工验证清单

基于代码分析，建议验证以下项目：
- [ ] [具体验证项1]
- [ ] [具体验证项2]
...

### 总结
- 检查文件数：N
- 视觉规范问题：N（必须修复 X，建议修复 Y）
- 交互完整性问题：N（必须修复 X，建议修复 Y）
- 人工验证项：N
```

---

## 严重度定义

| 级别 | 定义 | 示例 |
|------|------|------|
| 🔴 必须修复 | 阻断任务或造成困惑 | 无 loading 态、错误无提示、按钮可重复点击 |
| 🟡 建议修复 | 影响体验但不阻断 | 硬编码间距、缺少空状态 |
| ⚪ 通过 | 符合规范 | - |

---

## 原则

1. **代码可验证**：Part A/B 的结论必须基于代码证据
2. **具体可操作**：指出文件:行号，给出修复代码
3. **分级处理**：区分必须修复和建议修复
4. **人工补充**：Part C 明确标注需要运行后验证，不伪装成代码检查结论

---

## 串联提示

报告末尾附加：

```
---
💡 代码合规检查完成。如需进一步审查视觉层级、色彩策略、间距节奏等设计质量，请运行 `/design-review`。
```
