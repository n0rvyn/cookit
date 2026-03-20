#!/usr/bin/env bash
# check-inspect-state.sh — SessionStart hook for linux-inspect v2
# Reports last inspection state and profile count if config exists.

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

# Extract fields from state YAML (flat key: value format)
last_run=$(grep "^last_run:" "$STATE_FILE" 2>/dev/null | sed 's/last_run: *"\?\([^"]*\)"\?/\1/' || echo "unknown")
fleet_score=$(grep "^fleet_score:" "$STATE_FILE" 2>/dev/null | sed 's/fleet_score: *//' || echo "?")
total_findings=$(grep "^total_findings:" "$STATE_FILE" 2>/dev/null | sed 's/total_findings: *//' || echo "?")
profile_count=$(grep "^profile_count:" "$STATE_FILE" 2>/dev/null | sed 's/profile_count: *//' || echo "0")
delta_new=$(grep "^delta_new:" "$STATE_FILE" 2>/dev/null | sed 's/delta_new: *//' || echo "0")
delta_resolved=$(grep "^delta_resolved:" "$STATE_FILE" 2>/dev/null | sed 's/delta_resolved: *//' || echo "0")

echo "[linux-inspect] Last: ${last_run} | Score: ${fleet_score}/100 | Findings: ${total_findings} | Profiles: ${profile_count} | Delta: +${delta_new} new, -${delta_resolved} resolved"
