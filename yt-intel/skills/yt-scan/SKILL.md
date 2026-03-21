---
name: yt-scan
description: "Use when the user says 'yt-scan', 'scan youtube', 'youtube recommendations', 'yt recommendations'. Scrapes YouTube recommended feed and topic search, extracts transcripts, scores videos with Claude AI on 6 dimensions, outputs TOP-5 recommendations with reasons + FYI summaries for the rest."
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

### Step 1: Scrape Videos

```
Bash(command="python3 {SCRIPTS}/scrape_youtube.py --topic 'AI' --cookie-dir ~/.yt-intel --max-recommended 30 --max-search 20")
```

Parse the JSON output from stdout. Check the `status` field:

- `"login_required"` → output:
  ```
  [yt-intel] YouTube login required. Please run again after logging in — the script will open a browser window for you.
  ```
  **Stop here.**

- `"partial"` → output warning:
  ```
  [yt-intel] Warning: Recommended feed unavailable (login may be stale). Proceeding with search results only.
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
[yt-intel] No new videos since last scan. All videos have been processed before.
```

**Stop here.**

### Step 3: Fetch Transcripts

Extract all `video_id` values from the filtered videos, join with commas.

```
Bash(command="python3 {SCRIPTS}/fetch_transcript.py --video-ids '<comma_separated_ids>' --lang 'en,zh-Hans'")
```

Parse the JSON output. For each video, attach the transcript text (or null) to the video data.

### Step 4: Score Videos

Prepare the input for the video-scorer agent. For each video, format:

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

### Step 7: Generate Report

#### File Report

Create the reports directory if it doesn't exist:
```
Bash(command="mkdir -p ./reports")
```

Write a markdown report to `./reports/{TODAY}-yt-scan.md` with this structure:

```markdown
---
date: {TODAY}
topic: AI
total_scanned: {total video count}
top_k: 5
---

# YT Intel — {TODAY}

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
[yt-intel] Scan complete — {TODAY}
  Scanned: {N} → New: {N} → Scored: {N}
  Report: ./reports/{TODAY}-yt-scan.md

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
