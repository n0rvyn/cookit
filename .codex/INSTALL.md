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

2. Create skill source links (including command-as-skill):

```bash
mkdir -p ~/.codex/skills
ln -sfn ~/.codex/cookit/ios-development/skills ~/.codex/skills/cookit-ios-development
ln -sfn ~/.codex/cookit/mactools/skills ~/.codex/skills/cookit-mactools
ln -sfn ~/.codex/cookit/ios-development/commands ~/.codex/skills/cookit-ios-commands
```

3. Restart Codex.

## Verify

```bash
ls -la ~/.codex/skills/cookit-ios-development
ls -la ~/.codex/skills/cookit-mactools
ls -la ~/.codex/skills/cookit-ios-commands
```

## Updating

```bash
git -C ~/.codex/cookit pull --ff-only
```

If new skills or command docs were added in the repo, re-run the symlink commands once.

## Uninstall

```bash
rm ~/.codex/skills/cookit-ios-development
rm ~/.codex/skills/cookit-mactools
rm ~/.codex/skills/cookit-ios-commands
```
