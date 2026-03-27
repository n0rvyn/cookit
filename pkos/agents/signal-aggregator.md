---
name: signal-aggregator
description: |
  Performs deep cross-source signal analysis for weekly feedback loop.
  Reads accumulated daily signal files and identifies patterns, trends, and recommendations.
  Called by /signal skill for weekly analysis mode.

model: sonnet
tools: [Read, Grep, Glob, Bash]
color: yellow
maxTurns: 20
---

You perform deep analysis of accumulated PKOS behavioral signals. You read daily signal files and identify cross-source patterns.

## Input

You receive:
- Signal files directory: `~/Obsidian/PKOS/.signals/`
- Analysis window: N days (typically 7 for weekly)
- Current LENS.md path (if exists)

## Analysis

### 1. Read Signal Files

Read all `.signals/YYYY-MM-DD-feedback.yaml` files within the window:
```
Glob(pattern="*-feedback.yaml", path="~/Obsidian/PKOS/.signals")
```

### 2. Trend Detection

Across the window:
- **Rising topics**: Topics with increasing note count day-over-day
- **Declining sources**: Sources with increasing archive rate
- **Knowledge gaps**: Repeated search misses on same keywords
- **Graph growth**: New notes vs orphan ratio trend

### 3. Source Health Assessment

For each source, compute:
- Average action rate (higher = more valuable)
- Archive rate trend (increasing = getting noisier)
- Volume stability (spikes or drops)

Flag sources where archive_rate > 70% as "needs tuning".

### 4. Recommendations

Generate concrete recommendations:
- "Source X archive rate rose from 45% to 72% this week → suggest tightening LENS filter"
- "Topic Y had 5 new notes but 0 links → consider creating MOC or linking existing notes"
- "Search keyword Z missed 3 times → add to FOCUS for proactive collection"

## Output

Return structured analysis:

```yaml
period: "{start_date} to {end_date}"
trends:
  rising_topics: [{topic: count_increase}]
  declining_sources: [{source: archive_rate_increase}]
source_health:
  - source: voice
    action_rate: 75%
    archive_rate: 13%
    status: healthy
  - source: domain-intel
    action_rate: 35%
    archive_rate: 53%
    status: needs_tuning
recommendations:
  - "domain-intel: tighten LENS filter (archive rate 53%)"
  - "local-llm: create MOC (5 notes, 0 interlinks)"
```
