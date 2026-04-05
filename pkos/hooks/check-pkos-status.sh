#!/bin/bash
# Show PKOS status on session start

VAULT="$HOME/Obsidian/PKOS"
STATE_DIR="$VAULT/.state"

if [ ! -d "$VAULT" ]; then
  exit 0
fi

# Count inbox items (quick check)
inbox_count=0

# Reminders count
rem_count=$(osascript -e 'tell application "Reminders" to return (count of (reminders of list "PKOS Inbox" whose completed is false))' 2>/dev/null || echo "0")
inbox_count=$((inbox_count + rem_count))

# Voice files count
voice_count=$(find "$HOME/Library/Mobile Documents/com~apple~CloudDocs/PKOS/voice" -name "*.m4a" -not -path "*/processed/*" 2>/dev/null | wc -l | tr -d '[:space:]')
inbox_count=$((inbox_count + voice_count))

# Recent vault activity
recent_notes=$(find "$VAULT"/{10-Knowledge,20-Ideas,50-References,80-MOCs} -name "*.md" -mtime -1 2>/dev/null | wc -l | tr -d '[:space:]')

# Latest health score
latest_lint=$(ls -t "$VAULT/70-Reviews"/lint-*.md 2>/dev/null | head -1)
health=""
if [ -n "$latest_lint" ]; then
  health=$(grep "^health_score:" "$latest_lint" 2>/dev/null | sed 's/health_score: *//')
fi

# Build status line
parts=()
if [ "$inbox_count" -gt 0 ]; then
  parts+=("inbox: ${inbox_count}")
fi
if [ "$recent_notes" -gt 0 ]; then
  parts+=("last 24h: +${recent_notes} notes")
fi
if [ -n "$health" ]; then
  parts+=("health: ${health}/100")
fi

if [ ${#parts[@]} -gt 0 ]; then
  IFS=", "
  echo "[pkos] ${parts[*]}"
fi
