#!/usr/bin/env python3
"""Fetch transcripts for YouTube videos using youtube-transcript-api.

Usage:
    python3 fetch_transcript.py --video-ids "abc123,def456" --lang "en,zh-Hans"

Output:
    stdout: JSON mapping video_id to {text, lang} or {text: null, error: "..."}
    stderr: diagnostic messages
    Exit codes: 0 = success (even if some videos have no transcript)
"""

import argparse
import json
import sys


def fetch_transcript(video_id: str, langs: list[str]) -> dict:
    """Fetch transcript for a single video, trying languages in priority order.

    Uses youtube-transcript-api v1.2.x API: YouTubeTranscriptApi().fetch()
    returns a FetchedTranscript with .snippets list, each having .text attribute.
    """
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        NoTranscriptFound,
        TranscriptsDisabled,
        VideoUnavailable,
    )

    api = YouTubeTranscriptApi()

    for lang in langs:
        try:
            result = api.fetch(video_id, languages=[lang])
            text = " ".join(snippet.text for snippet in result.snippets)
            if text.strip():
                return {"text": text, "lang": lang}
        except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
            continue
        except Exception as e:
            print(f"  [{video_id}] Error with lang={lang}: {type(e).__name__}: {e}", file=sys.stderr)
            continue

    return {"text": None, "error": "no_transcript"}


def main():
    parser = argparse.ArgumentParser(
        description="Fetch YouTube video transcripts"
    )
    parser.add_argument(
        "--video-ids",
        required=True,
        help="Comma-separated video IDs",
    )
    parser.add_argument(
        "--lang",
        default="en,zh-Hans",
        help="Comma-separated language priority list (default: en,zh-Hans)",
    )
    args = parser.parse_args()

    video_ids = [vid.strip() for vid in args.video_ids.split(",") if vid.strip()]
    langs = [lang.strip() for lang in args.lang.split(",") if lang.strip()]

    if not video_ids:
        print("No video IDs provided", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching transcripts for {len(video_ids)} videos...", file=sys.stderr)

    results = {}
    for i, video_id in enumerate(video_ids, 1):
        print(f"  [{i}/{len(video_ids)}] {video_id}", file=sys.stderr)
        results[video_id] = fetch_transcript(video_id, langs)

    success = sum(1 for r in results.values() if r.get("text") is not None)
    print(f"Done: {success}/{len(video_ids)} transcripts fetched", file=sys.stderr)

    print(json.dumps(results))


if __name__ == "__main__":
    main()
