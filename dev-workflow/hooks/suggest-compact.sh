#!/bin/bash
# Stop hook: suggest context compaction when tool call count is high
# and workflow is at a phase transition point.

input=$(cat)

# Prevent infinite loops — if this hook already triggered, exit immediately
stop_active=$(echo "$input" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('stop_hook_active', False))
except:
    print('False')
" 2>/dev/null)

if [ "$stop_active" = "True" ]; then
  exit 0
fi

# Extract transcript path
transcript_path=$(echo "$input" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('transcript_path', ''))
except:
    print('')
" 2>/dev/null)

if [ -z "$transcript_path" ] || [ ! -f "$transcript_path" ]; then
  exit 0
fi

# Count tool calls in transcript
tool_count=$(grep -c '"tool_use"' "$transcript_path" 2>/dev/null || echo "0")

# Read last suggested count
state_file=".claude/compact-suggested-at"
last_suggested=0
if [ -f "$state_file" ]; then
  last_suggested=$(cat "$state_file" 2>/dev/null || echo "0")
fi

delta=$((tool_count - last_suggested))

# Not enough tool calls since last suggestion
if [ "$delta" -lt 50 ]; then
  exit 0
fi

# Check if at a phase transition (good compaction point)
workflow_state=".claude/dev-workflow-state.yml"
at_transition=false

if [ -f "$workflow_state" ]; then
  phase_step=$(grep '^phase_step:' "$workflow_state" | sed 's/phase_step: *//')
  if [ "$phase_step" = "review" ] || [ "$phase_step" = "done" ]; then
    at_transition=true
  fi
fi

# Suggest if at transition, or if absolute count is very high
if [ "$at_transition" = true ] || [ "$tool_count" -gt 80 ]; then
  mkdir -p .claude
  echo "$tool_count" > "$state_file"
  echo "[dev-workflow] ${tool_count} tool calls this session (${delta} since last checkpoint). Consider running /compact to free context before continuing."
fi

exit 0
