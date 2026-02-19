---
name: running-phase
description: "Use when the user says 'run phase', 'start phase N', 'next phase', or when continuing development guided by a dev-guide. Orchestrates the plan-execute-review cycle for one phase of a development guide."
user-invocable: false
---

## Overview

This skill orchestrates one iteration of the development cycle:

```
Locate Phase → /write-plan → /verify-plan → /execute-plan → Document Features → review → fix gaps → Phase done
```

It does not do the work itself. It coordinates the sequence and ensures nothing is skipped.

## Process

### Step 1: Locate Current Phase

1. Find the dev-guide: `docs/06-plans/*-dev-guide.md` (if multiple, ask user which one)
2. Read the document and check each Phase's acceptance criteria
3. Phases with all criteria checked = completed
4. Identify the first incomplete Phase
5. Present Phase summary:
   - Goal
   - Scope
   - Architecture decisions to make
   - Acceptance criteria
6. Ask: "Start Phase N?"

If the user specifies a different Phase number, use that instead.

### Step 2: Plan, Verify, Execute

#### 2a. Write Plan

Invoke `dev-workflow:writing-plans` with Phase context:
- Goal: Phase N's goal from the dev-guide
- Scope: Phase N's scope items
- Acceptance criteria: Phase N's acceptance criteria
- Design doc reference: from dev-guide header (if exists)

The plan will be saved to `docs/06-plans/YYYY-MM-DD-phase-N-<name>.md`.

#### 2b. Verify Plan

Invoke `dev-workflow:verifying-plans` on the plan just written.

If verification finds 必须修订 items: apply the revisions to the plan, then re-verify.

#### 2c. Execute Plan

Invoke `dev-workflow:executing-plans` to execute the verified plan.

When execution completes (all tasks done and verified), proceed to Step 3.

### Step 3: Document Features

Before running reviews, generate feature specs for completed user journeys in this Phase.

1. Check the Phase scope for feature completions (user journeys, not individual components)
2. For each completed feature: run `/write-feature-spec`
3. Infrastructure-only Phase (no user journeys): skip this step

This ensures `/feature-review` in Step 4 has a spec to work with.

### Step 4: Run Reviews

Based on the Phase's Review checklist, run reviews in sequence:

1. **Always:** `/execution-review`
2. **If Phase modified UI files:** `/ui-review`
3. **If Phase created new pages/components:** `/design-review`
4. **If Phase completed a full user journey:** `/feature-review`
5. **If this is the submission prep Phase:** `/submission-preview`

For each review:
- Invoke the command
- Collect the output
- Continue to the next review

After all reviews complete, present a consolidated summary of all findings.

### Step 5: Fix Gaps

If any review found issues:

1. List all gaps sorted by severity (red first, then yellow)
2. Ask the user: "Fix these gaps before moving on, or mark as known issues?"
3. If fixing: address the gaps, then re-run only the reviews that had failures
4. If skipping: note the known issues and proceed

### Step 6: Phase Completion

1. Update the dev-guide: check off this Phase's acceptance criteria
2. Mark Phase status in the dev-guide: add `**Status:** ✅ Completed — YYYY-MM-DD` after the Phase heading
3. Remind the user to update project docs:
   - `docs/07-changelog/` — record changes
   - `docs/03-decisions/` — if architectural decisions were made
4. Report:
   > Phase N complete.
   > Next: Phase N+1 — [name]: [goal].
   > Run `/run-phase` to continue, or `/commit` to save progress first.

## Rules

- **Never skip Step 4.** Reviews are not optional.
- **Never skip verification.** Step 2b must run before 2c.
- **Phase order matters.** Don't start Phase N+1 if Phase N has unchecked acceptance criteria (unless user explicitly overrides).
- **Consolidate review output.** Don't dump 4 separate reports — merge into one summary with sections.
