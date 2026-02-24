---
name: docs-rag
description: "Use when you need to search the project knowledge base manually. Accepts a query from the user, searches the RAG index, and presents results with file links for deeper reading."
user-invocable: true
---

## Overview

This skill runs an ad-hoc search over the RAG knowledge base and presents results with enough context to read further. If the RAG index returns no results, it automatically falls back to a Spotlight search via the `spotlight-search` sub-agent.

## Process

### Step 1: Collect Query Parameters

Ask the user (or extract from the invocation message):

1. **Query** — the search string (required)
2. **Source type filter** — optional; one or more of: `doc`, `error`, `lesson`, `api-ref`; default is all types
3. **Top K** — number of results to return; default is 5

If the user invoked `/docs-rag <query>`, use the text after `/docs-rag` as the query directly without asking.

### Step 2: Search RAG Index

Call `search` with:
- `query`: the user's query
- `source_type`: the filter list (omit parameter to search all types)
- `top_k`: the requested result count
- `project_root`: current working directory

If the search tool is unavailable:
  Tell the user: "The RAG search tool is not connected. Ensure the MCP server is running
  and registered in ~/.claude.json. Proceeding with local file search fallback."
  Skip to Step 4 (Spotlight/Grep fallback).

### Step 3: Present RAG Results

If the result list contains items with a `source_path` field (normal results), present each:

```
[{rank}] {source_path} — {section}
Score: {score}
Lines: {line_range[0]}–{line_range[1]}
Preview:
  {content — first 200 characters, truncated with ... if longer}

To read the full section:
  Read({source_path}, offset={line_range[0]}, limit={line_range[1] - line_range[0] + 1})
```

After presenting results, ask: "Read any of these sections in full? Specify the result number(s)."

If the user names result(s): call `Read` with the file path, offset, and limit from that result's `line_range` and present the content.

If results were found, stop here.

### Step 4: Fallback (zero RAG results OR search tool unavailable)

**Tier 1 — Spotlight (preferred, requires mactools):**

Check if mactools is available by checking if the spotlight-search sub-agent is registered.
If available: invoke `spotlight-search` sub-agent with the same query (current behavior).
If Spotlight returns results: present them prefixed with "[Spotlight fallback]" and stop.

**Tier 2 — Grep/Glob (always available, no external dependency):**

If mactools not available OR Spotlight returns 0 results:
1. `Grep(query, path="docs/", output_mode="content", context=2)`
2. `Grep(query, path="docs/09-lessons-learned/", output_mode="content", context=2)`
3. `Glob("**/*.md", path=".")` then Grep the top matches
Present results prefixed with "[Local file search fallback — 字面匹配，无语义排名，结果相关性低于 RAG]"

If mactools is absent, also append:
"💡 Install mactools for richer Spotlight-based local search."

**If both tiers return nothing:**
"Neither RAG, Spotlight, nor local file search found results for '{query}'.
 Check that `rag build` has been run and that mactools is installed for Spotlight support."
