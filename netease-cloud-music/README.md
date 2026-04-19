# netease-cloud-music Plugin

NetEase Cloud Music helper plugin for cloud-drive uploads and cookie-based login flows.

## Install

```bash
/plugin install netease-cloud-music@indie-toolkit
```

## Why This Plugin Uses `ncmctl`

This plugin is built around the maintained `chaunsin/netease-cloud-music` CLI instead of reimplementing reverse-engineered requests:

- `Binaryify/NeteaseCloudMusicApi` is historically important, but the main repository was archived on 2024-04-16
- `pyncm` is still useful as a Python library, but cloud upload is exposed as low-level upload primitives
- `ncmctl` already wraps login, Cookie import, CookieCloud import, and cloud upload into one CLI

For day-to-day use, `ncmctl` is the cleaner operational surface.

## Skill

| Skill | Description |
|---|---|
| `/netease-cloud-music` | Use `ncmctl` for login, Cookie/CookieCloud import, and NetEase cloud-drive upload |

## Prerequisites

Install `ncmctl` first.

Upstream install methods verified from the maintained README:

```bash
go install github.com/chaunsin/netease-cloud-music/cmd/ncmctl@latest
```

Or download a prebuilt binary from:

```text
https://github.com/chaunsin/netease-cloud-music/releases
```

## Supported Login Flows

- Cookie import
- Cookie file import
- CookieCloud import

QR login is documented upstream as currently blocked by NetEase risk control, so this plugin does not recommend it as the primary path.

## Examples

Installed via `/plugin install`, invoke the skill by description (e.g. "帮我上传 music.mp3 到网易云云盘") — the skill resolves its script paths via the render-time `${CLAUDE_SKILL_DIR}` substitution and runs the wrapper.

For repo-local development, the scripts can be called directly from this repo's root:

```bash
netease-cloud-music/skills/netease-cloud-music/scripts/netease_cloud_music.sh login cookie -f cookie.txt
netease-cloud-music/skills/netease-cloud-music/scripts/netease_cloud_music.sh login cookiecloud -u user -p pass -s http://127.0.0.1:8088
netease-cloud-music/skills/netease-cloud-music/scripts/netease_cloud_music.sh cloud '/path/to/music.mp3'
netease-cloud-music/skills/netease-cloud-music/scripts/netease_cloud_music.sh cloud '/path/to/music/'
```
