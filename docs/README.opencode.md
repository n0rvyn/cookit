# Cookit for OpenCode

OpenCode does not use Claude marketplace metadata directly.

Use native OpenCode skill loading by cloning this repo and linking skill folders.

## Quick Install

Tell OpenCode:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/n0rvyn/cookit/main/.opencode/INSTALL.md
```

## Update

```bash
git -C ~/.config/opencode/cookit pull --ff-only
```

If new skills were added, re-run the symlink step from `.opencode/INSTALL.md`.
