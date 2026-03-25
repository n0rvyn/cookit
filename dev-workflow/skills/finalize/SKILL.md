---
name: finalize
description: "Use after all phases of a dev-guide are complete, or when the user says 'finalize', 'final check', 'cross-phase validation'. Runs full test suite, verifies acceptance criteria across all phases, audits cumulative test coverage, and produces a final validation report."
allowed-tools: Bash(npm:*) Bash(cargo:*) Bash(pytest:*) Bash(go:*) Bash(xcodebuild:*) Bash(swift:*) Bash(git:*) Bash(mkdir:*) Bash(test:*) Bash(cat:*) Bash(ls:*) Bash(date:*) Bash(wc:*) Bash(find:*)
---

## Overview

Cross-phase validation gate. Runs after all dev-guide phases are complete to catch regressions, missing tests, and broken acceptance criteria that per-phase reviews miss.

```
Validate preconditions (all phases done?)
  → Full test suite (0 fail, 0 skip)
  → Cross-phase acceptance criteria regression check
  → Dev-guide scope deliverable verification
  → Cumulative test coverage audit
  → Generate report
  → Present results
```

## Process

### Step 1: Validate Preconditions

1. Check for `.claude/dev-workflow-state.yml`:
   !`cat .claude/dev-workflow-state.yml 2>/dev/null || echo "NO_STATE_FILE"`
   - If state file exists: read `dev_guide` path from it
   - If no state file: search `docs/06-plans/*-dev-guide.md`. If `docs/06-plans/` does not exist, ask user for the dev-guide path via AskUserQuestion. If multiple dev-guides found, prefer the file with `current: true` in frontmatter; if none has `current:`, ask user.
2. Read the dev-guide file
3. Parse all `## Phase N:` sections. For each Phase:
   - Count acceptance criteria: `- [x]` = checked, `- [ ]` = unchecked
   - Record: phase number, phase name, total criteria, checked criteria
4. If ANY Phase has unchecked acceptance criteria:
   - List incomplete Phases with their unchecked criteria
   - **BLOCK** with AskUserQuestion:
     - Option A: "Go back and complete phases" → stop
     - Option B: "Override and validate anyway" → proceed, note override in report
5. Record: `total_phases`, `phase_list`, `dev_guide_path`, `override` (true/false)

### Step 2: Full Test Suite

1. Auto-detect test runner:
   - `package.json` exists → `npm test`
   - `Cargo.toml` exists → `cargo test`
   - `pyproject.toml` or `setup.py` exists → `pytest`
   - `go.mod` exists → `go test ./...`
   - `*.xcodeproj` or `*.xcworkspace` exists → detect scheme via `xcodebuild -list -json`, pick the scheme containing "Tests" or the main app scheme; use `-destination 'platform=iOS Simulator,name=iPhone 16'` (fallback: `platform=macOS`); if detection fails, fall through to "ask user"
   - None found → ask user for the test command via AskUserQuestion
2. Run the full test suite. Capture output.
3. Parse results: total, passed, failed, skipped
4. **If failed > 0:**
   - List each failing test (name + failure reason)
   - **BLOCK**: "Fix failing tests before finalization."
   - Stop. User must fix and re-run `/finalize`.
5. **If skipped > 0:**
   - List each skipped test
   - **BLOCK**: "Finalization requires 0 skips. Unskip or remove these tests."
   - Stop. User must fix and re-run `/finalize`.
6. All pass, 0 skip → proceed

### Step 3: Cross-Phase Acceptance Criteria Regression

1. For each completed Phase, read its acceptance criteria from the dev-guide
2. For each criterion, extract **identifiers** (proper-cased words like `ConfigManager`, paths with `/` or `.swift`/`.ts` extensions) and determine verification type:

| Criterion pattern | Check method | Example |
|---|---|---|
| Contains file/directory path (has `/` or file extension) | `test -f {path}` or `ls {path}` | "Config file at Sources/Config.swift" → check file |
| Contains a proper-cased identifier (PascalCase or camelCase) | Grep for that identifier | "ConfigManager handles settings" → grep `ConfigManager` |
| Contains "test" + file reference | Verify test file exists and is non-empty | "Unit tests for DataStore" → check test file |
| Contains "compiles" / "builds" / "no errors" | Already covered by Step 2 | skip |
| No extractable identifier or path | Mark as "manual verification needed" | "Users can log in with OAuth" → manual |

   **Do NOT** pattern-match generic English words like "class", "function", "set". Only extract identifiers that are code symbols (PascalCase, camelCase, snake_case, or quoted names).

3. Run each check. Record: Phase, criterion text, check type, result (pass/fail/manual)
4. Output table:

```
Cross-Phase Acceptance Criteria:

| Phase | Criterion | Check | Result |
|-------|-----------|-------|--------|
| 1 | Config file at Sources/Config.swift | file exists | ✅ |
| 2 | SettingsView renders options | grep SettingsView | ✅ |
| 3 | Push notifications registered | grep UNUserNotification | ❌ REGRESSION |
```

5. Failures = regression warnings. Do NOT block here; the test suite (Step 2) is the hard gate. Include in report.

### Step 3.5: Dev-Guide Scope Deliverable Verification

This step catches scope items promised in the dev-guide but never created — the gap that per-phase reviews miss when phases are executed without the full plan/verify/review cycle.

1. For each Phase section in the dev-guide, read the **scope description** (the bullet list or paragraph under the Phase heading, before acceptance criteria).
2. Extract **file deliverables**: any token that looks like a file or component name:
   - Tokens with file extensions: `ChannelForm.tsx`, `ConfigManager.swift`, `auth.test.ts`
   - Tokens matching `path/to/file` patterns: `web/src/components/channels/ChannelCard.tsx`
   - PascalCase tokens immediately followed by a file-type context word (e.g., "ChannelForm component", "AuthService class") — extract as `{Token}.{inferred extension}` based on project language
   - Ignore generic words, acceptance-criteria identifiers (already covered by Step 3), and test files (covered by Step 4)
3. For each extracted deliverable:

| Check | Method |
|---|---|
| Exact path given | `test -f {path}` |
| Filename only (no directory) | `find . -name "{filename}" -not -path "*/node_modules/*" -not -path "*/.git/*"` |
| Component name (no extension) | Grep for `{name}` in source files matching the project's primary extensions |

4. Output table:

```
Dev-Guide Scope Deliverables:

| Phase | Deliverable | Check | Result |
|-------|-------------|-------|--------|
| 12 | ChannelForm.tsx | find -name | ❌ NOT FOUND |
| 12 | ChannelCard.tsx | find -name | ❌ NOT FOUND |
| 12 | ChannelMessages.tsx | find -name | ✅ Found at web/src/pages/Channels.tsx:L45 |
```

5. Deliverables not found = scope gaps. Do NOT block (soft gate, same as Step 3). Include in report.

### Step 4: Cumulative Test Coverage Audit

This step catches tests that per-phase implementation-reviewer missed.

1. **Collect all plan files:**
   - Read the dev-guide. For each Phase section, look for a plan file reference (link or `Plan:` field)
   - If the dev-guide references plan file paths directly: use those
   - If not: search `docs/06-plans/*-plan.md` and match by phase name/number in the plan's `## Context` or `Scope:` header
   - List any plan files that cannot be matched to a Phase as "orphaned" in the report

2. **Extract test requirements from plans:**
   - For each plan file: read all tasks
   - Find tasks with test files in `**Files:**` sections, or tasks that are explicitly test tasks (title contains "test", "Test", category "testing")
   - Build cumulative list of required test files

3. **Verify each required test file:**

| Check | Method | Status |
|---|---|---|
| File exists | `test -f {path}` | T-exist |
| Non-empty (has test functions) | File length > minimal threshold + contains test function signatures | T-content |
| Has assertions | Grep for assertion patterns: `#expect`, `XCTAssert`, `expect(`, `assert`, `it("`, `test("`, `.to(`, `.toBe(` | T-assert |

   Classify each test file:
   - ✅ Covered: exists + has assertions
   - ⚠️ Shell: exists but no assertions (empty body)
   - ❌ Missing: file does not exist

4. **Scan for untested source files:**
   - Identify the commit that added the dev-guide file and store the hash:
     !`git log --diff-filter=A --format=%H -- {dev_guide_path} | head -1`
   - If no result (dev-guide not tracked in git): skip the untested-source-files scan and note "base commit not found — untested files scan skipped" in the report
   - Get source files modified since that point (omit HEAD to include uncommitted changes):
     !`git diff --name-only <the hash from above> -- '*.swift' '*.ts' '*.tsx' '*.js' '*.jsx' '*.py' '*.go' '*.rs'`
   - For each modified source file: check if a corresponding test file exists (convention: `FooTests.swift` for `Foo.swift`, `foo.test.ts` for `foo.ts`, `test_foo.py` for `foo.py`)
   - List source files with no corresponding test

5. Output:

```
Cumulative Test Coverage:

Plan-required tests: {N}
- ✅ Covered (exist + assertions): {M}
- ⚠️ Shell (exist, no assertions): {K}
- ❌ Missing: {J}

| Plan | Test File | Status |
|------|-----------|--------|
| Phase 1 plan | Tests/ConfigTests.swift | ✅ |
| Phase 2 plan | Tests/SettingsViewTests.swift | ⚠️ Shell |
| Phase 3 plan | Tests/NotificationTests.swift | ❌ Missing |

Untested source files (no corresponding test):
- Sources/Helpers/DateFormatter.swift
- Sources/Services/CacheManager.swift
```

### Step 5: Generate Report

1. **Update state file:** If `.claude/dev-workflow-state.yml` exists, update it:
   ```yaml
   phase_step: finalized
   last_updated: "<now>"
   ```
   This prevents the SessionStart hook from prompting "Resume phase?" after finalization.
2. `mkdir -p .claude/reviews`
3. Write to `.claude/reviews/finalize-{YYYY-MM-DD-HHmmss}.md`:

```markdown
# Finalization Report

**Dev-guide:** {path}
**Date:** {YYYY-MM-DD HH:MM}
**Phases:** {N} total, {M} validated
{If override: **⚠️ Override:** Phases {list} had unchecked criteria}

## Test Suite
- Runner: {detected runner}
- Total: {N}, Passed: {P}, Failed: {F}, Skipped: {S}
- Result: ✅ All tests pass / ❌ {F} failures, {S} skipped

## Cross-Phase Acceptance Criteria
- Total criteria: {N}
- Auto-verified: {M} ✅
- Regressions: {K} ❌
- Manual verification needed: {J} ⚠️

{criteria table from Step 3}

## Scope Deliverables
- Total deliverables extracted: {N}
- Found: {M} ✅
- Not found: {K} ❌

{deliverables table from Step 3.5}

## Cumulative Test Coverage
- Plan-required tests: {N}
- Covered: {M} ✅
- Shell/empty: {K} ⚠️
- Missing: {J} ❌

{coverage table from Step 4}

## Untested Source Files
{list from Step 4, or "None"}

## Verdict
{One of:}
✅ Ready for integration — all tests pass, no regressions, full coverage
⚠️ Conditionally ready — all tests pass, {N} warnings (see above)
❌ Not ready — {summary of blocking issues}

### Action Items
{Numbered list of issues to fix, if any}

### Manual Verification Checklist
{Items marked "manual" from Step 3, if any}
- [ ] {criterion — in spatial/behavioral language}
```

### Step 6: Present Results

1. Print compact summary:

```
Finalization complete.
Tests: {P}/{N} pass, {S} skip, {F} fail
Criteria: {M}/{N} verified, {K} regressions, {J} manual
Scope: {M}/{N} deliverables found, {K} missing
Coverage: {M}/{N} plan-required covered, {K} shell, {J} missing
Untested files: {count}
Report: .claude/reviews/finalize-{timestamp}.md
Verdict: ✅ Ready / ⚠️ Warnings / ❌ Not ready
```

2. If regressions found: list each with Phase number and criterion text
3. If test coverage gaps: list shell/missing test file paths
4. If manual verification items exist: print the checklist
5. Suggest next action:
   - ✅ Ready: "Run `/commit` to save, then `/finish-branch` to integrate."
   - ⚠️ Warnings: "Review the warnings above. If acceptable, `/commit` and `/finish-branch`. Otherwise fix and re-run `/finalize`."
   - ❌ Not ready: "Fix the issues above, then re-run `/finalize`."

## Rules

- **Step 2 is a hard gate.** Test failures and skips block finalization. No override.
- **Steps 3-4 (including 3.5) are soft gates.** Regressions, scope gaps, and coverage gaps are reported but do not block. The test suite is the authoritative pass/fail.
- **One report per run.** Each `/finalize` invocation produces a new timestamped report. Previous reports are not overwritten.
- **No code fixes.** This skill validates and reports. It does not fix issues. The user fixes and re-runs.

## Completion Criteria

- Full test suite passes with 0 fail, 0 skip
- Cross-phase acceptance criteria checked (regressions flagged if any)
- Dev-guide scope deliverables verified (missing items flagged if any)
- Cumulative test coverage audited (gaps flagged if any)
- Report written to `.claude/reviews/`
- Verdict communicated to user
