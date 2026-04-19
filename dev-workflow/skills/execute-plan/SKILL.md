---
name: execute-plan
description: "Use when the user says 'execute the plan', 'run the plan', 'implement the plan', '执行计划', '跑计划', or has a verified plan file ready for execution. Executes plan tasks mechanically in chunked batches (5 tasks per batch) without judgment calls; auto-resumes on truncation via per-task state file. Reports blocked/failed tasks for the user to fix — does not attempt fixes itself. Not when: plan has not been verified (run verify-plan first). Also invoked by run-phase at Step 4."
---

## Overview

This skill dispatches the `dev-workflow:execute-plan` agent (sonnet) to execute a verified plan in batches of 5 tasks. A JSON state file tracks per-task progress, enabling automatic resume on truncation. The plan's final verification task is no longer required — full test suite execution is handled separately by `dev-workflow:test-changes`.

## Process

### Step 1: Pre-checks

1. Read the plan file
2. **Verification pre-check**: Look for a `## Verification` section with `Verdict: Approved` in the plan file
   - If found: verification is done, continue
   - If not found: invoke `dev-workflow:verify-plan` before proceeding. If verify-plan returns "must-revise", apply revisions and re-verify before continuing
<!-- Inline short-form DP handling. Full ruleset at ${CLAUDE_PLUGIN_ROOT}/references/decision-points.md §"Note on inline variant" — sync on rule changes. -->
3. **Decision Points:** If the plan file contains a `## Decisions` section with unresolved decisions (no `**Chosen:**` line), present them before dispatching:
   - For each DP, write a short-form translation in the `question` field: one-line summary of what the decision controls + each option prefixed with its original `A:` / `B:` / `C:` label describing what concretely happens. Do NOT paste the full DP block (Context / Options / Recommendation headings) verbatim. The plan file's DP body stays unchanged.
   - For each `blocking` decision: present via AskUserQuestion (one call per DP).
   - For `recommended` decisions: batch via a single AskUserQuestion; all content inside the `question` field, DPs separated by `\n---\n`, ending with `\n\n全部接受推荐，还是逐个审查？`.
   - If the user does NOT choose to accept all: present each DP individually via separate AskUserQuestion calls. Do not assume any DP is accepted until the user explicitly confirms it.
   - Record user choices: edit the plan file, replace `**Recommendation:**` or `**Recommendation (unverified):**` with `**Chosen:** {Option A | B | C}` using the original label.

### Step 2: Initialize and Dispatch

1. Read the plan file and count total tasks (count `### Task N:` headings)
2. Check for existing state file at `.claude/execute-plan-state.json`:
   - If exists and `status` is `in_progress`: resume from `last_completed + 1`
   - If exists and `status` is `complete`: skip execution, proceed to Step 3
   - If does not exist: create with initial state:
     ```json
     {
       "plan_file": "{plan file path}",
       "total": {N},
       "batch_size": 5,
       "last_completed": 0,
       "status": "in_progress"
     }
     ```
3. **Dispatch loop:**
   - Read state file: `start = last_completed + 1`, `end = min(last_completed + batch_size, total)`
   - Dispatch `dev-workflow:execute-plan` agent:
     ```
     Execute tasks {start} through {end} of the implementation plan.

     Plan file: {plan file path}
     Project root: {project root}
     State file: .claude/execute-plan-state.json
     ```
   - When agent returns: read `.claude/execute-plan-state.json`
     - If `last_completed < total`: loop back (re-dispatch next batch)
     - If `last_completed >= total`: update state `status: "complete"`, exit loop
   - **Truncation recovery:** If the agent was truncated mid-batch, the state file still has the last successfully completed task number. The next loop iteration dispatches from wherever `last_completed` stopped — no manual intervention needed.
4. Delete `.claude/execute-plan-state.json` after successful completion (cleanup)

### Step 3: Process Results

When execution completes (all batches done):

1. Read the report file at `docs/06-plans/execution-report.md`
   - If the agent's return message contains `Report written to:`, use that path
   - If the file does not exist: fall back to parsing the agent's return message
2. Present summary to the user: completed/blocked/failed counts
3. If blocked or failed tasks exist: list them with reasons

**Standalone mode** (not within run-phase):
- If failures: fix in main context (opus)
- Suggest `dev-workflow:test-changes` to run the full test suite
- Suggest `dev-workflow:implementation-reviewer` for plan-vs-code audit
- Suggest `dev-workflow:finish-branch` for branch integration

## State Integration

When running within a phase orchestrated by `run-phase`:

If `.claude/dev-workflow-state.yml` exists and `phase_step` is `execute`:
- After all batches complete, do NOT update `phase_step` (orchestrator owns state transitions)
- Output: "Execution complete. Returning to run-phase."

## Completion Criteria

- All plan tasks attempted by the agent across all batches
- Execution report reviewed and presented to user
- State file cleaned up (deleted after successful completion)
- When in run-phase context: handoff signal output
- When standalone: wrap-up suggestions presented
