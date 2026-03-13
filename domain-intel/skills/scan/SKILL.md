---
name: scan
description: "Use when the user says 'scan', 'collect intel', 'run scan', or when invoked by cron. Orchestrates the full domain intelligence pipeline: collect from sources, filter duplicates, analyze insights, detect convergence signals, store results. Primary cron target."
model: sonnet
user-invocable: true
---

## Overview

Pipeline orchestrator for domain-intel. Reads config, dispatches collection and analysis agents, applies 3-tier filtering, stores results, and detects cross-source convergence signals.

Uses sonnet because the 3-tier filter requires precise arithmetic (Jaccard similarity, weighted keyword scoring) and convergence signal detection requires topic clustering — haiku is unreliable for these.

Designed for **automated cron execution** — minimal output, no interactive prompts, fail-safe.

## Process

### Step 1: Load Config

1. Read `~/.claude/domain-intel.local.md`
   - If file does not exist → output `[domain-intel] Not configured. Run /intel setup first.` → **stop**
   - Parse YAML frontmatter. Extract `data_dir`.
   - If `data_dir` is missing or empty → output `[domain-intel] data_dir not set in config. Run /intel setup.` → **stop**

2. Expand `data_dir` (resolve `~` to home directory). Check directory exists:
   ```
   ls {data_dir}
   ```
   - If directory does not exist → create it:
     ```
     mkdir -p {data_dir}/{insights,digests,trends}
     ```

3. Extract from config frontmatter:
   - `domains[]` — each with name, keywords, boost_terms, blacklist_terms
   - `sources.github` — enabled flag, languages, min_stars
   - `sources.rss[]` — list of {name, url}
   - `sources.official[]` — list of {name, url, changelog_path}
   - `scan.max_items_per_source` (default: 20)
   - `scan.significance_threshold` (default: 2)

4. Get today's date and month:
   ```
   date +%Y-%m-%d
   date +%Y-%m
   ```

5. Ensure month directory exists:
   ```
   mkdir -p {data_dir}/insights/{YYYY-MM}
   ```

6. Read `{data_dir}/state.yaml` if it exists (for stats tracking).

### Step 2: Dispatch source-scanner

Dispatch the `source-scanner` agent with:
- **sources**: the full sources block from config
- **domains**: all domain entries (name + keywords only — scanner uses these for search queries)
- **date**: today's date
- **max_items_per_source**: from config

Wait for completion. The agent returns:
```yaml
items:
  - url, title, source, snippet, metadata, collected_at
failed_sources:
  - url, source_type, error
stats:
  github: N, rss: N, official: N, failed: N, total: N
```

If total items == 0 → output `[domain-intel] Scan complete — no items collected. Check source configuration.` → update state → **stop**

### Step 3: 3-Tier Filter

Apply filters sequentially. Track counts at each stage.

#### Tier 1: URL Deduplication

For each item, normalize the URL:
- Strip protocol (http:// or https://)
- Lowercase the hostname
- Remove trailing slash
- Remove query parameters matching `utm_*`, `ref=`, `source=`

**Regex-escape the normalized URL** before using as Grep pattern: replace `.` with `\\.`, `+` with `\\+`, `?` with `\\?`, `[` with `\\[`, `]` with `\\]`.

Check if the normalized URL exists in **recent** insight files only (current month + previous month):
```
Grep(pattern="{escaped_url}", path="{data_dir}/insights/{YYYY-MM}/", output_mode="files_with_matches", head_limit=1)
```
If current day is within the first 7 days of the month, also check previous month:
```
Grep(pattern="{escaped_url}", path="{data_dir}/insights/{PREV-YYYY-MM}/", output_mode="files_with_matches", head_limit=1)
```

Remove items whose URL already exists. Track: `after_url_dedup = N`

#### Tier 2: Title Deduplication

Get titles from recent insight files (past 7 days):
```
Grep(pattern="^title:", path="{data_dir}/insights/{YYYY-MM}/", output_mode="content")
```
Also check previous month if within first 7 days.

For each remaining item, compare its title against existing titles:
- Lowercase both titles
- Split into words, remove common stop words (the, a, an, is, of, for, in, on, to, and, with)
- Calculate word overlap: `|intersection| / |union|`
- If overlap > 0.80 → mark as duplicate

Remove duplicates. Track: `after_title_dedup = N`

#### Tier 3: Keyword Scoring

For each remaining item, compute relevance score across ALL configured domains:

```
score = 0
For each domain in domains:
  For each boost_term in domain.boost_terms:
    if boost_term appears in item.title OR item.snippet (case-insensitive):
      score += 2
  For each keyword in domain.keywords:
    if keyword appears in item.title OR item.snippet (case-insensitive):
      score += 1
  For each blacklist_term in domain.blacklist_terms:
    if blacklist_term appears in item.title OR item.snippet (case-insensitive):
      score -= 3
```

Drop items with score <= 0. Sort remaining by score descending.

Take top N items where N = min(`max_items_per_source` * number of enabled source types, **30**).

Hard cap at 30 total items to stay within agent turn budgets.

Track: `after_keyword = N`

### Step 4: Dispatch insight-analyzer

Group filtered items by source type (github, rss, official).

For each non-empty group, dispatch one `insight-analyzer` agent with:
- **items**: the filtered items for that source type
- **source_type**: github | rss | official
- **domains**: domain definitions from config
- **significance_threshold**: from config
- **date**: today's date

**Dispatch strategy:**
- If total filtered items <= 30: dispatch all groups **in parallel** (multiple Agent tool calls in one message)
- If total filtered items > 30: dispatch groups **sequentially** to avoid turn limit exhaustion

Wait for all to complete. Each returns:
```yaml
insights:
  - id, source, url, title, significance, tags, category, domain,
    problem, technology, insight, difference, selection_reason
dropped:
  - url, reason
```

### Step 5: Store Insights

Merge results from all analyzers. For each insight with `significance >= significance_threshold`:

1. Verify the ID doesn't collide with existing files. If it does, increment the sequence number.

2. Write insight file to `{data_dir}/insights/{YYYY-MM}/{id}.md`:

```markdown
---
id: {id}
source: {source}
url: "{url}"
title: "{title}"
significance: {N}
tags: [{tags joined by comma}]
category: {category}
domain: {domain}
date: {YYYY-MM-DD}
read: false
---

# {title}

**Problem:** {problem}

**Technology:** {technology}

**Insight:** {insight}

**Difference:** {difference}

---

*Selection reason: {selection_reason}*
```

Track: `stored = N`

### Step 6: Convergence Signal Detection

Read all insights stored today (from Step 5 results).

Group by normalized topic:
- Extract the primary tag (first tag) + category as topic key
- Also group by similar problem descriptions (shared key terms)

For each topic that appears across 2+ different source types (e.g., github + rss):

Write a convergence signal file to `{data_dir}/insights/{YYYY-MM}/{YYYY-MM-DD}-convergence.md`:

```markdown
---
id: {YYYY-MM-DD}-convergence
type: signal
date: {YYYY-MM-DD}
---

# Convergence Signals — {YYYY-MM-DD}

| Topic | Sources | Insight IDs | Summary |
|-------|---------|-------------|---------|
| {topic} | {source1}, {source2} | {id1}, {id2} | {1-sentence cross-source synthesis} |
```

If no convergence detected, skip this file. Track: `convergence_signals = N`

### Step 7: Update State

Write `{data_dir}/state.yaml`:

```yaml
last_scan: "{YYYY-MM-DD}T{HH:MM:SS}"
total_insights: {previous_total + stored}
total_scans: {previous_scans + 1}
last_scan_stats:
  collected: {raw items from scanner}
  after_url_dedup: {N}
  after_title_dedup: {N}
  after_keyword: {N}
  analyzed: {sent to analyzers}
  stored: {above threshold}
  convergence_signals: {N}
  failed_sources: {N}
```

### Step 8: Report

Output a concise summary:

```
[domain-intel] Scan complete — {YYYY-MM-DD}
  Collected: {N} → Filtered: {N} → Analyzed: {N} → Stored: {N}
  Convergence signals: {N}
  By domain: {domain1}: {N}, {domain2}: {N}
  Failed sources: {N}
```

If failed_sources > 0, list them.

## Error Handling

- If source-scanner returns 0 items: report and stop gracefully
- If all insight-analyzers return 0 insights above threshold: report "no significant insights found" and stop
- If a single analyzer fails: report the failure, continue with others
- Never leave state.yaml in an inconsistent state — write it as the last step
