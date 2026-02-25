---
name: run-phase
description: "Use when the user says 'run phase', 'start phase N', 'next phase', or when continuing development guided by a dev-guide. Orchestrates the plan-execute-review cycle for one phase of a development guide."
---

## Overview

This skill orchestrates one iteration of the development cycle by dispatching agents for document-generation steps and keeping only code execution in the main context.

```
Locate/Resume Phase
  → dispatch plan-writer agent (separate context)
  → dispatch plan-verifier agent (separate context)
  → execute plan (main context — writes code)
  → dispatch feature-spec-writer agent (separate context)
  → dispatch review agents in parallel (separate contexts)
  → fix gaps (main context)
  → Phase done
```

It does not do the work itself. It dispatches agents and coordinates the sequence.

## State File

Location: `.claude/dev-workflow-state.yml`

This file tracks progress across sessions. Update it **before** starting each step (so crash-resume works). Read/write via the Read and Write tools.

```yaml
project: <name>
current_phase: 2
phase_name: "Phase Name"
phase_step: plan    # plan | verify | execute | spec | review | fix | done
dev_guide: docs/06-plans/YYYY-MM-DD-project-dev-guide.md
plan_file: null
verification_report: null
batch_progress: null
review_reports: []
gaps_remaining: 0
last_updated: "YYYY-MM-DDTHH:MM:SS"
```

## Process

### Step 1: Resume or Locate Phase

1. Check for `.claude/dev-workflow-state.yml` (Read tool)
   - If exists AND `phase_step` is not `done`:
     - Present: "Phase {N} ({name}) in progress — step: {phase_step}. Resume?"
     - If user accepts: skip to the step indicated by `phase_step`
     - If user declines: ask which Phase to start
2. If no state file or starting fresh:
   - Find dev-guide: `docs/06-plans/*-dev-guide.md` (if multiple, ask user)
   - Read the document and check each Phase's acceptance criteria
   - Phases with all criteria checked = completed
   - Identify the first incomplete Phase
   - Present Phase summary: Goal, Scope, Architecture decisions, Acceptance criteria
   - Ask: "Start Phase N?"
3. Initialize state file:

```yaml
project: <from dev-guide title>
current_phase: <N>
phase_name: "<Phase name>"
phase_step: plan
dev_guide: <dev-guide path>
plan_file: null
verification_report: null
batch_progress: null
review_reports: []
gaps_remaining: 0
last_updated: "<now>"
```

If the user specifies a different Phase number, use that instead.

### Step 2: Plan (agent dispatch)

1. Update state: `phase_step: plan`, `last_updated: <now>`
2. Gather Phase context from dev-guide:
   - Goal: Phase N's goal
   - Scope: Phase N's scope items
   - Acceptance criteria: Phase N's acceptance criteria
   - Design doc reference: from dev-guide header (if exists)
3. Use the Task tool to dispatch the `plan-writer` agent:

```
Write an implementation plan with the following inputs:

Goal: {Phase goal}
Scope:
{Phase scope items}

Acceptance criteria:
{Phase acceptance criteria}

Design doc: {path or "none"}
Project root: {project root}

Context: This is Phase {N} of the dev-guide at {dev-guide path}.
```

4. When agent returns: note the plan file path from the summary
5. Update state: `plan_file: <path>`, `last_updated: <now>`
6. Present plan summary to user (task count, key files)
7. Auto-select verification speed: count tasks in the returned plan file.
   If task count < 5: mark `--fast` flag for Step 3 (use Sonnet for verification).
   If task count ≥ 5: no flag (use Opus default).

### Step 3: Verify

1. Update state: `phase_step: verify`, `last_updated: <now>`
2. Invoke `dev-workflow:verify-plan` with the plan from Step 2 (pass `--fast` flag if set in Step 2)
3. Update state: `verification_report: <summary>`, `last_updated: <now>`

**If still "Must revise" after 2 revision cycles:**
Present the remaining issues to the user:
> "Plan verification failed after 2 revision attempts. Remaining issues:
> [list specific issues from verifier output]
>
> Options:
> A. Stop and manually revise the plan, then re-run this step
> B. Proceed with imperfect plan (issues noted in execution — treat as extra caution points)"

Wait for user choice. If A: stop. If B: mark state `verification_report: "partial"` and continue.

### Step 4: Execute (main context)

1. Update state: `phase_step: execute`, `last_updated: <now>`
2. Invoke `dev-workflow:execute-plan` to execute the verified plan
   - This stays in the main context because it writes code and needs checkpoint approval
3. When execution completes, update state: `last_updated: <now>`

### Step 5: Document Features (agent dispatch)

1. Update state: `phase_step: spec`, `last_updated: <now>`
2. Check the Phase scope for completed user journeys
   - Infrastructure-only Phase (no user journeys): skip to Step 6
3. For each completed feature:
   - Confirm feature name and scope with the user
   - Use the Task tool to dispatch the `feature-spec-writer` agent:

```
Generate a feature spec with the following inputs:

Feature name: {name}
Feature scope: {scope}
Design doc paths:
{relevant design doc paths and sections}
Dev-guide: {dev-guide path} Phase {N}
Key implementation files:
{list of key files}
Project root: {project root}
```

4. Present spec summary when agent returns
5. Update state: `last_updated: <now>`

### Step 6: Reviews (parallel agent dispatch)

1. Update state: `phase_step: review`, `last_updated: <now>`
2. Determine which reviews to run from the Phase's Review checklist:
   - **Always:** `implementation-reviewer` agent
   - **If Phase modified UI files:** `/ui-review`
   - **If Phase created new pages/components:** `/design-review`
   - **If Phase completed a full user journey:** `/feature-review`
   - **If this is the submission prep Phase:** `/submission-preview`
3. Dispatch ALL applicable review agents **in parallel** using the Task tool in a single message:
   - `implementation-reviewer` agent (always): pass plan file path + project root
   - `ios-development:ui-reviewer` (if UI files modified): pass list of modified `*View.swift` files
   - `ios-development:design-reviewer` (if new pages/components): pass list of new View files
   - `ios-development:feature-reviewer` (if full user journey completed): pass feature scope + key files
   - `dev-workflow:implementation-reviewer` handles plan vs code; ios agents handle quality

   Each agent receives a fresh context — they have no memory of how the code was written.
   This removes confirmation bias from self-review.
4. When all return: collect results, present a consolidated summary of all findings
5. Update state: `review_reports: [<paths>]`, `last_updated: <now>`

### Step 7: Fix Gaps

If any review found issues:

1. Update state: `phase_step: fix`, `last_updated: <now>`
2. List all gaps sorted by severity (critical first, then warnings)
3. Ask the user: "Fix these gaps before moving on, or mark as known issues?"
4. If fixing: address the gaps, then re-run only the reviews that had failures
5. If skipping: note the known issues and proceed
6. Update state: `gaps_remaining: <count>`, `last_updated: <now>`

### Step 8: Phase Completion

1. Update state: `phase_step: done`, `last_updated: <now>`
2. Update the dev-guide:
   - Check off this Phase's acceptance criteria
   - Add status line: `**Status:** ✅ Completed — YYYY-MM-DD` after the Phase heading
3. Remind the user to update project docs:
   - `docs/07-changelog/` — record changes
   - `docs/03-decisions/` — if architectural decisions were made
4. Report:

> Phase N complete.
> Next: Phase N+1 — [name]: [goal].
> Run `/run-phase` to continue, or `/commit` to save progress first.

## Rules

- **Never skip Step 6.** Reviews are not optional.
- **Never skip verification.** Step 3 must run before Step 4.
- **Phase order matters.** Don't start Phase N+1 if Phase N has unchecked acceptance criteria (unless user explicitly overrides).
- **Consolidate review output.** Merge all review results into one summary with sections.
- **State before action.** Update state file before starting each step, not after.

## Completion Criteria

- Phase acceptance criteria checked off in dev-guide (Step 8)
- State file `phase_step` set to `done`
- Next phase communicated to user
