#!/usr/bin/env python3
"""Calculate token costs from session data with configurable pricing."""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta

DEFAULT_PRICING = {
    "claude-opus-4-6": {"input": 15.0, "output": 75.0, "cache_read": 1.5},
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0, "cache_read": 0.3},
    "claude-haiku-4-5": {"input": 0.8, "output": 4.0, "cache_read": 0.1},
    "gpt-5.4": {"input": 10.0, "output": 30.0, "cache_read": 1.0},
}


def load_pricing(config_path=None):
    """Load pricing from .local.md config, merged with defaults.

    User overrides in ~/.claude/session-intel.local.md take precedence.
    """
    pricing = dict(DEFAULT_PRICING)
    if config_path is None:
        config_path = os.path.expanduser("~/.claude/session-intel.local.md")

    if not os.path.exists(config_path):
        return pricing

    try:
        with open(config_path) as f:
            content = f.read()
        # Extract YAML frontmatter between --- markers
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return pricing
        frontmatter = match.group(1)
        # Simple YAML parsing for pricing section
        in_pricing = False
        current_model = None
        for line in frontmatter.split("\n"):
            stripped = line.strip()
            if stripped == "pricing:":
                in_pricing = True
                continue
            if in_pricing:
                if not line.startswith(" ") and not line.startswith("\t"):
                    break
                # Model line: "  claude-opus-4-6: { input: 15, output: 75, cache_read: 1.5 }"
                model_match = re.match(
                    r"\s+([\w.-]+):\s*\{([^}]+)\}", stripped
                )
                if model_match:
                    model_name = model_match.group(1)
                    fields_str = model_match.group(2)
                    fields = {}
                    for field in fields_str.split(","):
                        kv = field.strip().split(":")
                        if len(kv) == 2:
                            key = kv[0].strip()
                            try:
                                val = float(kv[1].strip())
                                fields[key] = val
                            except ValueError:
                                pass
                    if fields:
                        pricing[model_name] = fields
    except (OSError, PermissionError):
        pass

    return pricing


def calculate_session_cost(session, pricing):
    """Calculate cost for a single session.

    Returns dict with input_cost, output_cost, cache_cost, total_cost and token counts.
    """
    tokens = session.get("tokens", {})
    model = session.get("model", "")
    model_pricing = pricing.get(model, {})

    input_tokens = tokens.get("input") or 0
    output_tokens = tokens.get("output") or 0
    cache_read_tokens = tokens.get("cache_read") or 0

    input_price = model_pricing.get("input", 0)
    output_price = model_pricing.get("output", 0)
    cache_price = model_pricing.get("cache_read", 0)

    input_cost = (input_tokens * input_price) / 1_000_000
    output_cost = (output_tokens * output_price) / 1_000_000
    cache_cost = (cache_read_tokens * cache_price) / 1_000_000

    return {
        "session_id": session.get("session_id", ""),
        "project": session.get("project", ""),
        "model": model,
        "date": (session.get("time", {}).get("start") or "")[:10],
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_read_tokens": cache_read_tokens,
        "input_cost": round(input_cost, 4),
        "output_cost": round(output_cost, 4),
        "cache_cost": round(cache_cost, 4),
        "total_cost": round(input_cost + output_cost + cache_cost, 4),
    }


def aggregate_costs(sessions, pricing):
    """Aggregate costs across sessions.

    Returns dict with total, by_project, by_model, and per-session details.
    """
    session_costs = []
    by_project = defaultdict(lambda: {
        "sessions": 0, "input_tokens": 0, "output_tokens": 0,
        "cache_read_tokens": 0, "total_cost": 0.0,
    })
    by_model = defaultdict(lambda: {
        "sessions": 0, "input_tokens": 0, "output_tokens": 0,
        "cache_read_tokens": 0, "total_cost": 0.0,
    })

    total_cost = 0.0
    total_input = 0
    total_output = 0
    total_cache = 0

    for s in sessions:
        cost = calculate_session_cost(s, pricing)
        session_costs.append(cost)
        total_cost += cost["total_cost"]
        total_input += cost["input_tokens"]
        total_output += cost["output_tokens"]
        total_cache += cost["cache_read_tokens"]

        proj = cost["project"] or "unknown"
        by_project[proj]["sessions"] += 1
        by_project[proj]["input_tokens"] += cost["input_tokens"]
        by_project[proj]["output_tokens"] += cost["output_tokens"]
        by_project[proj]["cache_read_tokens"] += cost["cache_read_tokens"]
        by_project[proj]["total_cost"] += cost["total_cost"]

        model = cost["model"] or "unknown"
        by_model[model]["sessions"] += 1
        by_model[model]["input_tokens"] += cost["input_tokens"]
        by_model[model]["output_tokens"] += cost["output_tokens"]
        by_model[model]["cache_read_tokens"] += cost["cache_read_tokens"]
        by_model[model]["total_cost"] += cost["total_cost"]

    # Round aggregated costs
    for proj_data in by_project.values():
        proj_data["total_cost"] = round(proj_data["total_cost"], 4)
    for model_data in by_model.values():
        model_data["total_cost"] = round(model_data["total_cost"], 4)

    # Sort sessions by cost descending
    session_costs.sort(key=lambda x: x["total_cost"], reverse=True)

    return {
        "total": {
            "sessions": len(sessions),
            "input_tokens": total_input,
            "output_tokens": total_output,
            "cache_read_tokens": total_cache,
            "total_cost": round(total_cost, 4),
        },
        "by_project": dict(by_project),
        "by_model": dict(by_model),
        "sessions": session_costs,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate token costs from session index"
    )
    parser.add_argument(
        "--index",
        default=os.path.expanduser("~/.claude/session-intel/index.json"),
        help="Path to session index",
    )
    parser.add_argument(
        "--days", type=int, default=7, help="Days to include (default: 7)"
    )
    parser.add_argument("--project", default=None, help="Filter by project")
    parser.add_argument("--model", default=None, help="Filter by model")
    parser.add_argument("--output", default=None, help="Output JSON file")
    args = parser.parse_args()

    with open(args.index) as f:
        data = json.load(f)

    sessions = data.get("sessions", [])

    # Filter by date
    cutoff = (datetime.now() - timedelta(days=args.days)).isoformat()
    sessions = [
        s for s in sessions
        if (s.get("time", {}).get("start") or "") >= cutoff
    ]

    if args.project:
        sessions = [
            s for s in sessions
            if args.project.lower() in (s.get("project") or "").lower()
        ]
    if args.model:
        sessions = [
            s for s in sessions
            if args.model.lower() in (s.get("model") or "").lower()
        ]

    pricing = load_pricing()
    result = aggregate_costs(sessions, pricing)

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
