---
name: wechat-login
description: "Connect to WeChat for the wechat-bridge plugin. Guides user through QR scan login and channel setup. Use when user says 'login to wechat', 'connect wechat', 'wechat login', or asks about WeChat bridge. Keywords: wechat, login, connect, QR, scan, bridge, channel."
allowed-tools: Bash(node*login-cli*) Bash(ls*/.adam/wechat*) Bash(cat*/.adam/wechat*)
---

# WeChat Bridge Login & Setup

## Step 1: Check Current State

First, check if the user already has a saved session:

```bash
ls ~/.adam/wechat/*.json 2>/dev/null
```

- If files exist: the user is already logged in. Skip to Step 3.
- If no files: proceed to Step 2.

## Step 2: QR Login

Run the login command:

```bash
node "${CLAUDE_PLUGIN_ROOT}/dist/login-cli.js" login
```

### Options

| Flag | Env Var | Default | Description |
|------|---------|---------|-------------|
| `--api-base-url` | `WECHAT_API_BASE_URL` | `https://ilinkai.weixin.qq.com` | iLink Bot API base URL |
| `--channel-id` | `WECHAT_CHANNEL_ID` | `default` | Channel identifier |
| `--route-tag` | `WECHAT_ROUTE_TAG` | (none) | API routing tag |
| `--force` | — | — | Re-login even if session exists |

The command outputs a QR code URL. Tell the user:
1. Open WeChat on your phone
2. Scan the QR code (use WeChat's scan feature)
3. Confirm on your phone

Wait for the command to complete (up to 5 minutes).

## Step 3: Guide Channel Setup

After login is confirmed (or if already logged in), tell the user:

> WeChat login is complete. To enable the WeChat bridge, you need to restart Claude Code with the `--channels` flag:
>
> ```
> claude --channels plugin:wechat-bridge@indie-toolkit
> ```
>
> After that, you can:
> - **Approve tool requests from WeChat**: Claude will send permission requests to your WeChat, reply "yes/no + request ID" to approve or deny
> - **Send messages from WeChat into this session**: Any message you send from WeChat appears here
> - **Claude can reply to your WeChat**: Claude uses the `reply` tool to message you back
>
> Note: `--channels` is a Claude Code research preview feature.

## Important

- This skill handles login only. The MCP channel server starts automatically when Claude Code launches with `--channels plugin:wechat-bridge@indie-toolkit`.
- If the user is already in a `--channels` session, login is sufficient; no restart needed.
- Credentials are stored at `~/.adam/wechat/`. Delete to force re-login, or use `--force`.
