#!/bin/bash
# Suggest /pkos skill when user prompt matches knowledge-related patterns
# Input: JSON on stdin with .prompt field (Claude Code hook convention)

input=$(cat)

prompt=$(echo "$input" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('prompt', ''))
except:
    print('')
" 2>/dev/null)

# Skip if user already typed a slash command
if echo "$prompt" | grep -q '^/'; then
  exit 0
fi

# Skip very short prompts
if [ ${#prompt} -lt 6 ]; then
  exit 0
fi

# Knowledge/vault related patterns
if echo "$prompt" | grep -qiE '知识|笔记|vault|obsidian|pkos|knowledge.?base|what.*know|我之前|看过|记过|inbox|收件箱'; then
  echo "[skill-hint] Related: /pkos — personal knowledge system"
  exit 0
fi

# Digest/review patterns
if echo "$prompt" | grep -qiE 'digest|摘要|review.*today|今日|日报|周报'; then
  echo "[skill-hint] Related: /pkos review — show today's wiki changes"
  exit 0
fi
