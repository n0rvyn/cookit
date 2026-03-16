#!/usr/bin/env python3
"""Build a session index JSON file from Claude Code and Codex session data."""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add scripts dir to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from parse_claude_session import parse_claude_session
from parse_codex_session import parse_codex_session

INDEX_SCHEMA_FIELDS = [
    "session_id", "source", "file_path", "project", "project_path", "branch", "model",
    "time", "turns", "tokens", "tools", "files", "quality",
    "session_dna", "user_prompts", "task_summary", "corrections", "emotion_signals",
]


def build_index(days=30, project_filter=None, output_path=None,
                claude_projects="~/.claude/projects/",
                codex_sessions="~/.codex/sessions/"):
    """Build session index from discovered and parsed sessions.

    Returns:
        dict with _index_meta and sessions array
    """
    if output_path is None:
        output_path = os.path.expanduser("~/.claude/session-intel/index.json")

    cutoff = datetime.now() - timedelta(days=days)
    cutoff_ts = cutoff.timestamp()

    # Stage 1: Discover sessions (lightweight metadata)
    discovered = _discover_all(claude_projects, codex_sessions, cutoff_ts, project_filter)

    # Stage 2: Parse each session
    parsed_sessions = []
    for meta in discovered:
        try:
            filepath = meta["file_path"]
            source = meta["source"]
            if source == "claude-code":
                summary = parse_claude_session(filepath)
            elif source == "codex":
                summary = parse_codex_session(filepath)
            else:
                continue
            # Carry file_path from discovery metadata
            summary["file_path"] = filepath
            parsed_sessions.append(summary)
        except Exception:
            continue

    # Stage 3: Enrich from /retro data (DP-004: B+C strategy)
    retro_enrichments = _load_retro_enrichments()
    for session in parsed_sessions:
        sid = session.get("session_id", "")
        if sid in retro_enrichments:
            enriched = retro_enrichments[sid]
            if enriched.get("task_summary"):
                session["task_summary"] = enriched["task_summary"]
            if enriched.get("session_dna") and enriched["session_dna"] != "mixed":
                session["session_dna"] = enriched["session_dna"]
            if enriched.get("corrections"):
                session["corrections"] = enriched["corrections"]
            if enriched.get("emotion_signals"):
                session["emotion_signals"] = enriched["emotion_signals"]

    # Build index
    index = {
        "_index_meta": {
            "built_at": datetime.now().isoformat(),
            "session_count": len(parsed_sessions),
            "days_covered": days,
        },
        "sessions": parsed_sessions,
    }

    # Write
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    return index


def get_index_age(index_path=None):
    """Returns hours since index was last rebuilt, or None if no index."""
    if index_path is None:
        index_path = os.path.expanduser("~/.claude/session-intel/index.json")
    if not os.path.exists(index_path):
        return None
    try:
        with open(index_path) as f:
            data = json.load(f)
        built_at = data.get("_index_meta", {}).get("built_at")
        if not built_at:
            return None
        built_dt = datetime.fromisoformat(built_at)
        age_hours = (datetime.now() - built_dt).total_seconds() / 3600
        return round(age_hours, 1)
    except (json.JSONDecodeError, ValueError, OSError):
        return None


def _discover_all(claude_projects, codex_sessions, cutoff_ts, project_filter):
    """Discover session files from both sources."""
    sessions = []
    claude_path = Path(claude_projects).expanduser()
    codex_path = Path(codex_sessions).expanduser()

    # Claude Code sessions
    if claude_path.is_dir():
        for project_dir in claude_path.iterdir():
            if not project_dir.is_dir():
                continue
            if project_filter and project_filter.lower() not in project_dir.name.lower():
                continue
            for jsonl_file in project_dir.glob("*.jsonl"):
                if jsonl_file.stat().st_mtime < cutoff_ts:
                    continue
                sessions.append({
                    "file_path": str(jsonl_file),
                    "source": "claude-code",
                    "session_id": jsonl_file.stem,
                })

    # Codex sessions
    if codex_path.is_dir():
        cutoff_date = datetime.fromtimestamp(cutoff_ts)
        for year_dir in codex_path.iterdir():
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
                        sid = jsonl_file.stem
                        # Extract session ID from Codex filename pattern
                        match = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", sid)
                        if match:
                            sid = match.group(1)
                        sessions.append({
                            "file_path": str(jsonl_file),
                            "source": "codex",
                            "session_id": sid,
                        })

    return sessions


def _load_retro_enrichments():
    """Load enriched session data from past /retro runs.

    Checks two sources:
    1. ~/.claude/retro/enriched/*.json — per-session enriched JSON saved by /retro
    2. Falls back to empty if no enriched data available

    Returns dict of session_id → {task_summary, session_dna, corrections}.

    Note: This requires /retro to save enriched per-session data as JSON.
    Until Phase 7 adds SessionEnd hook auto-enrichment, coverage depends on
    how often the user runs /retro.
    """
    enrichments = {}

    # Check for enriched JSON files (saved by /retro skill)
    enriched_dir = os.path.expanduser("~/.claude/retro/enriched")
    if os.path.isdir(enriched_dir):
        for fname in os.listdir(enriched_dir):
            if not fname.endswith(".json"):
                continue
            filepath = os.path.join(enriched_dir, fname)
            try:
                with open(filepath) as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for entry in data:
                        sid = entry.get("session_id")
                        if sid:
                            enrichments[sid] = {
                                "task_summary": entry.get("task_summary", ""),
                                "session_dna": entry.get("session_dna", "mixed"),
                                "corrections": entry.get("corrections", []),
                            }
                elif isinstance(data, dict) and data.get("session_id"):
                    enrichments[data["session_id"]] = {
                        "task_summary": data.get("task_summary", ""),
                        "session_dna": data.get("session_dna", "mixed"),
                        "corrections": data.get("corrections", []),
                        "emotion_signals": data.get("emotion_signals", []),
                    }
            except (json.JSONDecodeError, OSError, PermissionError):
                continue

    return enrichments


def main():
    parser = argparse.ArgumentParser(
        description="Build session index from Claude Code and Codex data"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output index file (default: ~/.claude/session-intel/index.json)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to include (default: 30)",
    )
    parser.add_argument(
        "--project",
        default=None,
        help="Filter by project name",
    )
    args = parser.parse_args()

    index = build_index(
        days=args.days,
        project_filter=args.project,
        output_path=args.output,
    )

    meta = index["_index_meta"]
    print(f"Index built: {meta['session_count']} sessions, {meta['days_covered']} days")
    print(f"Saved to: {args.output or '~/.claude/session-intel/index.json'}")


if __name__ == "__main__":
    main()
