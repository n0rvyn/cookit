#!/bin/bash
# UserPromptSubmit hook: match user input and suggest relevant skills.
# Injects a one-line suggestion as context. Max 1 suggestion per prompt.

input=$(cat)

# Extract user prompt
prompt=$(echo "$input" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('prompt', ''))
except:
    print('')
" 2>/dev/null)

# Skip if user is already invoking a slash command
if echo "$prompt" | grep -q '^/'; then
  exit 0
fi

# Skip very short prompts (greetings, yes/no)
if [ ${#prompt} -lt 6 ]; then
  exit 0
fi

# Lowercase for matching
lower=$(echo "$prompt" | tr '[:upper:]' '[:lower:]')

# Pattern → skill mapping (first match wins)
if echo "$lower" | grep -qE 'commit|提交|save progress'; then
  echo "[skill-hint] Related: /commit — analyzes changes and commits with conventional format"
elif echo "$lower" | grep -qE 'bug|报错|crash|stack.?trace|fix.*error|error.*fix'; then
  echo "[skill-hint] Related: /fix-bug — systematic diagnosis through reproduction and hypothesis"
elif echo "$lower" | grep -qE 'write.*plan|计划|implementation plan'; then
  echo "[skill-hint] Related: /write-plan — creates implementation plan with bite-size tasks"
elif echo "$lower" | grep -qE 'brainstorm|创意|explore.*idea|头脑风暴'; then
  echo "[skill-hint] Related: /brainstorm — explores intent, requirements and design before implementation"
elif echo "$lower" | grep -qE 'design.*prompt|stitch.*prompt|figma.*prompt|generate.*prompt.*design|设计提示词|生成.*prompt'; then
  echo "[skill-hint] Related: /generate-design-prompt — generates Stitch/Figma prompts from project features"
elif echo "$lower" | grep -qE 'design.*prototype|prototype.*design|understand.*design|analyze.*design|stitch.*design|figma.*design|design.*analysis|设计原型|分析设计|理解设计'; then
  echo "[skill-hint] Related: /understand-design — analyzes design prototypes with dual-channel image+code understanding"
elif echo "$lower" | grep -qE 'phase|阶段|next phase|run.phase'; then
  echo "[skill-hint] Related: /run-phase — orchestrates plan-execute-review cycle"
elif echo "$lower" | grep -qE 'handoff|交接|continue.*session|session.*transfer'; then
  echo "[skill-hint] Related: /handoff — generates cold-start prompt for session transfer"
elif echo "$lower" | grep -qE 'crystal|crystallize|固化.*决策|决策.*结晶|结晶|settle.*decision|lock.*decision'; then
  echo "[skill-hint] Related: /crystallize — locks settled decisions into a crystal file before planning"
elif echo "$lower" | grep -qE 'design.*decision|设计决策|tradeoff|trade.off'; then
  echo "[skill-hint] Related: /design-decision — analyzes trade-offs between approaches"
elif echo "$lower" | grep -qE 'lesson|教训|踩坑|pitfall'; then
  echo "[skill-hint] Related: /collect-lesson — extracts structured lesson to knowledge base"
elif echo "$lower" | grep -qE 'kickoff|新项目|init.*project|project.*init'; then
  echo "[skill-hint] Related: /project-kickoff — guided iOS project initialization"
elif echo "$lower" | grep -qE 'dev.?guide|开发指南|development guide'; then
  echo "[skill-hint] Related: /write-dev-guide — creates phased development guide"
elif echo "$lower" | grep -qE 'review.*(code|impl)|代码审查|审查.*实现'; then
  echo "[skill-hint] Related: /execution-review — plan-vs-code verification + iOS scan"
fi

exit 0
