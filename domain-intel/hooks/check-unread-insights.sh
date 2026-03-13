#!/bin/bash
# domain-intel SessionStart hook
# Checks config validity and reports unread insight count

CONFIG_FILE="$HOME/.claude/domain-intel.local.md"

# Check config exists
if [ ! -f "$CONFIG_FILE" ]; then
  echo "[domain-intel] Not configured. Run /intel setup to get started."
  exit 0
fi

# Extract data_dir from YAML frontmatter
data_dir=$(sed -n '/^---$/,/^---$/p' "$CONFIG_FILE" | grep '^data_dir:' | sed 's/data_dir: *//' | tr -d '"' | tr -d "'" | sed "s|^~|$HOME|")

# Check data_dir is set
if [ -z "$data_dir" ]; then
  echo "[domain-intel] data_dir not set. Run /intel setup to configure."
  exit 0
fi

# Check data_dir exists
if [ ! -d "$data_dir" ]; then
  echo "[domain-intel] data_dir $data_dir not found. Run /intel setup to fix."
  exit 0
fi

# Check state file for last scan
state_file="$data_dir/state.yaml"
last_scan="never"
if [ -f "$state_file" ]; then
  last_scan=$(grep '^last_scan:' "$state_file" | sed 's/last_scan: *//' | tr -d '"')
fi

if [ "$last_scan" = "never" ]; then
  echo "[domain-intel] Ready but no scans yet. Run /scan to start collecting."
  exit 0
fi

# Count unread insights
insights_dir="$data_dir/insights"
if [ ! -d "$insights_dir" ]; then
  exit 0
fi

unread_count=$(grep -rl 'read: false' "$insights_dir/" 2>/dev/null | wc -l | tr -d ' ')

if [ "$unread_count" -gt 0 ]; then
  echo "[domain-intel] $unread_count unread insight(s). Last scan: $last_scan. Use /intel for a briefing."
fi
