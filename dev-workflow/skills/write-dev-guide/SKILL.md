---
name: write-dev-guide
description: "Use when starting a new project's development after design is approved, or the user says 'write dev guide'. Creates a phased, project-level development guide that serves as the cornerstone document for all subsequent /write-plan cycles."
---

## Overview

This skill dispatches the `dev-guide-writer` agent to create a phased development guide in a separate context, keeping the main conversation lean.

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

### Step 2: Dispatch Agent

Use the Task tool to launch the `dev-guide-writer` agent with all gathered context. Structure the task prompt as:

```
Create a phased development guide with the following inputs:

Project root: {path}
Design doc: {path}
Project brief: {path or "none"}
Architecture docs: {path or "none"}
```

### Step 3: Structural Review

When the agent completes:

1. Read the dev-guide file the agent created
2. Extract the Phase outline and present as an overview table:

| Phase | Goal | Dependencies |
|-------|------|-------------|
| Phase 1 | {goal} | None |
| Phase 2 | {goal} | Phase 1 |
| ... | ... | ... |

3. Ask user (AskUserQuestion): **确认结构** / **调整结构**（reorder, merge, split）
4. If user chooses「调整结构」:
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
| 关键文件/组件 | {key files and components} |
| 待定架构决策 | {architecture decisions to resolve} |
| 验收标准 | {acceptance criteria} |

2. Ask user (AskUserQuestion): **确认** / **调整范围**
3. If user chooses「调整范围」:
   - Re-dispatch the agent with phase-scoped revision: "Revise Phase {i} with {user's changes}. Keep all other Phases unchanged."
   - Re-read output, re-present this Phase, repeat until user confirms
4. Proceed to next Phase

All Phases confirmed → proceed to Step 5.

### Step 5: Next Steps

After user confirms:

> Development guide saved. Use `/run-phase` to start the Phase 1 development cycle (plan → execute → review).

## Completion Criteria

- Dev-guide file saved to `docs/06-plans/`
- Structure confirmed by user (Step 3)
- All phases individually confirmed by user (Step 4)
- Next step (run-phase) communicated
