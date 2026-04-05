#!/usr/bin/env python3
"""Deduplication helper for yt-intel.

Tracks seen video IDs across runs using SHA-256 hashes stored in a JSONL file.

Usage:
    # Filter out already-seen videos (reads JSON array from stdin, outputs filtered array)
    echo '[{"video_id": "abc123", ...}]' | python3 dedup.py filter

    # Mark videos as seen (reads JSON array from stdin, appends to seen.jsonl)
    echo '[{"video_id": "abc123", "title": "..."}]' | python3 dedup.py mark-seen

Storage:
    ~/.yt-intel/seen.jsonl — one JSON line per seen video:
    {"hash": "a1b2c3d4", "video_id": "abc123", "date": "2026-03-21", "title": "..."}
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime


SEEN_FILE = os.path.expanduser("~/.yt-intel/seen.jsonl")


def get_hash(video_id: str) -> str:
    """Get SHA-256 hash of video_id, first 8 hex chars."""
    return hashlib.sha256(video_id.encode()).hexdigest()[:8]


def load_seen() -> set[str]:
    """Load seen video hashes from seen.jsonl."""
    seen = set()
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    seen.add(json.loads(line)["hash"])
                except (json.JSONDecodeError, KeyError):
                    pass
    return seen


def filter_new(videos: list[dict]) -> list[dict]:
    """Filter out already-seen videos."""
    seen = load_seen()
    new_videos = []
    for video in videos:
        h = get_hash(video["video_id"])
        if h not in seen:
            new_videos.append(video)
    return new_videos


def mark_seen(videos: list[dict]):
    """Append new videos to seen.jsonl."""
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    with open(SEEN_FILE, "a") as f:
        for video in videos:
            entry = {
                "hash": get_hash(video["video_id"]),
                "video_id": video["video_id"],
                "date": datetime.now().strftime("%Y-%m-%d"),
                "title": video.get("title", ""),
            }
            f.write(json.dumps(entry) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Dedup helper for yt-intel")
    parser.add_argument(
        "action",
        choices=["filter", "mark-seen"],
        help=(
            "filter: read JSON array from stdin, output filtered JSON; "
            "mark-seen: read JSON array from stdin, append to seen.jsonl"
        ),
    )
    args = parser.parse_args()

    data = json.load(sys.stdin)

    if args.action == "filter":
        before = len(data)
        result = filter_new(data)
        print(f"Dedup: {before} → {len(result)} ({before - len(result)} duplicates removed)", file=sys.stderr)
        json.dump(result, sys.stdout)
    elif args.action == "mark-seen":
        mark_seen(data)
        print(f"Marked {len(data)} videos as seen", file=sys.stderr)


if __name__ == "__main__":
    main()
