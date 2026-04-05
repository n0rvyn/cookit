# youtube-scout

YouTube video intelligence plugin for Claude Code. Scrapes recommended feed and topic search, extracts transcripts, scores videos with Claude AI on 6 quality dimensions, and exports findings as IEF-compliant insights.

## Quick Start

```
/youtube-scan              # Run scan with default config
```

First run opens a browser for YouTube login. Cookies are cached for 30 days.

## Skills

| Skill | Model | Purpose |
|-------|-------|---------|
| `/youtube-scan` | sonnet | Full pipeline: scrape → dedup → transcripts → score → export → report |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| video-scorer | sonnet | 6-dimension quality scoring with IEF field extraction |

## Scoring Dimensions

| Dimension | Weight | What |
|-----------|--------|------|
| density | 25% | Actionable information per unit time |
| freshness | 20% | Recency of covered developments |
| originality | 20% | Original insight vs aggregation |
| depth | 15% | Technical detail level |
| signal_to_noise | 10% | Content vs filler ratio |
| credibility | 10% | Creator expertise evidence |

## Configuration

Optional config at `~/.youtube-scout/config.yaml`:

```yaml
scan:
  topic: "AI"

export:
  path: ~/.youtube-scout/exports
  min_score: 3.0
  domains:
    - ai-ml
```

## Integration with domain-intel

youtube-scout produces IEF-compliant insight files that domain-intel can consume:

1. Configure in domain-intel's `config.yaml`:
   ```yaml
   sources:
     external:
       - name: YouTube Scout
         path: ~/.youtube-scout/exports
         pre_collect: /youtube-scan
   ```
2. Run `/scan` in domain-intel — it will invoke `/youtube-scan` first, then import the exports

## Cron Usage

Standalone:
```
CronCreate(cron="47 8 * * *", prompt="/youtube-scan [cron]")
```

As part of domain-intel pipeline (recommended):
```
CronCreate(cron="47 8 * * *", prompt="cd ~/Knowledge/ai-ml && /scan [cron]")
```

## Directory Structure

```
~/.youtube-scout/
├── config.yaml        # Scan and export settings
├── cookies.json       # YouTube session cookies (30-day expiry)
├── seen.jsonl         # Dedup tracking across runs
├── exports/           # IEF insight files for domain-intel
└── cron.log           # Cron mode error log
./reports/             # Scan reports (in working directory)
```
