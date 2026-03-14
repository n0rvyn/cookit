---
name: digest
description: "Use when the user says 'digest', 'generate report', 'weekly summary', or when invoked by cron. Generates a daily or weekly digest from accumulated insights by dispatching trend-synthesizer for pattern detection and synthesis."
model: sonnet
user-invocable: true
---

## Overview

Digest orchestrator for domain-intel. Collects insight files for a time range, dispatches trend-synthesizer (sonnet) for the heavy analytical work, formats and saves the report.

Designed for **cron execution** — produces a complete report without interaction.

## Process

### Step 0: Resolve Working Directory

```
Bash(command="pwd")
```

Store the result as `WD`. **All file paths in this skill are relative to `WD`** — prefix every `./` path with `{WD}/` when calling Read, Write, Glob, or Grep. Bash commands can use relative paths as-is.

### Step 1: Load Config

1. Read `{WD}/config.yaml`
   - If missing → output `[domain-intel] Not initialized. Run /intel setup in this directory.` → **stop**

### Step 2: Determine Time Range

Parse the argument (if any):

| Input | Interpretation |
|-------|---------------|
| (no argument) | Daily: today only |
| `week` | Past 7 days |
| `YYYY-MM-DD` | Single specific date |
| `YYYY-MM-DD YYYY-MM-DD` | Custom range (start end) |

Get today's date: `date +%Y-%m-%d`

Set `start_date` and `end_date`.

### Step 3: Collect Insights

1. For each date in the range, find matching insight files individually:
   ```
   For each date (YYYY-MM-DD) from start_date to end_date:
     Glob(pattern="{WD}/insights/{YYYY-MM}/{YYYY-MM-DD}-*.md")
   ```
   Glob does not support numeric date ranges, so iterate day by day. For efficiency, batch by month: compute which `YYYY-MM` directories are relevant, then within each directory, glob each date.

2. Read all matching insight files (exclude convergence signal files for now — collect those separately).

3. Also find convergence signal files:
   ```
   Grep(pattern="type: signal", path="{WD}/insights/", output_mode="files_with_matches")
   ```
   Filter to those within the date range: for each matched file, check that the filename date prefix (`YYYY-MM-DD` in the filename) falls within [start_date, end_date]. Discard files outside the range.

4. If zero insights found → output `[domain-intel] No insights found for {start_date} to {end_date}. Run /scan first.` → **stop**

### Step 4: Load Previous Trends (for continuity)

Find the most recent trend snapshot:
```
Glob(pattern="{WD}/trends/*-trends.md")
```

Read the most recent one (by filename date). If none exists, this is the first digest — no previous trends available.

### Step 4.5: Load LENS.md

Read `{WD}/LENS.md` if it exists:
- Extract the markdown body (everything after frontmatter) → store as `lens_context`
- If LENS.md does not exist → proceed without it

### Step 5: Dispatch trend-synthesizer

Dispatch `trend-synthesizer` agent with:
- **insights**: all collected insight file contents
- **convergence_signals**: any convergence signal file contents
- **domains**: domain definitions from config
- **time_range**: start_date to end_date
- **previous_trends**: previous trend snapshot content (or note that none exists)
- **lens_context**: LENS.md body content (or omit if no LENS.md)
- **query**: (not provided — Mode A: general synthesis)

Wait for completion. The agent returns:
```yaml
headline: "..."
trends: [...]
surprises: [...]
collective_wisdom: "..."
domain_summaries: [...]
```

### Step 6: Save Trend Snapshot

Write to `{WD}/trends/{end_date}-trends.md`:

```markdown
---
date: {end_date}
range: "{start_date} to {end_date}"
insight_count: {N}
trend_count: {N}
---

# Trend Snapshot — {start_date} to {end_date}

## Trends

{For each trend:}
### {name} ({direction})
Evidence: {insight IDs}
{summary}

## Surprises

{For each surprise:}
- **{title}** ({insight_id}): {why}
```

### Step 7: Check Evolution Signals

Skip this step if `{WD}/.lens-signals.yaml` does not exist.

1. Read `{WD}/.lens-signals.yaml`
2. If signals have accumulated since last digest:
   - Group signals by type
   - Prepare an "Evolution" section (to be included in the digest file in Step 8):

```markdown
## Evolution

The following patterns were detected that aren't reflected in your current profile:

| Type | Value | Evidence | Suggestion |
|------|-------|----------|------------|
| New interest | {value} | {N} insights | Consider adding to "What I Care About" |
| New figure | {value} | {N} mentions | Consider adding to figures[] |
| New company | {value} | {N} mentions | Consider adding to companies[] |
| New RSS | {url} | {N} insights | Consider adding to RSS feeds |
| New path | {company}: {path} | scanner discovery | Consider adding to company paths |
| New domain | {name} | {N} insights | Consider adding as tracking domain |

Run `/intel evolve` to review and apply these suggestions.
```

3. Do NOT auto-modify LENS.md or config.yaml. All changes require user approval via `/intel evolve`.

### Step 8: Format and Save Digest

Ensure directory: `mkdir -p ./digests`

Write to `{WD}/digests/{end_date}-digest.md` (include the Evolution section from Step 7 if signals were found):

```markdown
---
date: {end_date}
range: "{start_date} to {end_date}"
insight_count: {N}
---

# Domain Intel Digest — {start_date} to {end_date}

> {headline}

## Trends

| Trend | Direction | Evidence |
|-------|-----------|----------|
{For each trend: | {name} | {direction} | {evidence count} insights |}

{For each trend:}
### {name}

{summary}

Evidence: {insight IDs as comma-separated list}

## Surprises

{For each surprise:}
**{title}** — {why}
*Ref: {insight_id}*

## Collective Wisdom

{collective_wisdom}

## By Domain

{For each domain_summary:}
### {domain} ({activity})

{summary}

Top insight: {top_insight_id}

## Convergence Signals

{If any convergence signals in range:}
{Include the signal table from convergence files}

{If none:}
No cross-source convergence detected in this period.

{If evolution section prepared in Step 7:}
{Include the Evolution section here}

---

*Generated: {timestamp} | Insights analyzed: {N} | Range: {start_date} to {end_date}*
```

### Step 9: Mark Insights as Read

Batch-update all included insight files in one command instead of editing each individually:
```
Bash: sed -i.bak 's/^read: false$/read: true/' {space-separated list of file paths} && rm -f {same paths with .bak suffix}
```

This handles all files in a single call regardless of count.

### Step 10: Output

Display the full digest content to the terminal.

## Error Handling

- Zero insights in range: report and stop
- trend-synthesizer failure: output raw insight list as fallback (titles + significance + selection_reason)
- File write failure: report error, do not update state
