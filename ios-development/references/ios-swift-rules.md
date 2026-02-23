# iOS/Swift Development Rules
<!-- SECTION MARKERS: Each "section" comment line immediately precedes the ##
     heading it labels. Use Grep("<!-- section:", file) to find sections, then
     Read(file, offset, limit) to fetch only the relevant lines. -->

> Extracted from global CLAUDE.md for plugin-based delivery. These rules are automatically loaded in iOS projects via the ios-development plugin.

<!-- section: Build-Check-Fix Cycle keywords: build, xcodebuild, check, fix, compile cycle, timing -->
## Build-Check-Fix Cycle

```
Write Code -> xcodebuild build -> Check errors -> Fix -> Repeat
```

**运行 xcodebuild 的时机**：
- 完成完整文件后
- 完成相关文件组后
- 修复错误后验证
- 提交代码前

**不要**：每几行代码就跑、只改注释/文档时跑

<!-- section: 通用约束 keywords: constraints, forbidden, required, main thread, API key, hardcoded -->
## 通用约束

```
禁止：在主线程执行耗时操作
禁止：硬编码 API Key 或敏感信息
禁止：硬编码 UI 文本（必须使用 LocalizedString）
禁止：硬编码 UI 尺寸/间距/颜色/字号（必须使用设计系统变量或系统语义值）
禁止：直接编辑 *.xcodeproj/project.pbxproj 或 *.xcworkspace（易损坏项目）

必须：所有 Service 使用 Protocol 抽象
必须：所有异步操作使用 async/await
必须：所有错误妥善处理
必须：所有 UI 文本使用本地化
必须：引用文件路径前用 Glob/Read 验证存在（不要照抄未验证的引用）
必须：写自定义状态管理/手势检测/布局逻辑前，先搜索平台是否提供声明式 API 解决同一问题（Apple 文档 / SwiftUI API 列表）。未搜索就写状态机或手工计算 = 违反本规则
```

<!-- section: Swift 6 并发原则 keywords: Swift 6, concurrency, MainActor, Sendable, @Model, actor -->
## Swift 6 并发原则

> 详细规范由 `references/swift-coding-standards.md` 提供。以下为关键要点。

- 所有 `@Model` 类型隐式 `@MainActor`，不可跨 actor 传递
- Service 单例统一 `@MainActor final class`
- 跨 actor 边界传递数据时，提取为 `Sendable` 值类型（struct/enum）
- `nonisolated` 用于不访问 actor 状态的纯计算方法
- 闭包捕获 `@MainActor` 属性时，用 `MainActor.run { ... }` 包裹

<!-- section: .foregroundColor 迁移策略 keywords: foregroundColor, foregroundStyle, migration, deprecation -->
## .foregroundColor 迁移策略

项目中 `.foregroundColor()` 存在大量调用（验证命令：`rg -c '\.foregroundColor\(' --type swift | awk -F: '{s+=$2}END{print s}'`）。无法一次性替换。
- 新代码：一律使用 `.foregroundStyle()`
- 改现有文件时：顺带替换该文件中的 `.foregroundColor()`
- 不做：专门发起批量替换（风险高、收益低）

<!-- section: iOS UI 规则（分层生效） keywords: UI rules, layers, design system, hardcoded values -->
## iOS UI 规则（分层生效）

**Layer 1 - 硬性禁令**（无条件生效，见上方「通用约束」）：
- 禁止硬编码 UI 尺寸/间距/颜色/字号

**Layer 2 - 计划阶段检查**（条件触发）：

触发条件：计划的主要目的是创建新 UI 页面/组件，或对现有 UI 做视觉重构。
不触发：修改业务逻辑顺带改一行 View 代码、添加调试 UI、纯文档修改。
示例：
  ✅ 触发：新建 SettingsTab、重构 InsightCard 布局
  ❌ 不触发：修改 SettingsTab 中一个按钮的 action closure

触发后执行：
1. 计划中所有 UI 尺寸必须标注对应设计系统变量
2. 无对应变量的值 → 标注 `⚠️ 待定` 并询问用户

<!-- section: 计划阶段架构审查（条件触发） keywords: architecture review, plan, triggers, parallel paths -->
## 计划阶段架构审查（条件触发）

触发条件：计划涉及新增触发/调度入口、新增数据处理路径、或重构已有机制的核心路径。
不触发：修复单个 bug（未涉及路径变更）、UI 显示修复、文档修改。
示例：
  ✅ 触发：新增定时任务调度器（新入口）
  ✅ 触发：重构 InspirationService 的事件分发机制（核心路径变更）
  ❌ 不触发：修复 InsightCard 的日期格式显示错误（单点 bug）
  ❌ 不触发：调整 SettingsTab 的布局间距（UI 显示）

触发后执行：
1. 追溯相关数据的完整路径（触发源 → 处理 → 持久化 → 展示），在计划中标注路径上每个节点的文件:行号
2. 在路径的每个处理节点，搜索是否有其他上游入口调用同一节点（= 并行路径）
3. 如发现并行路径，在计划中标注：
   ```
   ⚠️ 并行路径：{核心函数} 被 {路径A 文件:行号} 和 {路径B 文件:行号} 独立调用
   协调机制：{有/无}
   计划处理：{合并到路径A / 保留并新增协调 / 问用户}
   ```
4. 标注了"问用户"的架构冲突，禁止在未得到用户回复前继续编写计划的该部分

<!-- section: 计划编写原则 keywords: plan writing, plan draft, requirements -->
## 计划编写原则

- **约束前置** 计划开头列出：用户明确要求、技术约束、禁止事项
- **UX 决策显式化** 导航方式、过渡动画、交互反馈需在计划中列出，不留给实现时判断

<!-- section: 计划自检（M&M 测试） keywords: plan self-check, M&M test, surface, hidden, reinventing -->
## 计划自检（M&M 测试）

> 触发条件：计划涉及 ≥ 3 个文件变更，或涉及架构/数据流变更。
> 跳过：单文件修改、文档更新、简单 bug 修复。
> 示例：
>   ✅ 触发：重构洞察系统（涉及 Service + ViewModel + View）
>   ✅ 触发：新增数据同步路径
>   ❌ 跳过：修复 SettingsTab 中一个显示 bug（单文件）
>   ❌ 跳过：更新 CHANGELOG.md

计划末尾必须包含：

```
[自检-表面] 本次任务最容易违反哪条规则？
答：{规则名称} — {为什么这个任务容易踩这条规则}

[自检-隐蔽] 本次任务中，哪个"看起来已完成"的步骤最可能实际未生效？
答：{步骤} — {为什么它可能未生效（运行时条件、数据依赖、环境差异）}

[自检-造轮子] 本次方案中是否有手写逻辑在解决平台 API 已覆盖的问题？
答：{具体逻辑} — {已查 / 未查对应平台 API}（未查 = 必须先查再继续）
```

<!-- section: 计划执行原则 keywords: execution, ambiguity, interruption, clarification -->
## 计划执行原则

**歧义词检查**（执行前必做）：

> 触发条件：歧义词指向用户可见的 UI/UX 决策。
> 不触发：纯内部实现（"自定义 struct"、"新建 helper 函数"）。
> 示例：
>   ✅ 触发：计划说"自定义导航栏"（用户可见，需确认自定义程度）
>   ✅ 触发：计划说"新建一个卡片组件"（用户可见 View）
>   ❌ 不触发：计划说"自定义 Codable 解码逻辑"（纯内部）
>   ❌ 不触发：计划说"新建 helper extension"（纯内部）

计划中出现以下词汇时，禁止直接执行，必须先问用户确认具体含义：
- "自定义"：是完全重写，还是在原生基础上添加元素？
- "新建"：是新建独立组件，还是在现有结构中添加？
- "改造"：改多少？哪些保留哪些替换？

格式：
```
计划说「{原文}」，我的理解是：{具体实现方式}。是否正确？
```

<!-- section: 计划执行中断处理（必须遵守） keywords: interruption, pause, resume, mid-execution -->
## 计划执行中断处理（必须遵守）

**触发条件**：执行计划时遇到以下情况之一：
- API/框架 bug 或不兼容
- 依赖缺失或版本冲突
- 技术方案不可行
- 任何导致"原计划无法继续"的障碍

**强制动作**：
1. 立即停止执行
2. 输出格式：
   ```
   [计划中断]
   原计划：{计划内容}
   阻断原因：{具体问题 + 证据}
   可选方案：
   A. {方案A}
   B. {方案B}
   请选择。
   ```
3. 等待用户决定后再继续

**禁止**：以任何技术理由自行选择方案

<!-- section: 错误修复原则 keywords: error fix, bug fix, reproduce, confirm -->
## 错误修复原则

> 触发条件：用户指出实现逻辑或行为错误。
> 不触发：拼写错误、格式错误等显而易见的修正，直接执行。
> 示例：
>   ✅ 触发：用户说"这个按钮应该触发保存而不是删除"（行为错误）
>   ✅ 触发：用户说"排序逻辑反了"（逻辑错误）
>   ❌ 不触发：用户说"这里少了个右括号"
>   ❌ 不触发：用户说"变量名拼错了"

用户指出实现错误时，**禁止立即修改代码**。必须先执行：

1. 复述用户指出的问题
2. 陈述我理解的期望效果
3. **等待用户确认后再改**


<!-- section: 删除代码原则 keywords: delete code, search references, dead code -->
## 删除代码原则

删除任何状态变量、函数、文件前，必须：

1. **搜索引用**：`Grep` 该变量/函数名，列出所有引用位置
2. **检查用途**：每个引用位置的功能是什么？删除后功能是否受影响？
3. **关联处理**：功能需要保留则保留代码或用替代方案实现

<!-- section: 死代码/未接入代码处置原则 keywords: dead code, unused code, unreferenced, disposal -->
## 死代码/未接入代码处置原则

触发条件：发现代码存在但未被调用、功能写好但未接入主路径、或代码路径不可达

强制流程：
(1) **识别目标**：这段代码原本要解决什么问题？（读注释、git blame、周边调用关系）
(2) **验证问题**：这个问题在当前代码中还存在吗？（必须用 Grep/Read 验证，不凭推测回答"不存在"）
    - "不存在"的证据：当前代码已有其他机制解决同一问题，且该机制已接入并生效
    - "存在"的证据：问题场景可构造（例：对话超过 N 条消息时无截断），且无其他机制覆盖
(3) **决定处置**（必须输出下表，不可省略）：

    | 死代码 | 原本解决的问题 | 问题是否仍存在（附证据） | 处置 |
    |--------|-------------|---------------------|------|

    处置选项：
    - 问题存在 + 实现方式匹配当前架构 → 接入（重新连通到主路径）
    - 问题存在 + 实现方式不匹配 → 在当前架构中重新解决该问题，删除旧代码
    - 问题不存在（附证据） → 删除

禁止：
- 未填写上表就删除或保留任何死代码
- "问题是否存在"列填写"可能"/"不确定" — 不确定就去验证
- 以"死代码"为由跳过问题分析，直接执行删除
- 以"先保留以后可能用到"为由跳过问题分析，直接保留
