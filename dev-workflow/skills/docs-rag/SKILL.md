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

If the search tool is unavailable: tell the user "The RAG search tool is not connected. Ensure the MCP server is running and registered in ~/.claude.json."

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

### Step 4: Spotlight Fallback (zero RAG results)

If the result list contains a `result_count: 0` entry (or is empty), the RAG index has no match. Invoke the `spotlight-search` sub-agent with the same query:

```
Invoking Spotlight search for: "<query>"
```

Pass the query to the `spotlight-search` agent and wait for its `[Spotlight Result]` output.

Present the Spotlight result to the user as-is, prefixed with:

```
[RAG: no results — Spotlight fallback]
```

If Spotlight also finds nothing, say: "Neither the RAG index nor Spotlight found relevant results. Check that `rag build` has been run for this project, and that the topic exists in local files."
