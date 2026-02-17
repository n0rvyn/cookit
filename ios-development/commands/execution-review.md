---
name: execution-review
description: 对照计划与代码执行结果，做实现完成度与偏差审查。
---

# Execution Review

Verify implementation matches plan. Use **after execution**.

## Principles

1. **Plan-to-code comparison**: Read actual code, compare field-by-field. Never assume "done".
2. **Actual execution**: Run build, run tests if required.
3. **Current phase only**: Future phase items are not missing.
4. **Distrust by default**: Existing files may not be correctly modified. Verify everything.

## Mandatory Checklist

### 1. Deletion Verification (必须)
For each file marked "删除" in plan:
```bash
ls <file_path> 2>/dev/null && echo "GAP: File should be deleted but exists"
```
- File still exists = **Critical Gap**
- Do NOT skip this check

### 2. Struct Field Comparison (必须)
For each struct defined in plan:
- Open plan's struct definition
- Open actual code's struct
- Compare line-by-line: field name, type, presence
- Missing field = **Gap**
- Different field name = **Gap** (unless explicitly renamed)

### 3. UI Element Verification (必须)
For each UI layout in plan:
- List all UI elements mentioned (e.g., `{headline}`, `{trend}`, `{surprise}`)
- Search actual View code for each element
- Missing element = **Gap**
- Element shows different data = **Gap**

### 4. "No Matches Found" = Red Flag (必须)
When search returns "No matches found":
- If plan says it should exist → **This is a Gap, must report**
- Do NOT skip or ignore
- Explicitly state: "Search for X returned no matches, but plan requires X"

### 5. Integration Point Verification (必须)
When plan says "A calls B" or "A uses B":
- Open A's code
- Search for B's invocation
- No call found = **Gap**

Example: Plan says "ChatView uses Backend /v1/chat"
→ Must find `LuminaBackendClient` or `/v1/chat` in ChatView/ChatViewModel
→ Finding `LocalChatModel` instead = **Gap**

### 6. Never Trust Existing Code (原则)
Even if file existed before plan:
- If plan says "modify" → Must read and verify modification
- If plan says "refactor" → Must verify new structure
- "File exists" ≠ "Correctly implemented"

### 7. 自作主张检测 (必须)
For each item in plan:
- Check if I marked it as "待决定"/"下一版本"/"可选"/"建议推迟"
- If plan explicitly required it → **Critical Gap**
- 计划明确要求 ≠ 我的建议
- 我没有权力决定不做计划中的明确要求

触发格式：
```
❌ Critical Gap: 自作主张推迟计划要求
   Plan: [计划原文]
   My excuse: [我给出的理由]
   Violation: 未经用户确认，擅自将计划要求降级为"建议"
```

### 8. Conditional Plan Branch Verification (必须)
When plan contains conditional logic ("如果 X 则 A，否则 B" / "verify first, then decide"):
- Check: was condition X actually verified during execution? (ran command, read output, tested on device)
- If no verification evidence exists → **Critical Gap**
- Choosing a branch without verifying the condition = 违反「证据先于声称」

触发格式：
```
❌ Critical Gap: 条件分支未验证
   Plan: [计划条件原文]
   Chosen branch: [执行时选择的分支]
   Verification evidence: [无 / 不充分]
   Violation: 未验证条件即选择分支
```

### 9. Removal-Replacement Reachability (必须)
When plan removes a UI element and claims a replacement exists elsewhere:
- Read the replacement code's **rendering conditions** (if/else, guard, optional binding)
- Trace data dependencies: what state must be non-nil/true for the replacement to render?
- Identify failure paths: what happens when the condition is false / data is nil?
- If replacement has conditional rendering and failure path shows nothing → **Gap**
- "Code exists" ≠ "User can see it at runtime"

触发格式：
```
❌ Gap: 替代元素运行时不可达
   Removed: [被移除的元素]
   Replacement: [声称的替代元素]
   Render condition: [替代元素的渲染条件]
   Failure path: [条件不满足时用户看到什么]
   Action Required: [确保替代元素在所有路径下可达，或保留原元素作为 fallback]
```

### 10. Term Consistency After Rename (必须)
When plan renames, replaces, or deprecates a component:
- List old terms that must not appear outside以下位置：`docs/07-changelog/`、`<details>` 折叠块内标注"已删除/已替代/历史"的段落
- Run: `rg -n "{old_terms}" {scope}` (exclude allowed paths with `--glob '!{path}'`)
- Each hit outside allowed locations = **Gap**
- 验证命令及输出必须展示

触发格式：
```
❌ Gap: 术语残留
   Old term: [旧术语]
   Found at: [file:line]
   Location type: [活跃文档 / changelog / 历史折叠块]
   Action Required: [替换 / 移入历史折叠块 / 添加"已删除"标注]
```

### 11. ADR Action Completeness (必须)
For each "替代/淘汰/废弃" statement in relevant ADRs:
- Check: does the ADR contain a concrete deletion checklist (file-level in ADR, method-level in execution plan)?
- Check: does the implementation actually delete/modify every listed item?
- "替代 X" in ADR + no deletion list = **Critical Gap** (ADR itself is incomplete)
- "替代 X" in ADR + deletion list present + X still in code = **Critical Gap** (execution incomplete)

触发格式：
```
❌ Critical Gap: ADR 删除清单未执行
   ADR: [ADR 编号 + "替代"原文]
   Deletion list item: [file/method/config]
   Actual status: [still exists / partially removed]
   Action Required: [complete the deletion]
```

### 12. Reverse Regression Reasoning (必须)

完成上述正向检查后，执行反向推理。正向检查验证"计划要求的是否做了"，反向推理验证"做了的是否会在运行时出问题"。

步骤：
1. 假设代码已部署，用户执行了本次变更涉及的核心操作，但遇到了一个 regression（不是 build 错误，是运行时行为异常）
2. 基于实际代码变更（不是计划，是代码），推理最可能的 regression：
   - 条件渲染：新增/修改的 if/guard/switch 在哪些状态组合下会导致 UI 不显示或显示错误内容？
   - 异步时序：新增的 async 调用是否可能在 View 已 dismiss 后回调？
   - 状态依赖：新增的状态变量初始值在冷启动 vs 热启动时是否一致？
   - 数据迁移：持久化模型的变更是否兼容旧数据？
3. 从用户操作反向追溯到代码变更点

输出格式（至少 1 条，至多 3 条）：
```
[反向推理] 假设 regression: {具体场景}
用户操作: {操作路径}
代码路径: {entry file:line} → {变更点 file:line} → {失败点 file:line}
正向检查是否覆盖: ✅ 已被检查项 {N} 覆盖 / ❌ 正向检查未覆盖
Action Required: {无 / 需验证 / 需修复}
```

如果所有推理出的 regression 均被正向检查覆盖 → 标注"反向推理未发现新问题"。
如果发现正向检查未覆盖的问题 → 作为额外 Gap 计入总结。

### 13. Rules Compliance Audit (必须)

基于本次 session 的 tool call 序列，对高频违反规则做事实提取。不做主观判断，只输出数字和事实。

#### 13.1 R6 — 证据先于声称

扫描本次 session 中所有"声称完成"的位置（输出包含"完成"、"已修复"、"通过"、"done"等词的 assistant 消息）。

对每个声称，向前检查最近的 tool call：
- ✅ 前方有 Bash（build/test）或 Grep 验证命令，且输出支持结论
- ⚠️ 前方有 Bash build 但无运行时路径验证（仅 build 通过）
- ❌ 前方无任何验证命令

输出：
```
[R6 审计] 声称完成 N 次：✅ X 次 / ⚠️ Y 次 / ❌ Z 次
```

#### 13.2 R9 — 遇阻修阻不绕路

列出本次 session 中所有被 Edit/Write 修改的文件，与计划中的目标文件列表对比。

输出：
```
[R9 审计] 编辑文件 N 个，计划内 X 个，计划外 Y 个
计划外文件：
- {file} — 原因：{次生问题修复 / 绕路 / 计划遗漏}
```

"原因"基于 tool call 上下文判断：如果计划外编辑前有该文件的 build error → 大概率次生问题；如果无 error 直接编辑 → 疑似绕路或计划遗漏。

#### 13.3 决策权 — UX 决策越权

扫描本次 session 中所有创建或大幅修改 View 文件（`*View.swift`、`*Screen.swift`、`*Card.swift`、`*Tab.swift`）的 Edit/Write 调用。

对每个 View 修改，检查：
- 修改是否涉及用户可见变化（布局、文案、导航、交互）
- 该决策是否在计划中明确指定
- 或是否通过 AskUserQuestion 确认过

输出：
```
[决策权审计] View 文件修改 N 个，涉及用户可见变化 X 个
- 计划指定：M 个
- 用户确认：K 个
- 未确认：J 个 → {文件列表}
```

#### 13.4 记录

如果 13.1-13.3 中任一项存在 ❌ 或"未确认"，将审计结果追加到 `~/.claude/rule-audit/YYYY-MM-DD.md`（当天文件已存在则追加，用 `---` 分隔不同 session）。

记录格式：
```markdown
## Session: {时间或任务简述}

### R6
{13.1 输出}
{❌ 项的具体位置和上下文}

### R9
{13.2 输出}

### 决策权
{13.3 输出}
```

全部 ✅ 且无"未确认"→ 不记录（只在报告中标注"规则审计通过"）。

---

## Code Scan (New Files)

- UI text uses `String(localized:)`
- UI state updates in Task wrapped with `await MainActor.run`
- Services have Protocol abstraction
- Errors have catch handling

## Doc Updates

- New/modified files → `docs/04-implementation/file-structure.md`
- Changes → `docs/07-changelog/YYYY-MM-DD.md`
- Architectural changes → create/update ADR

## Output Format

For each gap found:
```
❌ Gap: [Description]
   Plan: [What plan says]
   Actual: [What code does]
   File: [path:line_number]
   Action Required: [What needs to be fixed]
```

Summary:
- Total gaps found: N
- Critical gaps: N
- Completed items: [list]
- Files to delete: [list]
- Files to modify: [list]
- Rules audit: R6 {✅/⚠️/❌} / R9 {计划外 N} / 决策权 {未确认 N}
