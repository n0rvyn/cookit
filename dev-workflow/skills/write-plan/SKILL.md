---
name: write-plan
description: "Use when you have a spec or requirements for a multi-step task, before touching code. Creates comprehensive implementation plans with bite-size tasks."
---

## Behavior Note

When invoked **standalone** (user runs write-plan directly): this skill automatically chains
to `dev-workflow:verify-plan` at Step 3 — plan writing and verification happen in one flow.

When invoked via **`run-phase`** orchestration: run-phase calls the `plan-writer` agent
directly (not this skill) and manages verification as a separate explicit step. Both paths
produce a verified plan; the difference is control granularity.

## Overview

This skill dispatches the `plan-writer` agent to generate an implementation plan in a separate context, keeping the main conversation lean.

## Process

### Step 0: Retrieve Prior Context (if search tool available)

Before gathering context, search for relevant ADRs, architecture decisions, and known pitfalls:

1. Extract 3-5 keywords from the plan goal (component names, technology names, pattern names)
2. Call `search(query="<goal text>", source_type=["doc", "error", "lesson"], project_root="<cwd>")`
3. If results are returned: note them as "Prior context from knowledge base:" and include any directly relevant findings in the `Additional context` block of the agent dispatch prompt (Step 2)
4. If the search tool is unavailable or returns no results: skip silently and continue to Step 1

### Step 1: Gather Context

Collect the following before dispatching:

1. **Goal** — one sentence describing what the plan achieves (from user request, dev-guide Phase, or conversation context)
2. **Scope items** — list of features/components to implement
3. **Acceptance criteria** — verifiable completion conditions (from dev-guide Phase or user)
4. **Design doc reference** — path to design doc if one exists (search `docs/06-plans/*-design.md`)
5. **Project root** — current working directory

If any of these are unclear, ask the user before dispatching.

### Step 2: Dispatch Agent

Use the Task tool to launch the `plan-writer` agent with all gathered context. Structure the task prompt as:

```
Write an implementation plan with the following inputs:

Goal: {goal}
Scope:
- {item 1}
- {item 2}

Acceptance criteria:
- {criterion 1}
- {criterion 2}

Design doc: {path or "none"}
Project root: {path}

Additional context:
{any relevant details from the conversation}
```

### Step 3: Present and Verify

When the agent completes:

1. Read the plan file the agent created
2. Present a summary to the user:
   - Plan file path
   - Number of tasks
   - Key files to be created/modified
3. Invoke `dev-workflow:verify-plan` to validate the plan before execution

## Completion Criteria

- Plan file written to `docs/06-plans/`
- Verification invoked and plan approved (or user chose to proceed with noted issues)
