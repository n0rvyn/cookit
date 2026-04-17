# Personal-OS Marketplace Split — Retrospective

**Date:** 2026-04-17
**Plan:** `docs/06-plans/2026-04-17-personal-os-marketplace-split-plan.md`
**Status:** Complete

---

## What moved

### Plugins (5 migrated to personal-os)

| Plugin | Source commit | Notes |
|--------|-------------|-------|
| `health-insights` | indie-toolkit | Shared-utils cross-marketplace dep (Option C); agents use absolute path `~/.claude/plugins/marketplaces/indie-toolkit/shared-utils/...`; `scripts/check_shared_utils.sh` enforces prerequisite |
| `session-reflect` | indie-toolkit | `insights_path` IEF output defaults to `{exchange_dir}/session-reflect/YYYY-MM/` via `personal_os_config.py` |
| `domain-intel` | indie-toolkit | Profile `config.yaml` ief_output_dir override field preserved; read paths (profile dirs) unchanged; write paths redirect to exchange dir |
| `youtube-scout` | indie-toolkit | Default export path moved to `{exchange_dir}/youtube-scout/YYYY-MM/`; cookie cache stays at `~/.youtube-scout/cookies/` |
| `pkos` | indie-toolkit | `ingest_exchange.py` `archive_root` default now reads `~/.claude/personal-os.yaml`; smoke-test /tmp paths updated to `{scratch_dir}/pkos-test/` |

### Plugins (1 newly created in personal-os)

| Plugin | Source | Notes |
|--------|--------|-------|
| `portfolio-lens` | Split from `indie-toolkit/product-lens` | Contains 5 stateful skills (portfolio-scan, project-progress-pulse, recent-feature-review, repo-reprioritize, verdict-refresh), 4 agents, 2 scripts |

### product-lens assets that moved to portfolio-lens

- `agents/ingress-publisher.md`
- `agents/repo-activity-scanner.md`
- `agents/feature-change-clusterer.md`
- `agents/verdict-delta-analyzer.md`
- `scripts/publish_exchange.py`
- `scripts/extract_session_signals.py`

### indie-toolkit assets removed (migrated to personal-os)

- 5 plugin directories: `health-insights/`, `session-reflect/`, `domain-intel/`, `youtube-scout/`, `pkos/`
- 5 skill directories from `product-lens/skills/`: `portfolio-scan/`, `project-progress-pulse/`, `recent-feature-review/`, `repo-reprioritize/`, `verdict-refresh/`
- 4 agent files from `product-lens/agents/`: `ingress-publisher.md`, `repo-activity-scanner.md`, `feature-change-clusterer.md`, `verdict-delta-analyzer.md`
- 2 scripts from `product-lens/scripts/`: `publish_exchange.py`, `extract_session_signals.py` (+ `__pycache__/`)

---

## Rejected design directions

The following approaches were considered and rejected during planning. They are listed here to prevent reintroduction without fresh deliberation.

1. **Plugin signal registration with Adam** — plugins do NOT register as Adam event sources via any schema or API. Instead, users wire plugins to Adam manually via Role/Template/Trigger config.

2. **Capability routing / capability abstraction layer** — no intermediate abstraction between plugins and their data destinations.

3. **`input_spec` expression DSL for Templates** — not introduced. Adam's existing Template mechanism is sufficient.

4. **Plugin seed/preset import flow** — not introduced.

5. **Plugin upgrade asset-protection mechanism** — not introduced.

6. **`personal-os-core` plugin with MCP tool wrappers** — no such plugin exists. Each plugin is self-sufficient with a copy of `scripts/personal_os_config.py`.

7. **"Template chain" / "signal-source Template" concepts** — not introduced.

8. **Any plugin POSTing `/webhooks/events`** — plugins do NOT post webhooks. Webhooks are for Adam-external systems only (iPhone shortcuts, remote bots, user-hosted cron scripts).

---

## Verification steps run

### Batch 1 (Tasks 1-5)
- Scaffold created: `marketplace.json` valid JSON, `auto-version.yml` and `release-plugin.yml` tag prefixes verified clean (`indie-toolkit-v` absent).
- `docs/personal-os-spec.md` and `docs/ief-format.md` written from plan spec.
- `personal-os/.git/` initialized with bootstrap commit.
- health-insights migrated: 4 agent files path-rewritten (`CLAUDE_PLUGIN_ROOT/../shared-utils/` replaced with absolute path), `check_shared_utils.sh` created, `python3` smoke test passed.

### Batch 2 (Tasks 6-9)
- session-reflect: `config.yaml` updated, `insights_path` resolved via `personal_os_config.py`, smoke test passed.
- domain-intel: IEF path precedence documented, README updated, smoke test passed.
- youtube-scout: export path updated to exchange dir, smoke test passed.
- pkos: `ingest_exchange.py` `archive_root` default fixed, README and SKILL.md examples updated, smoke test passed.

### Batch 3 (Tasks 10-12)
- portfolio-lens: 5 skills + 4 agents + 2 scripts copied, path fixes applied (`/tmp/pkos-e2e/` -> scratch_dir), `python3` config smoke test passed, registered in marketplace + workflows.
- product-lens shrunk: 5 skill dirs + 4 agent files + 2 scripts deleted, `plugin.json`/`marketplace.json` description+tags synced, README pruned.
- product-lens README cleaned: PKOS smoke-test examples, Notion Notes section, AI Entry section removed; `pkos/skills|ingest-exchange|/tmp/pkos` grep confirmed empty.

### Batch 4 (Tasks 13-20)
- 5 plugin dirs staged for removal.
- `marketplace.json` updated: 5 entries removed, product-lens description/tags synced, version bumped 1.36.1 -> 1.36.2.
- `auto-version.yml`: 5 plugin paths + ALL_PLUGINS entries removed.
- `release-plugin.yml`: 5 plugin names removed from target.options + PLUGINS.
- `check-marketplace.yml`: verified clean (no plugin names hardcoded).
- `README.md`: plugins table trimmed, Cross-Plugin Knowledge Flow section removed, personal-os pointer added, install commands removed.
- `CLAUDE.md`: IEF section removed entirely.
- T4.8 atomic commit: `feat!:` prefix triggers major version bump.

### Batch 5 (Tasks 21-25, this session)
- T5.1 (personal-os install test): `marketplace.json` has 6 plugins (health-insights, session-reflect, domain-intel, youtube-scout, pkos, portfolio-lens); each plugin has `.claude-plugin/plugin.json` with matching name; each has `skills/` and/or `agents/` directories. Result: filesystem validation passed; manual `/plugin install` deferred to user.
- T5.2 (indie-toolkit install test): `marketplace.json` has 11 plugins (all except the 5 migrated); `product-lens/skills/` has exactly 6 stateless skills (compare, demand-check, evaluate, feature-assess, product-lens, teardown) with no stateful ones. Result: filesystem validation passed; manual `/plugin install` deferred to user.
- T5.3: GitHub repo `n0rvyn/personal-os` created (public), pushed `main`, tagged `v0.1.0`.
- T5.4: `git pull --rebase` pulled 2 auto-version commits (dev-workflow-v2.24.2, indie-toolkit-v1.36.2), pushed rebased `main` to GitHub.
- T5.5: This retro document written.

---

## Known follow-ups (NOT done in this plan)

1. **health-insights direct Notion writes** — plugin writes directly to Notion DBs. If single-ingestion-authority routing through PKOS is desired, that is a user-level config decision, not a marketplace rule.

2. **shared-utils cross-marketplace dependency** — Resolved as Option C: health-insights uses absolute path `~/.claude/plugins/marketplaces/indie-toolkit/shared-utils/`. Requires both marketplaces installed. If fragile, consider duplicating helpers into a personal-os `shared-utils` plugin.

3. **mactools write-type skills** — `/calendar create`, `/reminders create`, etc. are actuator capabilities. Future consideration for personal-os as Apple-ecosystem-writer tier.

4. **portfolio-lens / product-lens shared evaluation logic** — duplication is acceptable for first cut. Revisit if portfolio-lens calls product-lens scoring primitives.

5. **IEF validator script** — consider `personal-os/scripts/validate_ief.py` as a test utility for CI use.

6. **Adam `docs/02-architecture/adam-signal-contract.md` rewrite** — current version describes plugins as webhook-posting sources. Rewrite: plugins do NOT post webhooks; webhook is for external systems only. Reframe `source` column as "any string identifying the client that POSTed" rather than enumerated plugin names.

7. **Adam norvyn-config layering verification** — re-scan Adam framework docs for residual norvyn-specific leakage (5D drift dimensions, `user_day_boundary=00:00`, daily push budget, specific signal sources). Move leakage to `docs/norvyn/personal-config.md`. Note: crystal `2026-04-14-adam-solo-founder-os-crystal.md` is historical — leave as-is.

8. **Update `docs/02-architecture/adam-plugin-integration.md`** — verify plugin/Role binding docs are accurate, `~/.claude/personal-os.yaml` convention matches spec, mutual independence contract is stated, webhook scope matches "no plugin webhooks" decision. Edit inline rather than rewrite.

Items 6-8 are independent of the plugin migration and should be handled in a separate Adam-focused session.
