---
name: executing-plans
description: "Use when you have a written implementation plan to execute. Batch execution with review checkpoints."
---

## Process

### Step 1: Load and Review Plan

1. Read the plan file
2. Review critically — identify gaps, ambiguities, or concerns
3. If concerns: raise them before starting. Do not proceed with a plan you disagree with
4. If no concerns: proceed to execution

### Step 2: Execute in Batches

Default batch size: 3 tasks.

For each task in the batch:
1. Read the task fully before starting
2. If the task has design anchor fields (Design ref, Expected values, etc.), read the referenced design section first
3. Follow steps exactly as written
4. Run all verification commands
5. If verification fails: stop and report, do not guess at fixes

### Step 3: Checkpoint Report

After each batch, report:
- What was implemented (per task)
- Verification output (pass/fail)
- Any deviations from the plan and why

Then say: **"Ready for feedback before next batch."**

Wait for user feedback. Apply requested changes before continuing.

### Step 4: Continue

Based on feedback:
- Apply corrections
- Execute next batch
- Repeat until all tasks complete

### Step 5: Wrap Up

When all tasks are done:
- Run full project build/test if applicable
- Suggest `dev-workflow:implementation-reviewer` agent for plan-vs-code audit
- Suggest `dev-workflow:finishing-branch` for branch integration

## Safety Rules

- **Never start implementation on main/master** without explicit user consent
- **Don't skip verifications** — even if you're confident the code is correct
- **Stop when blocked** — hit a blocker mid-batch? Stop and ask. Don't guess.
- **Plan has critical gaps?** — raise them. Don't fill gaps with assumptions.

## When to Stop and Ask

- Blocker mid-batch that the plan doesn't address
- Plan step is ambiguous or contradictory
- Verification fails repeatedly (2+ times on same step)
- Discovered dependency the plan didn't account for
