---
name: digest
description: "Internal skill — generates daily/weekly digest. Triggered by Adam cron (daily 7:30am, weekly Sunday 9am)."
model: sonnet
---

## Overview

Generate a daily or weekly digest summarizing PKOS activity. Includes new captures, domain-intel highlights, processing statistics, and actionable items.

## Arguments

- `--type TYPE`: daily (default) or weekly
- `--date DATE`: Generate for specific date (default: today, format: YYYY-MM-DD)

## Process

### Step 1: Gather Data

**Recent captures from Notion Pipeline DB:**
```bash
NO_PROXY="*" python3 ~/.claude/skills/notion/scripts/notion_api.py query-db \
  32a1bde4-ddac-81ff-8f82-f2d8d7a361d7 \
  --filter '{"property": "Created", "date": {"on_or_after": "{start_date}"}}'
```

**Recent Obsidian notes:**
```bash
find ~/Obsidian/PKOS/10-Knowledge ~/Obsidian/PKOS/20-Ideas ~/Obsidian/PKOS/50-References \
  -name "*.md" -newer ~/Obsidian/PKOS/.signals/{yesterday}-feedback.yaml 2>/dev/null
```

**Domain-intel highlights (if available):**
```bash
ls ~/Obsidian/PKOS/50-References/domain-intel/{today}* 2>/dev/null
```

**Signal data (if available):**
```bash
cat ~/Obsidian/PKOS/.signals/{today}-feedback.yaml 2>/dev/null
```

### Step 2: Compose Digest (dispatch digest-writer agent)

Dispatch `pkos:digest-writer` agent with all gathered data. The agent composes the digest markdown.

### Step 3: Write to Obsidian Daily Note

Write or append to `~/Obsidian/PKOS/60-Digests/{today}.md`:

```markdown
---
type: daily
created: {today}
---

# {today}

## PKOS Daily Digest

### New Captures ({count} items)
{list from digest-writer}

### Intel Highlights
{from digest-writer}

### Pending ({count} items in inbox/triaged)
{from digest-writer}

### Quick Stats
- Processed: {N} | Actioned: {N} | Archived: {N}
- Knowledge graph: +{N} notes, +{N} links
```

If the file already exists (manual notes present), append the digest section after existing content.

### Step 4: Create Notion Summary (optional)

If a Weekly Review database exists in Notion, create an entry with the digest summary.

### Step 5: Push Notification

For high-priority items (urgency: high), create a Reminder:
```bash
${CLAUDE_PLUGIN_ROOT}/../mactools/skills/reminders/scripts/reminders.sh create \
  "PKOS: {count} high-priority items need attention" --list "PKOS Inbox"
```

### Step 6: Report

```
📋 PKOS {daily|weekly} Digest — {date}
  Captures: {N} new items
  Highlights: {N} intel items
  Pending: {N} items
  Written to: ~/Obsidian/PKOS/60-Digests/{date}.md
```
