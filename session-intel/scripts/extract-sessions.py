#!/usr/bin/env python3
"""Discover and list Claude Code and Codex session files with metadata."""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


def discover_claude_sessions(projects_dir, cutoff_ts):
    """Discover Claude Code session JSONL files newer than cutoff."""
    sessions = []
    projects_path = Path(projects_dir).expanduser()
    if not projects_path.is_dir():
        return sessions

    for project_dir in projects_path.iterdir():
        if not project_dir.is_dir():
            continue
        for jsonl_file in project_dir.glob("*.jsonl"):
            mtime = jsonl_file.stat().st_mtime
            if mtime < cutoff_ts:
                continue
            session_id = jsonl_file.stem
            meta = extract_claude_metadata(jsonl_file, session_id, project_dir.name)
            if meta:
                sessions.append(meta)
    return sessions


def extract_claude_metadata(filepath, session_id, project_dir_name):
    """Extract lightweight metadata from first few lines of a Claude Code session."""
    meta = {
        "session_id": session_id,
        "source": "claude-code",
        "file_path": str(filepath),
        "file_size_kb": filepath.stat().st_size // 1024,
        "project_dir": project_dir_name,
        "project_path": None,
        "branch": None,
        "timestamp": None,
    }
    try:
        with open(filepath, "r") as f:
            for i, line in enumerate(f):
                if i > 20:
                    break
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("cwd") and not meta["project_path"]:
                    meta["project_path"] = record["cwd"]
                if record.get("gitBranch") and not meta["branch"]:
                    meta["branch"] = record["gitBranch"]
                if record.get("timestamp") and not meta["timestamp"]:
                    meta["timestamp"] = record["timestamp"]
                if record.get("sessionId"):
                    meta["session_id"] = record["sessionId"]
    except (OSError, PermissionError):
        pass

    if not meta["timestamp"]:
        meta["timestamp"] = datetime.fromtimestamp(
            filepath.stat().st_mtime
        ).isoformat() + "Z"

    return meta


def discover_codex_sessions(sessions_dir, cutoff_ts):
    """Discover Codex session JSONL files newer than cutoff."""
    sessions = []
    sessions_path = Path(sessions_dir).expanduser()
    if not sessions_path.is_dir():
        return sessions

    cutoff_date = datetime.fromtimestamp(cutoff_ts)
    for year_dir in sessions_path.iterdir():
        if not year_dir.is_dir():
            continue
        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir():
                continue
            for day_dir in month_dir.iterdir():
                if not day_dir.is_dir():
                    continue
                try:
                    dir_date = datetime(
                        int(year_dir.name), int(month_dir.name), int(day_dir.name)
                    )
                    if dir_date < cutoff_date.replace(hour=0, minute=0, second=0):
                        continue
                except (ValueError, TypeError):
                    continue
                for jsonl_file in day_dir.glob("*.jsonl"):
                    meta = extract_codex_metadata(jsonl_file)
                    if meta:
                        sessions.append(meta)
    return sessions


def extract_codex_metadata(filepath):
    """Extract lightweight metadata from a Codex session file."""
    meta = {
        "session_id": None,
        "source": "codex",
        "file_path": str(filepath),
        "file_size_kb": filepath.stat().st_size // 1024,
        "project_dir": None,
        "project_path": None,
        "branch": None,
        "timestamp": None,
    }
    try:
        with open(filepath, "r") as f:
            for i, line in enumerate(f):
                if i > 10:
                    break
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("type") == "session_meta":
                    payload = record.get("payload", {})
                    meta["session_id"] = payload.get("id")
                    meta["project_path"] = payload.get("cwd")
                    if meta["project_path"]:
                        meta["project_dir"] = os.path.basename(meta["project_path"])
                    meta["timestamp"] = payload.get("timestamp")
                    git_info = payload.get("git", {})
                    if isinstance(git_info, dict):
                        meta["branch"] = git_info.get("branch")
                    break
    except (OSError, PermissionError):
        pass

    if not meta["session_id"]:
        meta["session_id"] = filepath.stem
    if not meta["timestamp"]:
        meta["timestamp"] = datetime.fromtimestamp(
            filepath.stat().st_mtime
        ).isoformat() + "Z"

    return meta


def main():
    parser = argparse.ArgumentParser(
        description="Discover Claude Code and Codex session files"
    )
    parser.add_argument(
        "--claude-projects",
        default="~/.claude/projects/",
        help="Path to Claude projects directory (default: ~/.claude/projects/)",
    )
    parser.add_argument(
        "--codex-sessions",
        default="~/.codex/sessions/",
        help="Path to Codex sessions directory (default: ~/.codex/sessions/)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)",
    )
    parser.add_argument(
        "--project",
        default=None,
        help="Filter by project name (substring match)",
    )
    parser.add_argument(
        "--source",
        choices=["claude-code", "codex", "all"],
        default="all",
        help="Filter by source (default: all)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    args = parser.parse_args()

    cutoff = datetime.now() - timedelta(days=args.days)
    cutoff_ts = cutoff.timestamp()

    sessions = []
    if args.source in ("claude-code", "all"):
        sessions.extend(discover_claude_sessions(args.claude_projects, cutoff_ts))
    if args.source in ("codex", "all"):
        sessions.extend(discover_codex_sessions(args.codex_sessions, cutoff_ts))

    if args.project:
        sessions = [
            s for s in sessions
            if args.project.lower() in (s.get("project_dir") or "").lower()
            or args.project.lower() in (s.get("project_path") or "").lower()
        ]

    sessions.sort(key=lambda s: s.get("timestamp") or "", reverse=True)

    if args.format == "text":
        output_lines = []
        for s in sessions:
            ts = (s.get("timestamp") or "")[:19]
            src = s["source"][:6]
            proj = (s.get("project_dir") or "?")[:25]
            size = s.get("file_size_kb", 0)
            output_lines.append(f"{ts}  {src:6s}  {proj:25s}  {size:>6d}KB  {s['session_id']}")
        output = "\n".join(output_lines)
    else:
        output = json.dumps(sessions, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
