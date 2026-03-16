#!/usr/bin/env python3
"""ASCII chart rendering utilities. Pure Python stdlib."""

import argparse
import json
import sys


def render_bar_chart(data, title, value_formatter=None, bar_width=40):
    """Render a horizontal bar chart with Unicode block characters.

    Args:
        data: list of {"label": str, "value": number} dicts
        title: chart title string
        value_formatter: function(value) -> str, or None for raw numbers
        bar_width: max width of bar in characters

    Returns:
        Rendered chart as string
    """
    if not data:
        return f"{title}\n(no data)"

    # Filter out None values
    data = [d for d in data if d.get("value") is not None]
    if not data:
        return f"{title}\n(no data)"

    if value_formatter is None:
        value_formatter = str

    max_value = max(d["value"] for d in data)
    if max_value == 0:
        max_value = 1

    max_label_len = max(len(str(d["label"])) for d in data)
    peak_idx = max(range(len(data)), key=lambda i: data[i]["value"])

    lines = [title]
    for i, d in enumerate(data):
        label = str(d["label"]).ljust(max_label_len)
        value = d["value"]
        filled = int((value / max_value) * bar_width) if max_value > 0 else 0
        empty = bar_width - filled
        bar = "█" * filled + "░" * empty
        formatted = value_formatter(value)
        peak_marker = "  ← peak" if i == peak_idx and len(data) > 1 else ""
        lines.append(f"{label} {bar} {formatted}{peak_marker}")

    return "\n".join(lines)


def format_number(n):
    """Format number with K/M suffixes."""
    if n is None:
        return "—"
    if abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if abs(n) >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(int(n))


def format_percent(n):
    """Format as percentage."""
    if n is None:
        return "—"
    return f"{n * 100:.0f}%" if n <= 1 else f"{n:.0f}%"


def format_duration(mins):
    """Format minutes as 'Xh Ym' or 'Xm'."""
    if mins is None:
        return "—"
    if mins >= 60:
        h = int(mins // 60)
        m = int(mins % 60)
        return f"{h}h {m}m"
    return f"{int(mins)}m"


def format_currency(n):
    """Format as USD currency."""
    if n is None:
        return "—"
    if abs(n) >= 1000:
        return f"${n:,.0f}"
    if abs(n) >= 1:
        return f"${n:.2f}"
    return f"${n:.4f}"


FORMATTERS = {
    "number": format_number,
    "percent": format_percent,
    "duration": format_duration,
    "currency": format_currency,
}


def main():
    parser = argparse.ArgumentParser(description="Render ASCII bar chart")
    parser.add_argument(
        "--data", required=True,
        help='JSON array of {"label": str, "value": number} objects'
    )
    parser.add_argument("--title", default="Chart", help="Chart title")
    parser.add_argument(
        "--format", choices=["number", "percent", "duration", "currency"],
        default="number", help="Value format type"
    )
    parser.add_argument(
        "--width", type=int, default=40, help="Bar width in chars"
    )
    args = parser.parse_args()

    data = json.loads(args.data)
    formatter = FORMATTERS[args.format]
    print(render_bar_chart(data, args.title, formatter, args.width))


if __name__ == "__main__":
    main()
