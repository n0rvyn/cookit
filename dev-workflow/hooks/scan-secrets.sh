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
if echo "$added_lines" | grep -qE -- '-----BEGIN.*(RSA|DSA|EC|OPENSSH|PGP).*PRIVATE KEY-----'; then
  matches="${matches}
  - Private key"
fi

# Password/secret/token assignments — entropy-aware detection
# Uses python3 (already a dependency for JSON parsing above) for multi-layer filtering:
#   1. Keyword presence  2. Skip type annotations  3. Extract quoted value
#   4. Min length 12     5. Safe-value patterns    6. Shannon entropy >= 3.5
credential_hits=$(echo "$added_lines" | python3 -c "
import sys, re, math

def entropy(s):
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    length = len(s)
    return -sum((count/length) * math.log2(count/length) for count in freq.values())

keyword_re = re.compile(
    r'(password|passwd|secret|token|api_key|apikey|api[._]key|auth_token|access_token|bearer)',
    re.IGNORECASE
)
value_re = re.compile(r'''(?:=|:)\s*[\"']([^\"']{2,})[\"']''')
safe_value_re = re.compile(
    r'(test|mock|fake|dummy|sample|demo|example|changeme|placeholder|xxx|your_|process\.env|\.env|\\\$\{|type=|TODO|FIXME)',
    re.IGNORECASE
)
schema_re = re.compile(
    r'(interface\s|type\s|:\s*(string|number|boolean)|typeof|PropTypes|@param|@type)',
    re.IGNORECASE
)

ENTROPY_THRESHOLD = 3.5
MIN_LENGTH = 12

for line in sys.stdin:
    line = line.rstrip('\n')
    if not keyword_re.search(line):
        continue
    if schema_re.search(line):
        continue
    m = value_re.search(line)
    if not m:
        continue
    value = m.group(1)
    if len(value) < MIN_LENGTH:
        continue
    if safe_value_re.search(value):
        continue
    if entropy(value) < ENTROPY_THRESHOLD:
        continue
    print(line.lstrip('+').strip())
" 2>/dev/null)

if [ -n "$credential_hits" ]; then
  matches="${matches}
  - Hardcoded credential assignment:"
  while IFS= read -r hit_line; do
    matches="${matches}
      ${hit_line}"
  done <<< "$credential_hits"
fi

if [ -n "$matches" ]; then
  printf "Blocked: secrets detected in staged content:%s\n" "$matches" >&2
  echo "Remove secrets and use environment variables or a secret manager." >&2
  exit 2
fi

exit 0
