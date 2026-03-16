#!/usr/bin/env python3
"""Aggregate session data by day for trend analysis."""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime


def aggregate_by_day(sessions):
    """Group sessions by date and compute daily metrics.

    Args:
        sessions: list of session summary dicts (from index)

    Returns:
        dict of date_str → daily aggregate dict, sorted by date
    """
    by_day = defaultdict(list)
    for s in sessions:
        time_info = s.get("time", {})
        start = time_info.get("start")
        if not start:
            continue
        try:
            date_str = start[:10]  # "2026-03-14"
            by_day[date_str].append(s)
        except (TypeError, IndexError):
            continue

    result = {}
    for date_str in sorted(by_day.keys()):
        day_sessions = by_day[date_str]
        result[date_str] = _compute_daily_metrics(date_str, day_sessions)

    return result


def _compute_daily_metrics(date_str, sessions):
    """Compute aggregate metrics for a single day's sessions."""
    n = len(sessions)

    # Duration
    durations = [
        s["time"]["duration_min"]
        for s in sessions
        if s.get("time", {}).get("duration_min") is not None
    ]
    avg_duration = sum(durations) / len(durations) if durations else None

    # Tokens
    total_tokens = 0
    for s in sessions:
        tokens = s.get("tokens", {})
        inp = tokens.get("input") or 0
        out = tokens.get("output") or 0
        total_tokens += inp + out

    # Cache hit rate — weighted by input tokens
    cache_numerator = 0
    cache_denominator = 0
    for s in sessions:
        tokens = s.get("tokens", {})
        inp = tokens.get("input")
        rate = tokens.get("cache_hit_rate")
        if inp is not None and rate is not None and inp > 0:
            cache_numerator += rate * inp
            cache_denominator += inp
    avg_cache_hit_rate = (
        cache_numerator / cache_denominator if cache_denominator > 0 else None
    )

    # Turns
    total_user_turns = sum(s.get("turns", {}).get("user", 0) for s in sessions)
    total_assistant_turns = sum(s.get("turns", {}).get("assistant", 0) for s in sessions)
    avg_turns = (total_user_turns + total_assistant_turns) / n if n > 0 else 0

    # Build first-pass rate (exclude sessions with 0 build attempts)
    build_sessions = [
        s for s in sessions
        if s.get("quality", {}).get("build_attempts", 0) > 0
    ]
    if build_sessions:
        passed = sum(
            1 for s in build_sessions
            if s.get("quality", {}).get("build_failures", 0) == 0
        )
        build_first_pass_rate = passed / len(build_sessions)
    else:
        build_first_pass_rate = None

    # Bash error rate
    total_bash_errors = sum(
        s.get("quality", {}).get("bash_errors", 0) for s in sessions
    )
    total_tool_calls = sum(
        s.get("tools", {}).get("total_calls", 0) for s in sessions
    )
    bash_error_rate = (
        total_bash_errors / total_tool_calls if total_tool_calls > 0 else 0
    )

    # Repeated edits
    repeated_edit_sessions = sum(
        1 for s in sessions
        if s.get("quality", {}).get("repeated_edits")
    )

    # Corrections
    corrections_count = sum(
        len(s.get("corrections", [])) for s in sessions
    )

    # DNA distribution
    dna_dist = defaultdict(int)
    for s in sessions:
        dna = s.get("session_dna", "mixed")
        dna_dist[dna] += 1

    # Emotion signals
    emotion_counts = defaultdict(int)
    for s in sessions:
        for signal in s.get("emotion_signals", []):
            etype = signal.get("type", "unknown")
            emotion_counts[etype] += 1

    return {
        "date": date_str,
        "sessions_count": n,
        "avg_duration_min": round(avg_duration, 1) if avg_duration is not None else None,
        "total_tokens": total_tokens,
        "avg_cache_hit_rate": (
            round(avg_cache_hit_rate, 3) if avg_cache_hit_rate is not None else None
        ),
        "avg_turns_per_session": round(avg_turns, 1),
        "build_first_pass_rate": (
            round(build_first_pass_rate, 2) if build_first_pass_rate is not None else None
        ),
        "bash_error_rate": round(bash_error_rate, 3),
        "repeated_edit_sessions": repeated_edit_sessions,
        "corrections_count": corrections_count,
        "dna_distribution": dict(dna_dist),
        "emotion_counts": dict(emotion_counts),
        "frustration_count": emotion_counts.get("frustration", 0),
        "impatience_count": emotion_counts.get("impatience", 0),
        "satisfaction_count": emotion_counts.get("satisfaction", 0),
        "emotion_total": sum(emotion_counts.values()),
    }


def filter_by_date_range(daily_aggregates, from_date=None, to_date=None):
    """Filter daily aggregates by date range.

    Args:
        daily_aggregates: dict of date_str → metrics (from aggregate_by_day)
        from_date: ISO date string (inclusive), or None
        to_date: ISO date string (inclusive), or None

    Returns:
        filtered dict
    """
    result = {}
    for date_str, metrics in daily_aggregates.items():
        if from_date and date_str < from_date:
            continue
        if to_date and date_str > to_date:
            continue
        result[date_str] = metrics
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate session index data by day"
    )
    parser.add_argument(
        "--index",
        default=os.path.expanduser("~/.claude/session-intel/index.json"),
        help="Path to session index (default: ~/.claude/session-intel/index.json)",
    )
    parser.add_argument(
        "--days", type=int, default=7,
        help="Aggregate last N days (default: 7)",
    )
    parser.add_argument("--from-date", default=None, help="Start date (ISO)")
    parser.add_argument("--to-date", default=None, help="End date (ISO)")
    parser.add_argument(
        "--output", default=None, help="Output JSON file (default: stdout)"
    )
    args = parser.parse_args()

    with open(args.index) as f:
        data = json.load(f)

    sessions = data.get("sessions", [])
    daily = aggregate_by_day(sessions)

    if args.from_date or args.to_date:
        daily = filter_by_date_range(daily, args.from_date, args.to_date)
    elif args.days:
        cutoff = datetime.now().strftime("%Y-%m-%d")
        from datetime import timedelta
        from_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
        daily = filter_by_date_range(daily, from_date, cutoff)

    output = json.dumps(list(daily.values()), indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
