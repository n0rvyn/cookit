---
name: evolve
description: "Internal skill — generates LENS/FOCUS profile update suggestions from accumulated signals. Triggered by Adam event after weekly review."
model: sonnet
---

## Overview

Generate LENS.md and FOCUS.md update suggestions based on accumulated behavioral signals from `.signals/` directory.

## Arguments

- `--days N`: Signal window in days (default: 7)
- `--apply`: Auto-apply confirmed suggestions without individual prompts

## Process

### Step 1: Read Signal Files

Read all signal files from the window:
```
Glob(pattern="*-feedback.yaml", path="~/Obsidian/PKOS/.signals")
```

Filter to files within the --days window. If no signal files found, report "No signal data available. Run /signal first." and stop.

### Step 2: Dispatch Signal Aggregator

For weekly analysis, dispatch `pkos:signal-aggregator` agent with accumulated signal data. The agent returns:
- Rising/declining topics
- Source health assessments
- Concrete recommendations

### Step 3: Generate Suggestions

From aggregated signals, generate update suggestions in these categories:

**Source weight adjustments:**
- If archive_rate > 70% for a source → "降权 {source}（归档率 {pct}%）"
- If action_rate > 80% for a source → "保持 {source}（转化率 {pct}%）"

**Topic adjustments:**
- Rising topic (note count increase > 3x) → "提升 {topic} 采集频率"
- Dead topic (0 new notes in 30 days) → "考虑降低 {topic} 优先级"

**Knowledge gap detection:**
- Repeated search misses → "加入 FOCUS: {keyword}"

**Source retirement:**
- Consistently high archive rate (>80% for 3+ weeks) → "考虑退订 {source}"

### Step 4: Present Suggestions

Display suggestions in a structured format:

```
🔄 PKOS Profile Evolution — {date} ({N}-day window)

📈 Source Adjustments:
  1. [adjust] domain-intel "blockchain": 降权（归档率 90%）
  2. [keep] voice: 保持（转化率 75%）

📊 Topic Adjustments:
  3. [boost] "local-llm": 提升采集频率（graph 密度 +6）
  4. [add] "MLX deployment": 加入 FOCUS（搜索 3 次未命中）

Confirm to apply, or select items to skip.
```

### Step 5: Apply Confirmed Changes

If user confirms (or --apply flag):

For LENS.md updates:
- Read existing LENS.md (if domain-intel is installed)
- Update relevant sections (interests, anti-interests, source weights)
- Write back

For FOCUS.md updates:
- Read existing FOCUS.md
- Add new topics / adjust weights
- Write back

Report what was changed.

## Notes

- Suggestions are never auto-applied without user confirmation (unless --apply flag)
- This skill is the "breathing" rhythm of the feedback loop (weekly)
- Signal data is produced by /signal skill (the "heartbeat" rhythm, daily)
