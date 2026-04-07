#!/bin/bash
# SessionEnd hook (session-reflect): write lightweight session summary to ~/.claude/session-reflect/summaries/

SUMMARY_DIR="${HOME}/.claude/session-reflect/summaries"
mkdir -p "$SUMMARY_DIR"

# Find the most recently modified session JSONL file (current session)
SESSION_FILE=$(find "${HOME}/.claude/projects" -name "*.jsonl" -type f -mmin -2 2>/dev/null | head -1)

if [ -z "$SESSION_FILE" ] || [ ! -f "$SESSION_FILE" ]; then
  exit 0
fi

SESSION_ID=$(basename "$SESSION_FILE" .jsonl)
PROJECT_NAME=$(basename "$PWD")

# Extract lightweight summary stats using Python
python3 - "$SESSION_FILE" "$SESSION_ID" "$PROJECT_NAME" "$SUMMARY_DIR" << 'PYTHON_SCRIPT'
import json
import sys
from datetime import datetime
from pathlib import Path

session_file, session_id, project_name, summary_dir = sys.argv[1:]

summary = {
    "session_id": session_id,
    "project": project_name,
    "timestamp": datetime.now().isoformat() + "Z",
    "turns": {"user": 0, "assistant": 0},
    "tokens": {"input": 0, "output": 0, "cache_read": 0},
    "tools": {},
    "files": {"read": [], "edited": []},
    "session_dna": "mixed",
}

tool_sequence = []
files_read = set()
files_edited = set()
assistant_ids = set()

try:
    with open(session_file, "r") as f:
        for line in f:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            rec_type = record.get("type")
            if rec_type == "user":
                summary["turns"]["user"] += 1
            elif rec_type == "assistant":
                msg = record.get("message", {})
                msg_id = msg.get("id")
                if msg_id:
                    assistant_ids.add(msg_id)

                usage = msg.get("usage", {})
                if usage:
                    summary["tokens"]["input"] += usage.get("input_tokens", 0)
                    summary["tokens"]["output"] += usage.get("output_tokens", 0)
                    summary["tokens"]["cache_read"] += usage.get("cache_read_input_tokens", 0)

                content = msg.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_use":
                            tool_name = block.get("name", "")
                            if tool_name:
                                tool_sequence.append(tool_name)
                                summary["tools"][tool_name] = summary["tools"].get(tool_name, 0) + 1
                                inp = block.get("input", {})
                                if isinstance(inp, dict) and "file_path" in inp:
                                    path = inp["file_path"]
                                    if tool_name == "Read":
                                        files_read.add(path)
                                    elif tool_name in ("Edit", "Write"):
                                        files_edited.add(path)
except Exception:
    pass

summary["turns"]["assistant"] = len(assistant_ids)

# Cache hit rate
total_in = summary["tokens"]["input"] + summary["tokens"]["cache_read"]
if total_in > 0:
    summary["tokens"]["cache_hit_rate"] = round(summary["tokens"]["cache_read"] / total_in, 3)
else:
    summary["tokens"]["cache_hit_rate"] = 0

summary["files"]["read"] = sorted(files_read)[:20]
summary["files"]["edited"] = sorted(files_edited)[:20]

# Session DNA from tool distribution
total_tools = len(tool_sequence)
if total_tools == 0:
    summary["session_dna"] = "chat"
elif total_tools < 5:
    summary["session_dna"] = "chat"
else:
    read_pct = sum(1 for t in tool_sequence if t in ("Read", "Grep", "Glob")) / total_tools
    edit_pct = sum(1 for t in tool_sequence if t in ("Edit", "Write")) / total_tools
    if read_pct > 0.6:
        summary["session_dna"] = "explore"
    elif edit_pct > 0.4:
        summary["session_dna"] = "build"
    elif summary["tools"].get("Bash", 0) > 0:
        summary["session_dna"] = "fix"

output_path = Path(summary_dir) / f"{session_id}.json"
with open(output_path, "w") as f:
    json.dump(summary, f, indent=2)
PYTHON_SCRIPT
