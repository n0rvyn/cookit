# Installing Cookit for Codex

Enable Cookit skills in Codex via native skill discovery.

## Prerequisites

- Codex CLI
- Git

## Installation (macOS/Linux)

1. Clone or update the repository:

```bash
if [ -d ~/.codex/cookit/.git ]; then
  git -C ~/.codex/cookit pull --ff-only
else
  git clone https://github.com/n0rvyn/cookit.git ~/.codex/cookit
fi
```

2. Create skill source links:

```bash
mkdir -p ~/.agents/skills
ln -sfn ~/.codex/cookit/ios-development/skills ~/.agents/skills/cookit-ios-development
ln -sfn ~/.codex/cookit/mactools/skills ~/.agents/skills/cookit-mactools
```

3. Restart Codex.

## Verify

```bash
ls -la ~/.agents/skills/cookit-ios-development
ls -la ~/.agents/skills/cookit-mactools
```

## Updating

```bash
git -C ~/.codex/cookit pull --ff-only
```

If new skills were added in the repo, re-run the symlink commands once.

## Uninstall

```bash
rm ~/.agents/skills/cookit-ios-development
rm ~/.agents/skills/cookit-mactools
```
