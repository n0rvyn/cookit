#!/usr/bin/env python3
"""Sync canonical product-lens PKOS notes to a Notion summary database."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


class SyncError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync product-lens PKOS note to Notion summary DB")
    parser.add_argument("--note", required=True, help="Canonical PKOS note path")
    parser.add_argument("--vault-root", default="~/Obsidian/PKOS", help="PKOS vault root")
    parser.add_argument("--database-id", default=None, help="Override Notion database id")
    parser.add_argument("--config-path", default="~/.claude/pkos/config.yaml", help="PKOS config path")
    parser.add_argument("--state-file", default=None, help="Override sync state file path")
    parser.add_argument(
        "--notion-api-script",
        default="~/.claude/skills/notion-with-api/scripts/notion_api.py",
        help="Path to notion_api.py",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print payload only")
    parser.add_argument("--apply", action="store_true", help="Call notion_api.py")
    return parser.parse_args()


def expand_path(raw: str | None) -> Path | None:
    if not raw:
        return None
    return Path(os.path.expanduser(raw)).resolve()


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise SyncError(f"Expected YAML mapping at {path}")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=False)


def parse_frontmatter(raw_text: str) -> tuple[dict[str, Any], str]:
    if not raw_text.startswith("---\n"):
        raise SyncError("Note missing YAML frontmatter")
    closing = raw_text.find("\n---\n", 4)
    if closing == -1:
        raise SyncError("Note missing frontmatter end marker")
    frontmatter_text = raw_text[4:closing]
    body = raw_text[closing + 5 :].lstrip()
    frontmatter = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(frontmatter, dict):
        raise SyncError("Frontmatter is not a mapping")
    return frontmatter, body


def parse_sections(body: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def clean_lines(lines: list[str]) -> list[str]:
    cleaned = [line.strip() for line in lines if line.strip()]
    return cleaned


def first_heading(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def extract_bullet_value(lines: list[str]) -> str:
    cleaned = clean_lines(lines)
    if not cleaned:
        return ""
    first = cleaned[0]
    return re.sub(r"^[\-\d\.\s]+", "", first).strip()


def join_items(lines: list[str]) -> str:
    cleaned = [re.sub(r"^[\-\d\.\s]+", "", line).strip() for line in clean_lines(lines)]
    return "; ".join(item for item in cleaned if item)


def load_database_id(args: argparse.Namespace) -> str:
    if args.database_id:
        return args.database_id
    config_path = expand_path(args.config_path)
    if config_path is None or not config_path.exists():
        raise SyncError("PKOS config not found and --database-id was not provided")
    config = load_yaml(config_path)
    product_lens_cfg = config.get("product_lens_notion", {})
    database_id = product_lens_cfg.get("database_id") if isinstance(product_lens_cfg, dict) else None
    if not database_id:
        raise SyncError("product_lens_notion.database_id missing in PKOS config")
    return str(database_id)


def state_path_for(args: argparse.Namespace, vault_root: Path) -> Path:
    if args.state_file:
        path = expand_path(args.state_file)
        if path is None:
            raise SyncError("Invalid --state-file")
        return path
    return vault_root / ".state" / "product-lens-notion-sync.yaml"


def build_payload(note_path: Path, vault_root: Path) -> tuple[str, dict[str, Any], dict[str, Any]]:
    raw = note_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    sections = parse_sections(body)

    source_type = str(meta.get("type", ""))
    if source_type not in {"signal", "verdict", "feature-review", "crystal"}:
        raise SyncError(f"Unsupported note type for product-lens Notion sync: {source_type}")

    title = first_heading(body, note_path.stem)
    row_type = "feature" if source_type == "feature-review" else "project"
    props: dict[str, Any] = {
        "source_note_id": note_path.stem,
        "row_type": row_type,
        "project": meta.get("project", ""),
        "decision": meta.get("decision", ""),
        "confidence": meta.get("confidence", ""),
        "biggest_risk": extract_bullet_value(sections.get("Biggest Risk", sections.get("Risks", []))),
        "next_actions": join_items(sections.get("Next Actions", sections.get("Suggested Follow-up", []))),
        "source_note_path": str(note_path),
        "source_note_type": source_type,
        "updated_at": datetime.now().date().isoformat(),
        "sync_status": "current",
    }

    if row_type == "project":
        props["project_state"] = meta.get("decision", "")
        if meta.get("producer_intent"):
            props["producer_intent"] = meta["producer_intent"]
        if meta.get("window_days"):
            props["window_days"] = meta["window_days"]
        if meta.get("project_root"):
            props["project_root"] = meta["project_root"]
    else:
        props["feature_name"] = meta.get("feature", "")
        props["feature_state"] = meta.get("decision", "")
        if meta.get("producer_intent"):
            props["producer_intent"] = meta["producer_intent"]
        if meta.get("commit_window_days"):
            props["commit_window_days"] = meta["commit_window_days"]

    state_record = {
        "note_path": str(note_path.relative_to(vault_root)),
        "note_type": source_type,
        "row_type": row_type,
        "updated_at": props["updated_at"],
        "sync_status": "current",
    }
    return title, props, state_record


def parse_page_id(output: str) -> str | None:
    try:
        data = json.loads(output)
        if isinstance(data, dict):
            for key in ("id", "page_id"):
                if data.get(key):
                    return str(data[key])
    except Exception:  # noqa: BLE001
        pass
    match = re.search(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", output, re.I)
    return match.group(0) if match else None


def run_apply(
    args: argparse.Namespace,
    database_id: str,
    note_path: Path,
    title: str,
    props: dict[str, Any],
    state: dict[str, Any],
    state_path: Path,
) -> int:
    api_script = expand_path(args.notion_api_script)
    if api_script is None or not api_script.exists():
        raise SyncError(f"Notion API script not found: {args.notion_api_script}")

    notes_state = state.setdefault("notes", {})
    note_key = str(note_path)
    page_id = notes_state.get(note_key, {}).get("notion_page_id")

    props_json = json.dumps(props, ensure_ascii=True)
    if page_id:
        cmd = [
            "python3",
            str(api_script),
            "update-db-item-properties",
            str(page_id),
            "--props",
            props_json,
        ]
    else:
        cmd = [
            "python3",
            str(api_script),
            "create-db-item",
            database_id,
            title,
            "--props",
            props_json,
        ]

    env = os.environ.copy()
    env["NO_PROXY"] = "*"
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)
    if result.returncode != 0:
        notes_state[note_key] = {
            "sync_status": "failed",
            "updated_at": props["updated_at"],
        }
        state["last_sync"] = datetime.now().isoformat(timespec="seconds")
        write_yaml(state_path, state)
        sys.stderr.write(result.stderr)
        return result.returncode

    new_page_id = page_id or parse_page_id(result.stdout)
    notes_state[note_key] = {
        "notion_page_id": new_page_id or "",
        "sync_status": "current",
        "updated_at": props["updated_at"],
    }
    state["last_sync"] = datetime.now().isoformat(timespec="seconds")
    write_yaml(state_path, state)
    sys.stdout.write(result.stdout)
    return 0


def main() -> int:
    args = parse_args()
    if args.apply and args.dry_run:
        raise SyncError("Use either --dry-run or --apply, not both")

    note_path = expand_path(args.note)
    vault_root = expand_path(args.vault_root)
    if note_path is None or vault_root is None or not note_path.exists():
        raise SyncError("Valid --note and --vault-root are required")

    title, props, state_record = build_payload(note_path, vault_root)
    state_path = state_path_for(args, vault_root)
    state = load_yaml(state_path) if state_path.exists() else {"notes": {}, "last_sync": None}

    if args.dry_run or not args.apply:
        print("Product Lens Notion Sync Dry Run")
        print(f"  Note: {note_path}")
        print(f"  Title: {title}")
        print(json.dumps(props, indent=2, ensure_ascii=True))
        return 0

    database_id = load_database_id(args)
    state.setdefault("notes", {})[str(note_path)] = state_record
    return run_apply(args, database_id, note_path, title, props, state, state_path)


if __name__ == "__main__":
    raise SystemExit(main())
