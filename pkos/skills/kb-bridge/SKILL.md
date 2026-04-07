---
name: kb-bridge
description: "Internal skill — exports PKOS vault notes to ~/.claude/knowledge/ for cross-project availability. Triggered manually via /pkos bridge or after intel-sync."
model: sonnet
---

## Overview

Bridges the PKOS Obsidian vault (`~/Obsidian/PKOS/`) with the dev-workflow knowledge base (`~/.claude/knowledge/`). Exports qualifying PKOS notes as dev-workflow KB entries so they appear in `/kb` searches across all projects.

This is a one-way export (PKOS → dev-workflow KB). The reverse direction (dev-workflow → PKOS) is handled by the `/kb` fallback search, not by this skill.

## Arguments

- `--dry-run`: Show what would be exported without writing files
- `--force`: Re-export notes even if already tracked in state file

## Process

### Step 1: Load Export State

Read `~/Obsidian/PKOS/.state/kb-bridge-exported.yaml`:
```yaml
exported:
  - vault_path: "10-Knowledge/some-note.md"
    kb_path: "api-usage/2026-04-07-some-note.md"
    date: "2026-04-07"
last_export: "2026-04-07T20:00:00"
```

If file does not exist, initialize with empty list.

### Step 2: Scan Qualifying Notes

Scan PKOS vault for notes that map to dev-workflow KB categories:

```
Glob(pattern="**/*.md", path="~/Obsidian/PKOS/10-Knowledge")
Glob(pattern="**/*.md", path="~/Obsidian/PKOS/50-References")
```

For each note, read its frontmatter `topics:` field. Apply topic-to-category mapping:

| PKOS Topic Contains | dev-workflow Category |
|---------------------|----------------------|
| architecture, system-design, patterns, design-patterns | `architecture` |
| api, sdk, library, framework, api-usage | `api-usage` |
| bug, error, crash, debugging | `bug-postmortem` |
| platform, ios, macos, swiftui, swift | `platform-constraints` |
| workflow, ci, deployment, tooling | `workflow` |

A note qualifies if ANY of its topics match a mapping. Use the first matching category.

Skip notes that:
- Are already in the exported list (by vault_path) unless `--force`
- Have `status: needs-reconciliation` (unresolved conflicts)
- Have `quality: 0` AND `citations: 0` AND were created more than 30 days ago (low-value seeds)

### Step 3: Convert Format

For each qualifying note:

1. Read the full note content
2. Extract keywords from `topics` array + `keywords` from content (if present)
3. Strip Obsidian-specific syntax:
   - `[[wikilinks]]` → plain text (just the link text)
   - `![[embeds]]` → remove entirely
   - Obsidian callouts `> [!note]` → standard blockquotes
4. Construct dev-workflow KB frontmatter:
```yaml
---
category: {mapped-category}
keywords: [{topics converted to keywords}]
date: {created date from PKOS frontmatter}
source_project: pkos
pkos_source: "{vault_path}"
---
```
5. Generate filename: `{date}-{title-slug}.md` (same slug rules as collect-lesson)

### Step 4: Write to dev-workflow KB

If `--dry-run`: present list of notes that would be exported with their target paths, then stop.

For each note:
1. Check for existing file with same slug: `Grep(pattern="{title-slug}", path="~/.claude/knowledge/{category}/", output_mode="files_with_matches")`
2. If exists and content is substantively the same → skip (already exported via another path)
3. Write to `~/.claude/knowledge/{category}/{date}-{slug}.md`

### Step 5: Update State

Write updated `~/Obsidian/PKOS/.state/kb-bridge-exported.yaml` with all newly exported entries.

### Step 6: Report

```
PKOS → KB Bridge Export
  Scanned: {N} vault notes
  Qualifying: {M} (matched category mapping)
  Exported: {K} new entries
  Skipped: {S} (already exported: {s1}, low-value: {s2}, conflicted: {s3})
  Categories: architecture={n1}, api-usage={n2}, bug-postmortem={n3}, ...
```
