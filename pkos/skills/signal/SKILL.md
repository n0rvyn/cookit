---
name: signal
description: "Internal skill — collects behavioral signals from Notion pipeline and Obsidian graph. Triggered by Adam cron (daily 10pm)."
model: sonnet
---

## Overview

Collect behavioral signals from the PKOS ecosystem for feedback loop analysis. Aggregates data from Notion pipeline flow, Obsidian graph density, and search behavior.

## Arguments

- `--days N`: Signal collection window in days (default: 1)
- `--verbose`: Show detailed signal breakdown per source

## Process

### Step 1: Collect Notion Pipeline Metrics

Query Notion Pipeline DB for items in the collection window:

```bash
NO_PROXY="*" python3 ~/.claude/skills/notion/scripts/notion_api.py query-db \
  32a1bde4-ddac-81ff-8f82-f2d8d7a361d7 \
  --filter '{"and": [{"property": "Created", "date": {"on_or_after": "{start_date}"}}]}'
```

From the results, calculate:
- **Flow speed**: Count items by Status (inbox/triaged/processed/actionable/done/archived)
- **Archive rate**: archived count / total count, grouped by Source
- **Action rate**: actionable+done count / total count, grouped by Source

### Step 2: Collect Obsidian Graph Density

Scan vault frontmatter for notes created in the window:

```bash
grep -rl "created: {date_pattern}" ~/Obsidian/PKOS/10-Knowledge/ ~/Obsidian/PKOS/20-Ideas/ ~/Obsidian/PKOS/50-References/ 2>/dev/null
```

For each note found:
- Count `tags` from frontmatter → topic hotness distribution
- Count `[[wikilinks]]` in body → new links added
- Find notes with zero incoming links → orphan count

Use Grep to find backlinks:
```
Grep(pattern="\\[\\[{note-name}\\]\\]", path="~/Obsidian/PKOS", output_mode="count")
```

### Step 3: Aggregate and Write Signal File

Combine all metrics and write to signal file:

```bash
mkdir -p ~/Obsidian/PKOS/.signals
```

Write `~/Obsidian/PKOS/.signals/{today}-feedback.yaml`:

```yaml
date: {today}
window_days: {N}
pipeline:
  total_items: {count}
  by_status:
    inbox: {N}
    processed: {N}
    actionable: {N}
    archived: {N}
  archive_rate_by_source:
    voice: {pct}
    reminder: {pct}
    domain-intel: {pct}
  action_rate_by_source:
    voice: {pct}
    reminder: {pct}
graph:
  new_notes: {N}
  topic_hotness:
    topic1: {count}
    topic2: {count}
  new_links: {N}
  orphan_count: {N}
```

### Step 4: Report

Present summary:
```
📊 PKOS Signal Report ({date}, {N}-day window)

Pipeline:
  Total items: {N}
  Action rate: {pct}% | Archive rate: {pct}%
  Noisiest source: {source} ({archive_rate}% archived)

Knowledge Graph:
  New notes: {N} | New links: {N} | Orphans: {N}
  Hottest tags: {tag1} ({N}), {tag2} ({N})

Signal written to .signals/{date}-feedback.yaml
```

## Dispatches

- `pkos:signal-aggregator` agent for cross-source pattern analysis (optional, for weekly deep analysis)
