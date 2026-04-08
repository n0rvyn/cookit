---
name: vault
description: "Obsidian vault operations for PKOS knowledge graph. Use when the user says 'vault', 'search vault', '搜索笔记', or wants direct vault access. Not the primary entry point — use /pkos for most interactions."
model: haiku
---

## Overview

Obsidian vault operations for the PKOS knowledge graph at `~/Obsidian/PKOS/`.

## Execution Channel

This skill uses a dual-channel approach:

**Primary: Obsidian CLI** (`obsidian-cli` command) — when Obsidian is running, use CLI for all operations. Benefits: instant index updates, backlink tracking, search uses Obsidian's built-in engine.

**Fallback: Direct file operations** (Read/Write/Grep) — when Obsidian is not running or CLI is unavailable.

### Channel Detection

At the start of every vault command, detect which channel to use:

```bash
obsidian-cli version 2>/dev/null
```

- Exit code 0 → use CLI channel
- Non-zero or command not found → use file fallback channel

Cache the result for the duration of the skill invocation (don't re-check per sub-operation).

## Commands

Parse the user's intent to determine which operation to perform:

### vault search \<query\>

**CLI channel:**
```bash
obsidian-cli search query="{query}" vault="PKOS" limit=20
```

Also search frontmatter:
```bash
obsidian-cli search-content query="tags:.*{query}" vault="PKOS" limit=10
```

**File fallback:**
```
Grep(pattern="{query}", path="~/Obsidian/PKOS", output_mode="content", context=2, head_limit=20)
Grep(pattern="tags:.*{query}", path="~/Obsidian/PKOS", output_mode="files_with_matches")
```

Also search frontmatter tags:
```
Grep(pattern="tags:.*{query}", path="~/Obsidian/PKOS", output_mode="files_with_matches")
```

Present results grouped by directory (10-Knowledge, 20-Ideas, etc.) with matched context.

### vault read \<path\>

**CLI channel:**
```bash
obsidian-cli read file="{path}" vault="PKOS"
```

**File fallback:**
```
Read(file_path="~/Obsidian/PKOS/{path}")
```
If path is ambiguous: `Glob(pattern="**/{path}*", path="~/Obsidian/PKOS")`

### vault write \<path\> \<content\>

**CLI channel:**
```bash
obsidian-cli create name="{title}" content="{content}" vault="PKOS" silent
```
For updates (file exists):
```bash
obsidian-cli append file="{path}" content="{content}" vault="PKOS"
```
Or for full replacement, use file fallback (CLI doesn't support full overwrite cleanly).

**File fallback:**
Use the Write tool with `~/Obsidian/PKOS/{path}`. Confirm before overwriting.

Ensure frontmatter is valid YAML if present.

### vault frontmatter \<path\> [--set key=value]

**CLI channel:**
```bash
obsidian-cli property:set name="{key}" value="{value}" file="{path}" vault="PKOS"
```

**File fallback:**
Parse YAML frontmatter manually as before.

### vault stats

Vault statistics (file operations only — CLI doesn't expose aggregate stats):
```bash
echo "Notes by directory:"
for dir in 10-Knowledge 20-Ideas 30-Projects 40-People 50-References 60-Digests 70-Reviews 80-MOCs; do
  count=$(find ~/Obsidian/PKOS/$dir -name "*.md" 2>/dev/null | wc -l | tr -d '[:space:]')
  echo "  $dir: $count"
done
```

Total links:
```
Grep(pattern="\\[\\[", path="~/Obsidian/PKOS", output_mode="count")
```

Orphan detection:
```
For each note in 10-Knowledge, check if any other note links to it.
```

### vault related \<path\>

Find notes related to a given note:
1. Read the note's frontmatter `tags` array
2. Search for other notes with overlapping tags
3. Rank by overlap count, return top 5

```
Grep(pattern="tags:.*{topic1}|tags:.*{topic2}", path="~/Obsidian/PKOS", output_mode="files_with_matches")
```

## Vault Structure Reference

```
~/Obsidian/PKOS/
├── 00-Inbox/        ← Manual quick capture
├── 10-Knowledge/    ← Structured knowledge
├── 20-Ideas/        ← Product ideas
├── 30-Projects/     ← Active project notes
├── 40-People/       ← Key figure profiles
├── 50-References/   ← Articles, videos, domain-intel
├── 60-Digests/      ← Daily/weekly digests
├── 70-Reviews/      ← Weekly review records
├── 80-MOCs/         ← Maps of Content
└── Templates/       ← Note templates
```
