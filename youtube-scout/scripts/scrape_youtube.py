#!/usr/bin/env python3
"""Scrape YouTube recommended feed and topic search results.

Usage:
    python3 scrape_youtube.py --topic "AI" --cookie-dir ~/.youtube-scout \\
        --max-recommended 30 --max-search 20

Output:
    stdout: JSON with status and video list
    stderr: diagnostic messages
    Exit codes: 0 = success, 1 = error
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime


COOKIE_FILE_NAME = "cookies.json"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def cookie_path(cookie_dir: str) -> str:
    return os.path.join(os.path.expanduser(cookie_dir), COOKIE_FILE_NAME)


def load_cookies(cookie_dir: str):
    """Load cookies if they exist and are not expired (30-day window)."""
    path = cookie_path(cookie_dir)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        created = datetime.fromisoformat(data.get("created", "2000-01-01"))
        if (datetime.now() - created).days > 30:
            print("Cookies expired (>30 days old)", file=sys.stderr)
            return None
        return data.get("cookies", [])
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Cookie file corrupt: {e}", file=sys.stderr)
        return None


def save_cookies(context, cookie_dir: str):
    """Save browser cookies to disk."""
    path = cookie_path(cookie_dir)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cookies = context.cookies()
    data = {
        "created": datetime.now().isoformat(),
        "cookies": cookies,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Cookies saved to {path}", file=sys.stderr)


def check_login(page) -> bool | None:
    """Check if user is logged into YouTube.

    Returns True (logged in), False (not logged in), or None (unknown).
    """
    try:
        page.wait_for_selector("#avatar-btn", timeout=5000)
        return True
    except Exception:
        pass
    try:
        page.wait_for_selector(
            "a[href*='accounts.google.com/ServiceLogin'], "
            "ytd-button-renderer a[href*='accounts.google.com'], "
            "tp-yt-paper-button#button:has-text('Sign in')",
            timeout=3000,
        )
        return False
    except Exception:
        return None


def interactive_login(page, context, cookie_dir: str) -> bool:
    """Handle interactive login flow. Returns True if login succeeded."""
    page.goto("https://www.youtube.com", wait_until="domcontentloaded", timeout=30000)
    login_status = check_login(page)

    if login_status is True:
        print("Already logged in", file=sys.stderr)
        save_cookies(context, cookie_dir)
        return True

    print(
        "\n"
        "=== YouTube Login Required ===\n"
        "A browser window has opened. Please log in to YouTube.\n"
        "After logging in, press Enter here to continue...\n",
        file=sys.stderr,
    )
    input()

    # Re-check after user says they logged in
    page.reload(wait_until="domcontentloaded", timeout=15000)
    time.sleep(2)
    login_status = check_login(page)

    if login_status is True:
        save_cookies(context, cookie_dir)
        return True
    elif login_status is None:
        # Unknown state — ask user to confirm
        print(
            "Could not detect login status automatically.\n"
            "Are you logged in? Press Enter to continue, or Ctrl+C to abort.",
            file=sys.stderr,
        )
        input()
        save_cookies(context, cookie_dir)
        return True
    else:
        print("Login not detected. Aborting.", file=sys.stderr)
        return False


def parse_view_count(text: str) -> int:
    """Parse YouTube view count text like '1.2M views' or '150K views'."""
    if not text:
        return 0
    text = text.lower().replace(",", "").replace(" views", "").replace(" view", "").strip()
    multipliers = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}
    for suffix, mult in multipliers.items():
        if text.endswith(suffix):
            try:
                return int(float(text[:-1]) * mult)
            except ValueError:
                return 0
    try:
        return int(text)
    except ValueError:
        return 0


def parse_duration(text: str) -> str:
    """Extract duration like '15:32' from potentially duplicated text."""
    if not text:
        return ""
    # YouTube sometimes renders duration twice; take the first match
    m = re.search(r"(\d+:[\d:]+)", text.strip())
    return m.group(1) if m else text.strip()


def extract_video_id(url: str) -> str | None:
    """Extract video ID from a YouTube URL."""
    m = re.search(r"(?:v=|youtu\.be/|/shorts/)([a-zA-Z0-9_-]{11})", url or "")
    return m.group(1) if m else None


def scrape_video_elements(page, max_items: int, source: str) -> list[dict]:
    """Extract video data from currently loaded YouTube page."""
    videos = []
    seen_ids = set()

    # Scroll to load more videos
    for _ in range(max(1, max_items // 10)):
        page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
        time.sleep(1.5)

    # Wait for video renderers to appear
    try:
        page.wait_for_selector("ytd-rich-item-renderer, ytd-video-renderer", timeout=10000)
    except Exception:
        print(f"No video elements found for {source}", file=sys.stderr)
        return videos

    # Extract video data using JavaScript
    raw_videos = page.evaluate("""() => {
        const results = [];
        const renderers = document.querySelectorAll('ytd-rich-item-renderer, ytd-video-renderer');
        for (const el of renderers) {
            try {
                const titleEl = el.querySelector('#video-title, #video-title-link, a#video-title');
                const href = titleEl?.href || titleEl?.closest('a')?.href || '';
                const title = titleEl?.textContent?.trim() || '';
                const channelEl = el.querySelector('#channel-name a, ytd-channel-name a, .ytd-channel-name a');
                const channel = channelEl?.textContent?.trim() || '';
                const metaEl = el.querySelector('#metadata-line, #metadata');
                const metaText = metaEl?.textContent || '';
                const viewMatch = metaText.match(/([\\d,.]+[KMB]?)\\s*views?/i);
                const viewsText = viewMatch ? viewMatch[1] : '';
                const timeEl = el.querySelector('ytd-thumbnail-overlay-time-status-renderer, span.ytd-thumbnail-overlay-time-status-renderer');
                const duration = timeEl?.textContent?.trim() || '';
                const descEl = el.querySelector('#description-text, .metadata-snippet-text');
                const description = descEl?.textContent?.trim() || '';
                const subscriberEl = el.querySelector('#owner-sub-count');
                const subscribers = subscriberEl?.textContent?.trim() || '';
                if (href && title) {
                    results.push({href, title, channel, viewsText, duration, description, subscribers});
                }
            } catch(e) {}
        }
        return results;
    }""")

    for item in raw_videos[:max_items]:
        video_id = extract_video_id(item.get("href", ""))
        if not video_id or video_id in seen_ids:
            continue
        seen_ids.add(video_id)

        videos.append({
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": item.get("title", ""),
            "channel": item.get("channel", ""),
            "channel_subscribers": item.get("subscribers", ""),
            "views": parse_view_count(item.get("viewsText", "")),
            "description": item.get("description", ""),
            "duration": parse_duration(item.get("duration", "")),
            "source": source,
        })

    return videos


def scrape_recommended(page, max_items: int) -> list[dict]:
    """Scrape YouTube homepage recommended feed."""
    print(f"Scraping recommended feed (max {max_items})...", file=sys.stderr)
    page.goto("https://www.youtube.com", wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    return scrape_video_elements(page, max_items, "recommended")


def scrape_search(page, topic: str, max_items: int) -> list[dict]:
    """Scrape YouTube search results for a topic, sorted by view count, filtered to this week."""
    print(f"Scraping search for '{topic}' (max {max_items})...", file=sys.stderr)
    # sp=CAMSBAgCEAE%253D = This week + View count sort
    search_url = (
        f"https://www.youtube.com/results?"
        f"search_query={topic}&sp=CAMSBAgCEAE%253D"
    )
    page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)
    return scrape_video_elements(page, max_items, "search")


def merge_and_dedup(recommended: list[dict], search: list[dict]) -> list[dict]:
    """Merge video lists, deduplicating by video_id (keep first occurrence)."""
    seen = set()
    merged = []
    for video in recommended + search:
        if video["video_id"] not in seen:
            seen.add(video["video_id"])
            merged.append(video)
    return merged


def main():
    parser = argparse.ArgumentParser(
        description="Scrape YouTube recommended feed and topic search"
    )
    parser.add_argument("--topic", default="AI", help="Search topic (default: AI)")
    parser.add_argument(
        "--cookie-dir",
        default="~/.youtube-scout",
        help="Directory for cookie storage (default: ~/.youtube-scout)",
    )
    parser.add_argument(
        "--max-recommended",
        type=int,
        default=30,
        help="Max recommended videos to scrape (default: 30)",
    )
    parser.add_argument(
        "--max-search",
        type=int,
        default=20,
        help="Max search results to scrape (default: 20)",
    )
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    cookies = load_cookies(args.cookie_dir)
    needs_login = cookies is None
    # Only require login if recommended feed is requested
    wants_recommended = args.max_recommended > 0
    needs_interactive = needs_login and wants_recommended

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not needs_interactive)
        try:
            context = browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1280, "height": 800},
            )

            if cookies and not needs_login:
                context.add_cookies(cookies)

            page = context.new_page()

            # Block heavy resources to speed up loading
            page.route(
                re.compile(r"\.(woff2?|ttf|eot|otf|mp4|webm|ogg)(\?|$)"),
                lambda route: route.abort(),
            )

            if needs_interactive:
                if not interactive_login(page, context, args.cookie_dir):
                    result = {
                        "status": "login_required",
                        "login_required": True,
                        "videos": [],
                    }
                    print(json.dumps(result, ensure_ascii=False))
                    sys.exit(0)

            # Scrape recommended feed (skip if max is 0)
            recommended = []
            if args.max_recommended > 0:
                try:
                    recommended = scrape_recommended(page, args.max_recommended)
                    print(f"Recommended: {len(recommended)} videos", file=sys.stderr)
                except Exception as e:
                    print(f"Recommended feed failed: {e}", file=sys.stderr)

            # Scrape search results
            search_results = []
            try:
                search_results = scrape_search(page, args.topic, args.max_search)
                print(f"Search: {len(search_results)} videos", file=sys.stderr)
            except Exception as e:
                print(f"Search scraping failed: {e}", file=sys.stderr)

            # Determine status
            if not recommended and not search_results:
                status = "login_required"
                login_required = True
            elif not recommended and search_results:
                status = "partial"
                login_required = False
            else:
                status = "ok"
                login_required = False

            # Save cookies on successful scrape
            if status in ("ok", "partial"):
                save_cookies(context, args.cookie_dir)

            merged = merge_and_dedup(recommended, search_results)
            print(f"Total after dedup: {len(merged)} videos", file=sys.stderr)

            result = {
                "status": status,
                "login_required": login_required,
                "videos": merged,
            }
            print(json.dumps(result, ensure_ascii=False))

        finally:
            browser.close()


if __name__ == "__main__":
    main()
