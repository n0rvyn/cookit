# domain-intel

Domain intelligence engine for Claude Code. Automated collection, AI analysis, and trend synthesis from GitHub, RSS, and official changelogs.

## Quick Start

```
/intel setup          # First-time configuration
/scan                 # Run collection pipeline
/digest               # Generate summary report
/intel                # Check status
/intel brief          # Get a briefing on unread insights
```

## Skills

| Skill | Model | Purpose |
|-------|-------|---------|
| `/scan` | haiku | Pipeline orchestrator: collect → filter → analyze → store |
| `/digest` | haiku | Generate daily/weekly digest with trend synthesis |
| `/intel` | haiku | Human entry point: status, briefing, Q&A, config |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| source-scanner | haiku | Web collection from GitHub, RSS, official changelogs |
| insight-analyzer | sonnet | Deep analysis with source-specific prompts |
| trend-synthesizer | sonnet | Cross-insight pattern detection and synthesis |

## Data Storage

Data is stored in a user-chosen directory (set during `/intel setup`), not inside `~/.claude/`. This means you can:
- Git-track your intelligence data
- Open insights in Obsidian or any markdown editor
- Sync via iCloud or other services

```
{data_dir}/
├── insights/YYYY-MM/    # Individual insight files
├── digests/             # Generated digest reports
├── trends/              # Trend snapshots for continuity tracking
└── state.yaml           # Scan statistics
```

## Automated Scanning (Cron)

Set up recurring scans with CronCreate:

```
# Morning scan at 8:47am
CronCreate(cron="47 8 * * *", prompt="/scan")

# Weekly digest every Friday at 5:03pm
CronCreate(cron="3 17 * * 5", prompt="/digest week")
```

Note: Cron jobs auto-expire after 3 days. Recreate in new sessions.

## Hooks

- **SessionStart**: Reports unread insight count and config status
- **PreToolUse (Write)**: Guards against writing intel data outside configured data_dir

## Pipeline

```
Sources (GitHub/RSS/Official)
    │ source-scanner (haiku)
    ▼
Raw Items
    │ 3-tier filter (URL dedup → title dedup → keyword scoring)
    ▼
Filtered Items
    │ insight-analyzer (sonnet) × N source types (parallel)
    ▼
Structured Insights
    │ convergence signal detection
    ▼
Stored Insights + Signals
    │ trend-synthesizer (sonnet)
    ▼
Digest / Briefing / Query Answer
```
