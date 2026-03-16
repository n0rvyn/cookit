---
name: retro
description: "Use when the user says 'retro', 'retrospective', '复盘', 'daily retro', or wants to review their AI collaboration patterns. Generates daily/weekly reports from Claude Code and Codex session data."
user_invocable: true
model: haiku
---

## Overview

Generate a retrospective report by analyzing recent Claude Code and Codex session data. Pipeline: discover sessions → parse stats → enrich with LLM → correlate with git → generate report.

## Arguments

- `--days N`: Number of days to look back (default: 1)
- `--project NAME`: Filter by project name (optional)
- `--codex`: Include Codex sessions (default: true)
- `--save`: Save report to file (default: true)

Parse arguments from the user's input. If no arguments, use defaults. Also check `~/.claude/session-intel.local.md` for configuration overrides (YAML frontmatter with `default_days`, `include_codex`, `projects` fields).

## Process

### Step 1: Discover Sessions

Run the extract-sessions script to find session files:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/extract-sessions.py --days {days} {--project NAME if specified} --source all --format json
```

If no sessions found: output "No sessions found for the last {days} day(s). Try `--days 7` for a wider range." and stop.

Count sessions. If more than 30, inform the user and suggest narrowing with `--project`.

### Step 2: Parse Each Session

For each discovered session, run the appropriate parser based on `source` field:

```bash
# For claude-code sessions:
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/parse_claude_session.py --input {file_path}

# For codex sessions:
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/parse_codex_session.py --input {file_path}
```

Collect all parsed JSON results. If a parser fails on a session file, log the error and continue with remaining sessions.

### Step 3: Enrich with LLM (session-parser agent)

For each parsed session, dispatch the `session-intel:session-parser` agent:

- Pass the parsed session JSON as the prompt
- Agent returns enriched fields: `task_summary`, `session_dna`, `corrections`, `emotion_signals`
- Merge all enriched fields back into the session data

**Batching**: Combine multiple sessions into a single agent prompt to reduce dispatch count:
- Up to 5 sessions per agent call (pass all 5 session JSONs in one prompt)
- For >20 sessions: skip LLM enrichment for sessions with <5 user turns (mark as "mixed" DNA, empty summary)
- This keeps total agent dispatches under 10 even for 30-day retros

**Parallelism**: Launch multiple batch agent calls in parallel when possible.

If an agent call fails, use placeholder values (session_dna: "mixed", task_summary: "Unable to analyze", corrections: [], emotion_signals: []).

### Step 3b: Save Enriched Data

Save all enriched session data for index reuse by other skills:
```bash
mkdir -p ~/.claude/retro/enriched
# Write enriched sessions as JSON array to date-stamped file
```
This allows `build_index.py` to load pre-enriched data instead of re-running session-parser.

### Step 4: Git Correlation

Write all parsed session JSONs to temp files, then run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/git_correlate.py --sessions {temp_file_paths}
```

This returns `{session_id: [commit_hash, ...]}` mapping.

### Step 5: Generate Report (retro-writer agent)

Dispatch the `session-intel:retro-writer` agent with:
- All enriched session summaries (as JSON array)
- Git correlation mapping
- Date range info

The agent returns a Markdown report.

### Step 6: Save and Present

1. If `--save` (default): save report to `~/.claude/retro/{YYYY-MM-DD}.md`
   - Create `~/.claude/retro/` directory if it doesn't exist
2. Present the full report to the user

## Error Handling

- **No sessions**: Clear message with suggestion to widen date range
- **Parser failure**: Skip session, note in report footer
- **Agent failure**: Use placeholder values, note in report footer
- **Git correlation failure**: Skip, report without git data
- **Config file missing**: Use defaults (days=1, include_codex=true)

## Integration with dev-workflow

After presenting the report, if notable findings exist, suggest related skills:

- **Corrections detected**: "{N} user corrections found. Use `/collect-lesson` to capture key lessons."
- **Build failures**: "Build failure patterns detected. Use `/collect-lesson` to document pitfalls."
- **High-value insights**: "Notable patterns found. Use `/collect-lesson` to save to knowledge base."

## Completion Criteria

- Report generated and displayed
- Report saved to file (if --save)
