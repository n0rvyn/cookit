#!/usr/bin/env bash
# check-inspect-state.sh — SessionStart hook for linux-inspect
# Reports last inspection state if config exists in the current directory.

set -euo pipefail

CONFIG_FILE="./inspect-config.yaml"
STATE_FILE="./.inspect-state.yaml"

# Only activate if this directory has a linux-inspect config
if [[ ! -f "$CONFIG_FILE" ]]; then
    exit 0
fi

if [[ ! -f "$STATE_FILE" ]]; then
    echo "[linux-inspect] Config found but no inspection has been run yet. Use /inspect to start."
    exit 0
fi

# Extract key fields from state
last_run=$(grep "^last_run:" "$STATE_FILE" 2>/dev/null | sed 's/last_run: *"\?\([^"]*\)"\?/\1/' || echo "unknown")
fleet_score=$(grep "^fleet_score:" "$STATE_FILE" 2>/dev/null | sed 's/fleet_score: *//' || echo "?")
total_findings=$(grep "^total_findings:" "$STATE_FILE" 2>/dev/null | sed 's/total_findings: *//' || echo "?")

echo "[linux-inspect] Last inspection: ${last_run} | Score: ${fleet_score}/100 | Findings: ${total_findings}. Use /inspect to re-run."
