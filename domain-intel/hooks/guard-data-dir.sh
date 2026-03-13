#!/bin/bash
# domain-intel PreToolUse(Write) hook
# Guards against writing domain-intel data outside the configured data_dir
#
# Strategy: Only activate when BOTH conditions are true:
#   1. The file content contains domain-intel-specific markers
#   2. The path is NOT within the configured data_dir
# This avoids false positives on unrelated files with generic path patterns.

input=$(cat)

# Extract file_path and content preview from the tool input JSON
file_path=$(echo "$input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)
content=$(echo "$input" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('content','')[:800])" 2>/dev/null)

# If we couldn't extract the path, allow (not our concern)
if [ -z "$file_path" ]; then
  exit 0
fi

# Step 1: Check if the content contains domain-intel-specific markers
# These markers are unique to domain-intel output and won't appear in unrelated files
is_intel_data=false

case "$content" in
  *"[domain-intel]"*)           is_intel_data=true ;;
  *"Domain Intel Digest"*)      is_intel_data=true ;;
  *"selection_reason:"*)        is_intel_data=true ;;
  *"# Convergence Signals"*)    is_intel_data=true ;;
  *"# Trend Snapshot"*)         is_intel_data=true ;;
esac

# Also check if content has the specific frontmatter combo used by insight files
# (significance + domain + source together = very unlikely in non-intel files)
if [ "$is_intel_data" = false ]; then
  has_significance=$(echo "$content" | grep -c '^significance:' 2>/dev/null)
  has_domain=$(echo "$content" | grep -c '^domain:' 2>/dev/null)
  if [ "$has_significance" -gt 0 ] && [ "$has_domain" -gt 0 ]; then
    is_intel_data=true
  fi
fi

# If not domain-intel data, allow — this is the key change vs the old version.
# We no longer match on generic path patterns like /insights/ or /state.yaml.
if [ "$is_intel_data" = false ]; then
  exit 0
fi

# Step 2: It IS domain-intel data — verify it's going to the configured data_dir
CONFIG_FILE="$HOME/.claude/domain-intel.local.md"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "BLOCK: [domain-intel] Cannot write intel data — no config found. Run /intel setup first."
  exit 2
fi

# Extract data_dir from YAML frontmatter
data_dir=$(sed -n '/^---$/,/^---$/p' "$CONFIG_FILE" | grep '^data_dir:' | sed 's/data_dir: *//' | tr -d '"' | tr -d "'" | sed "s|^~|$HOME|")

if [ -z "$data_dir" ]; then
  echo "BLOCK: [domain-intel] Cannot write intel data — data_dir not configured. Run /intel setup."
  exit 2
fi

# Resolve data_dir to absolute path (handle symlinks and ..)
if [ -d "$data_dir" ]; then
  data_dir_resolved=$(cd "$data_dir" && pwd -P)
else
  # Directory doesn't exist yet — do best-effort expansion
  data_dir_resolved=$(echo "$data_dir" | sed "s|^~|$HOME|")
fi

# Resolve file_path's parent directory if possible
file_dir=$(dirname "$file_path")
if [ -d "$file_dir" ]; then
  file_path_resolved="$(cd "$file_dir" && pwd -P)/$(basename "$file_path")"
else
  file_path_resolved="$file_path"
fi

# Check if the resolved file_path starts with resolved data_dir
case "$file_path_resolved" in
  "$data_dir_resolved"/*)
    exit 0
    ;;
esac

# Also check unresolved paths as fallback
case "$file_path" in
  "$data_dir"/*)
    exit 0
    ;;
esac

echo "BLOCK: [domain-intel] Write blocked: $file_path is outside configured data_dir ($data_dir). Run /intel config to check settings."
exit 2
