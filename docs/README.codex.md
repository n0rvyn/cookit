# Indie Toolkit for Codex

Codex does not use Claude marketplace metadata directly.

This file is the human-facing guide.

Command source of truth is `.codex/INSTALL.md`.

- Machine/bootstrap entry: `.codex/INSTALL.md`
- Explanation and structure notes: this file

## Which File Is For What

1. `.codex/INSTALL.md`
- Purpose: executable install/update/uninstall commands for Codex sessions.
- Rule: when command steps change, update this file first.

2. `docs/README.codex.md`
- Purpose: explain architecture and usage boundaries.
- Rule: avoid duplicating full command blocks from INSTALL.

## Notes

- Codex directly loads `skills/`; `agents/` and `hooks/` are plugin internals and are not linked directly.
- Current Codex-loadable plugin skill folders: `dev-workflow`, `apple-dev`, `mactools`, `product-lens`, `skill-master`, `skill-audit`, `domain-intel`, `session-reflect`, `youtube-scout`, `pkos`, `wechat-bridge`, `health-insights`, `minimax-platform`, `netease-cloud-music`.
- `x-api` is not a Codex skill folder. It is an MCP server plugin and needs separate MCP setup.

## Utility Scripts

- `scripts/minimax-coding-plan-remains.mjs`
- Purpose: compatibility entry that forwards to `minimax-platform/skills/minimax-coding-plan/scripts/minimax-coding-plan.mjs`.
- Auth boundary: current live verification shows this internal endpoint accepts `HERTZ-SESSION` cookie and returns `status_code: 1004` when cookie is missing; there is no verified env-only username/password login flow in this repo.
- Refresh model: if `MINIMAX_SESSION_COMMAND` is set, the script will call it once to obtain a fresh `HERTZ-SESSION` and cache it to `MINIMAX_COOKIE_FILE`.

## How To Install

Use either path below:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/n0rvyn/indie-toolkit/main/.codex/INSTALL.md
```

Or run commands directly from:

```text
./.codex/INSTALL.md
```
