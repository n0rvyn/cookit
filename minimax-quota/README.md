# minimax-platform Plugin

MiniMax platform helper plugin focused on internal coding-plan quota checks.

## Install

```bash
/plugin install minimax-platform@indie-toolkit
```

## Skill

| Skill | Description |
|---|---|
| `/minimax-coding-plan` | Query MiniMax coding-plan remains and manage `HERTZ-SESSION` based auth |

## Authentication Boundary

This plugin is built around the live-verified auth path for the internal remains endpoint:

- Works with `HERTZ-SESSION`
- Fails with `status_code: 1004` and `cookie is missing, log in again` when the cookie is absent or invalid
- Does not claim username/password env login support
- Does not claim official refresh-token support

If you want automatic renewal, provide a command that can fetch a fresh `HERTZ-SESSION` from your local browser or automation flow.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `MINIMAX_GROUP_ID` | Yes | MiniMax group id used by the remains endpoint |
| `MINIMAX_HERTZ_SESSION` | No | Session cookie value; overrides cookie file |
| `MINIMAX_COOKIE_FILE` | No | File that stores `HERTZ-SESSION`; default is `~/.config/minimax/hertz-session.txt` |
| `MINIMAX_SESSION_COMMAND` | No | Command that prints a fresh `HERTZ-SESSION` or `HERTZ-SESSION=...` |
| `MINIMAX_OUTPUT` | No | Set to `json` for raw JSON output |

## Script

Installed via `/plugin install`, invoke the skill by description (e.g. "check MiniMax coding plan quota") — the skill resolves `SKILLS_ROOT` via `CLAUDE_PLUGIN_ROOT` and runs the script.

For repo-local development, the script lives at:

```bash
minimax-platform/skills/minimax-coding-plan/scripts/minimax_coding_plan.sh
```

Examples (from repo root):

```bash
export MINIMAX_GROUP_ID='2036327615073096267'
export MINIMAX_HERTZ_SESSION='your-session'

minimax-platform/skills/minimax-coding-plan/scripts/minimax_coding_plan.sh
minimax-platform/skills/minimax-coding-plan/scripts/minimax_coding_plan.sh --json
```
