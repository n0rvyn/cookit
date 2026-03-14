# domain-intel

Domain intelligence engine for Claude Code. Automated collection, AI analysis, and trend synthesis from GitHub (via API), Product Hunt, RSS, official changelogs, notable figures, and company news.

## Quick Start

```
cd ~/Knowledge/ai-ml       # Each directory is a separate profile
/intel setup                # Initialize this directory
/scan                       # Run collection pipeline
/intel brief                # Get a briefing on unread insights
/digest                     # Generate summary report
/intel evolve               # Review and update your preferences
```

## Directory = Profile

Each initialized directory is a self-contained domain-intel workspace. Different directories track different interests:

```
~/Knowledge/ai-ml/          # AI/ML tracking
~/Knowledge/ios-dev/        # iOS development tracking
~/Knowledge/indie-biz/      # Indie business tracking
```

Switch profiles by switching directories. No global config needed.

### Directory Structure

```
./
├── config.yaml             # Source URLs and scan parameters
├── LENS.md                 # Your interests, figures, companies (evolves over time)
├── state.yaml              # Scan statistics
├── .lens-signals.yaml      # Accumulated preference evolution signals
├── insights/YYYY-MM/       # Individual insight files
├── briefings/              # Saved briefings
├── digests/                # Generated digest reports
└── trends/                 # Trend snapshots for continuity tracking
```

## Skills

| Skill | Model | Purpose |
|-------|-------|---------|
| `/scan` | sonnet | Pipeline orchestrator: collect, filter, analyze, store |
| `/digest` | sonnet | Generate daily/weekly digest with trend synthesis |
| `/intel` | sonnet | Human entry point: status, briefing, Q&A, config, evolve |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| source-scanner | sonnet | Collection from GitHub (gh API), Product Hunt (GraphQL API), RSS, official changelogs, figures, companies (optional Playwright fallback for JS-rendered pages) |
| insight-analyzer | sonnet | Deep analysis with source-specific prompts, LENS-aware |
| trend-synthesizer | sonnet | Cross-insight pattern detection and synthesis |

## LENS.md

Your information filtering profile. Contains:
- **Frontmatter**: structured data (figures to track, companies to monitor)
- **Body**: natural language interests, current questions, anti-interests

LENS.md drives personalized relevance scoring and evolves over time through `/intel evolve`.

## Evolution

Both your preferences (LENS.md) and sources (config.yaml) evolve over time:

1. **Signal collection** — each `/scan` detects patterns not reflected in your profile:
   - New interests (frequent tags not in LENS.md)
   - New figures/companies (names appearing across insights)
   - New RSS feeds (figure blogs, high-value domains)
   - New official paths (discovered company pages)
   - New domains (emerging tag clusters)

2. **Signal storage** — accumulated in `.lens-signals.yaml`

3. **User review** — `/intel evolve` presents each signal for approval or rejection. Approved changes are written to LENS.md or config.yaml.

No changes are ever applied automatically. All evolution requires explicit user approval.

## Automated Scanning (Cron)

Set up recurring scans with CronCreate:

```
# Morning scan at 8:47am (specify directory)
CronCreate(cron="47 8 * * *", prompt="cd ~/Knowledge/ai-ml && /scan")

# Weekly digest every Friday at 5:03pm
CronCreate(cron="3 17 * * 5", prompt="cd ~/Knowledge/ai-ml && /digest week")
```

Note: Cron jobs auto-expire after 3 days. Recreate in new sessions.

## Optional: Browser Fallback

Some company pages and official changelogs use JavaScript rendering (SPA). `fetch_url.py` returns empty content for these (exit code 2). Enable browser fallback for better collection:

```bash
pip install playwright && playwright install chromium
```

Then in your `config.yaml`:

```yaml
scan:
  browser_fallback: true
```

When enabled, the source-scanner retries failed `fetch_url.py` calls (exit code 1 or 2) using a headless Chromium browser (up to 5 pages per scan). Pages that work with `fetch_url.py` are not affected.

## Hooks

- **SessionStart**: Reports unread insight count if CWD is an initialized directory
- **PreToolUse (Write)**: Guards against writing intel data outside the current directory

## Pipeline

```
Sources (GitHub API/Product Hunt/RSS/Official/Figures/Companies)
    │ source-scanner (sonnet)
    ▼
Raw Items
    │ 3-tier filter (URL dedup → title dedup → relevance scoring)
    ▼
Filtered Items
    │ insight-analyzer (sonnet) × N source types (parallel)
    ▼
Structured Insights
    │ convergence signal detection + lens signal collection
    ▼
Stored Insights + Signals
    │ trend-synthesizer (sonnet)
    ▼
Digest / Briefing / Query Answer
```
