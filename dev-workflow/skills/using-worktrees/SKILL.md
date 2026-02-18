---
name: using-worktrees
description: "Use when starting feature work that needs isolation from current workspace. Optional tool — not required for every development task."
---

## Directory Selection (Priority Order)

### 1. Check Existing Directories

```bash
ls -d .worktrees 2>/dev/null     # Preferred (hidden)
ls -d worktrees 2>/dev/null      # Alternative
```

Use whichever exists. If both exist, `.worktrees` wins.

### 2. Check CLAUDE.md

```bash
grep -i "worktree.*director" CLAUDE.md 2>/dev/null
```

If a preference is specified, use it without asking.

### 3. Ask User

If no directory exists and no CLAUDE.md preference:

```
No worktree directory found. Where should I create worktrees?

1. .worktrees/ (project-local, hidden)
2. A custom location

Which do you prefer?
```

## Safety Verification

For project-local directories (`.worktrees` or `worktrees`):

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**If NOT ignored:** Add to `.gitignore` and commit before creating the worktree.

## Creation Steps

### 1. Create Worktree

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

### 2. Run Project Setup (auto-detect)

```bash
# Node.js
[ -f package.json ] && npm install

# Rust
[ -f Cargo.toml ] && cargo build

# Python
[ -f requirements.txt ] && pip install -r requirements.txt
[ -f pyproject.toml ] && poetry install

# Go
[ -f go.mod ] && go mod download

# iOS/Swift
[ -f Package.swift ] && swift build
```

### 3. Verify Clean Baseline

Run the project's test suite. If tests fail, report failures and ask whether to proceed or investigate.

### 4. Report

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## Quick Reference

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| Neither exists | Check CLAUDE.md; ask user |
| Directory not ignored | Add to .gitignore + commit |
| Tests fail at baseline | Report + ask user |
