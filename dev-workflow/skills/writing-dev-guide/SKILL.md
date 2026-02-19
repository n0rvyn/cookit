---
name: writing-dev-guide
description: "Use when starting a new project's development after design is approved, or the user says 'write dev guide'. Creates a phased, project-level development guide that serves as the cornerstone document for all subsequent /plan cycles."
user-invocable: false
---

## When to Use

- After `project-kickoff` and `brainstorming` are done
- User says "write dev guide", "development roadmap", "plan the project"
- A project has a design doc and needs a phased implementation strategy

## Not This Skill

- Single feature plan → use `dev-workflow:writing-plans`
- Per-phase implementation details → use Claude `/plan` mode
- Design exploration → use `dev-workflow:brainstorming`

## Process

### Step 1: Collect Inputs

Read these documents (if they exist):
- `docs/01-discovery/project-brief.md` (from project-kickoff)
- `docs/06-plans/*-design.md` (from brainstorming)
- `docs/02-architecture/` (architecture docs)
- Project `CLAUDE.md` (tech stack, constraints)

If no project-brief or design doc exists, inform the user and suggest running the corresponding workflow first. Do not proceed without understanding the full scope.

### Step 2: Phase Planning

Based on the feature list and architecture, split the full development into ordered Phases.

**Phase splitting principles:**
- Each Phase has an independently verifiable deliverable (can build and see results)
- Phases have explicit dependencies (Phase 2 builds on Phase 1's infrastructure)
- Early Phases: infrastructure (data model, core Services, Design System)
- Middle Phases: main features
- Late Phases: secondary features, polish, submission prep
- No MVP splits — each Phase builds a part of the complete product, not a "minimum viable" version

Present the Phase outline to the user. **Wait for confirmation before writing the full document.** The user may want to reorder, merge, or split Phases.

### Step 3: Write the Development Guide

Save to: `docs/06-plans/YYYY-MM-DD-<project>-dev-guide.md`

**Document format:**

```markdown
# [Project Name] Development Guide

**Project brief:** docs/01-discovery/project-brief.md
**Design doc:** docs/06-plans/YYYY-MM-DD-<topic>-design.md
**Architecture:** docs/02-architecture/README.md

## Global Constraints

- Tech stack: [from CLAUDE.md]
- Coding standards: [from CLAUDE.md]
- Project-specific constraints: [from CLAUDE.md]

---

## Phase 1: [Name]

**Goal:** One sentence describing the state after this Phase completes.
**Depends on:** None / Phase N
**Scope:**
- Feature A
- Feature B

**Architecture decisions:** Key technical decisions this Phase needs to make (list decision points, don't pre-decide — leave to /plan stage).

**Acceptance criteria:**
- [ ] Specific verifiable condition 1
- [ ] Specific verifiable condition 2

**Review checklist:**
- [ ] /execution-review
- [ ] /ui-review (if Phase has UI)
- [ ] /design-review (if Phase has new pages)
- [ ] /feature-review (if Phase completes a full user journey)

---

## Phase 2: [Name]
...

---

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
```

**Writing guidelines:**
- Acceptance criteria must be concrete and testable (not "works well")
- Architecture decisions are listed as questions, not answers — the answers come during /plan
- Review checklist is per-Phase, tailored to what that Phase produces
- Each Phase's scope references specific features from the project brief / design doc

### Step 4: Next Steps

After saving, inform the user:

> Development guide saved. Use `/run-phase` to start the Phase 1 development cycle (plan → execute → review).
