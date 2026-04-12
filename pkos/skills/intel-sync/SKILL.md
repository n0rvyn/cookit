---
name: intel-sync
description: "Internal skill — imports new insights from domain-intel into PKOS vault. Tracks imported IDs to avoid duplicates. Triggered by Adam event after domain-intel scan completes."
model: sonnet
---

## Overview

Consumes insights from domain-intel's insights directory. Maintains an imported-ID list in `.state/imported-insights.yaml` for zero-coupling deduplication (does not modify domain-intel files).

## Configuration

The skill reads the intel source configuration from `~/.claude/pkos/config.yaml`:

```yaml
intel_sources:
  domain_intel:
    insights_path: ""    # REQUIRED — set to your domain-intel workspace's insights/ path
    significance_threshold: 3
    max_per_sync: 20
    source_name: domain-intel
  session_reflect:
    insights_path: ~/.claude/session-reflect/insights/
    significance_threshold: 3
    max_per_sync: 20
    category: pattern
    source_name: session-reflect
```

Validation:
- If config file does not exist → log `[pkos] intel-sync: ~/.claude/pkos/config.yaml not found. Copy from pkos/config/pkos-config.template.yaml and configure.` → stop.
- If `intel_sources` is empty or missing → log `[pkos] intel-sync: no intel_sources configured. Set at least one source in ~/.claude/pkos/config.yaml.` → stop.
- For each source in `intel_sources`: if `insights_path` is empty or missing → log warning and skip that source.

## Process

### Step 1: Load State

Read `~/Obsidian/PKOS/.state/imported-insights.yaml`:
```yaml
imported_ids: ["2026-04-01-github-001", "2026-04-02-rss-003"]
last_sync: "2026-04-04T20:00:00"
```

If file does not exist, initialize with empty list.

### Step 2: Scan Intel Insights

Read all configured sources from `~/.claude/pkos/config.yaml` using Python YAML parsing:
```bash
python3 -c "
import yaml, glob, os
from pathlib import Path
from datetime import datetime, timedelta

config_path = Path.home() / '.claude' / 'pkos' / 'config.yaml'
with open(config_path) as f:
    config = yaml.safe_load(f)

all_insight_files = []
sources_with_files = []
today = datetime.now()

for source_key, source_cfg in config.get('intel_sources', {}).items():
    insights_path = os.path.expanduser(source_cfg.get('insights_path', ''))
    if not insights_path:
        continue
    path_obj = Path(insights_path)
    if not path_obj.exists():
        continue

    # Current month folder
    yyyy_mm = today.strftime('%Y-%m')
    month_dir = path_obj / yyyy_mm
    files = sorted(month_dir.glob('*.md')) if month_dir.exists() else []

    # Previous month if within first 7 days
    if today.day <= 7:
        prev = (today.replace(day=1) - timedelta(days=1))
        prev_yyyy_mm = prev.strftime('%Y-%m')
        prev_dir = path_obj / prev_yyyy_mm
        files += sorted(prev_dir.glob('*.md'))

    for fp in files:
        all_insight_files.append((str(fp), source_key, source_cfg))
    if files:
        sources_with_files.append(source_key)

print(f'Sources: {len(sources_with_files)}, Files: {len(all_insight_files)}')
"
```

### Step 3: Filter New Insights

For each insight file (from all sources):
1. Read YAML frontmatter
2. Skip if `id` is in `imported_ids` list
3. Skip if `significance` < per-source `significance_threshold` (from that source's config)
4. Skip if `read: true` (already consumed by the user)
5. Collect as candidate, annotating with `source_key`

Sort candidates by `significance` descending. Per source, take top `max_per_sync`.

### Step 4: Import to PKOS

For each candidate:

1. Determine classification from IEF `category` field:
   - `framework`, `tool`, `library`, `platform` → `reference`
   - `pattern`, `ecosystem`, `ai-ml` → `knowledge`
   - `security`, `performance`, `devex` → `knowledge`
   - `business`, `community` → `reference`

2. Map IEF fields to PKOS frontmatter and body (using the candidate's `source_key`):
   ```yaml
   ---
   type: {classification}
   source: "{source_key}"
   created: {IEF date field}
   tags: [{IEF tags, mapped to existing vault tags where possible}]
   quality: 0
   citations: 0
   related: []
   status: seed
   ief_id: "{IEF id}"
   source: "{IEF source}"
   aliases: []
   ---

   # {title}

   > [!insight] Key Insight
   > {IEF Insight field — the single most valuable takeaway}

   **Problem:** {IEF Problem field}

   **Technology:** {IEF Technology field}

   **Difference:** {IEF Difference field}

   ## Connections

   {If IEF category maps to a known MOC topic, add: `- See also: [[MOC-{topic}]]`}
   ```

   > Format reference: see `references/obsidian-format.md` for wikilink and callout conventions.

3. Write note to Obsidian:
   - `reference` → `~/Obsidian/PKOS/50-References/{title-slug}.md`
   - `knowledge` → `~/Obsidian/PKOS/10-Knowledge/{title-slug}.md`

4. Create Notion Pipeline DB entry:
   ```bash
   NO_PROXY="*" python3 ~/.claude/skills/notion-with-api/scripts/notion_api.py create-db-item \
     32a1bde4-ddac-81ff-8f82-f2d8d7a361d7 \
     "{title}" \
     --props '{"status": "processed", "source": "domain-intel", "type": "{classification}", "topics": "{tags_csv}"}'
   ```

5. Dispatch `pkos:ripple-compiler` for each imported note (sequentially).

5b. **KB Bridge Export** (best-effort): If the imported note's classification + IEF tags match a dev-workflow KB category, also write a copy to `~/.claude/knowledge/`:

   | Classification + Tag Contains | Target Category |
   |-------------------------------|----------------|
   | reference + api/sdk/library/framework | `api-usage` |
   | knowledge + architecture/design/pattern | `architecture` |
   | knowledge + bug/error/security | `bug-postmortem` |
   | knowledge + platform/ios/swift | `platform-constraints` |

   Write a simplified version (strip PKOS-specific frontmatter, use dev-workflow format):
   ```yaml
   ---
   category: {mapped-category}
   keywords: [{IEF tags}]
   date: {IEF date}
   source_project: domain-intel-via-pkos
   pkos_source: "{obsidian_path}"
   ---
   # {title}

   {IEF body content}
   ```

   Target path: `~/.claude/knowledge/{category}/{date}-{slug}.md`

   If the category mapping doesn't match any rule, skip the KB export (the note still lives in PKOS vault). This step failing does not block the import pipeline.

6. Add `id` to `imported_ids` list.

### Step 5: Update State

Write updated `~/Obsidian/PKOS/.state/imported-insights.yaml`:
```yaml
imported_ids: [{updated list}]
last_sync: "{now ISO}"
```

### Step 6: Report

```
PKOS Intel Sync — {date}
  Sources scanned: {list of source_keys}
  Per-source breakdown:
    {source_key}: scanned={N}, new={M}, imported={K}, skipped={S}
  Classifications: knowledge={N1}, reference={N2}
  MOCs updated: {from ripple results}
```

## Error Handling

- If insights path does not exist → log and stop (no error — domain-intel may not have run yet)
- If a single insight import fails → log, skip, continue with next
- If Notion API fails → log error, keep the Obsidian note (data not lost)
- If ripple fails → log warning, note is still saved
