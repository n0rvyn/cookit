---
name: writing-dev-guide
description: "Use when starting a new project's development after design is approved, or the user says 'write dev guide'. Creates a phased, project-level development guide that serves as the cornerstone document for all subsequent /write-plan cycles."
user-invocable: false
---

## Overview

This skill dispatches the `dev-guide-writer` agent to create a phased development guide in a separate context, keeping the main conversation lean.

## Not This Skill

- Single feature plan → use `dev-workflow:writing-plans`
- Per-phase implementation details → use `/write-plan`
- Design exploration → use `dev-workflow:brainstorming`

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

### Step 3: Present Results and Confirm

When the agent completes:

1. Read the dev-guide file the agent created
2. Extract the Phase outline (Phase names, goals, scope summaries)
3. Present the outline to the user for confirmation
4. **Wait for user approval** before considering the guide complete
5. If the user requests changes (reorder, merge, split Phases):
   - Re-dispatch the agent with revision instructions appended to the original prompt
   - Repeat until user approves

### Step 4: Next Steps

After user confirms:

> Development guide saved. Use `/run-phase` to start the Phase 1 development cycle (plan → execute → review).
