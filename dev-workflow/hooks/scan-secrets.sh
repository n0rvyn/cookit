#!/bin/bash
# PreToolUse(Bash) hook: scan staged git content for secrets before commit.
# Blocks the commit if secrets are detected. Passes through all non-commit commands.

input=$(cat)

# Extract command from tool input JSON
command=$(echo "$input" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('tool_input', {}).get('command', ''))
except:
    print('')
" 2>/dev/null)

# Only intercept git commit commands
if ! echo "$command" | grep -q 'git commit'; then
  exit 0
fi

# Scan staged content for secrets
staged=$(git diff --cached 2>/dev/null)
if [ -z "$staged" ]; then
  exit 0
fi

# Secret patterns (added lines only)
added_lines=$(echo "$staged" | grep '^+' | grep -v '^+++')

matches=""

# AWS access keys
if echo "$added_lines" | grep -qE 'AKIA[0-9A-Z]{16}'; then
  matches="${matches}
  - AWS access key (AKIA...)"
fi

# Common token prefixes
if echo "$added_lines" | grep -qE '(sk-[a-zA-Z0-9]{20,}|pk_live_|ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9]{22,})'; then
  matches="${matches}
  - API token (sk-/pk_live_/ghp_/gho_/github_pat_)"
fi

# Private keys
if echo "$added_lines" | grep -qE '-----BEGIN.*(RSA|DSA|EC|OPENSSH|PGP).*PRIVATE KEY-----'; then
  matches="${matches}
  - Private key"
fi

# Password/secret assignments
if echo "$added_lines" | grep -qiE '(password|secret|token|api_key|apikey|api\.key)[[:space:]]*[=:][[:space:]]*["'"'"'][^[:space:]]{8,}'; then
  matches="${matches}
  - Hardcoded credential assignment"
fi

if [ -n "$matches" ]; then
  printf "Blocked: secrets detected in staged content:%s\n" "$matches" >&2
  echo "Remove secrets and use environment variables or a secret manager." >&2
  exit 2
fi

exit 0
