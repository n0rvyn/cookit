---
name: run-phase
description: "Use when the user says 'run phase', 'start phase N', 'next phase', '继续开发', '跑下一阶段', '开始第N阶段', or when continuing development guided by a dev-guide. Orchestrates the plan-execute-review cycle for one phase of a development guide."
---

## Overview

This skill orchestrates one iteration of the development cycle. Opus handles judgment-intensive steps (planning, fixing) in main context; Sonnet handles mechanical execution as a dispatched agent; Opus reviews in dispatched agents for unbiased assessment.

```
Locate/Resume Phase
  → scope confirmation checkpoint (main context — opus)
  → write plan (main context — opus, full conversation context)
  → UX review checkpoint (main context — if design has UX Assertions)
  → verify plan (dispatch opus agent — unbiased review)
  → execute plan (dispatch sonnet agent — mechanical, follows verified plan)
  → dispatch feature-spec + review agents in parallel (separate contexts)
  → fix all issues (main context — opus: execution failures + review gaps)
  → Phase done
```

## State File

Location: `.claude/dev-workflow-state.yml`

This file tracks progress across sessions. Update it **before** starting each step (so crash-resume works). Read/write via the Read and Write tools.

```yaml
project: <name>
current_phase: 2
phase_name: "Phase Name"
phase_step: plan    # plan | ux-review | verify | execute | review | fix | done
dev_guide: docs/06-plans/YYYY-MM-DD-project-dev-guide.md
plan_file: null  # set to docs/06-plans/YYYY-MM-DD-<name>-plan.md after Step 2
verification_report: null
task_progress: null
review_reports: []
gaps_remaining: 0
last_updated: "YYYY-MM-DDTHH:MM:SS"
```

## Process

### Step 1: Resume or Locate Phase

1. Check for `.claude/dev-workflow-state.yml`:
   !`cat .claude/dev-workflow-state.yml 2>/dev/null || echo "NO_STATE_FILE"`
   If output is "NO_STATE_FILE": proceed to step 2 (starting fresh).
   Otherwise: parse the YAML content from the output.
   - If `phase_step` is `spec` (legacy): treat as `review` and proceed to Step 5
   - If `phase_step` is `build-test` (legacy): treat as `review` and proceed to Step 5. Note: build/test from the old separate step was not run; finalize will catch any issues via full test suite.
   - If `phase_step` is not `done`:
     - Present: "Phase {N} ({name}) in progress — step: {phase_step}. Resume?"
     - If user accepts:
       - **Scope drift check** (only when `phase_step` is `plan` AND `plan_file` is not null): Read the Phase's current scope from the dev-guide and compare with the plan file's `Scope:` section. If they differ: "Dev-guide scope has changed since the plan was written. Re-run scope confirmation (Step 1.5)?" If user accepts: reset `phase_step: plan`, `plan_file: null`, and run Step 1.5. If user declines: proceed with existing plan. For steps after `plan` (verify/execute/review/fix): no check needed — the plan is the working document.
       - Skip to the step indicated by `phase_step`
     - If user declines: ask which Phase to start
2. If no state file or starting fresh:
   - Find dev-guide: `docs/06-plans/*-dev-guide.md` (if multiple, prefer the file with `current: true` in frontmatter; if no file has a `current:` field in frontmatter, treat all as candidates and ask user)
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
task_progress: null
review_reports: []
gaps_remaining: 0
last_updated: "<now>"
```

If the user specifies a different Phase number, use that instead.

### Step 1.5: Scope & Visual Expectation Confirmation

Before writing the plan, present the Phase scope and visual expectations for explicit user confirmation.

**Skip condition:** When resuming from state file with `phase_step` not `plan`, skip this step — scope was already confirmed in a prior session.

**Freshness check:** Before presenting, read the dev-guide's YAML frontmatter for `confirmed_at:`. If the timestamp is within 60 minutes of now, use **lightweight mode** (step 1b). Otherwise, use **full mode** (step 1a).

**1a. Full mode** (default):

Read the Phase's scope items and `**用户可见的变化:**` section from the dev-guide. Present to the user:

```
Phase {N} — confirm before planning:

范围：
1. {scope item 1}
2. {scope item 2}
...

用户可见的变化：
- {visual expectation 1, from dev-guide}
- {visual expectation 2}
（如果有需要补充的布局、交互细节，请在这一步告诉我）

确认以上内容，或补充/修正后继续。
```

If `**用户可见的变化:**` starts with "无" (infrastructure Phase, e.g., "无" or "无 — 纯基建阶段"), present scope only (omit the visual section).

**1b. Lightweight mode** (confirmed_at within 60 min):

```
Phase {N} 范围已在 dev-guide 中确认。
有新增视觉/交互细节要补充吗？没有则直接开始规划。
```

User responds:
- No additions → proceed to Step 2 (skip steps 3-4 below)
- Adds visual/interaction details → proceed to step 4 (auto-crystal), same as full mode

3. Wait for user response (full mode only):
   - User confirms without additions → proceed to Step 2
   - User corrects scope → edit the Phase's `**Scope:**` bulleted list in the dev-guide file to match user's corrections, then check acceptance criteria sync (see below), re-present for confirmation
   - User adds visual/interaction details → proceed to step 4 (auto-crystal)
   - Max 2 correction cycles; after that, proceed with last-confirmed content

   **Acceptance criteria sync** (after scope correction): Compare the Phase's `**Acceptance criteria:**` with the updated scope:
   - If any criterion references a removed scope item → flag: "验收标准 '{criterion}' 对应的范围项已移除，是否同步删除？"
   - If new scope items lack corresponding criteria → flag: "新增范围项 '{item}' 无验收标准，是否补充？"
   - Present flags to user. Apply user's decisions (delete/add criteria) to the dev-guide before re-presenting the Phase.
   - If no mismatches found, skip silently.

4. **Auto-crystal** (conditional): If the user's response contains any new visual/interaction detail not already in the dev-guide's `用户可见的变化` section, treat as "adds details" regardless of whether they also said "confirmed."

   **4a. Assemble decisions:** Extract from the user's input:
   - Each confirmed visual/interaction detail → `[D-xxx]` in imperative form
   - Each explicitly rejected approach → `## Rejected Alternatives` + `## Constraints`
   - If no alternatives were discussed or rejected, write `None.` for those sections

   **4b. Confirm with user:** Present the assembled decisions in-line:
   ```
   以下视觉/交互决策将记录供后续规划使用：
   - [D-001] {detail}
   - [D-002] {detail}
   约束：{constraints, or "无"}

   确认记录，或修改后继续。
   ```
   Apply user edits if any, then proceed to write.

   **4c. Write crystal file:**
   - First, search `docs/11-crystals/*-crystal.md` for an existing crystal file
   - **If an existing crystal file is found:** append the visual decisions to it — add new `[D-xxx]` entries (continuing the existing numbering) to `## Decisions (machine-readable)`, merge new items into `## Constraints` and `## Scope Boundaries`. Do not overwrite existing content.
   - **If no existing crystal file:** create `docs/11-crystals/YYYY-MM-DD-phase-{N}-visual-crystal.md` using this format:

   ```markdown
   # Decision Crystal: Phase {N} Visual Expectations

   Date: YYYY-MM-DD

   ## Initial Idea
   {User's original visual description, denoised but not rewritten}

   ## Discussion Points
   {Any back-and-forth from the confirmation, if applicable}

   ## Rejected Alternatives
   {Approaches the user explicitly rejected, or "None."}

   ## Decisions (machine-readable)
   - [D-001] {confirmed visual/interaction detail in imperative form}
   - [D-002] {detail}

   ## Constraints
   {Explicitly rejected visual approaches, or "None."}

   ## Scope Boundaries
   - IN: {items from user's visual additions}

   ## Source Context
   - Design doc: {path or "none"}
   - Dev-guide: {dev-guide path} Phase {N}
   ```

   - Do NOT invoke /crystallize as a separate skill — write the file directly

This checkpoint catches scope pollution and aligns visual expectations before writing the plan.

### Step 2: Plan (main context)

1. Update state: `phase_step: plan`, `last_updated: <now>`
2. Gather Phase context from dev-guide:
   - Goal: Phase N's goal
   - Scope: Phase N's scope items
   - Acceptance criteria: Phase N's acceptance criteria
   - Design doc reference: from dev-guide header (if exists)
   - Design analysis reference: search `docs/06-plans/*-design-analysis.md`; if exactly 1 file, use it; if multiple, use the one whose filename matches the Phase's feature topic; if still ambiguous, ask the user; if none, set to "none"
   - Crystal file reference: search `docs/11-crystals/*-crystal.md`; if exactly 1 file, use it; if multiple, ask the user which one applies; if none, set to "none"
   - If no crystal file found AND the Phase has architecture decisions marked as "resolved" in the dev-guide: suggest `/crystallize` to capture these decisions before planning. Do not block — user can decline and proceed without a crystal file.
3. If a design doc path exists: read the design doc and check for a `## UX Assertions` section. Note the result — it controls Step 2.5.
4. **Preload relevant lessons:**
   - Extract keywords from Phase scope items and goal (component names, technology terms, domain terms)
   - Search `docs/09-lessons-learned/` for entries matching these keywords:
     `Grep(pattern="<keyword1>|<keyword2>|<keyword3>", path="docs/09-lessons-learned/", output_mode="content", context=5)`
   - If matches found: note the matching lesson entries for reference during plan writing
   - If no matches or directory does not exist: skip silently
5. **Read source files:** Read the design doc, design analysis, crystal file (if any), and key codebase files relevant to the Phase scope. This grounds the plan in actual code state.
6. **Write the plan** following the Plan Writing Reference in `${CLAUDE_PLUGIN_ROOT}/skills/write-plan/SKILL.md`. Use the gathered Phase context as inputs. Save to `docs/06-plans/YYYY-MM-DD-<feature-name>-plan.md`.
7. Update state: `plan_file: <path>`, `last_updated: <now>`
8. Present plan summary to user (task count, key files)
9. **Decision Points:** Check the `## Decisions` section of the plan file.
   - If Decisions > 0: read the section
   - For each `blocking` decision: present to user via AskUserQuestion with options from the decision point
   - For `recommended` decisions: present as a group via a single AskUserQuestion. **Critical:** all DP content must be inside the `question` field — text printed before AskUserQuestion gets visually covered by the question widget. Read each recommended DP's full block (heading + Context + Options + Recommendation) from the plan file and concatenate them verbatim in the question field, separated by `\n---\n`. End with: `\n\n全部接受推荐，还是逐个审查？`
   - If the user does NOT choose to accept all: present each DP individually via separate AskUserQuestion calls. Do not assume any DP is accepted until the user explicitly confirms it
   - Record user choices: edit the plan file, replace the `**Recommendation:**` or `**Recommendation (unverified):**` line with `**Chosen:** {user's choice}`
10. Auto-select verification speed: count tasks in the plan file.
    If task count < 5: mark `--fast` flag for Step 3 (use Sonnet for verification).
    If task count ≥ 5: no flag (use Opus default).

### Step 2.5: UX Review (conditional)

**Trigger condition:** The design doc contains a `## UX Assertions` section with at least one assertion row (not just the header). If no design doc, no UX Assertions section, or the table has zero assertion rows, skip to Step 3.

1. Update state: `phase_step: ux-review`, `last_updated: <now>`
2. Read the generated plan file
3. Read the design doc's `## UX Assertions` table and `## User Journeys` section
4. Build a mapping table:

For each UX assertion:
- Find plan tasks with `UX ref: UX-NNN` matching this assertion
- Extract the task's `User interaction:` line (if present)

For each UI-facing plan task without a `UX ref:`:
- Note as unmapped

5. Present to user:

```
UX Assertion Coverage:

| UX ID | Assertion | Plan Task(s) | User Interaction | Status |
|-------|-----------|-------------|-----------------|--------|
| UX-001 | {assertion text} | Task 3, Task 5 | {from task's User interaction: line, or "—"} | ✅ Mapped |
| UX-002 | {assertion text} | — | — | ❌ No task |
| UX-003 | {assertion text} | Task 7 | {from task} | ✅ Mapped |

Unmapped UI tasks (no UX ref):
- Task 4: {task title} — {reason or "needs UX assertion?"}

Confirm this mapping is correct, or provide corrections.
```

6. Wait for user response:
   - **User confirms**: proceed to Step 3
   - **User provides corrections**:
     - For minor fixes (add/correct `UX ref:` lines, adjust `User interaction:` text): edit the plan file directly
     - For structural changes (add missing tasks, redesign task scope): revise the plan directly in main context
     - Re-present the mapping for confirmation after corrections
   - Max 2 correction cycles; after that, proceed with noted gaps

7. Update state: `last_updated: <now>`

### Step 3: Verify

**Auto-approve condition:** If ALL of the following are true:
- Plan has 3 or fewer tasks
- No design doc reference (or set to "none")
- No crystal file reference (or set to "none")

Then skip full agent verification. Instead:
1. Read the plan file
2. Perform inline sanity check in main context:
   - Each task has `**Files:**` and `**Steps:**` sections
   - Task dependencies (if any) are ordered correctly
   - No obvious gaps (e.g., task references a file not listed in any task's Files)
3. Update state: `phase_step: verify`, `verification_report: "auto-approved (small plan)"`, `last_updated: <now>`
4. Skip to Step 4

**Otherwise:** proceed with full verification below.

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

### Step 4: Execute (sonnet agent dispatch)

1. Update state: `phase_step: execute`, `last_updated: <now>`
2. Dispatch the `dev-workflow:execute-plan` agent (sonnet) with the plan file path and project root
3. When the agent returns: read the execution report
4. Present summary: completed/blocked/failed task counts
5. If blocked or failed tasks exist: note them for Step 6 (Fix)
6. Update state: `last_updated: <now>`

### Step 5: Document Features & Reviews (parallel agent dispatch)

1. Update state: `phase_step: review`, `last_updated: <now>`

2. **Determine agents to dispatch:**

   **Feature spec agents (conditional):**
   - Check the Phase scope for completed user journeys (a user journey is "completed" when all its acceptance criteria in the dev-guide are checked off)
   - If this is NOT an infrastructure-only Phase: confirm feature name and scope with the user, then prepare `dev-workflow:feature-spec-writer` dispatch for each completed feature
   - If infrastructure-only (no user journeys): no feature-spec-writer dispatch

   **Review agents (always at least one):**
   - **Always:** `dev-workflow:implementation-reviewer` agent
   - **If Phase modified UI files:** `apple-dev:ui-reviewer` — pass list of modified `*View.swift` files
   - **If Phase created new pages/components:** `apple-dev:design-reviewer` — pass list of new View files
   - **If Phase completed a full user journey:** `apple-dev:feature-reviewer` — pass feature scope + key files
   - **If this is the submission prep Phase:** invoke `/submission-preview` skill after agents complete

3. **Dispatch ALL agents in parallel** using the Task tool in a single message:

   For feature-spec-writer (if applicable):
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

   For implementation-reviewer (always): pass plan file path + project root
   For apple-dev agents (conditional):
   - `apple-dev:ui-reviewer` (if UI files modified): pass list of modified `*View.swift` files
   - `apple-dev:design-reviewer` (if new pages/components): pass list of new View files
   - `apple-dev:feature-reviewer` (if full user journey completed): pass feature scope + key files

   Each agent receives a fresh context — they have no memory of how the code was written.
   This removes confirmation bias from self-review.

4. **When all return:** Verify each agent's reported output file exists (Read the path). If any file is missing, note it as "❌ File not produced" in the summary — do not retry review agents (their output is informational, not blocking).

5. Present a consolidated summary table:

| Agent | Verdict | Issues | Report/Spec |
|-------|---------|--------|-------------|
| Feature Spec: {name} | ✅/❌ | {user story counts} | {path} |
| Implementation | ✅/❌ | {gap counts} — Tests: {required}/{exist}/{covered} | {path} |
| UI | ✅/❌ | {counts} | {path} |
| Design | ✅/❌ | {counts} | {path} |
| Feature Review | ✅/❌ | {counts} | {path} |

6. **Feature spec decision points:** If feature-spec-writer was dispatched, check its return for `Decisions:` count.
   - If Decisions > 0: read the `## Decisions` section from the spec file
   - For each `blocking` decision: present to user via AskUserQuestion with options from the decision point
   - For `recommended` decisions: present as a group via a single AskUserQuestion. **Critical:** all DP content must be inside the `question` field — text printed before AskUserQuestion gets visually covered by the question widget. Read each recommended DP's full block (heading + Context + Options + Recommendation) from the spec file and concatenate them verbatim in the question field, separated by `\n---\n`. End with: `\n\n全部接受推荐，还是逐个审查？`
   - If the user does NOT choose to accept all: present each DP individually via separate AskUserQuestion calls. Do not assume any DP is accepted until the user explicitly confirms it
   - Record user choices: edit the spec file, replace the `**Recommendation:**` or `**Recommendation (unverified):**` line with `**Chosen:** {user's choice}`

7. **Surface human verification items:** If any review report's compact summary shows 人工验证项 > 0 or 设备验证项 > 0:
   - Read each report file that has verification items
   - Extract items from these sections:
     - ui-reviewer: `### Part C: 人工验证清单`
     - design-reviewer: `### Part B: 设备验证清单`
     - feature-reviewer: `### Part C: 设备验证清单`
   - Consolidate, deduplicate, and present in plain language below the summary table:

   > 以下需要在设备上确认（来自 review 报告）：
   > - [ ] {item, translated to spatial language — use screen position and appearance, NO code identifiers}
   > - [ ] {item}
   > - [ ] ⚠️ 需真机：{animation/transition items}

   This is informational — do not block with AskUserQuestion. The user can raise issues during Step 6 (Fix Gaps).

8. **Surface test coverage summary:** If implementation-reviewer's compact return includes a `Tests:` line:
   - Extract: required, exist, pass, shell counts
   - If shell > 0 or pass < required: present warning below the human verification items:
     > ⚠️ 测试覆盖不完整：{N} 个计划要求的测试中，{M} 个为空壳或未覆盖核心路径

9. Update state: `review_reports: [<report file paths from agent summaries>]`, `last_updated: <now>`

### Step 6: Fix Issues

If any of the following have issues: execution report (blocked/failed tasks) or review reports (gaps):

1. Update state: `phase_step: fix`, `last_updated: <now>`
2. Collect all issues from two sources:
   a. **Execution failures** (from Step 4): blocked/failed tasks from the execute-plan agent report (includes build/test failures from the plan's final verification task)
   b. **Review gaps** (from Step 5): plan-vs-code gaps, pre-existing issues
   Read the relevant report files for full details. Skip entries that are not file paths (e.g., `"user-override"` sentinel values).
3. List all issues sorted by severity (critical first, then warnings)
   Separate by origin:
   - **执行阻塞（{N} 个）：**
   > - {blocked/failed tasks with reasons, including build/test failures}
   - **Review 问题（{N} 个）：**
   > - {plan-vs-code gaps}
   - **已有问题（{M} 个）：**
   > - {pre-existing issues from implementation-reviewer}

4. Ask the user: "Fix these issues before moving on, or mark as known issues?"
5. If fixing:
   a. **Separate design issues from code issues.** If design-reviewer report exists among review_reports:
      - Extract all 🔴 items from design-reviewer Part A
      - Group by category: Hierarchy (A1, A11), Spacing (A3, A12), Consistency (A5, A6), Color (A2)
      - Present design issues separately from other review issues:
        > 设计问题（{N} 个必须修复）：
        > - {category}: {count}
        > 代码/UI 问题（{M} 个）：
        > - {summary}
   b. Fix all issues (design + code), then re-run only the reviews that had failures
   c. **Design re-verification limit**: If design-reviewer still fails after 1 fix cycle,
      report remaining design issues and proceed — do not loop.
      Other reviewers (implementation, UI, feature) follow existing behavior.
6. If skipping: note the known issues and proceed
7. Update state: `gaps_remaining: <count>`, `last_updated: <now>`
8. **Decision Points:** Check each review report for `Decisions:` count.
   - If any report has Decisions > 0: read the `## Decisions` section from that report
   - For each `blocking` decision: present to user via AskUserQuestion with options from the decision point
   - For `recommended` decisions: present as a group via a single AskUserQuestion. **Critical:** all DP content must be inside the `question` field — text printed before AskUserQuestion gets visually covered by the question widget. Read each recommended DP's full block (heading + Context + Options + Recommendation) from the report file and concatenate them verbatim in the question field, separated by `\n---\n`. End with: `\n\n全部接受推荐，还是逐个审查？`
   - If the user does NOT choose to accept all: present each DP individually via separate AskUserQuestion calls. Do not assume any DP is accepted until the user explicitly confirms it
   - Record user choices: edit the report file, replace the `**Recommendation:**` or `**Recommendation (unverified):**` line with `**Chosen:** {user's choice}`
   - Then proceed to Step 7

### Step 7: Phase Completion

0. **Pre-completion gate** (structural enforcement):
   - Read `review_reports` from state file
   - If `review_reports` is empty (no reports):
     **BLOCK**: "Cannot complete phase: no review reports found. Run Step 5 before marking phase as done."
     Do NOT proceed. Use AskUserQuestion:
     - Option A: "Run Step 5 now" → return to Step 5
     - Option B: "Skip review and complete phase" → add `review_reports: ["user-override"]`, log override, proceed
   - If any review report has verdict ❌ AND `gaps_remaining` > 0:
     **BLOCK**: "Cannot complete phase: {gaps_remaining} unresolved gaps."
     Do NOT proceed. Use AskUserQuestion:
     - Option A: "Fix gaps (Step 6)" → return to Step 6
     - Option B: "Mark as known issues and complete" → proceed with gaps noted

1. Update state: `phase_step: done`, `last_updated: <now>`
2. Update the dev-guide:
   - Check off this Phase's acceptance criteria
   - Add status line: `**Status:** ✅ Completed — YYYY-MM-DD` after the Phase heading
3. **Issue archival** (conditional): If Step 6 has items marked as "known issues" or skipped gaps:
   - Ask: "Create GitHub Issues for {N} deferred items?"
   - If yes:
     - Check label existence: `gh label list --json name -q '.[].name'`
     - If `deferred` label doesn't exist, create it: `gh label create "deferred" --color "FBCA04" --description "Deferred from phase review"`
     - If `phase-{N}` label doesn't exist, create it: `gh label create "phase-{N}" --color "0E8A16" --description "Phase {N}"`
     - For each deferred item, run `gh issue create` with labels `deferred` and `phase-{current phase number}`. Use the item description as issue body under `### Symptom`.
   - Display all created issue URLs.
4. Remind the user to update project docs:
   - `docs/07-changelog/` — record changes
   - `docs/03-decisions/` — if architectural decisions were made
5. Report:

   **Detect if this is the last phase:** After checking off this Phase's acceptance criteria (step 2 above), re-read the dev-guide. If ALL phases now have all acceptance criteria checked (`- [x]`), this is the last phase.

   **If more phases remain:**
   > Phase N complete.
   > Next: Phase N+1 — [name]: [goal].
   > Run `/run-phase` to continue, or `/commit` to save progress first.

   **If all phases are complete:**
   > Phase N complete. All phases done.
   > Run `/finalize` for cross-phase validation, or `/commit` to save progress.

## Rules

- **Never skip Step 5.** Reviews are not optional.
- **Never skip verification.** Step 3 must run before Step 4.
- **Phase order matters.** Don't start Phase N+1 if Phase N has unchecked acceptance criteria (unless user explicitly overrides).
- **Consolidate review output.** Merge all review results into one summary with sections.
- **State before action.** Update state file before starting each step, not after.

## Completion Criteria

- Phase acceptance criteria checked off in dev-guide (Step 7)
- State file `phase_step` set to `done`
- Next phase communicated to user
