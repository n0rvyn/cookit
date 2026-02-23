---
name: execution-review
description: 对照计划与代码执行结果，做实现完成度与偏差审查。
---

# Execution Review (iOS)

Verify implementation matches plan. Use **after execution**.

## Step 0: Retrieve Known Issues (if search tool available)

Before invoking the implementation reviewer, search for known issues related to the modified modules:

1. Identify the modified modules from the plan file or recent git changes (file names, component names, Swift type names)
2. Call `search(query="<modified module names and component keywords>", source_type=["error", "lesson"], project_root="<cwd>")`
3. If results are returned: note them as "Known issues for these modules:" — include them in the review context when presenting findings in the Output section
4. If the search tool is unavailable or returns no results: skip silently

## Step 1: Invoke Implementation Reviewer

Use the `dev-workflow:implementation-reviewer` agent to perform the full plan-vs-code verification and design fidelity audit (if design doc exists).

Wait for the agent to complete and present its findings before proceeding to Step 2.

## Step 2: iOS-Specific Code Scan

After the agent completes, perform these iOS/Swift-specific checks on all new or modified files:

### Localization
- UI text uses `String(localized:)` — no hardcoded user-facing strings
- Grep new files for quoted strings that look like user-facing text without `String(localized:)`

### Concurrency
- UI state updates wrapped with `await MainActor.run` or marked `@MainActor`
- ViewModels have `@MainActor`
- `@Model` types not passed across actor boundaries

### Abstraction
- Services have Protocol abstraction
- Dependencies injected, not hardcoded

### Error Handling
- Errors have catch handling
- No force unwraps (`!`) on optionals from external sources

## Step 3: Doc Updates

Verify documentation was updated:
- New/modified files → `docs/04-implementation/file-structure.md`
- Changes → `docs/07-changelog/YYYY-MM-DD.md`
- Architectural changes → ADR in `docs/03-decisions/`

## Output

Combine the implementation-reviewer agent's output with iOS-specific findings:

```
## Execution Review Summary (iOS)

### Implementation Review
{agent output — plan-vs-code gaps + design fidelity audit}

### iOS Code Scan
- Localization: {N} issues
- Concurrency: {N} issues
- Abstraction: {N} issues
- Error handling: {N} issues

### Doc Updates
- file-structure.md: ✅ updated / ❌ not updated
- changelog: ✅ updated / ❌ not updated
- ADR: ✅ created / ⚠️ not needed / ❌ missing

### Total
- Implementation gaps: {N}
- iOS issues: {N}
- Doc gaps: {N}
```
