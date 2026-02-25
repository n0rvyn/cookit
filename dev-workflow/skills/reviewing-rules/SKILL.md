---
name: reviewing-rules
description: "Use when Claude exhibited unexpected behavior, for periodic rule health checks, or after adding new rules. Audits CLAUDE.md rules from the AI execution perspective for conflicts, loopholes, gaps, and redundancies."
disable-model-invocation: true
---

## Overview

This skill dispatches the `rules-auditor` agent to audit CLAUDE.md rules in a separate context, keeping the main conversation lean.

## Process

### Step 1: Gather Context

Collect the following before dispatching:

1. **Deviation description** — from the user's message (e.g., "Claude added animations without asking"). Set to "periodic check" if none provided
2. **Global CLAUDE.md path** — `~/.claude/CLAUDE.md`
3. **Project CLAUDE.md path** — check for `CLAUDE.md` in project root (may not exist)

### Step 2: Dispatch Agent

Use the Task tool to launch the `rules-auditor` agent with all gathered context. Structure the task prompt as:

```
Audit CLAUDE.md rules with the following inputs:

Deviation description: {description or "periodic check"}
Global CLAUDE.md: ~/.claude/CLAUDE.md
Project CLAUDE.md: {path or "none"}
```

### Step 3: Present Results

When the agent completes:

1. Present the Rules Review Report returned by the agent
2. If fix recommendations were made:
   - List each recommendation
   - Ask the user: "Execute these fixes?"
3. If user approves: apply the recommended changes to the CLAUDE.md files
4. If user declines: done

## Completion Criteria

- Audit report presented to user
- If fixes recommended: user has approved or declined each recommendation
- If approved: changes applied to CLAUDE.md files
