---
name: kb-bridge
description: "Internal skill — exports PKOS vault notes to ~/.claude/knowledge/ for cross-project availability. Triggered manually via /pkos bridge or after intel-sync."
model: sonnet
---

## Overview

Bridges the PKOS Obsidian vault (`~/Obsidian/PKOS/`) with the dev-workflow knowledge base (`~/.claude/knowledge/`).

**Forward (PKOS → KB):** Exports qualifying PKOS notes as dev-workflow KB entries for `/kb` searches.
**Reverse (KB → PKOS):** Imports dev-workflow crystals and lessons into the PKOS vault for Bases querying and graph integration.

## Arguments

- `--dry-run`: Show what would be exported without writing files
- `--force`: Re-export/re-import even if already tracked in state file
- `--direction DIR`: forward (PKOS→KB, default) | reverse (KB→PKOS) | both

## Process

### Step 1: Load Export State

Read `~/Obsidian/PKOS/.state/kb-bridge-exported.yaml`:
```yaml
exported:
  - vault_path: "10-Knowledge/some-note.md"
    kb_path: "api-usage/2026-04-07-some-note.md"
    date: "2026-04-07"
reverse_imported:
  - source_path: "docs/11-crystals/2026-03-21-pkos-crystal.md"
    vault_path: "30-Projects/indie-toolkit/pkos-crystal.md"
    date: "2026-04-08"
last_export: "2026-04-07T20:00:00"
last_reverse_import: "2026-04-08T10:00:00"
```

If file does not exist, initialize with empty list.

### Step 2: Scan Qualifying Notes (forward direction only)

Skip this step if `--direction` is `reverse`.

Scan PKOS vault for notes that map to dev-workflow KB categories:

```
Glob(pattern="**/*.md", path="~/Obsidian/PKOS/10-Knowledge")
Glob(pattern="**/*.md", path="~/Obsidian/PKOS/50-References")
```

For each note, read its frontmatter `tags:` field. Apply tag-to-category mapping:

| PKOS Tag Contains | dev-workflow Category |
|---------------------|----------------------|
| architecture, system-design, patterns, design-patterns | `architecture` |
| api, sdk, library, framework, api-usage | `api-usage` |
| bug, error, crash, debugging | `bug-postmortem` |
| platform, ios, macos, swiftui, swift | `platform-constraints` |
| workflow, ci, deployment, tooling | `workflow` |

A note qualifies if ANY of its tags match a mapping. Use the first matching category.

Skip notes that:
- Are already in the exported list (by vault_path) unless `--force`
- Have `status: needs-reconciliation` (unresolved conflicts)
- Have `quality: 0` AND `citations: 0` AND were created more than 30 days ago (low-value seeds)

### Step 2.5: Scan dev-workflow Artifacts (reverse direction only)

Skip this step if `--direction` is `forward`.

**Crystals:**
```
Glob(pattern="*-crystal.md", path="docs/11-crystals/")
```

**Lessons (project-local):**
```
Glob(pattern="*.md", path="docs/09-lessons-learned/")
```

**Lessons (global KB):**
```
Glob(pattern="**/*.md", path="~/.claude/knowledge/")
```

For each file, read frontmatter. Skip if:
- Already in reverse-imported list (by source path) unless `--force`
- Crystal has `status: superseded`

Apply category mapping (reverse of forward):

| dev-workflow Type | PKOS Destination | PKOS `type` |
|-------------------|------------------|-------------|
| crystal | `30-Projects/{project-name}/` | `reference` |
| lesson (api-usage) | `50-References/` | `reference` |
| lesson (architecture) | `10-Knowledge/` | `knowledge` |
| lesson (bug-postmortem) | `10-Knowledge/` | `knowledge` |
| lesson (platform-constraints) | `10-Knowledge/` | `knowledge` |
| lesson (workflow) | `50-References/` | `reference` |

### Step 3: Convert Format (forward direction only)

Skip this step if `--direction` is `reverse`.

For each qualifying note:

1. Read the full note content
2. Extract keywords from `tags` array (if present)
3. Strip Obsidian-specific syntax:
   - `[[wikilinks]]` → plain text (just the link text)
   - `![[embeds]]` → remove entirely
   - Obsidian callouts `> [!note]` → standard blockquotes
4. Construct dev-workflow KB frontmatter:
```yaml
---
category: {mapped-category}
keywords: [{tags converted to keywords}]
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

### Step 4.5: Write to PKOS Vault (reverse direction only)

Skip this step if `--direction` is `forward`.

For each qualifying dev-workflow artifact:

1. Convert to PKOS format with Obsidian Flavored Markdown:
   ```yaml
   ---
   type: {mapped PKOS type}
   source: dev-workflow
   created: {date from source frontmatter}
   tags: [{keywords/tags from source, mapped to PKOS vault tags}]
   quality: 2
   citations: 0
   related: []
   status: seed
   dev_workflow_source: "{source file path}"
   aliases: []
   ---

   # {title}

   > [!insight] Origin
   > Imported from dev-workflow {crystal|lesson}: `{source path}`

   {body content with wikilinks added where related PKOS notes exist}

   ## Connections

   {Scan PKOS vault for topic-overlapping notes, add as [[wikilinks]]}
   ```

2. Write to PKOS vault at the mapped destination path.

3. Dispatch `pkos:ripple-compiler` for each imported note (sequentially).

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

KB → PKOS Reverse Import
  Scanned: {N} dev-workflow artifacts
  Imported: {K} notes
  Skipped: {S} (already imported: {s1}, superseded: {s2})
  Destinations: 10-Knowledge={n1}, 50-References={n2}, 30-Projects={n3}
```
