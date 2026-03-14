#!/usr/bin/env python3
"""Fetch recent products from Product Hunt using their GraphQL API.

# Why this script exists
#
# Product Hunt is a valuable source for discovering new developer tools, AI
# products, and indie launches. Unlike GitHub (where `gh` CLI handles auth),
# PH requires OAuth2 client credentials flow + GraphQL queries — too complex
# for inline Bash commands in the source-scanner agent.
#
# This script encapsulates the full PH API interaction:
#   1. OAuth2 token exchange (client_credentials grant)
#   2. GraphQL query for recent posts (sorted by votes)
#   3. Optional topic filtering
#   4. JSON output for the source-scanner to parse
#
# Based on the implementation in:
#   ~/Code/Projects/Lumina/lumina-backend/internal/collector/producthunt.go
#
# API reference:
#   OAuth: POST https://api.producthunt.com/v2/oauth/token
#   GraphQL: POST https://api.producthunt.com/v2/api/graphql
#   Docs: https://api.producthunt.com/v2/docs

Usage:
    python3 fetch_producthunt.py --client-id ID --client-secret SECRET [options]

Options:
    --topics TOPICS    Comma-separated topic filter (default: none, return all)
    --days-back N      How many days back to search (default: 7)
    --max-items N      Maximum posts to fetch (default: 50)
    --timeout N        Request timeout in seconds (default: 30)

Output:
    stdout: JSON array of posts
    stderr: diagnostic messages

Exit codes:
    0 — success, JSON written to stdout
    1 — auth failure, network error, or API error
    2 — success but zero posts found (not an error, just empty)
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

OAUTH_URL = "https://api.producthunt.com/v2/oauth/token"
GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"


def authenticate(client_id: str, client_secret: str, timeout: int) -> str:
    """Exchange client credentials for an access token.

    Uses OAuth2 client_credentials grant type. The returned token is
    short-lived but we only need it for one scan session.
    """
    body = json.dumps({
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }).encode()

    req = urllib.request.Request(
        OAUTH_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())

    token = data.get("access_token")
    if not token:
        raise ValueError(f"No access_token in OAuth response: {data}")

    expires_in = data.get("expires_in", "unknown")
    print(f"Authenticated (token expires in {expires_in}s)", file=sys.stderr)
    return token


def fetch_posts(token: str, max_items: int, days_back: int, timeout: int) -> list:
    """Fetch recent posts from Product Hunt GraphQL API.

    Queries posts sorted by VOTES from the last `days_back` days.
    Returns raw post data with topics for optional filtering.
    """
    posted_after = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # GraphQL query matching Lumina's implementation.
    # VOTES ordering surfaces the most popular products first.
    query = f'''
    query {{
        posts(first: {max_items}, order: VOTES, postedAfter: "{posted_after}") {{
            edges {{
                node {{
                    id
                    name
                    tagline
                    votesCount
                    url
                    createdAt
                    topics(first: 5) {{
                        edges {{
                            node {{
                                name
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}'''

    body = json.dumps({"query": query}).encode()

    req = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())

    # Check for GraphQL-level errors (auth expired, invalid query, etc.)
    if data.get("errors"):
        error_msg = data["errors"][0].get("message", "Unknown GraphQL error")
        raise ValueError(f"GraphQL error: {error_msg}")

    # Parse the relay-style edges/node response into flat post objects.
    posts = []
    for edge in data.get("data", {}).get("posts", {}).get("edges", []):
        node = edge["node"]
        topics = [
            t["node"]["name"]
            for t in node.get("topics", {}).get("edges", [])
        ]
        posts.append({
            "id": node["id"],
            "name": node["name"],
            "tagline": node["tagline"],
            "votes": node["votesCount"],
            "url": node["url"],
            "created_at": node["createdAt"],
            "topics": topics,
        })

    return posts


def filter_by_topics(posts: list, topics: list[str]) -> list:
    """Filter posts to those matching at least one target topic.

    Case-insensitive matching. If no topics specified, return all posts.
    """
    if not topics:
        return posts

    target_set = {t.strip().lower() for t in topics}
    filtered = []
    for post in posts:
        post_topics = {t.lower() for t in post.get("topics", [])}
        if post_topics & target_set:
            filtered.append(post)

    return filtered


def main():
    parser = argparse.ArgumentParser(
        description="Fetch recent Product Hunt posts via GraphQL API"
    )
    parser.add_argument("--client-id", required=True, help="PH OAuth client ID")
    parser.add_argument("--client-secret", required=True, help="PH OAuth client secret")
    parser.add_argument("--topics", default="", help="Comma-separated topic filter (empty = all)")
    parser.add_argument("--days-back", type=int, default=7, help="Days of history (default: 7)")
    parser.add_argument("--max-items", type=int, default=50, help="Max posts to fetch (default: 50)")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds (default: 30)")
    args = parser.parse_args()

    # --- Step 1: Authenticate ---
    print("Authenticating with Product Hunt...", file=sys.stderr)
    try:
        token = authenticate(args.client_id, args.client_secret, args.timeout)
    except urllib.error.HTTPError as e:
        print(f"Auth failed: HTTP {e.code} — check client_id and client_secret", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Auth failed: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Step 2: Fetch posts ---
    print(f"Fetching posts (last {args.days_back} days, max {args.max_items})...", file=sys.stderr)
    try:
        posts = fetch_posts(token, args.max_items, args.days_back, args.timeout)
    except Exception as e:
        print(f"Fetch failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Fetched {len(posts)} posts", file=sys.stderr)

    # --- Step 3: Filter by topics (optional) ---
    topics = [t.strip() for t in args.topics.split(",") if t.strip()] if args.topics else []
    if topics:
        posts = filter_by_topics(posts, topics)
        print(f"After topic filter ({', '.join(topics)}): {len(posts)} posts", file=sys.stderr)

    # --- Step 4: Output ---
    if not posts:
        print("No posts found matching criteria", file=sys.stderr)
        sys.exit(2)

    print(f"Output: {len(posts)} posts", file=sys.stderr)
    json.dump(posts, sys.stdout, indent=2, ensure_ascii=False)
    print()  # trailing newline


if __name__ == "__main__":
    main()
