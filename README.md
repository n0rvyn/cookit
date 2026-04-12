# Indie Toolkit

Multi-plugin monorepo for Claude Code plugins, published to the `indie-toolkit` marketplace. Contains production plugins, development workflow tools, and macOS automation.

## Plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| `dev-workflow` | development | Cross-stack workflow system with plan-execute-review lifecycle, phase orchestration, and session state persistence |
| `apple-dev` | development | iOS/macOS/iPadOS development workflows, reviews, design-token checks, CI/CD, localization, App Store review prep |
| `mactools` | productivity | macOS automation for Notes, Calendar, Mail, Safari, Spotlight, Reminders, OCR, Photos, Contacts, OmniFocus |
| `product-lens` | product | Product evaluation: demand validation, market analysis, moat assessment, feature assessment, comparison matrix |
| `skill-master` | development | Unified plugin lifecycle: brainstorm, create, eval, review, iterate, package Claude Code plugins |
| `skill-audit` | development | [DEPRECATED — use skill-master] Plugin auditor from AI executor perspective |
| `domain-intel` | intelligence | Domain intelligence engine: GitHub, RSS, changelogs, figures, companies, deep research with evolving LENS profiles |
| `session-reflect` | coaching | AI collaboration coach: analyze sessions, improve prompting, workflow, and AI collaboration skills |
| `youtube-scout` | intelligence | YouTube video intelligence: scrape, transcript extraction, AI scoring, IEF-compliant export |
| `pkos` | productivity | Personal Knowledge Operating System: inbox, harvest, signal, digest, lint, vault operations, ripple compilation |
| `wechat-bridge` | integration | WeChat message bridge via MCP `--channels` protocol: permission relay, push messages, reply |
| `x-api` | integration | X (Twitter) API v2 MCP server: 131+ tools with Bearer Token and OAuth2 PKCE support |
| `health-insights` | health | Personal health intelligence: ingest Apple Health data, establish baselines, generate AI-driven narrative insights |
| `minimax-platform` | integration | MiniMax platform helper: coding-plan quota checks and browser-session based auth management |
| `netease-cloud-music` | integration | NetEase Cloud Music helper: cookie-based login flows and cloud-drive upload via maintained CLI |
| `shared-utils` | development | Reusable utility scripts and skills shared across plugins: Notion API, MongoDB queries, cross-plugin primitives |

## Repository Layout

```text
.
├── dev-workflow/
├── apple-dev/
├── mactools/
├── product-lens/
├── skill-master/
├── skill-audit/
├── domain-intel/
├── session-reflect/
├── youtube-scout/
├── pkos/
├── wechat-bridge/
├── x-api/
├── health-insights/
├── minimax-platform/
├── netease-cloud-music/
├── shared-utils/
├── docs/
├── .claude-plugin/   # marketplace manifest
├── .codex/           # Codex install docs
└── .opencode/        # OpenCode install docs
```

## Cross-Plugin Knowledge Flow

For PKOS-integrated plugins, the repo follows these cross-plugin rules:

1. **Markdown first; Notion second**
   - Local Markdown is the fact source.
   - Notion is the management view for status, sorting, and dashboards.

2. **Producer plugins do not own final vault placement**
   - Plugins such as `domain-intel`, `product-lens`, and `session-reflect` should produce structured results.
   - They should publish those results into a PKOS-owned ingress / exchange layer, not write directly into final vault locations with plugin-specific rules.

3. **PKOS owns ingestion**
   - PKOS applies canonical tags, deduplication, note placement, ripple compilation, and downstream sync rules.
   - This keeps one ingestion authority for the vault instead of each plugin inventing its own storage logic.

4. **Stable decisions are promoted, not dumped**
   - High-frequency outputs belong in `signal` / `verdict` style notes.
   - Only stable, user-confirmed conclusions should become `crystal` notes.

5. **Cross-plugin precedent**
   - `domain-intel` writes into its own workspace and `pkos:intel-sync` imports into PKOS.
   - `pkos:inbox` already acts as a multi-source ingestion entry for raw captures.
   - `product-lens` should follow the same separation of concerns: produce structured analysis; let PKOS ingest and organize it.

At a glance, the intended flow is:

```text
Producer plugin
  -> PKOS ingress / exchange
  -> PKOS vault ingestion and enrichment
  -> Obsidian / local Markdown as source of truth
  -> Notion summary sync as management projection
```

## Claude Code

Add the marketplace:

```bash
/plugin marketplace add n0rvyn/indie-toolkit
```

Install plugins:

```bash
/plugin install dev-workflow@indie-toolkit
/plugin install apple-dev@indie-toolkit
/plugin install mactools@indie-toolkit
/plugin install product-lens@indie-toolkit
/plugin install skill-master@indie-toolkit
/plugin install domain-intel@indie-toolkit
/plugin install session-reflect@indie-toolkit
/plugin install youtube-scout@indie-toolkit
/plugin install pkos@indie-toolkit
/plugin install wechat-bridge@indie-toolkit
/plugin install x-api@indie-toolkit
/plugin install health-insights@indie-toolkit
/plugin install minimax-platform@indie-toolkit
/plugin install netease-cloud-music@indie-toolkit
/plugin install shared-utils@indie-toolkit
```

Current marketplace entries from `.claude-plugin/marketplace.json`:

| Plugin | Version | Description |
|---|---|---|
| `dev-workflow` | `2.23.0` | Cross-stack workflow with plan-execute-review |
| `apple-dev` | `1.10.2` | iOS/macOS/iPadOS development workflows |
| `mactools` | `1.0.1` | macOS automation for Apple apps |
| `product-lens` | `1.0.0` | Product evaluation and market analysis |
| `skill-master` | `1.0.0` | Unified plugin lifecycle management |
| `skill-audit` | `1.1.4` | [DEPRECATED] Plugin auditor |
| `domain-intel` | `1.4.0` | Domain intelligence and trend analysis |
| `session-reflect` | `2.0.0` | AI collaboration coaching |
| `youtube-scout` | `1.0.1` | YouTube video intelligence |
| `pkos` | `0.6.1` | Personal Knowledge OS |
| `wechat-bridge` | `1.0.3` | WeChat message bridge |
| `x-api` | `1.0.0` | X (Twitter) API v2 MCP server |
| `health-insights` | `1.0.0` | Personal health intelligence |
| `minimax-platform` | `0.1.0` | MiniMax platform helper |
| `netease-cloud-music` | `0.1.0` | NetEase Cloud Music helper |
| `shared-utils` | `0.1.0` | Reusable cross-plugin utility scripts and skills |

## Codex / OpenCode

Both Codex and OpenCode use file-based installation. The sources of truth are:

- Codex: `.codex/INSTALL.md`
- OpenCode: `.opencode/INSTALL.md`

Skills for each platform are linked via these install guides. Each plugin's `skills/` folder contains its skill definitions.

## Plugin Docs

Each plugin has its own `README.md`:

- `dev-workflow/README.md` — Cross-stack workflow system
- `apple-dev/README.md` — iOS/macOS/iPadOS development
- `mactools/README.md` — macOS automation
- `product-lens/README.md` — Product evaluation
- `skill-master/README.md` — Plugin lifecycle management
- `skill-audit/README.md` — Plugin audit (deprecated)
- `domain-intel/README.md` — Domain intelligence engine
- `session-reflect/README.md` — AI collaboration coach
- `youtube-scout/README.md` — YouTube intelligence
- `pkos/README.md` — Personal Knowledge OS
- `wechat-bridge/README.md` — WeChat bridge
- `x-api/README.md` — X API v2 MCP server
- `health-insights/README.md` — Personal health intelligence
- `minimax-platform/README.md` — MiniMax platform helper
- `netease-cloud-music/README.md` — NetEase Cloud Music helper
- `shared-utils/README.md` — Reusable cross-plugin utility scripts and skills
