---
name: writing-plans
description: "Use when you have a spec or requirements for a multi-step task, before touching code. Creates comprehensive implementation plans with bite-size tasks."
user-invocable: false
---

## When to Use

- Cross-session features that need a persistent plan document (for `dev-workflow:handing-off` or future sessions)
- Plan is a deliverable itself (sharing with collaborators, archiving decisions)
- Need design anchor fields (`Design ref`, `Expected values`, `Replaces`) to ensure design fidelity during execution

## Core Principle

Write plans assuming the implementing engineer has zero context. Document everything: files to touch, code snippets, commands, expected output.

## Plan Document Format

Save to: `docs/06-plans/YYYY-MM-DD-<feature-name>.md`

### Required Header

```markdown
# [Feature Name] Implementation Plan

**Goal:** [One sentence]

**Architecture:** [2-3 sentences on approach and key decisions]

**Tech Stack:** [Key technologies and frameworks]

**Design doc:** [path to design doc, if one exists — links to verifying-plans DF strategy]

---
```

### Task Structure

Each task should be a coherent unit of work. Don't force artificial granularity — a task can be small or substantial as long as it's self-contained and verifiable.

```markdown
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
```

These fields are optional per-task. Use them when the task has design-critical details that could drift during implementation.

## Writing Guidelines

1. **Complete file paths** — always absolute from project root
2. **Actual code** — not pseudocode, not "implement X here"
3. **Exact commands** — copy-pasteable verification commands with expected output
4. **Dependencies explicit** — if Task 3 depends on Task 1, say so
5. **No forced TDD** — write tests where they add value; don't mandate test-first for every step
6. **Reasonable task size** — self-contained and independently verifiable; not artificially split

## After Writing the Plan

Inform the user of execution options:
- `dev-workflow:executing-plans` — batch execution with checkpoints and review
- Claude `/plan` mode — plan-mode execution with approval gates
