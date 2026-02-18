#!/bin/bash
# Protect .pbxproj and .xcworkspace files from direct editing.
# Used as a PreToolUse hook for Edit/Write tools.
# Reads tool input JSON from stdin, checks file_path.

input=$(cat)

file_path=$(echo "$input" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    path = data.get('tool_input', {}).get('file_path', '')
    print(path)
except:
    print('')
" 2>/dev/null)

if echo "$file_path" | grep -qE '\.(pbxproj|xcworkspace)'; then
    echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Direct editing of .pbxproj/.xcworkspace files is prohibited. Use Xcode or xcodebuild to manage project structure."}}'
else
    exit 0
fi
