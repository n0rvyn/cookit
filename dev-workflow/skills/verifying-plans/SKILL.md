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

### Step 1.5: Retrieve Error Patterns (if search tool available)

After collecting plan and design doc paths, extract technical keywords from the plan (framework names, API names, component names found in the plan file) and search for known error patterns:

1. Call `search(query="<technical keywords from plan>", source_type=["error", "lesson"], project_root="<cwd>")`
2. If results are returned: collect them as `retrieved_context` — a compact list of (source_path, section, content preview) for each hit
3. If the search tool is unavailable or returns no results: set `retrieved_context` to empty and continue

### Step 2: Dispatch Agent

Use the Task tool to launch the `plan-verifier` agent with all gathered context. Structure the task prompt as:

```
Verify this implementation plan:

Plan file: {path}
Design doc: {path or "none"}
Project root: {path}

Retrieved error patterns and lessons (from knowledge base):
{retrieved_context — one entry per line, or "none" if empty}
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
