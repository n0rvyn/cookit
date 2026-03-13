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

1. Read `./config.yaml`
   - If file does not exist → output `[domain-intel] Not initialized. Run /intel setup in this directory.` → **stop**

2. Extract from config:
   - `domains[]` — each with name
   - `sources.github` — enabled flag, languages, min_stars
   - `sources.rss[]` — list of {name, url}
   - `sources.official[]` — list of {name, url, paths[]}
   - `scan.max_items_per_source` (default: 20)
   - `scan.significance_threshold` (default: 2)

3. Read `./LENS.md` if it exists:
   - Parse YAML frontmatter → extract `figures[]` and `companies[]`
   - Extract the markdown body (everything after frontmatter) → store as `lens_context`
   - Extract "What I Don't Care About" items from body → use as additional blacklist terms in Tier 3
   - If LENS.md does not exist → proceed without it (scan works without LENS)

4. Get today's date and month:
   ```
   date +%Y-%m-%d
   date +%Y-%m
   ```

5. Ensure month directory exists:
   ```
   mkdir -p ./insights/{YYYY-MM}
   ```

6. Read `./state.yaml` if it exists (for stats tracking).

### Step 2: Dispatch source-scanner

Dispatch the `source-scanner` agent with:
- **sources**: the full sources block from config
- **domains**: all domain entries (name only — scanner uses these for search queries)
- **figures**: from LENS.md frontmatter (or empty list if no LENS.md)
- **companies**: from LENS.md frontmatter (or empty list if no LENS.md)
- **date**: today's date
- **max_items_per_source**: from config
- **rss_feeds**: list of URLs from `sources.rss[].url` (for source signal detection)
- **browser_fallback**: from config `scan.browser_fallback` (default: false)
- **fallback_script_path**: (only if browser_fallback is true) resolve via `Bash(command="echo ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_rendered.py")` and pass the absolute path. If `CLAUDE_PLUGIN_ROOT` is empty, set `browser_fallback` to false and log a warning.

Wait for completion. The agent returns:
```yaml
items:
  - url, title, source, snippet, metadata, collected_at
failed_sources:
  - url, source_type, error
source_signals:
  - type, value, reason
stats:
  github: N, rss: N, official: N, figure: N, company: N, failed: N, total: N
```

Save `source_signals` for merging in Step 6.5.

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
Grep(pattern="{escaped_url}", path="./insights/{YYYY-MM}/", output_mode="files_with_matches", head_limit=1)
```
If current day is within the first 7 days of the month, also check previous month (only if it exists):
```
Glob(pattern="./insights/{PREV-YYYY-MM}/*.md", head_limit=1)
```
If glob returns results:
```
Grep(pattern="{escaped_url}", path="./insights/{PREV-YYYY-MM}/", output_mode="files_with_matches", head_limit=1)
```

Remove items whose URL already exists. Track: `after_url_dedup = N`

#### Tier 2: Title Deduplication

Get titles from recent insight files (current month + previous month if applicable):
```
Grep(pattern="^title:", path="./insights/{YYYY-MM}/", output_mode="content")
```
If within first 7 days and `./insights/{PREV-YYYY-MM}/` exists (checked via Glob in Tier 1), also check previous month.

For each remaining item, compare its title against existing titles:
- Lowercase both titles
- Split into words, remove common stop words (the, a, an, is, of, for, in, on, to, and, with)
- Calculate word overlap: `|intersection| / |union|`
- If overlap > 0.80 → mark as duplicate

Remove duplicates. Track: `after_title_dedup = N`

#### Tier 3: Relevance Scoring

For each remaining item, compute relevance score using domain names and LENS context:

```
score = 0

# Domain name matching — item title/snippet matches a configured domain name
For each domain in domains:
  if domain.name appears in item.title OR item.snippet (case-insensitive):
    score += 1

# LENS "What I Don't Care About" blacklist (if LENS.md exists)
For each anti_interest extracted from LENS.md body:
  if anti_interest appears in item.title OR item.snippet (case-insensitive):
    score -= 3

# Source-type baseline — figure and company items were explicitly requested via LENS.md,
# so they get a baseline relevance score
if item.source == "figure" OR item.source == "company":
  score += 1
```

Drop items with score <= 0. Sort remaining by score descending.

Take top N items where N = min(`max_items_per_source` * number of enabled source types, **30**).

Hard cap at 30 total items to stay within agent turn budgets.

Track: `after_keyword = N`

### Step 4: Dispatch insight-analyzer

Group filtered items by source type (github, rss, official, figure, company).

For each non-empty group, dispatch one `insight-analyzer` agent with:
- **items**: the filtered items for that source type
- **source_type**: github | rss | official | figure | company
- **domains**: domain definitions from config
- **significance_threshold**: from config
- **date**: today's date
- **lens_context**: the LENS.md body content (or omit if no LENS.md)

Dispatch all groups **in parallel** (multiple Agent tool calls in one message).

Wait for all to complete. If a single analyzer fails, log the failure and continue with the results from the others. Each successful analyzer returns:
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

2. Write insight file to `./insights/{YYYY-MM}/{id}.md`:

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
- Also group by similar problem descriptions: two insights are similar if their `problem` fields share 2+ non-stop-words (using the same stop word list as Tier 2)

For each topic that appears across 2+ different source types (e.g., github + rss):

Write a convergence signal file to `./insights/{YYYY-MM}/{YYYY-MM-DD}-convergence.md`:

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

### Step 6.5: Lens Signal Collection

Skip this step if LENS.md does not exist.

Check today's stored insights for evolution signals — topics or entities that appear frequently but aren't reflected in LENS.md.

1. **New interest detection**: Extract all tags from today's insights with significance >= 4. If any tag appears 3+ times but is NOT mentioned in LENS.md "What I Care About" section → record as `new-interest` signal.

2. **New figure detection**: Scan `problem`, `technology`, `insight`, and `difference` fields across today's insights. Look for capitalized multi-word names that appear to reference a person (e.g., "Andrej Karpathy", "Tim Cook"). Exclude known technical terms (framework names, language names, domain names). If a person name appears in 2+ insights and is NOT in LENS.md `figures[]` frontmatter → record as `new-figure` signal. This is best-effort detection; false negatives are acceptable.

3. **New company detection**: Same field scan as above. Look for capitalized names that appear to reference an organization or company (e.g., "Mistral AI", "Hugging Face"). If an organization name appears in 2+ insights and is NOT in LENS.md `companies[]` frontmatter → record as `new-company` signal. Best-effort; false negatives acceptable.

4. **New RSS detection**: Group today's stored insights by URL domain (extract hostname from `url` field). If 3+ insights with significance >= 4 share the same URL domain, and that domain is NOT in `sources.rss[].url` or `sources.official[].url` → record as `suggest-rss` signal with value = the domain URL.

5. **New domain detection**: Group today's insights by primary tag (first tag). If a tag appears on 3+ insights but does NOT match any `domains[].name` (case-insensitive) → record as `suggest-domain` signal.

6. **Merge source-scanner signals**: Append any `source_signals` returned by the source-scanner in Step 2 (suggest-rss, suggest-official-path).

7. Append all signals to `./.lens-signals.yaml`:
   ```yaml
   - date: YYYY-MM-DD
     type: new-interest  # or new-figure, new-company, suggest-rss, suggest-official-path, suggest-domain
     value: "{tag, name, or URL}"
     evidence: [insight IDs or source description]
   ```

   If `.lens-signals.yaml` doesn't exist, create it. If it does, append to the existing list.

Track: `lens_signals = N`

### Step 7: Update State

Write `./state.yaml`:

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
  lens_signals: {N}
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

If lens_signals > 0, append:
```
  LENS evolution signals: {N} (run /intel evolve to review)
```

## Error Handling

- If source-scanner returns 0 items: report and stop gracefully
- If all insight-analyzers return 0 insights above threshold: report "no significant insights found" and stop
- If a single analyzer fails: report the failure, continue with others
- Never leave state.yaml in an inconsistent state — write it as the last step
