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
ln -sfn ~/.config/opencode/indie-toolkit/dev-workflow/skills ~/.config/opencode/skills/indie-toolkit-dev-workflow
ln -sfn ~/.config/opencode/indie-toolkit/apple-dev/skills ~/.config/opencode/skills/indie-toolkit-apple-dev
ln -sfn ~/.config/opencode/indie-toolkit/mactools/skills ~/.config/opencode/skills/indie-toolkit-mactools
ln -sfn ~/.config/opencode/indie-toolkit/product-lens/skills ~/.config/opencode/skills/indie-toolkit-product-lens
ln -sfn ~/.config/opencode/indie-toolkit/skill-master/skills ~/.config/opencode/skills/indie-toolkit-skill-master
ln -sfn ~/.config/opencode/indie-toolkit/skill-audit/skills ~/.config/opencode/skills/indie-toolkit-skill-audit
ln -sfn ~/.config/opencode/indie-toolkit/domain-intel/skills ~/.config/opencode/skills/indie-toolkit-domain-intel
ln -sfn ~/.config/opencode/indie-toolkit/session-reflect/skills ~/.config/opencode/skills/indie-toolkit-session-reflect
ln -sfn ~/.config/opencode/indie-toolkit/youtube-scout/skills ~/.config/opencode/skills/indie-toolkit-youtube-scout
ln -sfn ~/.config/opencode/indie-toolkit/pkos/skills ~/.config/opencode/skills/indie-toolkit-pkos
ln -sfn ~/.config/opencode/indie-toolkit/wechat-bridge/skills ~/.config/opencode/skills/indie-toolkit-wechat-bridge
ln -sfn ~/.config/opencode/indie-toolkit/health-insights/skills ~/.config/opencode/skills/indie-toolkit-health-insights
ln -sfn ~/.config/opencode/indie-toolkit/minimax-platform/skills ~/.config/opencode/skills/indie-toolkit-minimax-platform
ln -sfn ~/.config/opencode/indie-toolkit/netease-cloud-music/skills ~/.config/opencode/skills/indie-toolkit-netease-cloud-music
```

3. Restart OpenCode.

## Verify

```bash
ls -la ~/.config/opencode/skills/indie-toolkit-dev-workflow
ls -la ~/.config/opencode/skills/indie-toolkit-apple-dev
ls -la ~/.config/opencode/skills/indie-toolkit-mactools
ls -la ~/.config/opencode/skills/indie-toolkit-product-lens
ls -la ~/.config/opencode/skills/indie-toolkit-skill-master
ls -la ~/.config/opencode/skills/indie-toolkit-skill-audit
ls -la ~/.config/opencode/skills/indie-toolkit-domain-intel
ls -la ~/.config/opencode/skills/indie-toolkit-session-reflect
ls -la ~/.config/opencode/skills/indie-toolkit-youtube-scout
ls -la ~/.config/opencode/skills/indie-toolkit-pkos
ls -la ~/.config/opencode/skills/indie-toolkit-wechat-bridge
ls -la ~/.config/opencode/skills/indie-toolkit-health-insights
ls -la ~/.config/opencode/skills/indie-toolkit-minimax-platform
ls -la ~/.config/opencode/skills/indie-toolkit-netease-cloud-music
```

## Updating

```bash
git -C ~/.config/opencode/indie-toolkit pull --ff-only
```

If new skills were added in the repo, re-run the symlink commands once.

## Uninstall

```bash
rm ~/.config/opencode/skills/indie-toolkit-dev-workflow
rm ~/.config/opencode/skills/indie-toolkit-apple-dev
rm ~/.config/opencode/skills/indie-toolkit-mactools
rm ~/.config/opencode/skills/indie-toolkit-product-lens
rm ~/.config/opencode/skills/indie-toolkit-skill-master
rm ~/.config/opencode/skills/indie-toolkit-skill-audit
rm ~/.config/opencode/skills/indie-toolkit-domain-intel
rm ~/.config/opencode/skills/indie-toolkit-session-reflect
rm ~/.config/opencode/skills/indie-toolkit-youtube-scout
rm ~/.config/opencode/skills/indie-toolkit-pkos
rm ~/.config/opencode/skills/indie-toolkit-wechat-bridge
rm ~/.config/opencode/skills/indie-toolkit-health-insights
rm ~/.config/opencode/skills/indie-toolkit-minimax-platform
rm ~/.config/opencode/skills/indie-toolkit-netease-cloud-music
```
