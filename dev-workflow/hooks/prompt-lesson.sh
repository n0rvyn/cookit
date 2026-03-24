#!/bin/bash
# SessionEnd hook: prompt lesson collection if session had significant work

# Check if git is available and we're in a repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  exit 0
fi

# Check for uncommitted changes
stat_output=$(git diff --stat HEAD 2>/dev/null)
if [ -n "$stat_output" ]; then
  echo "本次 session 有值得记录的 lesson 吗？（/collect-lesson）"
  exit 0
fi

# No uncommitted changes; check recent commits (last 2 hours as session proxy)
recent=$(git log --since="2 hours ago" --oneline 2>/dev/null | wc -l | tr -d ' ')
if [ "$recent" -ge 3 ]; then
  echo "本次 session 有值得记录的 lesson 吗？（/collect-lesson）"
fi
