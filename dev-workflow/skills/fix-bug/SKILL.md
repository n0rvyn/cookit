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

0. **Retrieve historical context**
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

3. **BV: Generate falsifiable assertions**

   Based on error symptoms and code context, generate 3-5 specific, falsifiable assertions.
   Each assertion must include: hypothesis + file location + verification method + expected outcome for both cases.

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

5. **Trace value domain** (trigger: bug symptom is an incorrect value in display/log/data transfer)
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

7. **Plan the fix**

   Before writing any code, classify fix complexity:

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

   → If **Simple**: use Claude Code's built-in `/plan` to outline the fix before implementing
   → If **Complex**: invoke `dev-workflow:write-plan` to create a structured plan

8. **Fix the root cause**
   - Address the actual cause, not just the symptom
   - Consider edge cases and related scenarios
   - Ensure the fix doesn't introduce new issues
   - After the fix is complete, suggest: "Consider running `/collect-lesson` to record this bug pattern for future retrieval."

9. **Verify the fix**
   - Build the project
   - Reproduce the original bug scenario - confirm it's fixed
   - Test related scenarios to catch regressions

## Escalation Rules

### 3-Strike Rule

If you have attempted 3+ fixes and none resolved the issue:

**Stop fixing. Question the architecture.**

Signals of an architectural problem:
- Each fix reveals new coupling or shared state in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

Action: Discuss with the user before attempting more fixes. This is not a failed hypothesis; this is likely a wrong architecture.

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
