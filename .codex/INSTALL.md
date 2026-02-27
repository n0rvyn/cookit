# Installing Indie Toolkit for Codex

Enable Indie Toolkit skills in Codex via native skill discovery.

## Prerequisites

- Codex CLI
- Git

## Installation (macOS/Linux)

1. Clone or update the repository:

```bash
if [ -d ~/.codex/indie-toolkit/.git ]; then
  git -C ~/.codex/indie-toolkit pull --ff-only
else
  git clone https://github.com/n0rvyn/indie-toolkit.git ~/.codex/indie-toolkit
fi
```

2. Create skill source links:

```bash
mkdir -p ~/.codex/skills
ln -sfn ~/.codex/indie-toolkit/ios-development/skills ~/.codex/skills/indie-toolkit-ios-development
ln -sfn ~/.codex/indie-toolkit/mactools/skills ~/.codex/skills/indie-toolkit-mactools
```

3. Restart Codex.

## Verify

```bash
ls -la ~/.codex/skills/indie-toolkit-ios-development
ls -la ~/.codex/skills/indie-toolkit-mactools
```

## Updating

```bash
git -C ~/.codex/indie-toolkit pull --ff-only
```

If new skills were added in the repo, re-run the symlink commands once.

## Uninstall

```bash
rm ~/.codex/skills/indie-toolkit-ios-development
rm ~/.codex/skills/indie-toolkit-mactools
```
