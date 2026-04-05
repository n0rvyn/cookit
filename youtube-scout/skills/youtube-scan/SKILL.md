---
name: youtube-scan
description: "Use when the user says 'youtube-scan', 'youtube scan', 'scan youtube', 'youtube recommendations'. Scrapes YouTube recommended feed and topic search, extracts transcripts, scores videos with Claude AI on 6 quality dimensions. Exports TOP findings as IEF-compliant insight files for domain-intel consumption."
model: sonnet
user-invocable: true
---

## Overview

YouTube video curation pipeline. Scrapes → deduplicates → extracts transcripts → scores → generates report.

Designed for **manual execution** — interactive output, handles login prompts.

## Process

### Step 0: Resolve Paths

```
Bash(command="echo ${CLAUDE_PLUGIN_ROOT}/scripts")
```

Store the result as `SCRIPTS`. All script paths below use `{SCRIPTS}/`.

Get today's date:
```
Bash(command="date +%Y-%m-%d")
```
Store as `TODAY`.

### Step 0.5: Load Config

Resolve config path:
```
Bash(command="echo ~/.youtube-scout/config.yaml")
```
Store the absolute path. Read the file if it exists. Extract:
- `export.path` (default: `~/.youtube-scout/exports`)
- `export.min_score` (default: 3.0) — minimum weighted_total for export
- `export.domains` (default: []) — domain list for category matching, passed to video-scorer
- `scan.topic` (default: "AI") — topic for YouTube search

If config file does not exist, use all defaults.

Resolve `export.path` to an absolute path:
```
Bash(command="echo {export.path}")
```
Store the resolved absolute path as `export_path`.

### Cron Mode Detection

If the invocation prompt contains `[cron]`:
- Set `CRON_MODE = true`
- All parameters from config (no AskUserQuestion)
- Suppress terminal TOP-5 detail output (file report still generated)
- Login and empty-result stops are handled differently in cron mode — see Step 1

### Step 1: Scrape Videos

```
Bash(command="python3 {SCRIPTS}/scrape_youtube.py --topic '{scan.topic}' --cookie-dir ~/.youtube-scout --max-recommended 30 --max-search 20")
```

Parse the JSON output from stdout. Check the `status` field:

- `"login_required"`:
  - If `CRON_MODE`: log `[youtube-scout] Login required (skipped in cron mode)` to `~/.youtube-scout/cron.log` via Bash append. **Skip to Step 7** with zero scored videos. The file report should note `status: login_required` in frontmatter. Then exit.
  - If NOT `CRON_MODE`: output:
    ```
    [youtube-scout] YouTube login required. Please run again after logging in — the script will open a browser window for you.
    ```
    **Stop here.**

- `"partial"` → output warning:
  ```
  [youtube-scout] Warning: Recommended feed unavailable (login may be stale). Proceeding with search results only.
  ```
  Continue with available videos.

- `"ok"` → continue normally.

Extract the `videos` array from the JSON output.

### Step 2: Deduplicate

Write the videos array to a temp JSON string and pipe through dedup:

```
Bash(command="echo '<videos_json>' | python3 {SCRIPTS}/dedup.py filter")
```

Parse the filtered JSON output. If the filtered list is empty:

```
[youtube-scout] No new videos since last scan. All videos have been processed before.
```

**Stop here.**

### Step 3: Fetch Transcripts

Extract all `video_id` values from the filtered videos, join with commas.

```
Bash(command="python3 {SCRIPTS}/fetch_transcript.py --video-ids '<comma_separated_ids>' --lang 'en,zh-Hans'")
```

Parse the JSON output. For each video, attach the transcript text (or null) to the video data.

### Step 4: Score Videos

Prepare the input for the video-scorer agent.

If `export.domains` is non-empty, prepend a preamble before the video list:
```
Domains: [{export.domains joined by comma}]
```

For each video, format:

```
VIDEO {N}:
video_id: {video_id}
title: {title}
channel: {channel}
views: {views}
channel_subscribers: {channel_subscribers}
duration: {duration}
description: {description}
has_transcript: {true/false}
transcript: |
  {transcript text, or "No transcript available" if null}
```

Dispatch the `video-scorer` agent with all formatted videos. The agent returns YAML with scores for each video.

### Step 5: Sort and Select TOP-5

Parse the agent's YAML output. Sort all videos by `weighted_total` descending. Select the top 5 as TOP-5 recommendations; the rest are FYI.

### Step 6: Mark as Seen

Write the full scored video list (all videos, not just TOP-5) as JSON and pipe through dedup mark-seen:

```
Bash(command="echo '<all_videos_json>' | python3 {SCRIPTS}/dedup.py mark-seen")
```

### Step 6.5: Export IEF Insights

Create export directory and clean stale files from today (handles re-runs):
```
Bash(command="mkdir -p {export_path} && rm -f {export_path}/{TODAY}-youtube-*.md")
```

For each scored video with `weighted_total >= export.min_score`:

1. Generate insight ID: `{TODAY}-youtube-{NNN}` (NNN = 001, 002, ... in weighted_total descending order)
2. Map `round(weighted_total)` to significance (1-5)
3. Write file to `{export_path}/{id}.md`:

```markdown
---
id: {id}
source: youtube
url: "https://www.youtube.com/watch?v={video_id}"
title: "{title}"
significance: {round(weighted_total)}
tags: [{tags from scorer}]
category: {category from scorer}
domain: {domain from scorer}
date: {TODAY}
read: false
channel: "{channel}"
duration: "{duration}"
weighted_total: {weighted_total}
---

# {title}

**Problem:** {problem}

**Technology:** {technology}

**Insight:** {insight}

**Difference:** {difference}

---

*Selection reason: {one_liner}*
```

4. Output: `[youtube-scout] Exported {N} insights to {export_path}`

### Step 7: Generate Report

#### File Report

Create the reports directory if it doesn't exist:
```
Bash(command="mkdir -p ./reports")
```

Write a markdown report to `./reports/{TODAY}-youtube-scan.md` with this structure:

```markdown
---
date: {TODAY}
topic: {scan.topic}
total_scanned: {total video count}
top_k: 5
---

# YouTube Scout — {TODAY}

## TOP 5 Recommendations

### 1. [{title}]({url})
**Channel:** {channel} | **Duration:** {duration} | **Views:** {views}
**Scores:** Density {d} | Freshness {f} | Originality {o} | Depth {dp} | S/N {sn} | Credibility {c} → **{weighted_total}**

> {recommendation_reason — two paragraphs}

---

[repeat for #2 through #5]

## FYI — Other Videos

| # | Title | Channel | Score | Summary |
|---|-------|---------|-------|---------|
| 6 | [{title}]({url}) | {channel} | {weighted_total} | {one_liner} |
[repeat for remaining videos, sorted by score descending]
```

#### Terminal Output

Print a compact summary to the conversation:

```
[youtube-scout] Scan complete — {TODAY}
  Scanned: {N} → New: {N} → Scored: {N}
  Report: ./reports/{TODAY}-youtube-scan.md

  TOP 5:
  1. {title} ({weighted_total}) — {one_liner}
     {url}
  2. ...

  FYI ({N} more):
  - {title} ({weighted_total})
  - ...
```

## Error Handling

- Script exits with non-zero code → report the error, do not continue
- Transcript fetch fails for all videos → proceed with metadata-only scoring (all videos get no-transcript constraint)
- Video-scorer agent returns incomplete output → report which videos are missing, score only those returned
