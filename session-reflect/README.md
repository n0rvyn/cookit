# session-reflect

AI collaboration coach: analyzes your Claude Code and Codex sessions to help you improve prompting, workflow, and AI collaboration skills.

## Skill

### /reflect
Analyze recent sessions and get coaching feedback.
```
/reflect                  # today's sessions
/reflect --days 7         # weekly reflection
/reflect --profile        # view/update your collaboration profile
/reflect --project myapp  # filter by project
```

## What It Analyzes

- **Prompt quality**: vague instructions, missing context, unclear goals — with concrete rewrite suggestions
- **Process maturity**: skipping exploration, no verification, correction loops
- **Correction patterns**: recurring types of AI redirections and how to prevent them
- **Emotion signals**: frustration triggers, satisfaction patterns
- **Growth over time**: behavioral changes across reflections

## Data Sources

- Claude Code sessions: `~/.claude/projects/*/*.jsonl`
- Codex sessions: `~/.codex/sessions/YYYY/MM/DD/*.jsonl`
- /insights facets: `~/.claude/usage-data/facets/*.json` (optional enrichment)

## Storage

- Reflections: `~/.claude/session-reflect/reflections/{date}.md`
- User profile: `~/.claude/session-reflect/profile.yaml`
- Analyzed sessions: `~/.claude/session-reflect/analyzed_sessions.json`

## Configuration

Copy `references/session-reflect.local.md.example` to `~/.claude/session-reflect.local.md` and customize.

## Architecture

```
Session JSONL + /insights facets
  → Python scripts (parse)
  → session-parser agent (enrich + assess prompt quality)
  → coach agent (coaching feedback) / profiler agent (user profile)
  → growth-tracker agent (cross-time comparison)
  → reflections/{date}.md + profile.yaml
```

- **Scripts**: Python stdlib only, no external dependencies
- **Agents**: session-parser (sonnet), coach (sonnet), profiler (sonnet), growth-tracker (sonnet)
- **Hook**: SessionEnd auto-summarization
