---
name: fix-bug
description: "Use when the user reports an error with stack trace or screenshot, describes unexpected behavior, or build/test failures occur. Systematically diagnoses through reproduction, hypothesis, value domain tracing, and parallel path detection."
---

## Input

Trigger this command when:
- User reports an error with stack trace or screenshot
- User describes unexpected behavior
- Build/test failures occur

If input is incomplete, ask for:
1. Steps to reproduce
2. Expected vs actual behavior
3. Full error message or stack trace

## Process

0. **Parse input and read GitHub Issue (if reference provided)**

   If input contains `#N` or `issue N` (e.g., `/fix-bug #5`, `/fix-bug issue 5`):

   1. Extract issue number N
   2. Run: `gh issue view N --json title,body,labels,milestone`
   3. If `gh issue view` returns an error (issue not found, `gh` not installed, no network): inform the user of the error and fall through to Step 0.5 without prior hypotheses
   4. Parse the issue body — extract content under `### Prior Hypotheses` section
   5. Present: "Prior hypotheses from issue #N:" followed by the extracted assertions
   6. Show the full issue body for context
   7. Store these hypotheses for use in Step 3

   If input does not contain an issue reference, skip to Step 0.5.

0.5. **Retrieve historical context**
   - Extract 3-5 keywords from the bug description (error type, component name, API name, symptom)
   - Call `search(query="<keywords from bug description>", source_type=["error","lesson"], project_root="<current working directory>")`
   - If results are returned: present them as "Related historical records:" before proceeding
   - If the index returns no results, or the search tool is unavailable: skip this step silently and proceed to Step 1
   - Do not block investigation if the search tool is slow or unresponsive
   - Note: Phase 1 searches project-level index only. Cross-scope search (project + global) will be added in Phase 2.

1. **Reproduce first**
   - Confirm the bug can be reproduced
   - If cannot reproduce: ask for more context, do not guess
   - Document the exact steps that trigger the bug

2. **Understand the error**
   - Read the complete error message and stack trace
   - Identify the exact location where the error occurs
   - Note any relevant context (user action, data state)

2.5. **Understand intent** (trigger: bug location involves non-trivial logic — conditional branches, state machines, multi-step transformations)

   Before generating assertions, answer these questions by reading code + git history:

   ```
   [Intent Analysis]
   - Original intent: what was this code trying to achieve?
     (cite: comments, function name, commit message, surrounding context)
   - Actual behavior: what does it actually do? (cite: code trace)
   - Gap type: intentional workaround / unintentional bug /
     incomplete implementation / outdated assumption
   - Evidence for gap type: {git blame date, TODO comment, related issue, etc.}
   - Current goal: what do we want it to do now?
   - Delta: {original intent} -> {current goal} — same or different?
   - If different: upstream/downstream impact assessment required before proceeding
   ```

   If gap type = "intentional workaround":
     Stop. Do not treat as bug. Present finding to user:
     "This appears to be an intentional workaround from {date/commit}.
      Confirm: fix it or preserve the workaround?"

3. **BV: Generate falsifiable assertions**

   Based on error symptoms and code context, generate 3-5 specific, falsifiable assertions.
   Each assertion must include: hypothesis + file location + verification method + expected outcome for both cases.

   **If Step 0 extracted prior hypotheses from a GitHub Issue:** prepend them to the assertion list as highest-priority items, marked with source: "Prior hypothesis from issue #N". Verify these first before generating additional assertions.

   ```
   [Bug Assertion 1] {specific hypothesis}
   Location: {file:line}
   Verify: read {file:line}; if correct, expect {X}; if wrong, expect {Y}
   ```

   Assertions must cover different dimensions (pick the 3-5 most suspicious):
   - **Value domain error** — type/range/format mismatch
   - **State timing error** — race condition, wrong lifecycle stage
   - **Path routing error** — data reaching wrong handler
   - **Missing guard** — null/empty/boundary unhandled
   - **Stale code interference** — replaced component still active

   Principle: backward verification (testing specific assertions) is significantly more accurate than forward generation (guessing a single cause). Even if all assertions are falsified, the verification process exposes reasoning paths that reveal the root cause.


4. **Verify assertions systematically**
   - Test each assertion from Step 3, one at a time
   - Record result: confirmed / falsified / inconclusive
   - If an assertion is confirmed: proceed to fix
   - If all falsified: the verification traces usually reveal the actual cause; form a new assertion based on what you learned
   - Do not test multiple assertions at once

4.5. **Hypothesis reset** (trigger: user negates a core assumption underlying the confirmed assertion)

   **Active self-check:** After each user response during Step 4 verification, ask yourself: "Does the user's response contradict any premise of the current assertions?" If yes, invoke this step.

   When the user provides information that invalidates the foundation of the current diagnosis (e.g., "the data is user-provided, not AI-generated"):

   1. Stop current investigation path
   2. Record what was invalidated and the user's correction
   3. Return to Step 3: regenerate assertions incorporating the user's new information
   4. After new assertions are verified, Step 7 (plan the fix) must be executed again — the previous plan (if any) was based on invalidated premises

   Do NOT patch the old hypothesis. A negated foundation requires new assertions.
   Do NOT skip ahead to implementation — reset means the full gate chain (Step 3 → 4 → 7) restarts.

5. **Trace value domain — MANDATORY GATE for value-related bugs**

   ⛔ **If bug symptom is value-related, this step is MANDATORY. Do not proceed to Step 7 without producing the `[值域检查]` table below.**

   A bug is value-related if: a wrong number/string/enum appears where a different one was expected, OR a field displays data from the wrong source, OR a computed result is incorrect. When in doubt, treat as value-related.

   - Reverse-trace from bug location to data source (record each variable rename)
   - Forward-Grep all consumers from source (using source field name + every intermediate variable name)
   - Verify unit/domain/format assumptions at each consumer
   - Output format:
     ```
     [值域检查] {file:line} — {生产/消费} — 假设值域 {X} — ✅ 一致 / ❌ 同类问题
     ```
   - All ❌ must be fixed in the same pass
   - Skipping this step for value-related fixes = incomplete fix, even if original symptom disappears

6. **Check for parallel paths** (trigger: Step 5 finds multiple producers, or same core function has multiple upstream callers)
   - List all processing paths from source to sink
   - Check coordination mechanisms between paths (shared state, mutex, idempotency check)
   - Format:
     ```
     [路径检查] {核心函数}
     - 路径 A: {file:line} → {file:line} → {核心函数}
     - 路径 B: {file:line} → {核心函数}
     - 协调机制: {具体代码位置 / 无}
     ```
   - Parallel paths without coordination = architectural issue; flag as "⚠️ needs architectural fix" and inform user; do not fix only one path

7. **Plan the fix — MANDATORY GATE**

   ⛔ **DO NOT write any fix code until this step is completed and the user has approved the plan.**

   **Pre-check:** If bug symptom involves value display/transfer, verify Step 5 `[值域检查]` table was produced. If not → return to Step 5 before proceeding.

   **Consumer impact (mandatory for any fix that changes a field's value or source):**

   Before presenting the plan, list all consumers of the modified field:
   ```
   [Consumer Impact]
   - {consumer file:line} — 当前读取: {X} — 修复后读取: {Y} — 行为变化: {description}
   ```
   Cannot produce this list = have not traced the data flow = return to Step 5.

   Classify fix complexity:

   **Simple** — ALL must be true:
   - Fix is confined to ≤2 file locations
   - All changes are directly evident from verified assertions
   - Step 5 not triggered, or all consumers showed ✅
   - Step 6 not triggered, or no parallel path issues flagged

   **Complex** — ANY is true:
   - Fix spans 3+ file locations
   - Step 5 found any ❌ consumer beyond the original bug site
   - Step 6 flagged parallel paths without coordination
   - Fix requires architectural changes

   **Required actions:**

   → If **Simple**: enter Claude Code native plan mode (`EnterPlanMode`).
     Present diagnosis context (confirmed assertions, consumer impact) in the plan.
     User reviews and approves within plan mode, then proceed to Step 8.

   → If **Complex**: invoke `/write-plan` with the diagnosis context
     (confirmed assertions, value domain trace, parallel path analysis) as input.
     Wait for plan approval before proceeding.

   **Proceeding to Step 8 without a user-approved plan is a violation of this skill's protocol.**

8. **Fix the root cause**
   - Address the actual cause, not just the symptom
   - Consider edge cases and related scenarios
   - Ensure the fix doesn't introduce new issues
   - After the fix is complete, suggest: "Consider running `/collect-lesson` to record this bug pattern for future retrieval."

9. **Verify the fix**
   - Build the project
   - Reproduce the original bug scenario - confirm it's fixed
   - Test related scenarios to catch regressions
   - **If this fix originated from a GitHub Issue (Step 0):** ask the user: "Close issue #N?" If yes, run: `gh issue close N`. Display the closed issue URL.

10. **Tradeoff Report**

   After verification, produce a fix report. Format depends on complexity
   (same classification as Step 7):

   **Simple fix (1-2 locations):**

   ```
   [Fix Summary] 修复 X/Y 项（跳过: {items} — {理由}）

   [Tradeoff] {修复内容} — 行为变化: {before -> after} — 代价: {known cost} — 验证: {status}
   ```

   **Complex fix (3+ locations):**

   ```
   [Fix Summary] 修复 X/Y 项（跳过: {items} — {理由}）

   | Issue | 修复前行为 | 修复后行为 | 收益 | 代价 | 验证状态 | 回归风险 |
   |-------|-----------|-----------|------|------|---------|---------|
   | ...   | ...       | ...       | ...  | ...  | ...     | ...     |
   ```

   **Mandatory fields:**
   - **验证状态**: `verified` (ran test/command and saw expected output) or
     `needs-device-verification: {specific steps}` (cannot verify in current environment)
   - **回归风险**: if behavioral change, state impact scope (which callers/consumers affected)
   - **Completeness**: "修复 X/Y 项" — every skipped item must have a reason

   Build passing alone is compile-time verification only. Runtime behavioral changes
   (conditional rendering, data-dependent logic, network failure paths) require either
   a test or explicit `needs-device-verification` annotation.

## Escalation Rules

### 3-Strike Rule

If you have attempted 3+ fixes and none resolved the issue:

**Stop fixing. Question the architecture.**

Signals of an architectural problem:
- Each fix reveals new coupling or shared state in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

Action: Discuss with the user before attempting more fixes. This is not a failed hypothesis; this is likely a wrong architecture.

### Proposal Rejection Circuit Breaker

If the user rejects 2 consecutive fix proposals:

**Stop proposing. Return to diagnosis.**

A rejection is any user response that does not approve proceeding with the proposed fix. Partial approvals ("direction is right but...") count as rejections; they indicate the proposal was insufficient.

1. The rejections indicate incomplete understanding, not a communication problem
2. Return to Step 5 (value domain trace) or Step 6 (parallel paths); whichever was skipped or incomplete
3. Produce the full `[值域检查]` or `[路径检查]` output before making another proposal
4. Do NOT ask "is this direction correct?"; show the trace results and let the data speak
5. If both Step 5 and Step 6 were already completed, escalate to the 3-Strike Rule or ask the user what dimension was missed

Continuing to propose without deeper investigation = repeating the same mistake with different words.

### Diagnostic Layering (multi-component systems)

When the bug spans multiple components (e.g., CI -> build -> signing, API -> service -> database):

**Before proposing any fix**, add diagnostic instrumentation at each component boundary:

```
For EACH component boundary:
  - Log what data enters the component
  - Log what data exits the component
  - Verify environment/config propagation
  - Check state at each layer
```

Run once to gather evidence showing WHERE the break occurs. Then narrow investigation to the specific failing component. Do not guess which layer is broken.

### Pattern Analysis

When the root cause isn't obvious from assertions alone:

1. **Find a working example** — locate similar working code in the same codebase
2. **Compare systematically** — list every difference between working and broken, however small
3. **Don't assume irrelevance** — "that can't matter" is how bugs hide

## Completion Criteria

- Root cause identified with code evidence (file:line)
- Fix applied and build passes
- Original bug scenario verified fixed (Step 9 completed)
- All ❌ consumers from value domain trace fixed (if Step 5 triggered)
- No parallel path coordination issues left unresolved (if Step 6 triggered)
- Tradeoff Report produced with verification status for every fix item (Step 10 completed)
