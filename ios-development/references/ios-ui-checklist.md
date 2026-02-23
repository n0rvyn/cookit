# iOS UI 检查清单
<!-- SECTION MARKERS: Each "section" comment line immediately precedes the ##
     heading it labels. Use Grep("<!-- section:", file) to find sections, then
     Read(file, offset, limit) to fetch only the relevant lines. -->

> 用于 execution-review 阶段检查 UI 代码合规性。
> 适用：iOS 26 / SwiftUI / Swift 6（兼容 iOS 18+）

---

<!-- section: 1. 间距与布局 keywords: spacing, layout, padding, 8pt grid, safe area, touch target -->
## 1. 间距与布局

### 1.1 8pt 网格
- 所有间距值必须是 8 的倍数（4pt 仅用于紧凑场景）
- ✅ `.padding(16)`, `.spacing(24)`
- ❌ `.padding(15)`, `.spacing(22)`

### 1.2 安全区域
- 内容不能被刘海/圆角/Home Indicator 遮挡
- ✅ `.safeAreaInset()`, `.ignoresSafeArea(.keyboard)`
- ❌ 全屏内容未处理安全区域

### 1.3 最小触摸目标
- 可点击元素最小 44×44pt
- ✅ `.frame(minWidth: 44, minHeight: 44)`
- ❌ 小于 44pt 的按钮/图标按钮

---

<!-- section: 2. 颜色 keywords: color, dark mode, contrast, semantic color, accessibility -->
## 2. 颜色

### 2.1 语义颜色优先
- 使用系统语义颜色，自动适配深色模式
- ✅ `Color.primary`, `Color.secondary`, `Color(uiColor: .systemBackground)`
- ❌ `Color.black`, `Color.white`, `Color(hex: "#000000")`

### 2.2 对比度
- 正文文字与背景对比度 ≥ 4.5:1
- 大字（18pt+粗体 或 24pt+）≥ 3:1
- 检查：浅灰文字在白色背景上是否可读

### 2.3 深色模式
- 所有自定义颜色必须定义 light/dark 变体
- ✅ Asset Catalog 中定义 Any/Dark
- ❌ 硬编码单一颜色值

### 2.4 对比度风险
- 避免浅色文字在浅色背景上（如 `.secondary` on `.secondary`）
- 避免深色文字在深色背景上
- `.opacity()` 值过低在深色模式下可能不可见

### 2.5 不只靠颜色
- 状态区分不能仅靠颜色（红绿色盲约 8% 男性）
- ✅ 错误状态 = 红色 + 错误图标 + 文字说明
- ❌ 仅用红/绿区分成功/失败

---

<!-- section: 3. 字体 keywords: typography, dynamic type, font size, SF Pro -->
## 3. 字体

### 3.1 动态字体
- 必须支持 Dynamic Type
- ✅ `.font(.body)`, `.font(.headline)`
- ❌ `.font(.system(size: 14))` 硬编码字号

### 3.2 字号下限
- 正文最小 11pt
- 辅助文字最小 9pt（仅用于极端空间受限）

### 3.3 SF 字体
- 系统 UI 使用 SF Pro
- 等宽数字使用 `.monospacedDigit()`
- ✅ 金额、倒计时使用 `.monospacedDigit()`

---

<!-- section: 4. 交互 keywords: interaction, button, loading, gesture, form, feedback -->
## 4. 交互

### 4.1 即时反馈
- 点击后 100ms 内必须有视觉反馈
- ✅ `.buttonStyle(.automatic)` 自带按下效果
- ❌ 自定义按钮无按下状态

### 4.2 加载状态
- 操作耗时 > 1s 必须显示加载指示器
- ✅ `ProgressView()`
- ❌ 界面冻结无反馈

### 4.3 手势
- 不覆盖系统手势（边缘返回、下拉刷新）
- 自定义手势需有明确的视觉提示

### 4.4 破坏性操作
- 删除/不可逆操作需二次确认
- ✅ `.confirmationDialog()` 或 `.alert()`
- 使用红色（`.destructive`）标识

### 4.5 状态完整性
- 每个异步操作必须处理四态：Loading / Success / Error / Empty
- ✅ 有 `isLoading` 状态 + `ProgressView()`
- ✅ 有 `error` 状态 + 错误视图
- ✅ 空列表显示 `ContentUnavailableView`
- ❌ 只处理 success，其他状态空白或卡死

### 4.6 错误可行动
- 错误提示必须告诉用户下一步
- ✅ "加载失败，请检查网络后重试" + 重试按钮
- ❌ "发生错误" + 确定按钮（用户不知道怎么办）

### 4.7 交互防护
- 提交类操作必须防止重复触发
- ✅ `Button("提交").disabled(isSubmitting)`
- ✅ 提交时显示 loading 替换按钮
- ❌ 无防护，可重复点击导致重复提交

### 4.8 表单校验时机
- 避免"输入即报错"（输入第一个字符就报格式错误）
- ✅ 失焦时校验 / 提交时校验
- ❌ `.onChange(of: text)` 立即校验空输入

### 4.9 导航状态保持
- 返回后不应丢失用户状态
- ✅ 滚动位置保持
- ✅ 表单部分填写内容保留
- ❌ `.onAppear` 无条件重载覆盖用户输入

---

<!-- section: 5. 可访问性 keywords: accessibility, VoiceOver, reduce motion, contrast -->
## 5. 可访问性

### 5.1 VoiceOver
- 所有可交互元素有 accessibility label
- 装饰性图片标记 `.accessibilityHidden(true)`
- ✅ `.accessibilityLabel("删除交易")`
- ❌ 图标按钮无标签

### 5.2 Reduce Motion
- 检查 `accessibilityReduceMotion`
- 尊重时提供替代动画或直接跳过

### 5.3 对比度调整
- 检查 `accessibilityDarkerSystemColors`
- 低对比度装饰色在开启时应加深

---

<!-- section: 6. 导航 keywords: navigation, NavigationStack, TabBar, back button -->
## 6. 导航

### 6.1 返回导航
- 支持边缘右滑返回（`NavigationStack` 默认支持）
- ❌ 自定义全屏手势覆盖系统返回

### 6.2 导航标题
- 使用 `.navigationTitle()` 而非自定义
- 大标题用于顶级页面，内联标题用于详情页

### 6.3 TabBar
- 最多 5 个 tab
- 每个 tab 有图标 + 文字标签
- 选中状态清晰可辨

---

<!-- section: 7. 系统控件 keywords: system controls, List, Sheet, Alert, Picker, TextField -->
## 7. 系统控件

### 7.1 优先使用原生（控件 + 行为 API）
- 有系统控件时不自定义
- ✅ `DatePicker`, `Picker`, `Toggle`, `Stepper`
- ❌ 自定义日期选择器（除非有特殊需求）
- 行为 API 同理：有声明式 API 时不手写状态机
- ✅ `ScrollPhase` 判断用户滚动 vs 系统布局
- ✅ `onScrollGeometryChange` 的 Bool transform 做阈值穿越检测
- ✅ `onGeometryChange` 替代 GeometryReader 嵌套
- ❌ 手写 hasSettled/canTrigger 状态机绕过值域错误
- ❌ 用原始 contentOffset 做绝对值判断（未归一化 contentInsets）

**替换系统控件前强制检查**（触发条件：即将使用 `.xxxHidden(true)`、自定义控件替代系统控件、或以"需要额外行为"为由覆盖系统默认行为时）：
1. 我在替换什么系统控件？
2. 替换理由是什么？
3. 列出至少 2 种不替换系统控件的替代方案（`.onDisappear`、`onChange`、容器层处理等）
4. 所有替代方案都不可行 → 问用户；否则 → 用替代方案

- ❌ "需要自定义行为"不是替换系统控件的充分理由
- ✅ 在系统控件之外的层级（容器、modifier、生命周期回调）添加行为

### 7.2 Sheet 与 Modal
- 使用 `.sheet()` 而非自定义遮罩
- 支持下拉关闭（`presentationDragIndicator(.visible)`）

### 7.3 Alert 与确认
- ✅ `.alert()`, `.confirmationDialog()`
- ❌ 自定义弹窗不符合系统风格

---

<!-- section: 8. 列表与滚动 keywords: list, scroll, LazyVStack, performance, ScrollView -->
## 8. 列表与滚动

### 8.1 List 规范
- 使用 `List` 而非 `ScrollView + VStack`（需要标准行为时）
- 行高一致，符合 HIG 推荐（44pt 最小）

### 8.2 空状态
- 列表为空时显示占位内容
- ✅ `ContentUnavailableView`
- ❌ 空白屏幕

### 8.3 加载更多
- 无限列表使用分页加载
- 底部显示加载指示器

---

<!-- section: 9. 表单 keywords: form, input, validation, keyboard, TextField -->
## 9. 表单

### 9.1 输入验证
- 错误信息就近显示
- 实时验证优于提交后验证

### 9.2 键盘
- 根据输入类型设置键盘（`.keyboardType()`）
- 支持键盘收起（`.scrollDismissesKeyboard()`）

### 9.3 必填标识
- 明确标识必填字段
- 提交前高亮未填必填项

---

<!-- section: 10. SwiftUI 反模式 keywords: anti-patterns, avoid, wrong, deprecated -->
## 10. SwiftUI 反模式

> 显式黑名单：AI 易犯的 SwiftUI 错误模式。

### 10.1 交互元素必须用 Button
- ❌ `.onTapGesture { action() }` 用于可交互元素
- ✅ `Button { action() } label: { ... }`
- 原因：`onTapGesture` 没有按下态视觉反馈、不被 VoiceOver 自动识别为可交互、不支持 `.disabled()`
- 例外：仅用于非语义性的手势（如双击缩放、画布拖拽）

### 10.2 异步任务必须绑定 View 生命周期
- ❌ 在 View body 或 `onAppear` 中用裸 `Task { await ... }`
- ✅ `.task { await ... }`（自动随 View 消失取消）
- ✅ 如果必须用 `Task {}`，保存 handle 并在 `.onDisappear` 中 `handle.cancel()`
- 原因：裸 Task 在 View 被 dismiss 后继续执行，更新已销毁的 @State 导致未定义行为

### 10.3 Sheet 状态管理
- ❌ 同一 View 上挂多个 `.sheet()` modifier（SwiftUI 可能只处理第一个）
- ✅ 用枚举统一管理：`@State private var activeSheet: SheetType?` + `.sheet(item: $activeSheet)`
- ❌ `DispatchQueue.main.asyncAfter(deadline: .now() + 0.3)` 做 sheet 切换（时机不可靠，dismiss 动画未完成时新 sheet 被静默丢弃）
- ✅ 用 `onChange(of: activeSheet)` 或 `.onDismiss` 回调触发下一个 sheet

### 10.4 废弃 API 黑名单
- ❌ `NavigationView` → ✅ `NavigationStack`
- ❌ `.foregroundColor()` → ✅ `.foregroundStyle()`
- ❌ `.background(Color.X)`（ShapeStyle 不匹配） → ✅ `.background { Color.X }` 或 `.background(.X)`（trailing closure / ShapeStyle）
- ⚠️ `@ObservedObject` / `@StateObject`（新代码不推荐） → ✅ `@Observable` + `@State`（iOS 17+）
  注：Apple 未正式废弃，但 Swift 6 并发模式下 @ObservedObject 有 init 隔离问题。新代码一律用 @Observable。
- ❌ `GeometryReader` 嵌套/滥用 → ✅ `containerRelativeFrame` (iOS 17+) / `onGeometryChange` (iOS 18+)

### 10.5 Dynamic Type 安全
- ❌ 文字旁边的图标/容器用固定 `.frame(width: 32, height: 32)`
- ✅ 用 `@ScaledMetric` 让尺寸随 Dynamic Type 缩放
- ❌ 固定高度的 HStack 包含 Text（AX5 下文字溢出）
- ✅ 去掉固定高度，或用 `ViewThatFits` 提供紧凑模式 fallback

### 10.6 大集合性能
- ❌ `ForEach(largeArray)` 在 `VStack` / `ScrollView + VStack` 中（全量渲染）
- ✅ 使用 `LazyVStack` 或 `List`
- 阈值：预估 > 20 项的集合必须用 Lazy 容器

### 10.7 iOS 26 Glass 反模式
- ❌ 对内容区域（列表、卡片、表单）使用 `.glassEffect()` — Glass 仅用于导航/控制层
- ❌ 手动给 Glass 元素添加 `.shadow()` — 系统自适应管理
- ❌ iOS 26 上用 `presentationBackground()` 覆盖 Sheet Glass 效果
- ❌ 嵌套 Glass 元素未用 `GlassEffectContainer` 包裹 — Glass 无法采样其他 Glass
- ❌ 用 `.glassEffect(.clear)` 替代 `.regular` — `.clear` 仅限媒体背景场景
- ✅ 用 `#available(iOS 26, *)` 包裹 Glass-only API，fallback 到 `.borderedProminent` 等

---

## 快速自检

执行 UI 代码 review 时，按顺序检查：

1. [ ] 是否使用硬编码颜色/间距/字号？
2. [ ] 触摸目标是否 ≥ 44pt？
3. [ ] 是否支持 Dynamic Type？
4. [ ] 是否有深色模式变体？
5. [ ] 交互元素是否有 accessibility label？
6. [ ] 破坏性操作是否有确认？
7. [ ] 空状态是否处理？
8. [ ] 是否使用系统控件而非自定义？
9. [ ] 手写状态逻辑是否有对应的声明式平台 API？（ScrollPhase、onGeometryChange 等）
10. [ ] 可交互元素是否使用 Button 而非 onTapGesture？
11. [ ] 异步任务是否使用 .task {} 而非裸 Task {}？
12. [ ] 是否有废弃 API？（NavigationView、.foregroundColor、GeometryReader 嵌套）
13. [ ] 同一 View 上是否有多个 .sheet() modifier？
14. [ ] 动效时长是否合理？（微交互 80-200ms，空间位移 200-500ms）
15. [ ] 图标是否统一？（同风格、同粗细、同渲染模式）
16. [ ] 深色模式下有色背景 opacity 是否 ≥ 0.15？
17. [ ] iOS 26: 是否对内容区域误用 .glassEffect()？
18. [ ] iOS 26: 是否手动给 Glass 元素加 .shadow()？
19. [ ] 页面是否有 ≥ 3 级文字层级且通过眯眼测试？
20. [ ] 页面区域划分是否清晰（不是一长串无分组元素）？

---

<!-- section: 11. 设计质量 keywords: design quality, visual, professional, polish -->
## 11. 设计质量

> 供 `/design-review` 命令参考。关注视觉打磨感而非代码合规。
> 完整设计原则和精确数值标准见 `~/.claude/docs/ui-design-principles.md`

### 11.1 视觉层级

- 页面至少 3 级文字层级（标题 / 正文 / 辅助），通过字重和颜色区分
- 标题与正文差异：字重 ≥ 2 级 或 字号 ≥ 4pt
- 辅助信息使用 `.secondary` / `.tertiary` 降级
- ❌ 所有文字同大小同颜色 = 无层级

### 11.2 色彩策略

- 一个强调色（key color）表示可交互，全局统一
- 页面颜色种类 ≤ 5（含语义色）
- 色彩比例按 App 类型（工具型 ~80/15/5，内容型 ~60/30/10）；强调色仅用于可交互元素
- 深色模式下高饱和色需降低亮度

### 11.3 间距节奏

- 同级元素间距一致
- 内部间距 ≤ 外部间距（卡片 padding ≤ 卡片间距）
- 避免连续紧凑间距导致视觉拥挤
- 页面水平边距统一（通常 16pt）

### 11.4 对齐一致性

- 同一列表/容器内元素统一对齐方式
- 不混用左对齐和居中对齐
- 多个 VStack alignment 保持一致

### 11.5 卡片与容器

- 同类卡片统一圆角 / 阴影 / 内边距
- 嵌套圆角递减（外 16 → 内 12 → 徽章 8）
- 阴影克制：opacity ≤ 0.08, radius ≤ 4
- 卡片内边距 ≥ 12pt

### 11.6 图标一致性

- 统一使用 SF Symbols
- 同上下文图标使用相同 rendering mode
- 同级元素图标大小一致

### 11.7 设备验证（人工）

以下无法通过代码验证，需在设备上执行：

1. **眯眼测试**：半闭眼看页面，能否分辨 3 级层级？主操作是否最突出？
2. **对齐审查**：截图画参考线，左边缘是否对齐？间距是否均匀？
3. **色彩感知**：灰度模式下层级是否仍清晰？深色模式下卡片层级可辨？
4. **留白与呼吸感**：内容是否有喘息空间？分组是否清晰？
5. **动效与过渡**：页面切换流畅？元素出现/消失有过渡？时长 200~350ms？
6. **首屏印象**：第一眼看到内容还是空白？整体感觉精致还是粗糙？
