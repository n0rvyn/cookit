---
name: kb
description: "Use when you need to search the cross-project knowledge base manually. Accepts a query, searches ~/.claude/knowledge/ for past lessons, API gotchas, architecture decisions, and learning notes."
user-invocable: true
---

## Overview

Search the cross-project knowledge base at `~/.claude/knowledge/`. Returns matching entries with context for quick scanning, and offers to read full files.

## Process

### Step 1: Collect Query

If the user invoked `/kb <query>`, use the text after `/kb` as the query directly.

Otherwise, ask:
1. **Query** — search string (required)
2. **Category filter** — optional; one of the subdirectory names (e.g., `api-usage`, `bug-postmortem`, `architecture`, `platform-constraints`). Omit to search all.

### Step 2: Search

First, resolve the knowledge base path: run `echo $HOME/.claude/knowledge/` via Bash to get the absolute path. Use this expanded path for all subsequent Grep and Read calls.

Run two parallel Grep searches over the resolved knowledge base path:

1. **Content search**: `Grep(pattern=<query>, path="~/.claude/knowledge/", output_mode="content", context=3)`
2. **Keyword search**: `Grep(pattern=<query>, path="~/.claude/knowledge/", glob="*.md", output_mode="content", context=0)` targeting `keywords:` lines in frontmatter

If the user specified a category filter, narrow the path to `~/.claude/knowledge/{category}/`.

If the query has multiple words, also try each word individually as a secondary search if the full-phrase search returns zero results.

### Step 3: Present Results

**Freshness indicator:** First, run `date +%Y-%m-%d` via Bash to get today's date. Then for each result file, extract the `date:` field from YAML frontmatter. Compare against today:
- 🟢 Fresh: < 30 days old
- 🟡 Aging: 30-90 days old
- 🔴 Stale: > 90 days old
- ⚪ Unknown: no `date:` field and no `YYYY-MM-DD-` filename prefix

If the frontmatter has no `date:` field, use the filename date prefix (`YYYY-MM-DD-*`) if present.

Group results by file. For each file, show:

```
[{rank}] {freshness_emoji} {file_path}
Category: {category from directory name}  |  Date: {from frontmatter}  |  Freshness: {Fresh/Aging/Stale}
Keywords: {from frontmatter keywords line}

{matching lines with context — up to 8 lines per file}
```

If any results are 🔴 Stale (> 90 days), append after the results list:
> ⚠️ {N} 条结果超过 90 天，信息可能过时。建议验证后再使用。

After presenting all results: "Read any of these in full? Specify the number(s)."

If the user names result(s): call `Read` with the file path and present the full content.

### Step 4: Zero Results

If no results from either search:

```
No entries found for "{query}" in ~/.claude/knowledge/.

Suggestions:
- Try broader or alternative keywords
- Use /collect-lesson to save new knowledge from this session
```

Also run a quick scan of the current project's `docs/09-lessons-learned/` as a local fallback:
`Grep(pattern=<query>, path="docs/09-lessons-learned/", output_mode="content", context=3)`

If local results found, present them with label: "[Project-local results — not in central knowledge base]"
