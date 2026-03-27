#### DF. 设计忠实度验证（有设计文档的计划）

**目的**：验证计划完整且忠实地覆盖设计文档的所有要求，在执行前捕获 Gap A-E。

**前置条件**：计划头部引用了设计文档路径。如果无设计文档引用，跳过本策略。完整读取设计文档。

步骤：

**步骤 1：双向映射检查**

构建两个映射：
- 正向：设计文档每个要求 → 哪个计划 task 覆盖它
- 反向：计划每个 task → 映射到设计的哪个要求

```
[DF-1] 设计要求 → 计划映射
  - {design:L100-105 "事件队列...由感知部拉取"} → ✅ Task 2 / ❌ 无对应 task
  - {design:L258 "CEO maxTurns: 50"} → ✅ Task 8 / ❌ 无对应 task
  无对应 task 的设计要求 = Gap D 候选

[DF-2] 计划 task → 设计映射
  - Task 1 "Fix session resume" → ✅ design:L249 (resume + sessionId)
  - Task 12 "Add logging" → ⚠️ 设计未提及，需确认是否必要
  无对应设计要求的 task = 计划杜撰候选，需确认是否为必要补充
```

**步骤 2：设计锚点检查**

对每个映射到设计要求的计划 task，检查并补充以下锚点字段：

| 锚点 | 检查内容 |
|------|---------|
| `Design ref:` | 计划 task 是否引用了设计文档的具体段落？未引用则补充 |
| `Expected values:` | 设计是否为此 task 指定了具体值（参数、schema、枚举）？指定了但计划中没有则标注 |
| `Replaces:` | 此 task 是否替代旧代码？是的话计划是否列出了旧代码位置？ |
| `Data flow:` | 设计是否指定了上游→组件→下游路径？是的话计划中是否包含？ |
| `Quality markers:` | 设计是否指定了算法、数据结构或实现方式？是的话计划中是否包含？ |
| `Verify after:` | 实现此 task 后应执行哪些具体检查？ |

```
[DF-3] 缺失设计锚点
  - Task 5: 无 Expected values → 补充：schema 应含 assessment, recommendation(enum), confidence(0-1), reasoning
  - Task 7: 无 Quality markers → 补充：必须用 SDK 原生 outputFormat，不是 system prompt 指令返回 JSON
  - Task 3: 无 Replaces → 补充：替代 {file:line} 的 {旧实现}（通过 Grep 确认）
```

**步骤 3：Gap 扫描**

逐类检查：
- **Gap A（值错误）**：设计中的具体值是否全部出现在计划中
- **Gap B（未接入）**：计划中的新组件是否都有明确的数据流路径
- **Gap C（旧代码）**：设计中的"替代/删除 X"是否都有对应的计划 task 列出删除目标
- **Gap D（未建设）**：设计要求是否全部有对应的计划 task（来自步骤 1 的正向映射）
- **Gap E（退化）**：设计中描述了具体算法/方式的功能，计划是否使用了不同的实现方式
  **严重性规则**：
  - 如果 task 使用 `⚠️ SIMPLIFIED:` 标注并包含 `Simplification:` + `Design approach:` 字段 → 分类为 **acknowledged**（用户知情的简化，对应 implementation-reviewer 的 known simplification）
  - 如果 task 描述了与设计不同的实现方式但未标注 → 分类为 **must-revise**（必须修改：添加标注或恢复设计方案；对应 implementation-reviewer 的 silent degradation）
  - 关键词检测：task 描述中包含 "simplified"、"heuristic"、"placeholder"、"for now"、"basic"、"stub" 且无 `⚠️ SIMPLIFIED:` 标注 → must-revise

**步骤 4：隐含上下文检查**

从设计文档中提取未被计划显式处理的隐含前提、约束和业务规则：

```
[DF-4] 隐含上下文
  - {design:L100 的表述} 隐含前提：{提取的假设} → ✅ 计划步骤 {N} 已覆盖 / ❌ 未覆盖
  - {design:L200 描述的业务规则} → ✅ 计划步骤 {N} 处理 / ❌ 未处理
```

检查维度：
- 设计文档中"假设..."、"前提是..."、"要求..."等表述暗示的前置条件
- 未被单独列为需求但影响实现的业务规则
- 设计文档引用的外部约束（平台限制、API 契约、数据格式）

**步骤 5：粒度审计**

比较设计文档描述的步骤/阶段粒度与计划 task 的粒度：

```
[DF-5] 粒度检查
  - 设计 {section} 描述 {A→B→C} 三阶段 → 计划 Task {N} 合并为一步 → ⚠️ 丢失 {B 阶段的约束/检查点}
  - 设计 {section} 描述原子操作 {X} → 计划拆为 Task {N}+{M} → ⚠️ 引入中间状态 {状态描述}
  - 无粒度问题 → ✅
```

关注：
- 合并导致的约束丢失（中间检查点、阶段性验证、状态转换条件）
- 拆分引入的中间状态（设计未考虑的临时状态是否会被其他消费者观察到）

**步骤 6：边界场景覆盖**

检查设计文档中的边界场景、异常流程、错误处理是否被计划覆盖：

```
[DF-6] 边界场景
  - {design:L300 的边界场景描述} → ✅ 计划 Task {N} 处理 / ❌ 仅处理正常流程
  - {design:L350 的错误处理要求} → ✅ 计划 Task {N} 覆盖 / ❌ 未覆盖
```

检查维度：
- 设计文档中明确提到的边界条件和异常流程
- 空状态、极端数据量、并发访问、网络失败等设计隐含的边界场景
- 设计文档中"如果...则..."的条件分支是否全部被计划覆盖

**步骤 7：UX 交互走查**

**前置条件**：设计文档包含 `## UX Assertions` 段落。如果无此段落，跳过本步骤。

读取设计文档的 `## UX Assertions` 表格，逐条验证：

对每条 UX 断言（UX-NNN）：
1. 在计划中搜索 `UX ref:` 引用了该 ID 的 task
2. 如果无 task 引用 → 标记为 Gap D（UX 断言未被任何 task 覆盖）
3. 如果有 task 引用 → 读取 task 的步骤，执行断言的 Verification 列描述的检查方法：
   - 检查指定的组件/文件是否在 task 的 Files 列表中
   - 检查 task 步骤是否建立了断言描述的行为（状态替换 vs 追加、条件渲染逻辑、导航路径等）
   - 对比 task 的 `User interaction:` 描述与设计文档 User Journeys 中对应步骤的一致性

```
[DF-7] UX 交互走查
  - UX-001 "{断言内容}" → Task {N} — ✅ task 步骤覆盖了断言行为 / ❌ task 步骤未体现断言行为（{具体差异}）
  - UX-002 "{断言内容}" → ❌ 无 task 引用此断言
  - UX-003 "{断言内容}" → Task {N} — ⚠️ task 引用了但验证方法无法通过静态检查确认（需运行时验证）
```

反向检查：扫描计划中所有标记 `⚠️ No UX ref` 的 UI task，验证是否确实无对应 UX 断言，或是计划编写时遗漏了映射。
