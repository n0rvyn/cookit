---
name: verifying-plans
description: "Use when a plan has been written and needs validation before execution, or the user says 'verify plan', 'check the plan', 'review the plan', 'validate plan', '检查计划', '验证计划'. Applies Verification-First method with falsifiable error candidates, failure reverse reasoning, optional Design Token consistency checks, Design Faithfulness anchoring, and Architecture Review."
---

## Overview

This skill dispatches the `plan-verifier` agent to validate an implementation plan in a separate context, keeping the main conversation lean.

## Process

### Step 1: Gather Context

Collect the following before dispatching:

1. **Plan file path** — identify from:
   - Most recent `writing-plans` output in conversation
   - User-specified path
   - Search `docs/06-plans/*.md` for recent plan files
2. **Design doc path** — check the plan header for a `Design doc:` reference; if none, set to "none"
3. **Project root** — current working directory

If the plan file path is unclear, ask the user.

### Step 2: Dispatch Agent

Use the Task tool to launch the `plan-verifier` agent with all gathered context. Structure the task prompt as:

```
Verify this implementation plan:

Plan file: {path}
Design doc: {path or "none"}
Project root: {path}
```

### Step 3: Present Results

When the agent completes:

1. Present the Plan Verification Summary returned by the agent
2. Report the verdict:
   - **Approved** — proceed to Step 4
   - **Must revise** — list the specific revision items; apply revisions to the plan, then re-dispatch the verifier (max 2 revision cycles)

### Step 4: Mark Verified

When the plan is approved:

1. Append a verification marker to the end of the plan file:

```markdown

---
## Verification
- **Verdict:** Approved
- **Date:** {YYYY-MM-DD}
```

2. Suggest next step: `dev-workflow:executing-plans`
