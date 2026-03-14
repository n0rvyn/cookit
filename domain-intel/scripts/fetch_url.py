#!/usr/bin/env python3
"""Fetch a URL with explicit timeout and return clean text.

# Why this script exists
#
# The source-scanner agent previously used Claude Code's built-in WebFetch tool
# for all HTTP fetches. WebFetch combines fetching + AI extraction in one call,
# which is convenient — but it has NO user-controllable timeout. When a target
# site is slow, blocks automated requests, or returns very large pages, WebFetch
# hangs indefinitely, causing the entire source-scanner agent to stall (observed:
# 8+ hours with no timeout).
#
# This script replaces WebFetch's *fetching* half. The *extraction* half is now
# handled by the source-scanner agent itself (Sonnet), which reads the clean text
# output and extracts structured data. This is the same pattern already used by
# the browser_fallback path (fetch_rendered.py → agent self-extraction).
#
# Fallback chain (managed by source-scanner agent instructions):
#   1. fetch_url.py  — stdlib urllib, fast, 30s default timeout
#   2. fetch_rendered.py — Playwright headless browser, for JS-rendered SPAs
#   3. Record as failed_source and move on
#
# Future migration back to WebFetch
# ----------------------------------
# If Claude Code adds a timeout parameter to WebFetch, this script can be retired.
# To migrate back:
#   1. In source-scanner.md, replace Bash(fetch_url.py ...) calls with WebFetch()
#   2. Remove the "self-extraction" instructions (WebFetch handles extraction)
#   3. Keep fetch_rendered.py as browser_fallback for JS-rendered pages
#   4. Delete this script
# Search for "FETCH_URL_MIGRATION" in source-scanner.md to find all call sites.

Usage:
    python3 fetch_url.py <url> [--timeout 30]

Output:
    stdout: cleaned text content of the page
    stderr: diagnostic messages (fetch status, char count, errors)

Exit codes:
    0 — success, clean text written to stdout
    1 — network error, timeout, HTTP error (4xx/5xx), or connection refused
    2 — page fetched successfully but content is empty or trivial (<20 chars)
        This usually means the page is a JS-rendered SPA that needs Playwright.
"""

import argparse
import http.client
import re
import ssl
import sys
import urllib.error
import urllib.request

# Mimic a real browser to avoid bot-detection blocks.
# Some sites (e.g., openai.com) reject requests without a plausible User-Agent.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

# Maximum output size in characters. Keeps agent context manageable.
# Matches fetch_rendered.py's MAX_CHARS for consistent behavior.
MAX_CHARS = 8000

# Maximum bytes to read from the HTTP response body.
# Prevents memory exhaustion on unexpectedly large pages (e.g., data dumps).
# 500KB of HTML typically yields well under MAX_CHARS of clean text.
MAX_READ_BYTES = 512_000


def strip_html(html: str) -> str:
    """Convert HTML to plain text by stripping tags and decoding entities.

    This is intentionally simple regex-based stripping, not a full parser.
    It handles the common cases well enough for the source-scanner's needs
    (extracting article titles, dates, and short descriptions).

    For pages where this produces garbage (heavy JS frameworks, complex layouts),
    the content will be short/empty and trigger exit code 2, which tells the
    source-scanner to escalate to fetch_rendered.py (Playwright).
    """
    # Remove entire <script>, <style>, <noscript> blocks — these never contain
    # useful article content and would pollute the output with code/CSS.
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<noscript[^>]*>.*?</noscript>", " ", text, flags=re.DOTALL | re.IGNORECASE)

    # Remove HTML comments (may contain conditional IE blocks, build hashes, etc.)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)

    # Remove common navigation/chrome elements that add noise.
    # These are matched as paired tags to avoid removing content between
    # unrelated nav/footer elements on poorly structured pages.
    text = re.sub(r"<(nav|header|footer)[^>]*>.*?</\1>", " ", text, flags=re.DOTALL | re.IGNORECASE)

    # Block-level tags become newlines to preserve document structure.
    # This helps the agent distinguish between article titles and body text.
    text = re.sub(r"<(?:br|p|div|h[1-6]|li|tr|section|article)[^>]*/?>", "\n", text, flags=re.IGNORECASE)

    # Strip all remaining HTML tags (inline elements, images, links, etc.)
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode the most common HTML entities. Full entity decoding would require
    # html.unescape(), but these 6 cover ~95% of cases in practice.
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    text = text.replace("&nbsp;", " ")

    return text


def clean_text(raw: str) -> str:
    """Normalize whitespace, collapse blank lines, truncate to MAX_CHARS.

    Shared logic with fetch_rendered.py — both scripts produce identically
    formatted output so the source-scanner's extraction prompts work the same
    regardless of which script produced the text.
    """
    lines = [line.strip() for line in raw.splitlines()]

    # Collapse runs of blank lines into a single blank line.
    # Raw HTML stripping often produces many consecutive empty lines.
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

    # Truncate at a line boundary to avoid cutting mid-sentence.
    if len(text) > MAX_CHARS:
        truncated = text[:MAX_CHARS]
        last_newline = truncated.rfind("\n")
        if last_newline > MAX_CHARS * 0.8:
            truncated = truncated[:last_newline]
        text = truncated + "\n\n[truncated]"

    return text


def _decompress(data: bytes, encoding: str) -> bytes:
    """Decompress gzip/deflate data, tolerating truncated streams.

    Uses zlib.decompressobj instead of gzip.decompress because:
    - gzip.decompress raises EOFError on truncated data
    - zlib.decompressobj returns whatever it can decompress, which is
      usually enough for our purposes (we only need article titles/dates)
    """
    import zlib

    if encoding == "gzip":
        # wbits=31 = gzip header (16) + max window size (15)
        try:
            return zlib.decompressobj(wbits=31).decompress(data)
        except zlib.error:
            return data  # If decompression fails entirely, return raw data
    elif encoding == "deflate":
        try:
            return zlib.decompress(data)
        except zlib.error:
            return data
    return data


def fetch(url: str, timeout: int) -> str:
    """Fetch URL and return raw HTML content.

    Key differences from WebFetch:
    - Explicit timeout (the whole reason this script exists)
    - Reads at most MAX_READ_BYTES (500KB) to bound memory usage
    - Follows redirects automatically (urllib default behavior)
    - Uses a real-browser User-Agent to avoid simple bot blocks

    Does NOT handle:
    - JavaScript rendering (use fetch_rendered.py for that)
    - Cookie consent walls (these produce empty/short content → exit code 2)
    - Rate limiting / CAPTCHAs (these return HTTP errors → exit code 1)
    """
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        # Accept HTML and common text formats; some servers vary response by Accept header.
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        # Declare language preference to avoid localized redirect loops.
        "Accept-Language": "en-US,en;q=0.9",
        # Tell the server we can handle gzip. Many servers (e.g., swift.org)
        # return gzip-compressed responses by default; without this header
        # AND explicit decompression, we get binary garbage.
        "Accept-Encoding": "gzip, deflate",
    })

    # Create a permissive SSL context for sites with certificate issues.
    # source-scanner is reading public web pages, not handling sensitive data;
    # a strict SSL check that blocks the fetch is worse than a permissive one.
    ctx = ssl.create_default_context()

    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        content_encoding = resp.headers.get("Content-Encoding", "").lower()
        charset = resp.headers.get_content_charset() or "utf-8"

        # Read with a byte cap to prevent memory exhaustion on huge pages.
        # IncompleteRead can occur when the server drops the connection
        # mid-transfer (common with bot detection). We use the partial data.
        try:
            data = resp.read(MAX_READ_BYTES)
        except http.client.IncompleteRead as e:
            print(f"Incomplete read ({len(e.partial)} bytes) — using partial content", file=sys.stderr)
            data = e.partial

        # Decompress if the server sent gzip/deflate content.
        # urllib does NOT auto-decompress (unlike requests library).
        # We use zlib.decompressobj which handles partial/truncated streams
        # gracefully — gzip.decompress raises EOFError on truncated data.
        # This is important because:
        #   a) MAX_READ_BYTES may truncate the compressed stream
        #   b) IncompleteRead gives us partial compressed data
        data = _decompress(data, content_encoding)

        return data.decode(charset, errors="replace")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch URL with timeout, return clean text"
    )
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )
    args = parser.parse_args()

    print(f"Fetching: {args.url}", file=sys.stderr)

    try:
        html = fetch(args.url, args.timeout)

    # --- Error handling: every path prints a diagnostic and exits 1 ---
    # The source-scanner agent checks exit code to decide whether to try
    # browser_fallback or record as failed_source.

    except urllib.error.HTTPError as e:
        # Server responded with an error status (403 Forbidden, 429 Rate Limited, etc.)
        print(f"HTTP {e.code}: {e.reason} — {args.url}", file=sys.stderr)
        sys.exit(1)

    except urllib.error.URLError as e:
        # DNS failure, connection refused, SSL error, or timeout.
        # urllib wraps socket.timeout in URLError on some Python versions.
        print(f"Network error: {e.reason} — {args.url}", file=sys.stderr)
        sys.exit(1)

    except TimeoutError:
        # Socket-level timeout (distinct from urllib's timeout on some platforms).
        print(f"Timeout after {args.timeout}s — {args.url}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        # Catch-all for unexpected errors (encoding issues, redirect loops, etc.)
        print(f"Fetch failed: {type(e).__name__}: {e} — {args.url}", file=sys.stderr)
        sys.exit(1)

    # --- Convert HTML to clean text ---
    text = strip_html(html)
    cleaned = clean_text(text)

    # Exit code 2 signals "page fetched but no useful content."
    # This typically means a JS-rendered SPA — the source-scanner should
    # escalate to fetch_rendered.py (Playwright) if browser_fallback is enabled.
    if not cleaned or len(cleaned) < 20:
        print("Page fetched but content is empty or trivial (likely JS-rendered SPA)", file=sys.stderr)
        sys.exit(2)

    print(f"Output: {len(cleaned)} chars", file=sys.stderr)
    print(cleaned)


if __name__ == "__main__":
    main()
