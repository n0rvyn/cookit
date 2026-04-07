# Session Reflect Configuration

User configuration is stored in `~/.claude/session-reflect.local.md` with YAML frontmatter.

## Configuration Fields

```yaml
---
# Number of days to look back by default
default_days: 1

# Include Codex sessions
include_codex: true

# Filter to specific projects (empty = all)
projects: []

# Enable SessionEnd hook for auto-summaries
auto_summary: true

# Storage directory for reflections, profile, and analyzed sessions
storage_dir: ~/.claude/session-reflect/

# /insights facets directory (for optional enrichment)
insights_facets_dir: ~/.claude/usage-data/facets/
---
```

## File Locations

| File | Purpose | Created By |
|------|---------|-----------|
| `~/.claude/session-reflect/reflections/{date}.md` | Coaching feedback | `/reflect` skill |
| `~/.claude/session-reflect/profile.yaml` | User collaboration profile | `/reflect --profile` |
| `~/.claude/session-reflect/analyzed_sessions.json` | Session dedup tracking | `/reflect` skill |
| `~/.claude/session-reflect/summaries/*.json` | Auto session summaries | SessionEnd hook |
| `~/.claude/session-reflect.local.md` | User config | User (manual) |
