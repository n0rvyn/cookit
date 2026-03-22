# Indie Toolkit

Indie Toolkit is a mono-repo of AI-facing plugins, skills, agents, and local tooling for indie app development workflows.

The current codebase contains:

- 10 top-level modules
- 57 skill folders with `SKILL.md`
- 22 agent files
- 1 local MCP server (`rag-server`)

## Modules

| Module | Type | What is in the repo |
|---|---|---|
| `dev-workflow` | Claude Code plugin | Cross-stack workflow system with 24 skills, 10 agents, hooks, and a persisted phase state flow |
| `apple-dev` | Claude Code plugin + Codex/OpenCode skills | iOS/macOS/iPadOS development workflows, reviews, design-token checks, CI/CD, localization, App Store review prep |
| `mactools` | Claude Code plugin + Codex/OpenCode skills | macOS automation for Notes, Calendar, Mail, Safari, Spotlight, Reminders, OCR, Photos, Contacts, OmniFocus |
| `product-lens` | Claude Code plugin | Product evaluation workflows such as `/evaluate`, `/compare`, `/demand-check`, `/teardown`, `/feature-assess` |
| `rag-server` | Local MCP server | Offline-first hybrid search server using SQLite FTS5 + `sqlite-vec` + Apple `NLContextualEmbedding` |
| `skill-audit` | Claude Code plugin | Auditor for plugins, skills, agents, hooks, commands, and trigger quality |
| `domain-intel` | Claude Code plugin | Domain intelligence engine with automated collection, AI analysis, trend synthesis, and evolving LENS profiles |
| `session-intel` | Claude Code plugin | AI session analytics: extract, analyze, and correlate Claude Code and Codex sessions with git history |
| `yt-intel` | Claude Code plugin | YouTube video curation: scrape, transcript extraction, AI scoring, TOP-5 recommendations |
| `pkos` | Claude Code plugin | Personal Knowledge Operating System: inbox processing, signal aggregation, digest generation, vault operations |

## Repository Layout

```text
.
├── dev-workflow/
├── apple-dev/
├── mactools/
├── product-lens/
├── rag-server/
├── skill-audit/
├── domain-intel/
├── session-intel/
├── yt-intel/
├── pkos/
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

Install any plugin you want:

```bash
/plugin install dev-workflow@indie-toolkit
/plugin install apple-dev@indie-toolkit
/plugin install mactools@indie-toolkit
/plugin install product-lens@indie-toolkit
/plugin install rag-server@indie-toolkit
/plugin install skill-audit@indie-toolkit
/plugin install domain-intel@indie-toolkit
/plugin install session-intel@indie-toolkit
/plugin install yt-intel@indie-toolkit
/plugin install pkos@indie-toolkit
```

Current marketplace entries from `.claude-plugin/marketplace.json`:

| Plugin | Version | Description | Docs |
|---|---|---|---|
| `dev-workflow` | `2.9.0` | Planning, execution, review, debugging, design analysis, commits, session management | `dev-workflow/README.md` |
| `apple-dev` | `1.5.0` | iOS/macOS/iPadOS development workflow plugin | `apple-dev/README.md` |
| `mactools` | `1.0.1` | macOS automation toolkit for Apple apps and local workflows | `mactools/README.md` |
| `product-lens` | `1.0.0` | Product evaluation, market analysis, moat assessment, feature assessment, comparison | `product-lens/README.md` |
| `rag-server` | `1.1.1` | Local hybrid search MCP server for project documentation | `rag-server/README.md` |
| `skill-audit` | `1.1.1` | Audit plugins, skills, agents, hooks, commands, and trigger quality | `skill-audit/README.md` |
| `domain-intel` | `1.1.0` | Domain intelligence: collection, analysis, trends, evolving LENS profiles | `domain-intel/README.md` |
| `session-intel` | `1.1.0` | AI session analytics: extract, analyze, correlate sessions with git history | `session-intel/README.md` |
| `yt-intel` | `1.0.0` | YouTube video curation, transcript extraction, AI scoring, recommendations | — |
| `pkos` | `0.1.0` | Personal Knowledge OS: inbox, signals, digests, vault, profiles, serendipity | — |

Note:

- `rag-server` is not just a prompt-only plugin; it requires extra setup in `rag-server/README.md`, including compiling the Swift embed binary and creating a Python virtual environment.

## Codex

Codex installation is file-based, not marketplace-based. The source of truth is:

```text
.codex/INSTALL.md
```

If you want Codex to bootstrap itself in-chat:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/n0rvyn/indie-toolkit/main/.codex/INSTALL.md
```

What the current install guide actually links:

- `dev-workflow/skills`
- `apple-dev/skills`
- `mactools/skills`
- `product-lens/skills`
- `skill-audit/skills`

Additional Codex notes:

- `rag-server` is separate MCP infrastructure, not a Codex skill folder.
- Role and structure notes live in `docs/README.codex.md`.

## OpenCode

OpenCode installation is also file-based. The source of truth is:

```text
.opencode/INSTALL.md
```

If you want OpenCode to bootstrap itself in-chat:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/n0rvyn/indie-toolkit/main/.opencode/INSTALL.md
```

The current OpenCode installer links only:

- `apple-dev/skills`
- `mactools/skills`

Detailed notes live in `docs/README.opencode.md`.

## Module Docs

- `dev-workflow/README.md`
- `apple-dev/README.md`
- `mactools/README.md`
- `product-lens/README.md`
- `rag-server/README.md`
- `skill-audit/README.md`
- `domain-intel/README.md`
- `session-intel/README.md`
