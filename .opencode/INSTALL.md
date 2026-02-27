# Installing Indie Toolkit for OpenCode

Enable Indie Toolkit skills in OpenCode via native skill discovery.

## Prerequisites

- OpenCode
- Git

## Installation (macOS/Linux)

1. Clone or update the repository:

```bash
if [ -d ~/.config/opencode/indie-toolkit/.git ]; then
  git -C ~/.config/opencode/indie-toolkit pull --ff-only
else
  git clone https://github.com/n0rvyn/indie-toolkit.git ~/.config/opencode/indie-toolkit
fi
```

2. Create skill source links:

```bash
mkdir -p ~/.config/opencode/skills
ln -sfn ~/.config/opencode/indie-toolkit/ios-development/skills ~/.config/opencode/skills/indie-toolkit-ios-development
ln -sfn ~/.config/opencode/indie-toolkit/mactools/skills ~/.config/opencode/skills/indie-toolkit-mactools
```

3. Restart OpenCode.

## Verify

```bash
ls -la ~/.config/opencode/skills/indie-toolkit-ios-development
ls -la ~/.config/opencode/skills/indie-toolkit-mactools
```

## Updating

```bash
git -C ~/.config/opencode/indie-toolkit pull --ff-only
```

If new skills were added in the repo, re-run the symlink commands once.

## Uninstall

```bash
rm ~/.config/opencode/skills/indie-toolkit-ios-development
rm ~/.config/opencode/skills/indie-toolkit-mactools
```
