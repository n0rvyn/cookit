#!/usr/bin/env python3
"""Correlate parsed sessions with git commits by cwd, branch, and time window."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta


def correlate_sessions(session_files):
    """Match sessions to git commits by project path, branch, and time window.

    Args:
        session_files: list of file paths to parsed session JSON files,
                      or list of parsed session dicts

    Returns:
        dict mapping session_id → list of commit hashes
    """
    sessions = []
    for item in session_files:
        if isinstance(item, dict):
            sessions.append(item)
        elif isinstance(item, str):
            path = item
            if os.path.isdir(path):
                for fname in os.listdir(path):
                    if fname.endswith(".json"):
                        fpath = os.path.join(path, fname)
                        with open(fpath, "r") as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                sessions.extend(data)
                            else:
                                sessions.append(data)
            else:
                with open(path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        sessions.extend(data)
                    else:
                        sessions.append(data)

    mapping = {}
    for session in sessions:
        session_id = session.get("session_id")
        if not session_id:
            continue

        project_path = session.get("project_path")
        if not project_path or not os.path.isdir(project_path):
            mapping[session_id] = []
            continue

        git_dir = os.path.join(project_path, ".git")
        if not os.path.exists(git_dir):
            mapping[session_id] = []
            continue

        time_info = session.get("time", {})
        start = time_info.get("start")
        end = time_info.get("end")
        branch = session.get("branch")

        commits = _get_commits_in_window(project_path, start, end, branch)
        mapping[session_id] = commits

    return mapping


def _get_commits_in_window(project_path, start_str, end_str, branch=None):
    """Get commit hashes in a time window for a git repo."""
    cmd = ["git", "-C", project_path, "log", "--format=%H"]

    if start_str:
        cmd.extend(["--since", start_str])
    if end_str:
        try:
            end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            end_padded = end_dt + timedelta(minutes=5)
            cmd.extend(["--until", end_padded.isoformat()])
        except (ValueError, TypeError):
            pass

    if branch:
        cmd.append(branch)

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            if branch:
                cmd_fallback = [c for c in cmd if c != branch]
                result = subprocess.run(
                    cmd_fallback, capture_output=True, text=True, timeout=10
                )
                if result.returncode != 0:
                    return []
            else:
                return []
        commits = [h.strip() for h in result.stdout.strip().split("\n") if h.strip()]
        return commits
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Correlate sessions with git commits"
    )
    parser.add_argument(
        "--sessions",
        nargs="+",
        required=True,
        help="Paths to parsed session JSON files",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON file (default: stdout)",
    )
    args = parser.parse_args()

    mapping = correlate_sessions(args.sessions)

    output = json.dumps(mapping, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
