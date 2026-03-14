---
name: write-dev-guide
description: "Use when starting a new project's development after design is approved, or the user says 'write dev guide'. Creates a phased, project-level development guide that serves as the cornerstone document for all subsequent /write-plan cycles."
---

## Overview

This skill dispatches the `dev-workflow:dev-guide-writer` agent to create a phased development guide in a separate context, keeping the main conversation lean.

## Not This Skill

- Single feature plan → use `dev-workflow:write-plan`
- Per-phase implementation details → use `/write-plan`
- Design exploration → use `dev-workflow:brainstorm`

## Process

### Step 1: Gather Context

Collect the following before dispatching:

1. **Project root** — current working directory
2. **Design doc path** — search `docs/06-plans/*-design.md`
3. **Project brief path** — check `docs/01-discovery/project-brief.md`
4. **Architecture docs path** — check `docs/02-architecture/`

If no project-brief or design doc exists, inform the user and suggest running the corresponding workflow first. Do not dispatch without these inputs.

### Step 1.5: Check for Existing Dev-Guide

Before dispatching the agent, check if a dev-guide already exists:

1. Glob `docs/06-plans/*-dev-guide.md`
2. If one or more files found: record them as `existing_dev_guides`
3. If no files found: skip to Step 2

### Step 2: Dispatch Agent

Use the Task tool to launch the `dev-workflow:dev-guide-writer` agent with all gathered context. Structure the task prompt as:

```
Create a phased development guide with the following inputs:

Project root: {path}
Design doc: {path}
Project brief: {path or "none"}
Architecture docs: {path or "none"}
```

### Step 2.5: Mark Old Dev-Guide as Superseded

After the agent writes the new dev-guide:

1. If `existing_dev_guides` is empty: skip this step
2. For each path in `existing_dev_guides`:
   a. Read the file
   b. Check if it starts with YAML frontmatter (first line is `---`)
   c. If frontmatter exists: find the `current:` field and change its value to `false`
   d. If no frontmatter exists (older file without frontmatter): skip this file (do not add frontmatter to files that weren't written with it)
   e. Write the updated file back
3. Report: "Marked {N} existing dev-guide(s) as `current: false`: {paths}"

### Step 3: Structural Review

When the agent completes:

1. Read the dev-guide file the agent created
2. Extract the Phase outline and present as an overview table:

| Phase | Goal | Dependencies |
|-------|------|-------------|
| Phase 1 | {goal} | None |
| Phase 2 | {goal} | Phase 1 |
| ... | ... | ... |

3. **Decision Points:**
   **Ordering constraint:** The Phase outline table (step 2 above) must be presented to the user BEFORE any decision points. Do not reorder.
   - Read the `## Decisions` section from the dev-guide file. If the section content is `None.`, skip to step 4. Otherwise, process each `### [DP-xxx]` entry:
   - **Comparison table** (all decisions): extract from the decision's `**Options:**` lines, keeping each option's `{description} — {trade-off}` as-is in one column:

     ### [DP-xxx] {title}

     **Context:** {from decision}

     | 方案 | 描述与代价 |
     |------|-----------|
     | A | {description} — {trade-off} |
     | B | {description} — {trade-off} |

   - **Recommendation line**: only for `recommended` decisions, append `**推荐:** {option} — {reason}` after the table. For `blocking` decisions, omit this line.
   - **AskUserQuestion**: for `recommended` decisions, mark the recommended option with "(推荐)" in the label. For `blocking` decisions, do not pre-select any option.
   - Record user choices: edit the dev-guide file, replace `**Recommendation:**` with `**Chosen:** {user's choice}`
4. Ask user (AskUserQuestion): **确认结构** / **调整结构**（reorder, merge, split）
5. If user chooses「调整结构」:
   - Re-dispatch the agent with structural revision instructions appended to the original prompt
   - Re-read output, re-present table, repeat until user confirms

### Step 4: Phase-by-Phase Confirmation

For each Phase i = 1..N:

1. Present Phase detail:

| 维度 | 内容 |
|------|------|
| 目标 | {phase goal} |
| 前置依赖 | {dependencies} |
| 范围项 | {scope items, bulleted} |
| 用户可见的变化 | {from dev-guide, or "无 — 纯基建阶段"} |
| 关键文件/组件 | {key files and components} |
| 待定架构决策 | {architecture decisions to resolve} |
| 验收标准 | {acceptance criteria} |

2. Ask user (AskUserQuestion):
   - If Phase has 用户可见的变化 (not "无") AND 待定架构决策: **确认** / **调整范围** / **调整视觉预期** / **解决架构决策**
   - If Phase has 用户可见的变化 (not "无") but no 待定架构决策: **确认** / **调整范围** / **调整视觉预期**
   - If Phase has no 用户可见的变化 (infrastructure) AND 待定架构决策: **确认** / **调整范围** / **解决架构决策**
   - If Phase has no 用户可见的变化 AND no 待定架构决策: **确认** / **调整范围**
3. If user chooses「调整范围」:
   - Re-dispatch the agent with phase-scoped revision: "Revise Phase {i} with {user's changes}. Keep all other Phases unchanged."
   - Re-read output, re-present this Phase, repeat until user confirms
4. If user chooses「调整视觉预期」:
   - User provides corrections/additions to visual expectations
   - Re-dispatch the agent: "Revise Phase {i}'s 「用户可见的变化」section with: {user's input}. Keep all other Phases unchanged."
   - Re-read output, re-present this Phase, repeat until user confirms
5. If user chooses「解决架构决策」:
   - List each pending decision as a numbered item
   - For each decision, ask user for their choice or direction
   - Re-dispatch the agent: "Update Phase {i}: resolve architecture decisions as follows: {user's decisions}. Keep all other Phases unchanged."
   - Re-read output, re-present this Phase (resolved decisions should move from「待定架构决策」into「范围项」or「验收标准」as appropriate), repeat until user confirms
6. Proceed to next Phase

All Phases confirmed → proceed to Step 5.

### Step 5: Next Steps

After user confirms:

> Development guide saved. Use `/run-phase` to start the Phase 1 development cycle (plan → execute → review).

## Completion Criteria

- Dev-guide file saved to `docs/06-plans/`
- Structure confirmed by user (Step 3)
- All phases individually confirmed by user (Step 4)
- Previous dev-guide(s) marked `current: false` (Step 2.5)
- Next step (run-phase) communicated
