---
name: write-dev-guide
description: "Use when starting a new project's development after design is approved, or the user says 'write dev guide', 'break down this project into phases', or '写开发指南'. Creates a phased, project-level development guide that serves as the cornerstone document for all subsequent /write-plan and /run-phase cycles. Not for single-feature plans (use write-plan) or design exploration (use brainstorm)."
---

## Overview

This skill writes a phased development guide directly in main context, benefiting from full conversation history and project discussion context.

## Not This Skill

- Single feature plan → use `dev-workflow:write-plan`
- Per-phase implementation details → use `/write-plan`
- Design exploration → use `dev-workflow:brainstorm`

## Process

### Step 1: Gather Context

Collect the following before writing:

1. **Project root** — current working directory
2. **Design doc path** — search `docs/06-plans/*-design.md`
3. **Project brief path** — check `docs/01-discovery/project-brief.md`
4. **Architecture docs path** — check `docs/02-architecture/`

If no project-brief or design doc exists, inform the user and suggest running the corresponding workflow first. Do not proceed without these inputs.

Read all found documents to ground the dev-guide in actual project state.

### Step 1.5: Check for Existing Dev-Guide

Before writing, check if a dev-guide already exists:

1. Glob `docs/06-plans/*-dev-guide.md`
2. If one or more files found: record them as `existing_dev_guides`
3. If no files found: skip to Step 2

### Step 2: Write Dev-Guide

Write the dev-guide following the **Dev-Guide Writing Reference** below. Save to `docs/06-plans/YYYY-MM-DD-<project>-dev-guide.md`.

### Step 2.5: Mark Old Dev-Guide as Superseded

After writing the new dev-guide:

1. If `existing_dev_guides` is empty: skip this step
2. For each path in `existing_dev_guides`:
   a. Read the file
   b. Check if it starts with YAML frontmatter (first line is `---`)
   c. If frontmatter exists: find the `current:` field and change its value to `false`
   d. If no frontmatter exists (older file without frontmatter): skip this file (do not add frontmatter to files that weren't written with it)
   e. Write the updated file back
3. Report: "Marked {N} existing dev-guide(s) as `current: false`: {paths}"

### Step 2.7: Quality Verification

After the dev-guide is written and old guides are superseded:

1. Dispatch the `dev-workflow:dev-guide-verifier` agent with:
   - Dev-guide file path
   - Design doc path (from Step 1)
   - Project brief path (from Step 1)
   - Architecture docs path (from Step 1)
   - Project root
   - Previously resolved decisions: none (decisions are resolved in Step 3, after verification)

2. Read the agent's compact summary.

3. If verdict is `approved`:
   - Report: "Quality verification passed."
   - Proceed to Step 3.

4. If verdict is `must-revise`:
   a. **V7 (Structural) issues**: directly Edit the dev-guide file to fix (frontmatter fields, missing sections, section markers — mechanical fixes only)
   b. **V1-V6 issues**: apply revision instructions directly in main context — re-read the relevant source docs and fix the flagged issues in the dev-guide file. Max 1 revision cycle.
   c. After revision: re-run V7 check only (structural, in main context — verify frontmatter fields, required sections, section markers) to confirm mechanical fixes. Do NOT re-dispatch the verifier agent.
   d. If V1-V6 issues persist after the single revision cycle: note the unresolved items and present them to the user in Step 3 alongside the Phase outline, so the user can decide whether to accept or manually adjust.
   e. If the verifier produced Decisions (DP-xxx entries): carry them forward to Step 3, where they will be presented alongside the dev-guide's own decisions.

### Step 3: Structural Review

After writing (and Step 2.7 passes or revision is done):

1. Extract the Phase outline and present as an overview table:

| Phase | Goal | Dependencies |
|-------|------|-------------|
| Phase 1 | {goal} | None |
| Phase 2 | {goal} | Phase 1 |
| ... | ... | ... |

2. **Decision Points:**
   **Ordering constraint:** The Phase outline table (step 1 above) must be presented to the user BEFORE any decision points. Do not reorder.
   - Collect decisions from two sources:
     a. Read the `## Decisions` section from the dev-guide file
     b. If Step 2.7 produced verifier Decisions, include those as well (prefix verifier DPs with `[V]` to distinguish source)
   - If both sources have `None.` content, skip to step 3. Otherwise, merge all `### [DP-xxx]` entries. Present blocking decisions first (regardless of source), then recommended.
   - Process each `### [DP-xxx]` entry:
   - **Comparison table** (all decisions): extract from the decision's `**Options:**` lines, keeping each option's `{description} — {trade-off}` as-is in one column:

     ### [DP-xxx] {title}

     **Context:** {from decision}

     | 方案 | 描述与代价 |
     |------|-----------|
     | A | {description} — {trade-off} |
     | B | {description} — {trade-off} |

   - **Recommendation line**: only for `recommended` decisions, append `**推荐:** {option} — {reason}` after the table. For `blocking` decisions, omit this line.
   - **AskUserQuestion**: for `recommended` decisions, mark the recommended option with "(推荐)" in the label. For `blocking` decisions, do not pre-select any option.
   - Record user choices: edit the dev-guide file, replace the `**Recommendation:**` or `**Recommendation (unverified):**` line with `**Chosen:** {user's choice}`
3. Ask user (AskUserQuestion): **确认结构** / **调整结构**（reorder, merge, split）
4. If user chooses「调整结构」:
   - Apply structural revision instructions directly in main context (re-read source docs, restructure Phases in the dev-guide file)
   - Re-present table, repeat until user confirms

### Step 4: Phase Details Review

Display all Phase details in one block, then confirm once.

1. For each Phase i = 1..N, present a detail table:

**Phase {i}: {goal}**

| 维度 | 内容 |
|------|------|
| 前置依赖 | {dependencies} |
| 范围项 | {scope items, bulleted} |
| 用户可见的变化 | {from dev-guide, or "无 — 纯基建阶段"} |
| 关键文件/组件 | {key files and components} |
| 待定架构决策 | {architecture decisions to resolve, or "无"} |
| 验收标准 | {acceptance criteria} |

2. After ALL Phase tables are displayed, ask user (AskUserQuestion): **整体确认** / **指定调整**
3. If user chooses「指定调整」:
   - User specifies which Phase(s) to change and what to change (scope, visual expectations, architecture decisions, or any combination)
   - **Content adjustments** (move scope items between Phases, edit visual expectations, resolve architecture decisions, adjust acceptance criteria): directly Edit the dev-guide file in main context. After editing, sync acceptance criteria if scope changed (same logic as run-phase Step 1.5: flag criteria referencing removed items, flag new items lacking criteria)
   - **Structural changes** (merge Phases, split a Phase, add/remove a Phase): apply directly in main context — restructure the dev-guide file
   - After content adjustments, re-present only the modified Phase table(s) for confirmation, not the full list
   - Max 2 adjustment cycles; after that, proceed with last-confirmed content
4. User confirms → proceed to Step 5.

### Step 4.5: Mark Confirmation Timestamp

After user confirms in Step 4, update the dev-guide file's YAML frontmatter:

1. Read the dev-guide file's first lines (frontmatter block between `---` markers)
2. If a `confirmed_at:` field exists: update its value to current ISO timestamp
3. If no `confirmed_at:` field: add `confirmed_at: YYYY-MM-DDTHH:MM:SS` after the `current:` field
4. Write back the file

This timestamp is consumed by run-phase Step 1.5 to avoid redundant scope confirmation.

### Step 5: Next Steps

After user confirms:

> Development guide saved. Use `/run-phase` to start the Phase 1 development cycle (plan → execute → review).

## Completion Criteria

- Dev-guide file saved to `docs/06-plans/`
- Quality verification passed or revision completed (Step 2.7)
- Structure confirmed by user (Step 3)
- Phase details reviewed and confirmed by user (Step 4)
- Previous dev-guide(s) marked `current: false` (Step 2.5)
- Next step (run-phase) communicated

---

## Dev-Guide Writing Reference

### Phase Splitting Principles

- Each Phase has an independently verifiable deliverable (can build and see results)
- Phases have explicit dependencies (Phase 2 builds on Phase 1's infrastructure)
- Early Phases: infrastructure (data model, core Services, Design System)
- Middle Phases: main features
- Late Phases: secondary features, polish, submission prep
- No MVP splits — each Phase builds a part of the complete product, not a "minimum viable" version

### Document Format

```markdown
---
type: dev-guide
status: active
tags: [tag1, tag2]
refs: []
current: true
---

# [Project Name] Development Guide

**Project brief:** docs/01-discovery/project-brief.md
**Design doc:** docs/06-plans/YYYY-MM-DD-<topic>-design.md
**Architecture:** docs/02-architecture/README.md

## Global Constraints

- Tech stack: [from CLAUDE.md]
- Coding standards: [from CLAUDE.md]
- Project-specific constraints: [from CLAUDE.md]

---

<!-- section: phase-1 keywords: {scope-keyword-1}, {scope-keyword-2} -->
## Phase 1: [Name]

**Goal:** One sentence describing the state after this Phase completes.
**Depends on:** None / Phase N
**Scope:**
- Feature A
- Feature B

**用户可见的变化:**
- {plain-language description of what the user will see/interact with after this Phase}
- {describe by screen location and appearance, not code identifiers}

**Architecture decisions:** Key technical decisions this Phase needs to make (list decision points, don't pre-decide — leave to /write-plan stage).

**Acceptance criteria:**
- [ ] Specific verifiable condition 1
- [ ] Specific verifiable condition 2
- [ ] Tests pass for this Phase's scope (UT for logic, E2E for user journeys)

**Review checklist:**
- [ ] /execution-review
- [ ] /ui-review (if Phase has UI)
- [ ] /design-review (if Phase has new pages)
- [ ] /feature-review (if Phase completes a full user journey)

<!-- /section -->

---

<!-- section: phase-N keywords: submission, app-store, accessibility -->
## Phase N: Submission Prep

**Goal:** App Store submission ready.
**Scope:**
- Performance optimization
- Accessibility audit
- Privacy compliance
- ASC materials

**Review checklist:**
- [ ] /submission-preview
- [ ] /appstoreconnect-review
<!-- /section -->
```

### Writing Guidelines

- Acceptance criteria must be concrete and testable (not "works well")
- Architecture decisions are listed as questions, not answers — the answers come during /write-plan
- Review checklist is per-Phase, tailored to what that Phase produces
- Each Phase's scope references specific features from the project brief / design doc
- 「用户可见的变化」uses spatial/functional language the user would use (e.g., "打开 App 后底部有 3 个标签" not "MainTabView with 3 tabs"). Source: design doc User Journeys and feature descriptions. Infrastructure-only Phases (no UI) write "无" for this section.
- **Section markers:** Each `## Phase N:` block is wrapped in `<!-- section: phase-N keywords: {kw1}, {kw2} -->` ... `<!-- /section -->`. Keywords are derived from the Phase's scope items: use noun forms of the key features and technologies (e.g., scope items "Implement SwiftData persistence", "Add offline queue" → keywords: `swiftdata, persistence, offline, queue`). 3-5 keywords per section.
- **Frontmatter fields:** `type` is always `dev-guide`. `status` is always `active` when first written. `tags` — derive 2-5 keywords from the project name and major feature areas in the Phases (e.g., `[sync, offline, swiftdata]`). `refs` — list paths to the design doc and project brief referenced in the header. `current` — always `true`; the write-dev-guide skill manages toggling this to `false` on the previously-current dev-guide.
- **Test acceptance criteria:** Every Phase must include at least one test-related acceptance criterion. Infrastructure Phases: "UT pass for {scope}". Phases with complete user journeys: "UT + E2E pass for {scope}". Phases with no logic (pure docs, ASC materials): may omit.

### Decisions

If any planning finding requires a user choice before the dev-guide can be finalized, output a `## Decisions` section in the dev-guide document. If no decisions needed, output `## Decisions\nNone.`

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
- `blocking` — must be resolved before dev-guide can be approved
- `recommended` — has a sensible default but user should confirm

Common decision triggers for dev-guide writing:
- Phase architecture decisions that affect multiple phases → pre-decide now or defer to /write-plan (recommended)
- Feature priority conflicts (two features compete for same Phase slot) → user decides ordering (blocking)
- Scope ambiguity in design doc → clarify before assigning to Phase (blocking)
