---
name: write-plan
description: "Use when the user says 'write a plan', 'plan this', 'break this into tasks', '写计划', '拆分任务', or has requirements/specs for a multi-step task before touching code. Creates structured implementation plans with self-contained, verifiable tasks — each task lists files to touch, steps to take, and verification commands. Not when: trivial single-file change (just do it), plan file already exists (use verify-plan), or requirements still unclear (use brainstorm). For phase-driven development, run-phase calls this internally."
---

## Behavior Note

When invoked **standalone** (user runs write-plan directly): this skill automatically chains
to `dev-workflow:verify-plan` at Step 4 — plan writing and verification happen in one flow.

When invoked via **`run-phase`** orchestration: run-phase writes the plan in main context
using the Plan Writing Reference below, and manages verification as a separate explicit step.

## Overview

This skill writes an implementation plan directly in the main context, benefiting from full conversation history and user intent.

## Process

### Step 0: Retrieve Prior Context (if search tool available)

Before gathering context, search for relevant ADRs, architecture decisions, and known pitfalls:

1. Extract 3-5 keywords from the plan goal (component names, technology names, pattern names)
2. Call `search(query="<goal text>", source_type=["doc", "error", "lesson"], project_root="<cwd>")`
3. If results are returned: note them as "Prior context from knowledge base:" for use in Step 2
4. If the search tool is unavailable or returns no results: skip silently and continue to Step 1

### Step 1: Gather Context

Collect the following before writing:

1. **Goal** — one sentence describing what the plan achieves (from user request, dev-guide Phase, or conversation context)
2. **Scope items** — list of features/components to implement
3. **Acceptance criteria** — verifiable completion conditions (from dev-guide Phase or user)
4. **Design doc reference** — path to design doc if one exists (search `docs/06-plans/*-design.md`). If found, read it.
5. **Design analysis reference** — path to design analysis if one exists (search `docs/06-plans/*-design-analysis.md`). If found, read it: it contains validated token mappings, platform translations, and UX assertion validation from a visual prototype.
6. **Crystal file reference** — path to crystallized decisions file if one exists (search `docs/11-crystals/*-crystal.md`). If found, read it: it contains settled architectural and UX decisions with machine-readable D-xxx assertions the plan must respect.
7. **Project root** — current working directory

If any of these are unclear, ask the user before writing.

### Step 2: Write Plan

Read relevant source files (design docs, existing code the plan will touch, crystal files) to understand the current state. Then write the plan following the **Plan Writing Reference** below.

Save the plan to `docs/06-plans/YYYY-MM-DD-<feature-name>-plan.md`.

### Step 3: Present and Verify

After writing the plan:

1. Present a summary to the user:
   - Plan file path
   - Number of tasks
   - Key files to be created/modified
2. **Decision Points:** Check the `## Decisions` section of the plan file.
   - If Decisions > 0:
     - First time this session: Read `${CLAUDE_PLUGIN_ROOT}/references/decision-points.md`
     - Apply the rules with parameters:
       - Source file: the plan file
       - Mode: `full`
       - Recording: `default`
3. Invoke `dev-workflow:verify-plan` to validate the plan before execution

## Completion Criteria

- Plan file written to `docs/06-plans/`
- Verification invoked and plan approved (or user chose to proceed with noted issues)

---

## Plan Writing Reference

This section contains the plan document format, scope guards, and writing guidelines. Referenced by both this skill and `run-phase` Step 2.

### Core Principle

Write plans assuming the implementing engineer has zero context. Document everything: files to touch, code snippets, commands, expected output.

### Scope Guards

1. **Absence != deletion**: If the current codebase has functionality X that is not mentioned in the scope items, X's status is "unchanged" (keep as-is). Only create deletion/removal tasks when the scope explicitly says "remove", "delete", "移除", or "删除" for that functionality. Design docs showing a target state without feature X does NOT authorize removing X — that's a UX change requiring explicit user instruction in the scope. Exception: if a crystal `[D-xxx]` decision explicitly calls for removal/replacement, that decision overrides this guard (D-xxx decisions represent user-confirmed intent).

2. **Scope boundary compliance** (when crystal file has `## Scope Boundaries`):
   - IN items: plan tasks should cover these
   - OUT items: plan tasks must NOT touch these areas. If a task would need to modify an OUT item to complete an IN item, add a `**Scope conflicts:**` subsection after `**Crystal file:**` in the plan header: `IN: {item} requires modifying OUT: {item} — {why}`. Do not create the conflicting task; let the verifier and user resolve it.

3. **No scope inference**: Decomposing a scope item into implementation steps is expected (e.g., "migrate color tokens" → one task per token category). But adding work that addresses a DIFFERENT concern not in the scope items is prohibited, even if it seems like a natural extension (e.g., scope says "migrate color tokens" → adding a font migration task is scope inference). If you believe additional work is necessary, note it in the plan header as "Recommended additions (not in scope)" — do not create tasks for it.

4. **Quality fidelity** — If the design doc specifies a concrete approach for a feature (e.g., "LLM analysis", "Bree cron scheduler", "WordPiece tokenizer"), the plan task MUST implement that exact approach. If the specified approach is not feasible in this phase (missing dependency, API not available, infrastructure not ready), the task must:
   - Mark the task title with `⚠️ SIMPLIFIED:`
   - Add a `**Simplification:**` field explaining what was changed and why
   - Add a `**Design approach:**` field stating the original design's approach
   - Add a `**Blocking dependency:**` field if the simplification is due to a dependency not yet available (informational for human reviewers; not consumed by automated verification)
   Silently replacing a design-specified approach with a simpler alternative (heuristic, placeholder, stub) without these annotations is prohibited.

### Plan Document Format

```markdown
---
type: plan
status: active
tags: [tag1, tag2]
refs: []
---

# [Feature Name] Implementation Plan

**Goal:** [One sentence]

**Architecture:** [2-3 sentences on approach and key decisions]

**Tech Stack:** [Key technologies and frameworks]

**Design doc:** [path to design doc, if one exists — links to verify-plan DF strategy]

**Design analysis:** [path to design analysis, if one exists]

**Crystal file:** [path to crystal file, if one exists — links to verify-plan CF strategy]

**Threat model:** [included / not applicable]

---
```

### Task Structure

Each task should be a coherent unit of work. Don't force artificial granularity — a task can be small or substantial as long as it's self-contained and verifiable.

```markdown
<!-- section: task-N keywords: keyword1, keyword2 -->
### Task N: [Component/Feature Name]

**Files:**
- Create: `exact/path/to/file.ext`
- Modify: `exact/path/to/existing.ext:line-range`
- Test: `tests/exact/path/to/test.ext`

**Steps:**
1. [Clear instruction with code snippet if needed]
2. [Next step]
3. [Verification step with exact command and expected output]

**Verify:**
Run: `<exact command>`
Expected: <what success looks like>
<!-- /section -->
```

### Optional Design Anchor Fields

When a task implements part of a design document, add these fields to help execution stay faithful:

```markdown
**Design ref:** [design-doc.md § Section Name]
**Expected values:** [key concrete values from design that must appear in code]
**Replaces:** [what existing code/pattern this replaces, if any]
**Data flow:** [source → transform → destination]
**Quality markers:** [specific acceptance criteria beyond "it works"]
**Verify after:** [verification specific to design faithfulness]
**UX ref:** [UX-NNN from design doc's UX Assertions table — which assertion(s) this task fulfills]
**User interaction:** [what the user sees and does — derived from User Journeys, not invented]
```

These fields are optional per-task. Use them when the task has design-critical details that could drift during implementation.

### Writing Guidelines

1. **Complete file paths** — always absolute from project root
2. **Actual code** — not pseudocode, not "implement X here"
3. **Exact commands** — copy-pasteable verification commands with expected output
   - **Task-level `Verify:` scope**: each task's Verify should contain only that task's specific checks (grep for expected strings, type-check a single file, run a single test file). Full build/test suite execution is handled by the `test-changes` skill after plan execution completes; do not include full-suite commands (`npm run build`, `npm test`, `swift build`, `xcodebuild test`, or equivalent) in any plan task.
4. **Dependencies explicit** — if Task 3 depends on Task 1, say so
5. **Test coverage required, ordering flexible** — every plan must include tests for logic and user journeys (see item 10). Test-first vs test-after is the author's choice; test absence is not
6. **Reasonable task size** — self-contained and independently verifiable; not artificially split
7. **Task section markers:** Each `### Task N:` block is wrapped in `<!-- section: task-N keywords: {kw1}, {kw2} -->` ... `<!-- /section -->`. Keywords are derived from the task's `**Files:**` paths and the technologies/APIs the task touches. Use the leaf file name (without extension) and key technology names. 2-4 keywords per task.
8. **UX-aware tasks** — when the design doc has a `## UX Assertions` section: read the User Journeys and UX Assertions table before writing any UI task. Each task that implements user-visible behavior must include `UX ref:` pointing to the assertion ID(s) it fulfills, and a brief `User interaction:` line describing what the user sees and does (derived from the User Journeys, not invented). Tasks that touch UI but don't map to any UX assertion should be flagged with `⚠️ No UX ref: [reason]`
9. **Frontmatter fields:** `type` is always `plan`. `status` is always `active` when first written. `tags` — derive 2-5 keywords from the feature name and key technologies in the tasks (e.g., tasks touching SwiftData and sync → `[swiftdata, sync, offline]`). `refs` — list the design doc path and crystal file path from the plan header (if set to a real path, not "none").
10. **Mandatory test assessment** — evaluate and assign tests based on code type (enforces item 5):
    - **Business logic** (algorithms, data transformations, validation): **requires** Unit Tests
    - **User journeys** (end-to-end flows, API integrations): **requires** E2E Tests — only when the Phase has a complete user journey (UI + logic + data flow). Infrastructure-only Phases with no user-facing flow require UT only
    - **Performance-critical** (rendering, data processing, large datasets): recommends Performance Tests
    - **UI components** (views, controls, animations): recommends Snapshot Tests or UI Tests
    - When a task involves any of these code types, either:
      a. Create a separate test task with appropriate test type, OR
      b. Embed test verification steps in the functional task's `**Verify:**` section
    - **Skip conditions:** tasks that are pure config (editing .md/.yml/.json with no logic), style-only (CSS/layout with no conditional logic), or transparent pass-through to a third-party API may skip tests. Skipped tasks MUST annotate `⚠️ No test: {reason}` in the task body. plan-verifier will audit the reason
    - Platform-specific test implementations can reference apple-dev plugin skills:
      - UT/Mock/TDD → `apple-dev:testing-guide`
      - E2E/Snapshot/A11y → `apple-dev:xc-ui-test`
      - Performance → `apple-dev:profiling`
    - Plans missing UT for business logic tasks or E2E for user journey tasks will be flagged as **must-revise** by plan-verifier
11. **No final verification task** — Plans do NOT include a final "run everything" task. The `test-changes` skill handles full build/test/lint execution as a separate step after plan execution completes. Plans still include test-writing tasks (per guideline 10) — tests are written as code during execution, then run by test-changes afterward. Per-task `**Verify:**` commands remain lightweight: type-check (`tsc --noEmit`, `swift build`), grep for expected strings, or single-file compilation only. **Backward compatibility:** Old plans with a `### Task N: Full verification` task still execute correctly — execute-plan runs all tasks literally. The suite runs twice (once in plan, once in test-changes); redundant but not harmful.

### Security Assessment

When the plan goal, task descriptions, or scope items contain any of these security-signal keywords — `sandbox`, `permission`, `auth`, `RBAC`, `deny`, `allow`, `isolation`, `encrypt`, `token`, `credential`, `secret`, `certificate`, `injection`, `escape`, `validate` — the plan MUST include a `## Threat Model` section after the plan header and before Task 1. Set the header field `**Threat model:** included`. When none of these keywords appear, set `**Threat model:** not applicable` and omit the section.

The Threat Model section contains four subsections:

1. **Attack surface** — For each controlled input that could be attacker-influenced, identify the input source and attack class. Example: user-supplied file paths → path traversal/injection; user-supplied regex → ReDoS; user-supplied template strings → template injection.

2. **Failure modes** — For each new security component introduced by the plan (permission check, sandbox profile, auth gate, validation layer), document what happens when it fails silently. Acceptable answers: deny-all (safe default), allow-all (unsafe — must justify), crash/abort (acceptable for dev tooling, not for user-facing). Unspecified failure mode = gap the verifier will flag.

3. **Resource lifecycle** — For each task that creates temp files, spawns child processes, opens file handles, or opens sockets: document who cleans up on success, on error (catch/finally), and on signal/crash (SIGTERM/SIGINT handler or equivalent). All three triggers must be addressed; missing any one is a gap.

4. **Input validation requirements** — For each task that embeds external input into a structured format (SQL, shell commands, SBPL profiles, regex, template strings, URL parameters), document what characters must be validated or escaped and where in the code the validation occurs.

### Crystal File Integration

When a crystal file is provided: ensure every `[D-xxx]` decision is reflected in at least one plan task. Rejected alternatives in the crystal must not appear as plan tasks. Add `Crystal ref: [D-xxx]` to task headers that implement specific decisions.

### Design Analysis Integration

When a design analysis is provided: read it and incorporate token mappings, platform translations, and UX assertion validations into the relevant plan tasks.

### Decisions

If any planning finding requires a user choice before execution can proceed, output a `## Decisions` section in the plan document. If no decisions needed, output `## Decisions\nNone.`

Format per decision:

```
### [DP-001] {title} ({blocking / recommended})

**Context:** {why this decision is needed, 1-2 sentences}
**Options:**
- A: {description} — {trade-off}
- B: {description} — {trade-off}
**Recommendation:** {option} — {reason, 1 sentence}
```

**Recommendation quality rule:**
- Recommendations must cite code evidence (file:line or structural reasoning grounded in specific code). Example: "Option A; `Router.swift:42` shows routes are registered centrally, extending that pattern is lower-risk"
- If code evidence is unavailable (decision about a new pattern with no existing precedent): use `**Recommendation (unverified):**` instead of `**Recommendation:**`, and state why evidence is absent
- Self-check: remove the recommendation. Can a reader reach the same conclusion by following the cited evidence? If not, the evidence is insufficient

Priority levels:
- `blocking` — must be resolved before plan execution; the dispatcher will ask the user via AskUserQuestion
- `recommended` — has a sensible default but user should confirm; dispatcher presents as batch

Common decision triggers for plan writing:
- Scope conflicts detected (IN item conflicts with OUT item) → resolve or exclude (blocking)
- Recommended additions identified (needed but not in scope) → add to scope or defer (recommended)
- `**Replaces:**` patterns where old code removal is non-trivial → confirm removal (blocking)
