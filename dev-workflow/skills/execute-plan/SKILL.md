---
name: execute-plan
description: "Use when the user says 'execute the plan', 'run the plan', 'implement the plan', or has a verified plan file ready for execution. Executes plan tasks mechanically without judgment calls; reports blocked/failed tasks for the user to fix. Not needed when run-phase is active — run-phase calls this internally at Step 4."
---

## Overview

This skill dispatches the `dev-workflow:execute-plan` agent (sonnet) to execute a verified plan. The agent follows plan tasks precisely without making judgment calls. The plan's final verification task runs the full build/test suite. Failure fixes happen after the agent returns, in main context.

## Process

### Step 1: Pre-checks

1. Read the plan file
2. **Verification pre-check**: Look for a `## Verification` section with `Verdict: Approved` in the plan file
   - If found: verification is done, continue
   - If not found: invoke `dev-workflow:verify-plan` before proceeding. If verify-plan returns "must-revise", apply revisions and re-verify before continuing
3. **Decision Points:** If the plan file contains a `## Decisions` section with unresolved decisions (no `**Chosen:**` line), present them before dispatching:
   - For each `blocking` decision: present to user via AskUserQuestion with options from the decision point
   - For `recommended` decisions: present as a group via a single AskUserQuestion. **Critical:** all DP content must be inside the `question` field — text printed before AskUserQuestion gets visually covered by the question widget. Read each recommended DP's full block (heading + Context + Options + Recommendation) from the plan file and concatenate them verbatim in the question field, separated by `\n---\n`. End with: `\n\n全部接受推荐，还是逐个审查？`
   - If the user does NOT choose to accept all: present each DP individually via separate AskUserQuestion calls. Do not assume any DP is accepted until the user explicitly confirms it
   - Record user choices: edit the plan file, replace the `**Recommendation:**` or `**Recommendation (unverified):**` line with `**Chosen:** {user's choice}`

### Step 2: Dispatch Agent

Use the Agent tool to dispatch the `dev-workflow:execute-plan` agent:

```
Execute the implementation plan.

Plan file: {plan file path}
Project root: {project root}
```

### Step 3: Process Results

When the agent returns:

1. Read the execution report
2. Present summary to the user: completed/blocked/failed counts
3. If blocked or failed tasks exist: list them with reasons

4. **Build/test coverage check**: If the execution report shows no final verification task was run (no task with build/test commands in its Verify section): discover and run build/test commands directly (read package.json/Makefile/etc. to find commands)

**Standalone mode** (not within run-phase):
- If failures: fix in main context (opus)
- Suggest `dev-workflow:implementation-reviewer` for plan-vs-code audit
- Suggest `dev-workflow:finish-branch` for branch integration

## State Integration

When running within a phase orchestrated by `run-phase`:

If `.claude/dev-workflow-state.yml` exists and `phase_step` is `execute`:
- After agent returns, do NOT update `phase_step` (orchestrator owns state transitions)
- Output: "Execution complete. Returning to run-phase."

## Completion Criteria

- All plan tasks attempted by the agent
- Execution report reviewed and presented to user
- When in run-phase context: handoff signal output
- When standalone: wrap-up suggestions presented
