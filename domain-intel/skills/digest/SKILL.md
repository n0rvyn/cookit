---
name: digest
description: "Use when the user says 'digest', 'generate report', 'weekly summary', or when invoked by cron. Generates a daily or weekly digest from accumulated insights by dispatching trend-synthesizer for pattern detection and synthesis."
model: haiku
user-invocable: true
---

## Overview

Digest orchestrator for domain-intel. Collects insight files for a time range, dispatches trend-synthesizer (sonnet) for the heavy analytical work, formats and saves the report.

Designed for **cron execution** — produces a complete report without interaction.

## Process

### Step 1: Load Config and Resolve data_dir

1. Read `~/.claude/domain-intel.local.md` frontmatter
   - If missing or no `data_dir` → output `[domain-intel] Not configured. Run /intel setup.` → **stop**
2. Expand and verify `data_dir` exists

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
     Glob(pattern="{data_dir}/insights/{YYYY-MM}/{YYYY-MM-DD}-*.md")
   ```
   Glob does not support numeric date ranges, so iterate day by day. For efficiency, batch by month: compute which `YYYY-MM` directories are relevant, then within each directory, glob each date.

2. Read all matching insight files (exclude convergence signal files for now — collect those separately).

3. Also find convergence signal files:
   ```
   Grep(pattern="type: signal", path="{data_dir}/insights/", output_mode="files_with_matches")
   ```
   Filter to those within the date range.

4. If zero insights found → output `[domain-intel] No insights found for {start_date} to {end_date}. Run /scan first.` → **stop**

### Step 4: Load Previous Trends (for continuity)

Find the most recent trend snapshot:
```
Glob(pattern="{data_dir}/trends/*-trends.md")
```

Read the most recent one (by filename date). If none exists, this is the first digest — no previous trends available.

### Step 5: Dispatch trend-synthesizer

Dispatch `trend-synthesizer` agent with:
- **insights**: all collected insight file contents
- **convergence_signals**: any convergence signal file contents
- **domains**: domain definitions from config
- **time_range**: start_date to end_date
- **previous_trends**: previous trend snapshot content (or note that none exists)
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

Write to `{data_dir}/trends/{end_date}-trends.md`:

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

### Step 7: Format and Save Digest

Ensure directory: `mkdir -p {data_dir}/digests`

Write to `{data_dir}/digests/{end_date}-digest.md`:

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

---

*Generated: {timestamp} | Insights analyzed: {N} | Range: {start_date} to {end_date}*
```

### Step 8: Mark Insights as Read

Batch-update all included insight files in one command instead of editing each individually:
```
Bash: sed -i '' 's/^read: false$/read: true/' {space-separated list of file paths}
```

This handles all files in a single call regardless of count.

### Step 9: Output

Display the full digest content to the terminal.

## Error Handling

- Zero insights in range: report and stop
- trend-synthesizer failure: output raw insight list as fallback (titles + significance + selection_reason)
- File write failure: report error, do not update state
