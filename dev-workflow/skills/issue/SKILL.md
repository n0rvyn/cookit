---
name: issue
description: "Use when the user says 'issue', wants to list/read/create GitHub Issues, or needs to record a bug/idea/question discovered during development. Unified GitHub Issue entry point."
user-invocable: true
---

## Overview

GitHub Issue unified entry point. Supports list, read, and create operations via `gh` CLI.

Core flow: `/issue` creates issues with prior hypotheses (via `/generate-vf-prompt`) that `/fix-bug` can later consume for higher diagnostic accuracy.

## Process

### Step 0: Parse Input

Determine operation from user input:

- **No arguments** -> Step 1 (list)
- **Argument starts with `#`** (e.g., `#5`) -> Step 2 (read)
- **Other text** -> Step 3 (create)

### Step 1: List Issues

1. Run: `gh issue list --state open --json number,title,labels,milestone`
2. Format output as table (use `--` for empty labels or missing milestone):

```
| # | Title | Labels | Milestone |
|---|-------|--------|-----------|
| {number} | {title} | {labels or "--"} | {milestone or "--"} |
```

3. End with: "Select an issue: `/issue #N` to read, or `/fix-bug #N` to start fixing."

### Step 2: Read Issue

1. Extract issue number N from input
2. Run: `gh issue view N --json title,body,labels,milestone,state`
3. Present:
   - Title + state (open/closed)
   - Labels + Milestone
   - Body (including prior hypotheses if present)
4. End with: "Run `/fix-bug #N` to start fixing this issue."

### Step 3: Create Issue

#### 3.1 Quick Validation (optional)

If the user's description references specific files or code locations, read those files to confirm the problem exists. Skip if the description is abstract (idea, question).

#### 3.2 Generate Prior Hypotheses

If the issue type is **bug** (from Step 3.3, can be determined early from description):

1. Read the files identified in Step 3.1 (or files mentioned in the user's description)
2. Generate 3-5 falsifiable candidate error assertions using the S1 template:

```
[Candidate Error 1] {specific hypothesis about what's wrong}
Location: {file:line}
Verify: {how to confirm or falsify}
```

Assertion dimensions (pick the most likely from the description):
- **Value domain error** — type/range/format mismatch
- **State timing error** — race condition, wrong lifecycle stage
- **Path routing error** — data reaching wrong handler
- **Missing guard** — null/empty/boundary unhandled
- **Stale code interference** — replaced component still active

These assertions become "prior hypotheses" written into the issue body.

If the issue is not a bug (enhancement/question), or no relevant files can be read, skip this step — write "N/A" in the prior hypotheses section.

#### 3.3 Classify

Determine issue type from description:

| Type | Label | Signal |
|------|-------|--------|
| Bug | `bug` | Error, crash, incorrect behavior, regression |
| Enhancement | `enhancement` | New feature, improvement, optimization |
| Question | `question` | Unclear behavior, design question, investigation needed |

#### 3.4 Pre-conditions

1. Verify repo: `gh repo view --json owner,name -q '.owner.login + "/" + .name'`
2. Verify required labels exist: `gh label list --json name -q '.[].name'`
   - If the classified label doesn't exist, create it before proceeding

#### 3.5 Create Issue

Build issue body:

```markdown
### Symptom

{user's description of the problem or need}

### Prior Hypotheses

{falsifiable assertions from Step 3.2, or "N/A — not a bug" for enhancement/question}

### Related Files

{files identified during validation, or "TBD"}

### Notes

{any additional context from user}
```

Create: `gh issue create --title "{title}" --label "{label}" --body "{body}"`

#### 3.6 Output

Display the created issue URL and number.

End with: "Run `/fix-bug #{N}` to start fixing, or `/issue` to see all open issues."

## Completion Criteria

- **List** (Step 1): open issues displayed in table format
- **Read** (Step 2): issue content displayed with title, state, labels, body
- **Create** (Step 3): issue created, URL displayed, prior hypotheses included (for bugs)

## Principles

1. **Zero overhead**: `gh` CLI only, no MCP or external service setup required
2. **Prior hypotheses are optional**: issue creation must not fail if files are unreadable or issue is not a bug
3. **Format consistency**: issue body sections must match what `/fix-bug` Step 0 expects to parse (section header: `### Prior Hypotheses`)
