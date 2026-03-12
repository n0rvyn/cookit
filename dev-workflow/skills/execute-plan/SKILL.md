---
name: execute-plan
description: "Use when you have a written implementation plan to execute. Batch execution with review checkpoints."
---

## Process

### Step 1: Load and Review Plan

1. Read the plan file
2. **Verification pre-check**: Look for a `## Verification` section with `Verdict: Approved` in the plan file
   - If found: verification is done, continue
   - If not found: invoke `dev-workflow:verify-plan` before proceeding. If verify-plan returns "must-revise", apply revisions and re-verify before continuing
3. Review critically — identify gaps, ambiguities, or concerns
4. If concerns: raise them before starting. Do not proceed with a plan you disagree with
5. If no concerns: proceed to execution

### Step 2: Execute in Batches

**Batch size:** Determined by total task count:
- Count total tasks in the plan
- `batch_size = max(3, ceil(total_tasks / 3))`, capped at 6
  - 1-9 tasks: batch of 3
  - 10-12 tasks: batch of 4
  - 13-15 tasks: batch of 5
  - 16+ tasks: batch of 6

**Before starting each batch (if rag-server MCP `search` tool available):**
1. Collect task titles and key technical terms from the batch (file names, API names, component names mentioned in task steps)
2. Call rag-server MCP tool: `search(query="<batch task titles and keywords>", source_type=["error", "lesson"], project_root="<cwd>")`
3. If results are returned: present them as "Relevant lessons for this batch:" before executing any task in the batch
4. If the search tool is unavailable or returns no results: skip silently and begin task execution

**Before starting each batch — pre-read batch files:**
1. Scan all tasks in this batch — collect every file path from their `**Files:**` sections
2. Deduplicate the file list
3. If more than 15 unique files: keep the 15 that appear in the most tasks (tiebreaker: prefer files listed earlier in the plan); the rest will be read per-task as needed
4. Read the selected files in parallel (single message, multiple Read tool calls)
5. Track which files you modify via Write/Edit tools during execution: after completing each task, note every file you wrote or edited. Before starting the next task, re-read any pre-read file that you modified

For each task in the batch:
1. Read the task description from the plan fully before starting
2. If the task has design anchor fields (Design ref, Expected values, etc.), read the referenced design section first (skip if already pre-read in this batch and not modified since)
3. **Batch Strategy Gate** — if this task involves cross-file rename, term replacement, or reference cleanup:
   - Output strategy before any edits (must be visible in chat): target list (from Grep, not memory), scan scope, allowed exceptions with reasons
   - Execute changes
   - Run verification (Grep), output command and results
   - Verify results match strategy before claiming task completion
4. Follow steps exactly as written
5. Run all verification commands
6. If verification fails: stop and report, do not guess at fixes

### Step 3: Checkpoint Report

After each batch, report:
- What was implemented (per task)
- Verification output (pass/fail)
- Any deviations from the plan and why

**Decision Points:** If the plan file contains a `## Decisions` section with unresolved decisions (no `**Chosen:**` line), present them before the first batch:
- For each `blocking` decision: present to user via AskUserQuestion with options from the decision point
- For each `recommended` decision: present as a group — "The plan has {N} unresolved recommended decisions. Accept all defaults, or review individually?"
- Record user choices: edit the plan file, replace `**Recommendation:**` with `**Chosen:** {user's choice}`

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
- Suggest `dev-workflow:finish-branch` for branch integration

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

## State Integration

When running within a phase orchestrated by `run-phase`:

If `.claude/dev-workflow-state.yml` exists and `phase_step` is `execute`:
- After each batch checkpoint (Step 3), update the state file:
  - `batch_progress`: `"{completed}/{total}"` (e.g., `"2/4"`)
  - `last_updated`: current timestamp
- This enables cross-session resume if the session ends mid-execution

## Completion Criteria

- All plan tasks executed and verified
- Full project build passes (Step 5)
- Wrap-up suggestions presented (implementation-reviewer, finish-branch)
