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

### Step 1b: Detect Query Mode

Classify the query as **question** or **browse**:

- **Question mode**: Query contains `?`, starts with how/why/what/when/where/does/can/is/should/will, or is a natural language sentence (>5 words with verb structure)
- **Browse mode**: Query is a single word, a short phrase (1-3 words), or a kebab-case/snake_case identifier

This classification determines how results are presented in Step 3.

### Step 2: Search

First, resolve the knowledge base path: run `echo $HOME/.claude/knowledge/` via Bash to get the absolute path. Use this expanded path for all subsequent Grep and Read calls.

Run two parallel Grep searches over the resolved knowledge base path:

1. **Content search**: `Grep(pattern=<query>, path="~/.claude/knowledge/", output_mode="content", context=3)`
2. **Keyword search**: `Grep(pattern=<query>, path="~/.claude/knowledge/", glob="*.md", output_mode="content", context=0)` targeting `keywords:` lines in frontmatter

If the user specified a category filter, narrow the path to `~/.claude/knowledge/{category}/`.

If the query has multiple words, also try each word individually as a secondary search if the full-phrase search returns zero results.

### Step 3: Present Results

**Freshness indicator** (used by both modes): First, run `date +%Y-%m-%d` via Bash to get today's date. Then for each result file, extract the `date:` field from YAML frontmatter. Compare against today:
- 🟢 Fresh: < 30 days old
- 🟡 Aging: 30-90 days old
- 🔴 Stale: > 90 days old
- ⚪ Unknown: no `date:` field and no `YYYY-MM-DD-` filename prefix

If the frontmatter has no `date:` field, use the filename date prefix (`YYYY-MM-DD-*`) if present.

---

#### Step 3A: Browse Mode

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

---

#### Step 3B: Question Mode (Synthesis)

1. **Rank results**: From the combined Grep results (Step 2), rank matched files by: keyword-line hit > content-only hit, then most recent date first. Take the top 5 files.

2. **Read full content**: For each of the top 5 files, call `Read(file_path, limit=100)` to get the complete entry (capped at 100 lines to bound context usage).

3. **Synthesize answer**: Using the read entries, compose a direct answer to the user's question. Format:

```
## Answer

{2-5 sentence direct answer to the question. Reference specific entries as [entry-filename] when citing a fact or recommendation.}

## Sources

[1] {freshness_emoji} {file_path}
    Category: {cat} | Date: {date} | Keywords: {kw}

[2] {freshness_emoji} {file_path}
    Category: {cat} | Date: {date} | Keywords: {kw}

...

Need more detail on a source? Specify the number.
```

4. **Confidence fallback**: If the read entries do not contain enough information to answer the question directly, fall back to browse mode output and prefix with: "Found related entries but can't confidently answer this question. Here are the relevant entries:"

5. **Stale warning**: If any cited source is 🔴 Stale, append the stale warning after the Sources section.

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

#### PKOS Vault Fallback

If still no results after the project-local fallback, and `~/Obsidian/PKOS/` exists:

1. `Grep(pattern=<query>, path="~/Obsidian/PKOS/10-Knowledge", output_mode="content", context=3, head_limit=10)`
2. `Grep(pattern=<query>, path="~/Obsidian/PKOS/50-References", output_mode="content", context=3, head_limit=10)`

If PKOS results found, present them with label: "[PKOS vault results — not in central knowledge base. Use /pkos kb-bridge to export relevant entries.]"

This is a read-only search fallback. It does not modify the PKOS vault.

**Note**: This PKOS fallback also applies to Step 3B (Question/Synthesis mode) — if the initial search in `~/.claude/knowledge/` returns zero results, try the PKOS vault before giving up on synthesis.
