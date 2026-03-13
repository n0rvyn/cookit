#!/usr/bin/env python3
"""Fetch a JS-rendered page using Playwright headless Chromium.

Usage:
    python3 fetch_rendered.py <url> [--timeout 15000]

Output:
    stdout: cleaned text content of the rendered page
    stderr: diagnostic messages
    Exit codes: 0 = success, 1 = navigation/timeout error, 2 = empty content
"""

import argparse
import re
import sys


NOISE_SELECTORS = [
    "nav",
    "footer",
    "header",
    "script",
    "style",
    "noscript",
    "iframe",
    "svg",
    '[role="navigation"]',
    '[role="banner"]',
    '[role="contentinfo"]',
    ".cookie-banner",
    "#cookie-consent",
    "#cookie-banner",
    "[class*='cookie']",
    "[class*='consent']",
    "[class*='popup']",
    "[class*='modal']",
    "[class*='newsletter']",
]

MAX_CHARS = 8000


def clean_text(raw: str) -> str:
    """Light cleaning: normalize whitespace, collapse blank lines, truncate."""
    lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        lines.append(stripped)

    # Collapse multiple blank lines into one
    result = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                result.append("")
            prev_blank = True
        else:
            result.append(line)
            prev_blank = False

    text = "\n".join(result).strip()

    if len(text) > MAX_CHARS:
        # Truncate at last complete line within limit
        truncated = text[:MAX_CHARS]
        last_newline = truncated.rfind("\n")
        if last_newline > MAX_CHARS * 0.8:
            truncated = truncated[:last_newline]
        text = truncated + "\n\n[truncated]"

    return text


def fetch(url: str, timeout: int) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 800},
            )
            page = context.new_page()

            # Block fonts and video to speed up loading.
            # Keep images — some SPA frameworks gate rendering on image load events.
            page.route(
                re.compile(r"\.(woff2?|ttf|eot|otf|mp4|webm|ogg)(\?|$)"),
                lambda route: route.abort(),
            )

            try:
                page.goto(url, wait_until="load", timeout=timeout)
            except Exception as e:
                print(f"Navigation failed: {e}", file=sys.stderr)
                sys.exit(1)

            # Scroll to trigger lazy-loaded content, then wait for text threshold
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_function(
                    "() => document.body && document.body.innerText.length > 500",
                    timeout=min(timeout, 8000),
                )
            except Exception:
                # Content threshold not met; still extract whatever loaded
                pass

            # Remove noise elements
            page.evaluate(
                """(selectors) => {
                selectors.forEach(sel => {
                    document.querySelectorAll(sel).forEach(el => el.remove());
                });
            }""",
                NOISE_SELECTORS,
            )

            text = page.inner_text("body")
        finally:
            browser.close()

    return text


def main():
    parser = argparse.ArgumentParser(description="Fetch JS-rendered page content")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument(
        "--timeout",
        type=int,
        default=15000,
        help="Navigation timeout in ms (default: 15000)",
    )
    args = parser.parse_args()

    print(f"Fetching: {args.url}", file=sys.stderr)

    text = fetch(args.url, args.timeout)
    cleaned = clean_text(text)

    if not cleaned or len(cleaned) < 20:
        print("Page rendered but content is empty or trivial", file=sys.stderr)
        sys.exit(2)

    print(f"Output: {len(cleaned)} chars", file=sys.stderr)
    print(cleaned)


if __name__ == "__main__":
    main()
