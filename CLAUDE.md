# indie-toolkit

Multi-plugin monorepo for Claude Code plugins, published to the `indie-toolkit` marketplace.

## Plugin-specific Build Rules

### wechat-bridge

- Uses **esbuild bundle** (not plain tsc output). The MCP server runs in the plugin cache where `node_modules` doesn't exist; all dependencies must be inlined into the dist files.
- Build: `npm run build` = `tsc --noEmit` (type check only) + `esbuild` (bundle to `dist/`).
- Release artifacts in `dist/` must be self-contained single files. If a new dependency is added, verify it gets bundled — `--packages=external` is NOT used.

## Insight Exchange Format (IEF)

Cross-plugin protocol for exchanging producer-to-consumer data. Any plugin can produce or consume IEF files.

Two payload shapes share the same envelope:
- **Insight** (`category` ∈ analytical set): analyzed intelligence (articles, videos, research) — original IEF use case.
- **Directive** (`category: directive`): producer-to-consumer action requests (e.g., product-lens → pkos "reprioritize project X", "update verdict Y"). Body replaces the Problem/Technology/Insight/Difference template with the decision payload defined by the producer.

### File Format

IEF files are Markdown with YAML frontmatter. Required fields:

```yaml
---
id: "{YYYY-MM-DD}-{source}-{NNN}"    # Unique ID: date + source name + sequence
source: "{source_name}"                # Producer identifier (e.g., youtube, podcast, product-lens)
url: "{original_url}"                  # Canonical URL or source ref (commit hash, notion page, repo path for directives)
title: "{title}"                       # Human-readable title
significance: {1-5}                    # Importance / confidence score (integer)
tags: [{keyword1}, {keyword2}]         # 3-5 lowercase hyphenated keywords
category: "{category}"                 # One of: framework, tool, library, platform, pattern, ecosystem, security, performance, ai-ml, devex, business, community, directive
domain: "{domain}"                     # Knowledge domain (e.g., ai-ml, ios-development, product-strategy)
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

For `category: directive` the body replaces the Insight template with:

```markdown
# {title}

**Intent:** {what the producer wants the consumer to do}

**Decision:** {concrete action, e.g., `reprioritize:project-x`, `verdict-update:y`}

**Confidence:** {0.0-1.0}

**Context:** {evidence / reasoning backing the directive}

**Targets:** {consumer-scoped identifiers the directive acts on}
```

### Naming Convention

- File name: `{id}.md` (e.g., `2026-04-05-youtube-001.md`)
- ID format: `{YYYY-MM-DD}-{source}-{NNN}` where NNN is zero-padded sequence

### Exchange Directory Convention

- Producer writes to a configured export directory (e.g., `~/.youtube-scout/exports/`)
- Consumer reads from the same directory via `sources.external[].path` in its config
- Consumer either deletes or archives files after successful import (producer must not assume files persist)
- Archive option: consumer may `mv` to its own tracked location (e.g., `~/.pkos/ingested/YYYY-MM/`) instead of deleting — convention is to move out of the producer's export directory so producer's next scan does not re-see it

### Producer Responsibilities

- Write well-formed IEF files with all required fields
- Ensure `id` uniqueness within a single export batch
- Only export items above a configurable quality threshold

### Consumer Responsibilities

- Validate required fields before import
- Deduplicate against existing items (URL-based for insights, id-based for directives)
- Apply own significance threshold
- Remove source files from the producer export directory after import (delete or move to a consumer-owned archive)
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

## Plugin Lifecycle

### When Creating a New Plugin

1. **Create plugin directory** with `.claude-plugin/plugin.json`
2. **Add to `marketplace.json`**: add entry with `name`, `source`, `description`, `version`, `category`, `tags`
3. **Add to `.github/workflows/auto-version.yml`**:
   - Add plugin directory path to the `on.push.paths` list (line 7-17)
   - Add plugin name to `ALL_PLUGINS` array (line 45)
4. **Add to `.github/workflows/release-plugin.yml`**:
   - Add plugin name to the `target.options` list (line 11-22)
   - Add plugin name to `PLUGINS` array if `TARGET == "all"` (line 87)
5. **Create plugin README** at `plugins/*/README.md`
6. **Update root `README.md`**: add plugin to the plugins table

### When Updating a Plugin

1. **Update plugin README**: ensure description, skills, agents, and architecture are current
2. **Update root `README.md`**: sync any description or metadata changes to the plugins table
3. **Update `marketplace.json`**: sync description and tags if changed

Version bumps happen automatically via `.github/workflows/auto-version.yml` (conventional commit based) or `.github/workflows/release-plugin.yml` (manual trigger).

## Commit Message Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) with automated semver bumping.

### Format

```
<type>(<scope>): <description>

[optional body]
```

### Types

| Type | Bump | When |
|------|------|------|
| `feat` | minor | New feature |
| `fix` | patch | Bug fix |
| `docs` | patch | Documentation only |
| `refactor` | patch | Code change that neither fixes a bug nor adds a feature |
| `perf` | patch | Performance improvement |
| `test` | patch | Adding or correcting tests |
| `chore` | patch | Build process, auxiliary tools, or dependency updates |
| `feat!` or `BREAKING CHANGE` in body | major | Breaking change |

### Scoping

Scope should reference the plugin or concern being changed:
- `feat(dev-workflow):`, `fix(apple-dev):`, `docs(mactools):`
- For changes spanning multiple plugins: `chore(release):`, `docs:`

### Auto-Version Bump

`.github/workflows/auto-version.yml` detects the highest bump type from commit messages and bumps:
- All changed plugins (each plugin's `version` in its `plugin.json`)
- The marketplace `metadata.version` (highest bump among changed plugins)

Commits from `github-actions[bot]` are excluded from bump detection.

### Examples

```
feat(domain-intel): add GitHub API rate limit handling
fix(apple-dev): correct SwiftData migration guide for iOS 26
docs: update wechat-bridge README with new auth flow
feat!(pkos): change inbox routing to require explicit destination
chore: bump dependencies across all plugins
```

