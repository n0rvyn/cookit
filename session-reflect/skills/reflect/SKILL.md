---
name: reflect
description: "Use when the user says 'reflect', 'reflection', '反思', '复盘', 'coaching', 'coach me', or wants to review and improve their AI collaboration patterns. Analyzes recent sessions and produces coaching feedback with specific improvement suggestions."
user_invocable: true
model: haiku
---

## Overview

Analyze recent AI coding sessions to produce coaching feedback on prompt quality, process maturity, correction patterns, and growth over time. Single entry point for all session-reflect capabilities.

## Arguments

Parse from user input:
- `--days N`: Number of days to look back (default: 1)
- `--project NAME`: Filter by project name (optional)
- `--profile`: Output/update user collaboration profile instead of coaching feedback
- `--auto`: (Reserved for future scheduled execution — not implemented yet, note if user tries it)

Also check `~/.claude/session-reflect.local.md` for configuration overrides (YAML frontmatter with `default_days`, `include_codex`, `projects` fields). If file doesn't exist, use defaults.

## Process

### Step 1: Discover Sessions

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/extract-sessions.py --days {days} {--project NAME if specified} --source all --format json
```

If no sessions found: output "No sessions found for the last {days} day(s). Try `--days 7` for a wider range." and stop.

Count sessions. If more than 30, suggest narrowing with `--project`.

### Step 2: Filter Already-Analyzed Sessions

Read `~/.claude/session-reflect/analyzed_sessions.json` (if it exists).

- For `--days 1` (default): **skip filtering** — always re-analyze today's sessions for fresh feedback
- For `--days >1`: filter out session IDs already in `analyzed_sessions.json`, unless `--profile` flag is set (profile benefits from full history)
- If all sessions filtered out: "All sessions in this range have been analyzed. Use `--days {larger N}` for more sessions, or re-run with `--days 1` for today."

If `analyzed_sessions.json` doesn't exist, proceed with all discovered sessions.

### Step 3: Parse Each Session

For each discovered session, run the appropriate parser based on `source` field:

```bash
# For claude-code sessions:
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/parse_claude_session.py --input {file_path}

# For codex sessions:
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/parse_codex_session.py --input {file_path}
```

Collect all parsed JSON results. If a parser fails on a session, log the error and continue.

### Step 3b: Merge /insights Facets (optional)

For each parsed session, check if /insights has facets data:

```bash
cat ~/.claude/usage-data/facets/{session_id}.json 2>/dev/null
```

If found: add `insights_facets` field to the parsed session JSON. This gives session-parser additional signals (outcome, friction, response times).

If not found: proceed without it. This is not an error.

### Step 4: Enrich via session-parser agent

Dispatch `session-reflect:session-parser` agent with parsed session data.

**Batching**: combine up to 10 sessions per agent call to reduce dispatches.
**Parallelism**: launch multiple batch agent calls in parallel when possible.
**Failure handling**: if an agent call fails, use placeholder values:
- `session_dna`: "mixed"
- `task_summary`: "Unable to analyze"
- `corrections`, `emotion_signals`, `prompt_assessments`, `process_gaps`: `[]`

### Step 5: Route by Mode

#### Default mode (coaching feedback):

1. Dispatch `session-reflect:coach` agent with all enriched sessions
2. Agent returns coaching feedback as Markdown
3. Save feedback to `~/.claude/session-reflect/reflections/{YYYY-MM-DD}.md`:
   - Create directory if it doesn't exist: `mkdir -p ~/.claude/session-reflect/reflections`
   - If file already exists for today, append with `---` separator
4. Update `~/.claude/session-reflect/analyzed_sessions.json`:
   - Read existing file (or start with `{}`)
   - Add each newly analyzed session ID with today's date: `{session_id: "YYYY-MM-DD"}`
   - Write back
5. Present coaching feedback to user

#### --profile mode:

1. Read existing profile: `cat ~/.claude/session-reflect/profile.yaml 2>/dev/null` (or "No existing profile")
2. Dispatch `session-reflect:profiler` agent with all enriched sessions + existing profile
3. Agent returns updated profile as YAML
4. Write to `~/.claude/session-reflect/profile.yaml`:
   - Create directory if needed: `mkdir -p ~/.claude/session-reflect`
5. Present profile summary to user

### Step 6: Growth Check

After Step 5 (default mode only), check if growth tracking is possible:

1. List reflection files: `ls ~/.claude/session-reflect/reflections/*.md 2>/dev/null | sort | tail -4`
2. If 3+ files exist (including today's):
   - Read the 2-3 most recent previous reflections (not today's)
   - Read profile if exists: `cat ~/.claude/session-reflect/profile.yaml 2>/dev/null`
   - Dispatch `session-reflect:growth-tracker` agent with current reflection + previous reflections + profile
   - Append growth observations to the output
3. If <3 files: append note "Growth tracking will activate after 3+ reflections."

## Error Handling

- **No sessions**: clear message with `--days` suggestion
- **Parser failure on a session**: skip, note in footer
- **session-parser agent failure**: use placeholder values, note in footer
- **coach/profiler agent failure**: show raw parsed session summaries as fallback
- **growth-tracker failure**: skip growth section, show coaching feedback only
- **/insights facets missing**: silent (not an error)
- **profile.yaml missing**: profiler creates from scratch
- **analyzed_sessions.json missing**: treat as empty, create on first write

## Completion Criteria

- Coaching feedback (or profile) generated and displayed
- Reflection saved to `~/.claude/session-reflect/reflections/{date}.md` (default mode)
- `analyzed_sessions.json` updated with newly analyzed session IDs (default mode)
