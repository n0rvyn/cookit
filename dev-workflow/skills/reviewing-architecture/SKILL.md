---
name: reviewing-architecture
description: "Use when a plan adds a new trigger, scheduler, observer, or entry point; replaces or deprecates an existing component; or modifies data flow paths. Checks entry point uniqueness, replacement completeness, data flow tracing, and fallback validation. Note: these checks are also included as the AR strategy in verifying-plans; use this skill for ad-hoc architectural review outside of plan verification."
---

## Trigger

Execute this command when:
- Plan adds a new trigger/scheduler/observer/entry point
- Plan replaces or deprecates an existing component
- Plan modifies data flow paths
- User requests architectural review (`/reviewing-architecture`)

## Process

### 1. Entry Point Uniqueness Check

For each new entry point (trigger, scheduler, observer, event handler) in the plan:
- Identify the core function this entry point will ultimately call
- Grep for all existing callers of that core function AND its key sub-functions
- Format:
  ```
  [入口检查] 计划新增入口: {new entry point}
  目标核心函数: {function name}
  现有调用者:
  - {file:line} — {caller description}
  - {file:line} — {caller description}
  结论: ✅ 无并行路径 / ⚠️ 已存在 {N} 条路径，需合并或说明共存理由
  ```
- If existing callers found on different upstream paths and plan doesn't address it → stop, report conflict

### 2. Replacement Completeness Check

For each "替代/淘汰/取代" in the plan or referenced ADRs:
- List concrete items to delete/modify:
  ```
  [替代清单] {old component} → {new component}
  需删除:
  - [ ] {file}: {method/config} — {用途}
  - [ ] {file}: {registration/import} — {用途}
  需修改:
  - [ ] {file:line}: {old reference} → {new reference}
  ```
- If the plan or ADR lacks this checklist → flag as incomplete, build the checklist by Grep before proceeding

### 3. Data Flow Tracing

For the primary data being modified:
- Trace from source to sink:
  ```
  [数据流] {data name}
  生产: {file:line} ({how it's created})
  处理: {file:line} → {file:line} ({transformations})
  持久化: {file:line} ({storage})
  展示: {file:line} ({UI display})
  ```
- At each processing node, search for other upstream callers (= parallel paths)
- Parallel path without coordination mechanism = architectural conflict

### 4. Fallback Validation

For any "保留作为保底/fallback" in the plan or existing code:
  ```
  [保底三问] {component kept as fallback}
  1. 协调机制: {谁决定走哪条路径? — 具体代码位置 / "无"}
  2. 触发条件: {什么条件走旧路径? — 可求值的布尔表达式 / "无"}
  3. 移除条件: {何时删除? — 可验证的里程碑 / "无"}
  结论: ✅ 三问均有具体答案 / ❌ {N}问无答案 → 建议用户决定是否删除旧实现
  ```
- "运行时决定" / "新路径失败时" / "测试通过后" = 描述性回答 = 无答案

## Output

```
## Architecture Review Summary

Entry point conflicts: N
- [list with file:line references]

Replacement checklist: complete / incomplete ({N} items missing)
- [missing items]

Parallel paths found: N
- [list with coordination status: 有协调 / 无协调]

Fallback validations: N passed, M failed
- [failed items with three-question status]

Recommendation: ✅ Proceed / ❌ Revise plan — [specific items to address]
```
