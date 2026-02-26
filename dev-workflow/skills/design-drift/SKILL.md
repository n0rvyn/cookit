---
name: design-drift
description: "Use when you need to check whether the codebase has drifted from its design documents, or the user says 'check drift', 'design drift', 'audit docs vs code'. Targets projects with standardized docs from project-kickoff. Supports full scan or focused mode."
---

# Design Drift Detection

检测设计文档与代码实现之间的漂移。从结构化文档中机械提取断言，逐条验证代码对齐状态。

## Overview

This skill dispatches the `design-drift-auditor` agent to extract and verify design assertions against the codebase, then optionally dispatches `flow-tracer` agents for items that need call-chain verification.

**Modes:**
- **Full scan**（default）— 5 个断言 category 全部检查
- **Focused mode** — 单个 category 或单个文档。用户指定 category name 或文档路径时触发。

## Process

### Step 1: Gather Context

定位项目设计文档。对每个文档，用 Glob 搜索并记录路径或 "not found"：

| 文档 | 搜索位置 | 必需 |
|------|---------|------|
| project-brief.md | `docs/01-discovery/project-brief.md` | 否 |
| 00-AI-CONTEXT.md | `docs/00-AI-CONTEXT.md` | 否 |
| CLAUDE.md（项目级） | `./CLAUDE.md` | 否 |
| Architecture | `docs/02-architecture/*.md` | 否 |
| ADRs | `docs/03-decisions/*.md` | 否 |
| Feature specs | `docs/05-features/*.md`（排除 README.md） | 否 |
| Dev guide | `docs/06-plans/*-dev-guide.md` | 否 |
| State file | `.claude/dev-workflow-state.yml` | 否 |

**前置条件**：至少 1 个文档存在。如果 0 个文档找到，停止并告知用户：

> No design documents found. Consider running `/project-kickoff` to create standardized docs, or manually create docs in `docs/`.

### Step 1.5: Determine Mode

检查用户消息中的 mode 指示：

- 用户指定了 category name（`scope` / `architecture` / `faithfulness` / `completion` / `consistency`）→ **focused-category mode**
- 用户指定了文档路径 → **focused-document mode**（检查该文档产出的所有 category 的断言）
- 否则 → **full scan**

### Step 2: Dispatch design-drift-auditor Agent

Use the Task tool to launch the `design-drift-auditor` agent with `model: "opus"`. Structure the task prompt based on the mode:

**Full scan:**
```
Audit design-vs-code alignment for this project.

Mode: full
Project root: {path}

Documents found:
- project-brief: {path or "not found"}
- AI-CONTEXT: {path or "not found"}
- CLAUDE.md: {path or "not found"}
- Architecture: {paths or "not found"}
- ADRs: {comma-separated paths or "none"}
- Feature specs: {comma-separated paths or "none"}
- Dev guide: {path or "not found"}
- State file: {path or "not found"}

Categories to check: all

For any assertion where you need call-chain verification, mark:
[needs-flow-trace] {flow description} starting from {file:function or "unknown"}
```

**Focused-category mode:**
```
Mode: focused-category: {category name}
(rest same as above)
Categories to check: {category name}
```

**Focused-document mode:**
```
Mode: focused-document: {document path}
(rest same as above)
Document to focus: {path}
Categories to check: all categories applicable to this document
```

### Step 3: Process Flow-Trace Items

扫描 agent 返回报告中的 `[needs-flow-trace]` 标记。

**如果 0 个**：跳到 Step 4。

**如果 1-3 个**：在**单条消息**中并行发起 `flow-tracer` agent（每个标记一个 Task tool call）：

```
Trace this flow through the codebase:

Flow description: {extracted from marker}
Starting point: {extracted from marker, or "search for entry point matching: {description}"}
Project root: {path}

Return a hop-by-hop trace with file:line at each hop.
Mark any breaks: signal with no consumer, call to nonexistent target, field written but never read.
```

**如果超过 3 个**：先发起前 3 个（并行），然后用 AskUserQuestion 问用户是否继续追踪剩余项。

### Step 4: Present Consolidated Report

合并 drift report + flow-trace 结果：

1. **替换标记**：用 flow-trace 结果替换报告中的 `[needs-flow-trace]` 标记，根据 trace 结果升级 Status：

   | Flow Trace 结果 | 升级后 Status |
   |----------------|--------------|
   | Flow Integrity = ✅ Complete | ✅ aligned |
   | Flow Integrity = ⚠️ Partial | ⚠️ partial（附 dead branch 摘要） |
   | Flow Integrity = ❌ Broken | ❌ drifted（附 break 摘要） |
   | "entry point not found" | 保留 `[unresolved]`（附 "trace failed: entry point not found"） |
   | Agent 超时或异常返回 | 保留 `[unresolved]`（附 "trace failed: {error}"） |

2. **Summary statistics**：
   - Total assertions checked: {N}
   - ✅ Aligned: {N} / ❌ Drifted: {N} / ⚠️ Stale: {N} / Unresolved: {N}
   - Flow traces completed: {N}, breaks found: {N}, failed: {N}
3. **修复建议**（仅对 ❌ drifted 项）：
   - 文档需更新 — 代码是对的，文档过时了
   - 代码需修复 — 代码偏离了设计意图
   - 需决策 — 两边都可能对，需要用户判断
4. **Unresolved 项处理**：如果有 `[unresolved]` 项，在报告末尾列出，建议用户手动验证或提供更精确的起点后重新 trace

## Completion Criteria

- Drift report 已呈现（full scan 含 5 categories，focused mode 含指定 category）
- 所有 flow-trace 标记已追踪，或用户选择不继续
- Summary statistics 已显示
- 对 ❌ drifted 项已给出修复方向建议
