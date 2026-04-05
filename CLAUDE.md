# indie-toolkit

Multi-plugin monorepo for Claude Code plugins, published to the `indie-toolkit` marketplace.

## Plugin-specific Build Rules

### wechat-bridge

- Uses **esbuild bundle** (not plain tsc output). The MCP server runs in the plugin cache where `node_modules` doesn't exist; all dependencies must be inlined into the dist files.
- Build: `npm run build` = `tsc --noEmit` (type check only) + `esbuild` (bundle to `dist/`).
- Release artifacts in `dist/` must be self-contained single files. If a new dependency is added, verify it gets bundled — `--packages=external` is NOT used.

## Insight Exchange Format (IEF)

Cross-plugin protocol for exchanging analyzed intelligence data. Any plugin can produce or consume IEF files.

### File Format

IEF files are Markdown with YAML frontmatter. Required fields:

```yaml
---
id: "{YYYY-MM-DD}-{source}-{NNN}"    # Unique ID: date + source name + sequence
source: "{source_name}"                # Producer identifier (e.g., youtube, podcast, twitter)
url: "{original_url}"                  # Canonical URL of the source content
title: "{title}"                       # Human-readable title
significance: {1-5}                    # Importance score (integer)
tags: [{keyword1}, {keyword2}]         # 3-5 lowercase hyphenated keywords
category: "{category}"                 # One of: framework, tool, library, platform, pattern, ecosystem, security, performance, ai-ml, devex, business, community
domain: "{domain}"                     # Knowledge domain (e.g., ai-ml, ios-development)
date: {YYYY-MM-DD}                     # Production date
read: false                            # Consumption flag (consumer sets to true)
---

# {title}

**Problem:** {what question or gap this addresses}

**Technology:** {tools, frameworks, methods involved}

**Insight:** {single most valuable takeaway}

**Difference:** {what makes this perspective unique}

---

*Selection reason: {why this was selected for export}*
```

### Naming Convention

- File name: `{id}.md` (e.g., `2026-04-05-youtube-001.md`)
- ID format: `{YYYY-MM-DD}-{source}-{NNN}` where NNN is zero-padded sequence

### Exchange Directory Convention

- Producer writes to a configured export directory (e.g., `~/.youtube-scout/exports/`)
- Consumer reads from the same directory via `sources.external[].path` in its config
- Consumer deletes files after successful import (consumed)
- Producer must not assume files persist after writing

### Producer Responsibilities

- Write well-formed IEF files with all required fields
- Ensure `id` uniqueness within a single export batch
- Only export items above a configurable quality threshold

### Consumer Responsibilities

- Validate required fields before import
- Deduplicate against existing insights (URL-based)
- Apply own significance threshold
- Delete source files after import
- Gracefully handle missing/malformed files

### Pre-collect Convention

Consumers may optionally trigger producers before importing:
```yaml
scan:
  external:
    - name: YouTube Scout
      path: ~/.youtube-scout/exports
      pre_collect: /youtube-scan    # Skill to invoke before import
```
Pre-collect is best-effort: failures do not block the consumer pipeline.

### Extended Fields

Producers may add source-specific fields to frontmatter (e.g., `channel`, `duration`, `weighted_total` for YouTube). Consumers must ignore unknown fields.

