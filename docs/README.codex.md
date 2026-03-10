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
- Current Codex-loadable plugin skill folders: `dev-workflow`, `apple-dev`, `mactools`, `product-lens`, `skill-audit`.
- `rag-server` is not a Codex skill folder. It is a separate MCP server component; see `rag-server/README.md`.

## How To Install

Use either path below:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/n0rvyn/indie-toolkit/main/.codex/INSTALL.md
```

Or run commands directly from:

```text
./.codex/INSTALL.md
```
