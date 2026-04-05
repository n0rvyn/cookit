---
name: lint
description: "Internal skill — performs wiki health check by dispatching wiki-linter agent. Generates health report, optionally applies auto-fixes for low/medium severity issues. Triggered by weekly cron or via /pkos lint."
model: sonnet
---

## Overview

Wiki health maintenance. Dispatches `pkos:wiki-linter` agent for read-only audit, then applies fixes based on severity level.

## Arguments

- `--fix`: Apply auto-fixes for low and medium severity issues after showing report
- `--report-only`: Generate report without any fixes (default behavior)

## Process

### Step 1: Dispatch Wiki Linter

Dispatch `pkos:wiki-linter` agent with vault path `~/Obsidian/PKOS/`.

Receive the structured YAML report.

### Step 2: Write Health Report

Write report to `~/Obsidian/PKOS/70-Reviews/lint-{today}.md`:

```markdown
---
type: lint
created: {today}
health_score: {score}
---

# Wiki Health Report — {today}

## Summary
- Total notes: {N} | Health score: {score}/100
- Orphans: {N} | Missing MOCs: {N} | Stale: {N}
- Broken links: {N} | Frontmatter issues: {N} | Contradictions: {N}

## High Severity — Needs Attention
{For each high issue: description + suggestion}

## Medium Severity — Recommended Fixes
{For each medium issue: description + suggestion + [auto-fixable] tag if applicable}

## Low Severity — Batch Fixable
{For each low issue: description + suggestion}
```

### Step 3: Apply Auto-Fixes (if --fix)

If `--fix` flag is set, apply these mechanical fixes:

**Orphan notes (low):**
- For each orphan, find notes with >=2 overlapping topics
- Add mutual entries to `related:` frontmatter arrays

**Frontmatter incomplete (medium):**
- Missing `topics`: infer from content keywords, add to frontmatter
- Missing `status`: set to `seed`
- Missing `type`: infer from directory (10-Knowledge → knowledge, etc.)

**MOC stale (medium):**
- Dispatch `pkos:ripple-compiler` for the most recent uncompiled note in each stale MOC's topic

**DO NOT auto-fix:**
- Broken links (may require user judgment on correct target)
- Contradictions (requires human evaluation)
- Missing MOCs (creation should go through ripple-compiler organically)

### Step 4: Report

```
PKOS Lint — {date}
  Health score: {score}/100
  Issues: {high} high, {medium} medium, {low} low
  {if --fix} Auto-fixed: {N} orphans linked, {N} frontmatter completed, {N} MOCs recompiled
  Report: ~/Obsidian/PKOS/70-Reviews/lint-{date}.md
```

## Notes

- Weekly cron runs with `--report-only` by default
- Users can request `--fix` via `/pkos lint --fix`
- Health score trends visible by comparing sequential lint reports
