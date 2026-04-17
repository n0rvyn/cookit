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
| `wechat-bridge` | integration | WeChat message bridge via MCP `--channels` protocol: permission relay, push messages, reply |
| `x-api` | integration | X (Twitter) API v2 MCP server: 131+ tools with Bearer Token and OAuth2 PKCE support |
| `minimax-quota` | integration | MiniMax coding plan quota checker: only requires MINIMAX_API_KEY |
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
├── wechat-bridge/
├── x-api/
├── minimax-quota/
├── netease-cloud-music/
├── shared-utils/
├── docs/
├── .claude-plugin/   # marketplace manifest
├── .codex/           # Codex install docs
└── .opencode/        # OpenCode install docs
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
/plugin install wechat-bridge@indie-toolkit
/plugin install x-api@indie-toolkit
/plugin install minimax-quota@indie-toolkit
/plugin install netease-cloud-music@indie-toolkit
/plugin install shared-utils@indie-toolkit
```

For personal OS plugins — `/health`, `/reflect`, `/intel`, `/scout`, `/pkos`, `/portfolio-scan` and related — see the [personal-os marketplace](https://github.com/n0rvyn/personal-os).

Current marketplace entries from `.claude-plugin/marketplace.json`:

| Plugin | Version | Description |
|---|---|---|
| `dev-workflow` | `2.24.1` | Cross-stack workflow with plan-execute-review |
| `apple-dev` | `1.10.2` | iOS/macOS/iPadOS development workflows |
| `mactools` | `1.0.1` | macOS automation for Apple apps |
| `product-lens` | `1.0.0` | Product evaluation and market analysis |
| `skill-master` | `1.0.0` | Unified plugin lifecycle management |
| `skill-audit` | `1.1.5` | [DEPRECATED] Plugin auditor |
| `wechat-bridge` | `1.0.3` | WeChat message bridge |
| `x-api` | `1.0.0` | X (Twitter) API v2 MCP server |
| `minimax-quota` | `0.2.1` | MiniMax coding plan quota checker |
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
- `wechat-bridge/README.md` — WeChat bridge
- `x-api/README.md` — X API v2 MCP server
- `minimax-quota/README.md` — MiniMax coding plan quota checker
- `netease-cloud-music/README.md` — NetEase Cloud Music helper
- `shared-utils/README.md` — Reusable cross-plugin utility scripts and skills
