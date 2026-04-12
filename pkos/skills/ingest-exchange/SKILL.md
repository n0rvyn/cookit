---
name: ingest-exchange
description: "Internal skill — ingests producer-owned exchange artifacts from PKOS .exchange directories, converts them into canonical vault notes, and prepares summary projections for downstream systems."
model: sonnet
---

## Overview

`ingest-exchange` is the PKOS-side bridge between producer plugins and the vault.

For `product-lens`, the producer writes structured artifacts under:

```text
~/Obsidian/PKOS/.exchange/product-lens/
```

This skill:
- reads exchange artifacts
- validates schema shape
- decides canonical vault note placement
- writes final PKOS notes
- tracks ingestion state

It does not re-run the upstream analysis.

## Script

Reference script:

```text
pkos/skills/ingest-exchange/scripts/ingest_exchange.py
```

Recommended dry-run:

```bash
python3 pkos/skills/ingest-exchange/scripts/ingest_exchange.py \
  --source pkos/examples/exchange/product-lens/reprioritize/2026-04-12-repo-reprioritize-appa.md \
  --vault-root /tmp/pkos-test \
  --dry-run
```

Recommended sandbox write test:

```bash
python3 pkos/skills/ingest-exchange/scripts/ingest_exchange.py \
  --source pkos/examples/exchange/product-lens/reprioritize/2026-04-12-repo-reprioritize-appa.md \
  --vault-root /tmp/pkos-test
```

Recommended Notion payload dry-run:

```bash
python3 pkos/skills/ingest-exchange/scripts/ingest_exchange.py \
  --source pkos/examples/exchange/product-lens/reprioritize/2026-04-12-repo-reprioritize-appa.md \
  --vault-root /tmp/pkos-test \
  --notion-dry-run
```

## Inputs

Parse from user input:
- `--producer NAME`: filter to one producer such as `product-lens`
- `--intent INTENT`: filter to one exchange subdirectory
- `--source PATH`: ingest one explicit artifact path instead of scanning the exchange tree
- `--dry-run`: show placement decisions only
- `--sync-notion`: after note write, call the product-lens Notion sync script
- `--notion-dry-run`: after note write, print the Notion payload without calling the API
- `--notion-database-id`: override the configured Notion summary database id

## State

Track ingestion state in:

```text
~/Obsidian/PKOS/.state/exchange-ingest.yaml
```

Suggested shape:

```yaml
artifacts:
  "/absolute/path/to/artifact.md":
    imported_at: "2026-04-12T10:00:00"
    checksum: "..."
    status: "imported"
    note_type: "verdict"
    note_path: "30-Projects/AppA/Verdicts/2026-04-12-AppA-verdict.md"
    superseded_notes:
      - "30-Projects/AppA/Verdicts/2026-04-01-AppA-verdict.md"
last_sync: "2026-04-12T10:00:00"
```

If the state file does not exist, initialize it with an empty `artifacts` map.

## Process

### Step 1: Discover Exchange Artifacts

If `--source PATH` is provided:
- read only that artifact
- do not scan sibling directories

Otherwise scan `.exchange/` for producer directories.

For `product-lens`, expected subdirectories are:
- `portfolio-scan`
- `progress-pulse`
- `reprioritize`
- `recent-feature-review`
- `verdict-refresh`

Skip artifacts already recorded in `exchange-ingest.yaml` unless the checksum changed.

### Step 1.5: Sample Artifact for Dry-Run Validation

Use this repository sample when you need a concrete artifact shape during design or dry-run reasoning:

```text
pkos/examples/exchange/product-lens/reprioritize/2026-04-12-repo-reprioritize-appa.md
```

Treat it as a reference sample only. Do not write imported state for repository examples unless the user explicitly asks for a simulated state entry.

### Step 2: Validate Artifact Schema

For each artifact confirm:
- `type = product-lens-exchange`
- `producer = product-lens`
- `intent` exists
- `decision` exists
- body contains summary, reasons, next actions, evidence

If validation fails:
- log the failure
- do not write a partial final note

### Step 3: Map to Canonical Note Type

Map producer intents to note types:

| Intent | Final Note Type |
|---|---|
| `portfolio_scan` | `signal` |
| `project_progress_pulse` | `signal` |
| `repo_reprioritize` | `verdict` |
| `recent_feature_review` | `feature-review` |
| `verdict_refresh` | `verdict` |

### Step 4: Choose Final Placement

PKOS owns final placement.

Recommended locations:
- `signal` → `~/Obsidian/PKOS/30-Projects/{project}/Signals/`
- `verdict` → `~/Obsidian/PKOS/30-Projects/{project}/Verdicts/`
- `feature-review` → `~/Obsidian/PKOS/30-Projects/{project}/Feature Reviews/`

For portfolio-level artifacts that span many projects:
- write a portfolio note under `~/Obsidian/PKOS/30-Projects/_Portfolio/`

File naming rules:
- `signal` → `YYYY-MM-DD-{project}-signal.md`
- `verdict` → `YYYY-MM-DD-{project}-verdict.md`
- `feature-review` → `YYYY-MM-DD-{project}-{feature-slug}-feature-review.md`

Project identifier rules:
- prefer explicit `project` if present after normalization
- else infer from the first concrete repo target path
- else use `_Portfolio`

### Step 5: Normalize Frontmatter

Add or normalize:
- `type`
- `source = product-lens`
- `created`
- `tags`
- `related`
- `status`
- `producer_intent`
- `decision`
- `confidence`
- project or feature identifiers
- `exchange_source` with the original artifact path
- `projection_status = pending` when `notion_sync_requested = true`

Frontmatter normalization should preserve the original `created` date from the artifact, not overwrite it with ingestion time.

### Step 5.5: Supersession Rules

Before writing a new canonical note, search the target project folder for older notes of the same type:
- same `type`
- same `project`
- same `producer_intent` when present

Rules:
- `signal`: do not supersede automatically; many signals may coexist
- `verdict`: mark older active notes as superseded when the new note answers the same project-level question
- `feature-review`: supersede only when the same feature slug is reviewed again

When supersession happens:
- add `replaces:` links in the new note
- record superseded note paths in `exchange-ingest.yaml`
- do not delete older notes

### Step 6: Write Final Notes

Write final vault notes only after schema validation succeeds.

If `--dry-run`, print:
- source artifact path
- target note path
- derived note type
- derived project or portfolio target
- whether supersession would happen
- whether projection status would be set to pending

and stop before writing.

Dry-run output format:

```text
PKOS Exchange Dry Run
  Artifact: {source path}
  Producer: {producer}
  Intent: {intent}
  Note type: {signal|verdict|feature-review}
  Target: {vault path}
  Supersedes: {none|list}
  Projection: {pending|not-requested}
```

### Step 7: Record State and Projection Status

Update `exchange-ingest.yaml`.

If a downstream Notion summary sync is requested:
- mark the final note as `projection_status: pending`
- do not block vault write on Notion
- if `--notion-dry-run` is passed, print the generated Notion payload for inspection
- if `--sync-notion` is passed, call `sync_product_lens_notion.py`

Required state fields per artifact entry:
- `imported_at`
- `checksum`
- `status`
- `note_type`
- `note_path`
- `superseded_notes`

Status values:
- `imported`
- `failed_validation`
- `failed_write`
- `skipped_unchanged`

## Rules

1. PKOS decides final placement; producers do not.
2. Exchange artifact failure must not create partial vault notes.
3. Markdown remains the source of truth even when projections are stale.
