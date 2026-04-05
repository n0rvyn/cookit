---
name: vault
description: "Obsidian vault operations for PKOS knowledge graph. Use when the user says 'vault', 'search vault', '搜索笔记', or wants direct vault access. Not the primary entry point — use /pkos for most interactions."
model: haiku
---

## Overview

Obsidian vault operations for the PKOS knowledge graph at `~/Obsidian/PKOS/`.

## Commands

Parse the user's intent to determine which operation to perform:

### vault search \<query\>

Full-text search across the vault:
```
Grep(pattern="{query}", path="~/Obsidian/PKOS", output_mode="content", context=2, head_limit=20)
```

Also search frontmatter topics:
```
Grep(pattern="topics:.*{query}", path="~/Obsidian/PKOS", output_mode="files_with_matches")
```

Present results grouped by directory (10-Knowledge, 20-Ideas, etc.) with matched context.

### vault read \<path\>

Read a note's full content:
```
Read(file_path="~/Obsidian/PKOS/{path}")
```

If path is ambiguous (no directory prefix), search for it:
```
Glob(pattern="**/{path}*", path="~/Obsidian/PKOS")
```

### vault write \<path\> \<content\>

Write or update a note. If the file exists, confirm before overwriting.

Use the Write tool with the full path: `~/Obsidian/PKOS/{path}`

Ensure frontmatter is valid YAML if present.

### vault frontmatter \<path\> [--set key=value]

Read or update frontmatter fields:

**Read**: Parse YAML frontmatter between `---` markers. Display as table.

**Update** (with --set): Parse existing frontmatter, update specified key, write back.
For numeric fields (quality, citations): parse as number.
For array fields (topics, related): parse as YAML array.
For string fields (status, type): direct replacement.

### vault stats

Vault statistics:
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
1. Read the note's frontmatter `topics` array
2. Search for other notes with overlapping topics
3. Rank by overlap count, return top 5

```
Grep(pattern="topics:.*{topic1}|topics:.*{topic2}", path="~/Obsidian/PKOS", output_mode="files_with_matches")
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
