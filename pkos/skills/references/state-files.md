# PKOS State & Config File Inventory

All runtime state and configuration files used by PKOS skills and agents.

## User Configuration

| File | Location | Owner | Purpose |
|------|----------|-------|---------|
| `config.yaml` | `~/.claude/pkos/` | User (manual) | Intel source paths, thresholds, ripple/lint settings. Template: `pkos/config/pkos-config.template.yaml` |

## Runtime State (Vault-Coupled)

These files live inside the PKOS vault because their content references vault notes by path or ID. They should move with the vault.

| File | Location | Owner Skill | Purpose |
|------|----------|-------------|---------|
| `imported-insights.yaml` | `~/Obsidian/PKOS/.state/` | intel-sync | Tracks imported IEF insight IDs to prevent duplicates |
| `kb-bridge-exported.yaml` | `~/Obsidian/PKOS/.state/` | kb-bridge | Tracks forward (vault→KB) and reverse (KB→vault) exports by path + date |
| `harvest-state.yaml` | `~/Obsidian/PKOS/.state/` | harvest | Tracks harvested project docs by source path + md5 hash |
| `exchange-ingest.yaml` | `~/Obsidian/PKOS/.state/` | ingest-exchange | Tracks imported `.exchange/` artifacts by source path, checksum, and canonical note path |
| `product-lens-notion-sync.yaml` | `~/Obsidian/PKOS/.state/` | sync_product_lens_notion | Tracks canonical note path to Notion summary row/page mapping and sync status |
| `ripple-log.yaml` | `~/Obsidian/PKOS/.state/` | ripple-compiler | Append-only changelog of MOC updates, cross-refs added, entities updated |
| `last-review-marker` | `~/Obsidian/PKOS/.state/` | signal, evolve | Timestamp marker for "since last review" queries |

## Runtime Signals (Vault-Coupled)

| File Pattern | Location | Owner Skill | Purpose |
|--------------|----------|-------------|---------|
| `{YYYY-MM-DD}-feedback.yaml` | `~/Obsidian/PKOS/.signals/` | inbox, signal | Daily feedback signal entries from inbox classification |

## Project-Level State (dev-workflow)

These files live in each project's `.claude/` directory, not in the PKOS vault.

| File | Location | Owner Skill | Purpose |
|------|----------|-------------|---------|
| `dev-workflow-state.yml` | `{project}/.claude/` | run-phase, finalize | Current phase, step, dev-guide path for the active project |
| `reviews/*.md` | `{project}/.claude/reviews/` | verify-plan, finalize, implementation-reviewer | Timestamped verification/review reports |

## Global Shared

| File Pattern | Location | Owner | Purpose |
|--------------|----------|-------|---------|
| `{category}/*.md` | `~/.claude/knowledge/` | collect-lesson, kb-bridge | Cross-project knowledge base entries |

## Design Rationale

- **Vault-coupled state** stays in `~/Obsidian/PKOS/.state/` because the IDs and paths in these files reference vault notes. Separating them from the vault would break referential integrity on vault backup/migration.
- **User config** lives in `~/.claude/pkos/` because it's user preferences (paths, thresholds), not vault-dependent data. It survives vault recreation.
- **Project-level state** stays in `{project}/.claude/` because each project has its own dev-guide progress and review history.
