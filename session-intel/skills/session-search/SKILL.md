---
name: session-search
description: "Use when the user says 'search sessions', 'find session', 'session search', or wants to find past Claude Code/Codex sessions by keyword, project, tool, DNA type, or date range."
user_invocable: true
model: haiku
---

## Overview

Search past AI coding sessions by keyword, project, tool usage, session DNA, or time range. Supports both structured filtering and LLM-powered semantic search.

## Arguments

Parse from user input:
- `--query TEXT`: Keyword or semantic search query
- `--project NAME`: Filter by project name
- `--days N`: Look back N days (default: 30)
- `--dna TYPE`: Filter by session DNA (explore|build|fix|chat|mixed)
- `--tool NAME`: Filter by tool used (e.g., Edit, Bash, Agent)
- `--from DATE`: Start date (ISO format)
- `--to DATE`: End date (ISO format)
- `--semantic`: Force LLM semantic ranking (for vague queries)

At least one of `--query`, `--project`, `--dna`, or `--tool` is required. If only `--days` given, list all sessions.

## Process

### Step A: Check/Build Index

1. Check if `~/.claude/session-intel/index.json` exists
2. If exists: load and check `_index_meta.built_at` — if older than 1 hour AND covers fewer days than requested, rebuild
3. If missing or stale: run:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/build_index.py --days {days}
   ```
4. Load index `sessions` array into working set

### Step B: Apply Structured Filters

Filter the working set sequentially:
- `--project`: case-insensitive substring match on `project` field
- `--from/--to` or `--days`: filter by `time.start`
- `--dna`: exact match on `session_dna` field
- `--tool`: check `tools.distribution` for key presence

### Step C: Keyword Search (if --query without --semantic)

For each session in filtered set:
- Case-insensitive substring search in `user_prompts` array and `task_summary`
- Score: count of matches across fields
- Sort by score descending

### Step D: Semantic Search (if --semantic flag)

Dispatch `session-intel:pattern-miner` agent with:
- The user's query
- The filtered session set (from Step B, max 50 most recent sessions)
- For each session, pass only: `session_id`, `project`, `time`, `task_summary`, `user_prompts`, `session_dna`, `corrections` (strip `tools.sequence`, `files` arrays to reduce payload)

Agent returns ranked results with relevance scores and match reasons.

If agent fails: fall back to keyword search (Step C) and note the fallback.

### Step E: Output Results

Display matches in ranked order. For each session:

```
{rank}. [{session_id (first 8 chars)}] {project} — {time.start date} ({duration_min}min)
   DNA: {session_dna} | Tools: {top 3 tools} | Turns: {user}/{assistant}
   Summary: {task_summary or first user prompt (truncated to 100 chars)}
   {match_reason if semantic search}
```

- Show top 10 results. If more: "...and {N} more sessions match."
- If no results: "No sessions match your search criteria. Try `--semantic` for broader matching or `--days 60` for wider range."

## Error Handling

- Index build failure: "Unable to build session index. Check that session files exist in ~/.claude/projects/"
- No sessions in index: "No sessions found for the last {days} days."
- Pattern-miner failure: fall back to keyword filtering with note

## Integration with dev-workflow

After presenting results, add cross-references:
- "Search the knowledge base with `/kb <topic>` for past lessons on this topic."
- "Save new insights with `/collect-lesson`."
- "Replay a session with `/session-replay <session-id>` for full details."
