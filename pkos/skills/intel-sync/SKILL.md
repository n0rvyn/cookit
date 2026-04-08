---
name: intel-sync
description: "Internal skill — imports new insights from domain-intel into PKOS vault. Tracks imported IDs to avoid duplicates. Triggered by Adam event after domain-intel scan completes."
model: sonnet
---

## Overview

Consumes insights from domain-intel's insights directory. Maintains an imported-ID list in `.state/imported-insights.yaml` for zero-coupling deduplication (does not modify domain-intel files).

## Configuration

The skill reads the intel source path from `~/.claude/pkos/config.yaml`:

```yaml
intel_sources:
  domain_intel:
    insights_path: ""    # REQUIRED — set to your domain-intel workspace's insights/ path
    significance_threshold: 3
    max_per_sync: 10
```

Validation:
- If config file does not exist → log `[pkos] intel-sync: ~/.claude/pkos/config.yaml not found. Copy from pkos/config/pkos-config.template.yaml and configure.` → stop.
- If `insights_path` is empty or missing → log `[pkos] intel-sync: insights_path not configured. Set intel_sources.domain_intel.insights_path in ~/.claude/pkos/config.yaml.` → stop.
- If resolved path does not exist → log `[pkos] intel-sync: insights path {path} does not exist.` → stop.

## Process

### Step 1: Load State

Read `~/Obsidian/PKOS/.state/imported-insights.yaml`:
```yaml
imported_ids: ["2026-04-01-github-001", "2026-04-02-rss-003"]
last_sync: "2026-04-04T20:00:00"
```

If file does not exist, initialize with empty list.

### Step 2: Scan Domain-Intel Insights

Resolve the insights path:
```bash
ls -d $(echo {insights_path})/{current_YYYY-MM}/  2>/dev/null
```

Glob for insight files:
```
Glob(pattern="*.md", path="{resolved_insights_path}/{YYYY-MM}")
```

Also check previous month if within first 7 days:
```
Glob(pattern="*.md", path="{resolved_insights_path}/{PREV-YYYY-MM}")
```

### Step 3: Filter New Insights

For each insight file:
1. Read YAML frontmatter
2. Skip if `id` is in `imported_ids` list
3. Skip if `significance` < `significance_threshold`
4. Skip if `read: true` (already consumed by the user in domain-intel)
5. Collect as candidate

Sort candidates by `significance` descending. Take top `max_per_sync`.

### Step 4: Import to PKOS

For each candidate:

1. Determine classification from IEF `category` field:
   - `framework`, `tool`, `library`, `platform` → `reference`
   - `pattern`, `ecosystem`, `ai-ml` → `knowledge`
   - `security`, `performance`, `devex` → `knowledge`
   - `business`, `community` → `reference`

2. Map IEF fields to PKOS frontmatter and body:
   ```yaml
   ---
   type: {classification}
   source: domain-intel
   created: {IEF date field}
   tags: [{IEF tags, mapped to existing vault tags where possible}]
   quality: 0
   citations: 0
   related: []
   status: seed
   ief_id: "{IEF id}"
   ief_source: "{IEF source}"
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
   NO_PROXY="*" python3 ~/.claude/skills/notion/scripts/notion_api.py create-db-item \
     32a1bde4-ddac-81ff-8f82-f2d8d7a361d7 \
     "{title}" \
     --props '{"Status": "processed", "Source": "domain-intel", "Type": "{classification}", "Topics": "{tags_csv}"}'
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
  Scanned: {N} insight files
  New (above threshold): {M}
  Imported: {K}
  Skipped (already imported): {S}
  Classifications: knowledge={N1}, reference={N2}
  MOCs updated: {from ripple results}
```

## Error Handling

- If insights path does not exist → log and stop (no error — domain-intel may not have run yet)
- If a single insight import fails → log, skip, continue with next
- If Notion API fails → log error, keep the Obsidian note (data not lost)
- If ripple fails → log warning, note is still saved
