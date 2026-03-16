#!/usr/bin/env python3
"""Parse a Claude Code session JSONL file into unified session summary JSON."""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime

BUILD_PATTERNS = re.compile(
    r"\b(npm run build|yarn build|swift build|cargo build|make\b|gradle build|"
    r"go build|mvn compile|tsc\b|webpack|vite build|next build|pytest|"
    r"python.*-m\s+pytest|npm test|yarn test|swift test|cargo test)\b",
    re.IGNORECASE,
)


def parse_claude_session(filepath):
    """Parse a Claude Code JSONL file and return unified session summary dict."""
    session_id = None
    cwd = None
    branch = None
    model = None
    timestamps = []
    user_turns = 0
    assistant_msg_ids = set()
    total_input = 0
    total_output = 0
    cache_read = 0
    cache_create = 0
    tool_calls = Counter()
    tool_sequence = []
    files_read = set()
    files_edited = set()
    files_created = set()
    repeated_edits = Counter()
    bash_errors = 0
    build_attempts = 0
    build_failures = 0
    user_prompts = []
    # Track Bash tool_use IDs and their commands for result correlation
    bash_tool_uses = {}  # tool_use_id → command string

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            rtype = record.get("type")
            ts = record.get("timestamp")
            if ts:
                timestamps.append(ts)

            if not session_id and record.get("sessionId"):
                session_id = record["sessionId"]
            if not cwd and record.get("cwd"):
                cwd = record["cwd"]
            if not branch and record.get("gitBranch"):
                branch = record["gitBranch"]

            if rtype == "user":
                user_turns += 1
                msg = record.get("message", {})
                content = msg.get("content", "")
                text = _extract_user_text(content)
                if text and len(user_prompts) < 10:
                    user_prompts.append(text[:500])
                # Check tool_result blocks for Bash errors
                if isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") == "tool_result":
                            tool_use_id = block.get("tool_use_id", "")
                            result_text = _extract_tool_result_text(block)
                            is_error = block.get("is_error", False)
                            if tool_use_id in bash_tool_uses:
                                cmd = bash_tool_uses[tool_use_id]
                                if BUILD_PATTERNS.search(cmd):
                                    build_attempts += 1
                                    if is_error or _looks_like_error(result_text):
                                        build_failures += 1
                                elif is_error:
                                    bash_errors += 1
                                elif _looks_like_error(result_text):
                                    bash_errors += 1

            elif rtype == "assistant":
                msg = record.get("message", {})
                msg_id = msg.get("id")
                if msg_id:
                    assistant_msg_ids.add(msg_id)

                if not model and msg.get("model"):
                    model = msg["model"]

                usage = msg.get("usage", {})
                total_input += usage.get("input_tokens", 0)
                total_output += usage.get("output_tokens", 0)
                cache_read += usage.get("cache_read_input_tokens", 0)
                cache_create += usage.get("cache_creation_input_tokens", 0)

                for block in msg.get("content", []):
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_use":
                        tool_name = block.get("name", "")
                        tool_id = block.get("id", "")
                        tool_calls[tool_name] += 1
                        tool_sequence.append(tool_name)
                        inp = block.get("input", {})
                        _track_file_ops(
                            tool_name, inp,
                            files_read, files_edited, files_created,
                            repeated_edits
                        )
                        if tool_name == "Bash" and tool_id:
                            bash_tool_uses[tool_id] = inp.get("command", "")

    if not session_id:
        session_id = os.path.splitext(os.path.basename(filepath))[0]

    time_start = timestamps[0] if timestamps else None
    time_end = timestamps[-1] if timestamps else None
    duration_min = _calc_duration_min(time_start, time_end)

    cache_hit_rate = None
    total_all_input = total_input + cache_read
    if total_all_input > 0:
        cache_hit_rate = round(cache_read / total_all_input, 3)

    return {
        "session_id": session_id,
        "source": "claude-code",
        "project": os.path.basename(cwd) if cwd else None,
        "project_path": cwd,
        "branch": branch,
        "model": model,
        "time": {
            "start": time_start,
            "end": time_end,
            "duration_min": duration_min,
        },
        "turns": {
            "user": user_turns,
            "assistant": len(assistant_msg_ids),
        },
        "tokens": {
            "input": total_input,
            "output": total_output,
            "cache_read": cache_read,
            "cache_create": cache_create,
            "cache_hit_rate": cache_hit_rate,
        },
        "tools": {
            "distribution": dict(tool_calls),
            "total_calls": sum(tool_calls.values()),
            "sequence": tool_sequence,
        },
        "files": {
            "read": sorted(files_read),
            "edited": sorted(files_edited),
            "created": sorted(files_created),
        },
        "quality": {
            "repeated_edits": {f: c for f, c in repeated_edits.items() if c > 2},
            "bash_errors": bash_errors,
            "build_attempts": build_attempts,
            "build_failures": build_failures,
        },
        "session_dna": "mixed",
        "user_prompts": user_prompts,
        "task_summary": "",
        "corrections": [],
    }


def _extract_user_text(content):
    """Extract plain text from user message content."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    texts.append(block.get("text", ""))
            elif isinstance(block, str):
                texts.append(block)
        return " ".join(texts)
    return ""


def _extract_tool_result_text(block):
    """Extract text content from a tool_result block."""
    content = block.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(item.get("text", ""))
        return " ".join(texts)
    return ""


def _looks_like_error(text):
    """Check if tool result text indicates an error (exit code != 0)."""
    if not text:
        return False
    # Claude Code Bash tool results start with error info
    if "Exit code" in text and "Exit code 0" not in text:
        return True
    return False


def _track_file_ops(tool_name, inp, files_read, files_edited, files_created, repeated_edits):
    """Track file operations from tool calls."""
    if tool_name == "Read":
        path = inp.get("file_path")
        if path:
            files_read.add(path)
    elif tool_name == "Edit":
        path = inp.get("file_path")
        if path:
            files_edited.add(path)
            repeated_edits[path] += 1
    elif tool_name == "Write":
        path = inp.get("file_path")
        if path:
            files_created.add(path)


def _calc_duration_min(start_str, end_str):
    """Calculate duration in minutes between two ISO timestamps."""
    if not start_str or not end_str:
        return None
    try:
        start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        delta = (end - start).total_seconds() / 60
        return round(delta, 1)
    except (ValueError, TypeError):
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Parse a Claude Code session JSONL file into unified JSON"
    )
    parser.add_argument(
        "--input", required=True, help="Path to Claude Code session JSONL file"
    )
    parser.add_argument(
        "--output", default=None, help="Output JSON file (default: stdout)"
    )
    args = parser.parse_args()

    result = parse_claude_session(args.input)

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
