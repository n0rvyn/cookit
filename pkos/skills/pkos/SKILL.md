---
name: pkos
description: "Use when the user says 'pkos', 'knowledge base', '知识库', 'what's in my inbox', 'what do I know about', or wants to interact with their personal knowledge system. Unified entry point for status, query, ingest, and review."
user_invocable: true
model: sonnet
---

## Overview

Unified human interface for PKOS. Routes user intent to the appropriate subsystem. This is the ONLY user-facing entry point — all other PKOS skills are internal (cron/event-triggered).

## Arguments

Parse from user input (natural language routing):

- No args / `status` → Status Dashboard
- `<question or topic>` → Knowledge Query
- `ingest <url|text>` → Manual Ingest
- `review` → Today's Wiki Changes
- `lint` → Latest Health Report

## Routes

### Route: Status Dashboard (default)

Show PKOS system status. Collect data in parallel:

**Inbox count:**
```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/collect-inbox.sh all
```

**Recent vault activity (last 24h):**
```bash
find ~/Obsidian/PKOS/{10-Knowledge,20-Ideas,50-References,80-MOCs} -name "*.md" -mtime -1 2>/dev/null | wc -l | tr -d '[:space:]'
```

**Latest lint health score (if exists):**
```
Glob(pattern="lint-*.md", path="~/Obsidian/PKOS/70-Reviews")
```
Read the most recent one, extract the Summary section.

**Latest digest (if exists):**
```
Glob(pattern="*.md", path="~/Obsidian/PKOS/60-Digests")
```
Read the most recent one's Quick Stats section.

Present:
```
PKOS Status
  Inbox: {N} items pending
  Last 24h: +{N} notes, +{N} MOC updates
  Health: {score from latest lint, or "no lint data"}
  Latest digest: {date}
```

### Route: Knowledge Query

When user provides a topic or question:

1. Search vault frontmatter for topic matches:
   ```
   Grep(pattern="topics:.*{keyword}", path="~/Obsidian/PKOS", output_mode="files_with_matches", head_limit=10)
   ```

2. Search vault content:
   ```
   Grep(pattern="{keyword1}|{keyword2}", path="~/Obsidian/PKOS/{10-Knowledge,20-Ideas,50-References,80-MOCs}", output_mode="files_with_matches", head_limit=10)
   ```

3. Check MOCs first — if an 80-MOCs/ file matches, read it (it contains synthesized knowledge):
   ```
   Glob(pattern="**/*{keyword}*", path="~/Obsidian/PKOS/80-MOCs")
   ```

4. Read the top 5 most relevant files (MOCs first, then by match count).

5. Synthesize an answer citing specific notes. Format:
   ```
   {Synthesized answer}

   Sources:
   - [[note-title]] (10-Knowledge/) — {key point}
   - [[moc-title]] (80-MOCs/) — {overview}
   ```

6. If the answer is substantial and novel (user confirms), offer to save as a new note via vault write.

### Route: Manual Ingest

When user says `ingest <url|text>`:

1. If URL detected: fetch content via WebFetch
2. Create a temporary inbox item and invoke the inbox skill internally:
   - Classification via `pkos:inbox-processor` agent
   - Route to Obsidian + Notion
   - Trigger ripple compilation via `pkos:ripple-compiler` agent
3. Report what was created and what MOCs were updated.

### Route: Review

Show today's wiki changes:

1. Find all files modified today:
   ```bash
   find ~/Obsidian/PKOS -name "*.md" -mtime -1 -newer ~/Obsidian/PKOS/.state/last-review-marker 2>/dev/null
   ```

2. Categorize changes:
   - New notes (10/20/50)
   - MOC updates (80-MOCs)
   - Digest generated (60-Digests)
   - Lint reports (70-Reviews)

3. For MOC updates, show a brief diff (what was added).

4. Update review marker:
   ```bash
   touch ~/Obsidian/PKOS/.state/last-review-marker
   ```

### Route: Lint

Show the latest lint report:

1. Find the most recent lint report:
   ```
   Glob(pattern="lint-*.md", path="~/Obsidian/PKOS/70-Reviews")
   ```

2. If found: read and display the summary + high-severity items.
3. If not found: report "No lint data. Lint runs automatically every Sunday, or invoke internally."
