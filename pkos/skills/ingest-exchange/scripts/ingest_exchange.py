#!/usr/bin/env python3
"""Ingest PKOS exchange artifacts into canonical vault notes.

Consumes IEF-compliant directive artifacts from producer export directories
(e.g., product-lens exchange output). Validates against the IEF envelope,
compiles into canonical PKOS note shapes, and archives the source artifact
out of the producer's directory so repeat scans do not re-see it.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


INTENT_TO_NOTE_TYPE = {
    "portfolio_scan": "signal",
    "project_progress_pulse": "signal",
    "repo_reprioritize": "verdict",
    "recent_feature_review": "feature-review",
    "verdict_refresh": "verdict",
}

NOTE_TYPE_TO_DIR = {
    "signal": "Signals",
    "verdict": "Verdicts",
    "feature-review": "Feature Reviews",
}


@dataclass
class Artifact:
    path: Path
    meta: dict[str, Any]
    body: str
    checksum: str


class IngestError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest PKOS exchange artifacts")
    parser.add_argument("--producer", default=None, help="Filter producer name")
    parser.add_argument("--intent", default=None, help="Filter producer intent")
    parser.add_argument("--source", default=None, help="Read one explicit artifact path")
    parser.add_argument("--dry-run", action="store_true", help="Show mapping without writing")
    parser.add_argument("--sync-notion", action="store_true", help="Run product-lens Notion sync after note write")
    parser.add_argument("--notion-dry-run", action="store_true", help="Print the Notion payload after note write")
    parser.add_argument("--notion-database-id", default=None, help="Override product-lens Notion database id")
    parser.add_argument(
        "--exchange-root",
        default="~/Obsidian/PKOS/.exchange",
        help="Exchange root directory",
    )
    parser.add_argument(
        "--vault-root",
        default="~/Obsidian/PKOS",
        help="Target PKOS vault root",
    )
    parser.add_argument(
        "--archive-root",
        default="~/.pkos/ingested",
        help="Where to move consumed artifacts after successful import (IEF 'consumer archives out of producer dir' convention)",
    )
    parser.add_argument(
        "--no-archive",
        action="store_true",
        help="Skip archiving consumed artifacts (useful for tests; breaks IEF cleanup contract)",
    )
    parser.add_argument(
        "--state-file",
        default=None,
        help="Override state file path",
    )
    return parser.parse_args()


def expand_path(raw: str | None) -> Path | None:
    if not raw:
        return None
    return Path(os.path.expanduser(raw)).resolve()


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value.strip())
    return cleaned.strip("-").lower() or "item"


def load_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise IngestError(f"State file is not a mapping: {path}")
    return data


def write_yaml_file(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=False)


def parse_frontmatter(raw_text: str) -> tuple[dict[str, Any], str]:
    if not raw_text.startswith("---\n"):
        raise IngestError("Artifact missing YAML frontmatter start marker")
    closing = raw_text.find("\n---\n", 4)
    if closing == -1:
        raise IngestError("Artifact missing YAML frontmatter end marker")
    frontmatter_text = raw_text[4:closing]
    body = raw_text[closing + 5 :].lstrip()
    frontmatter = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(frontmatter, dict):
        raise IngestError("Artifact frontmatter is not a mapping")
    return frontmatter, body


def compute_checksum(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def load_artifact(path: Path) -> Artifact:
    raw = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    return Artifact(path=path, meta=meta, body=body, checksum=compute_checksum(path))


def discover_artifacts(args: argparse.Namespace, exchange_root: Path) -> list[Path]:
    explicit = expand_path(args.source)
    if explicit:
        if not explicit.exists():
            raise IngestError(f"Explicit artifact not found: {explicit}")
        return [explicit]

    base = exchange_root
    if args.producer:
        base = base / args.producer
    if args.intent:
        base = base / args.intent
    if not base.exists():
        return []
    return sorted(base.rglob("*.md"))


IEF_REQUIRED_FIELDS = ("id", "source", "url", "title", "significance", "tags", "category", "domain", "date", "read")


def validate_artifact(artifact: Artifact, expected_producer: str | None) -> None:
    meta = artifact.meta
    # IEF envelope checks
    missing = [f for f in IEF_REQUIRED_FIELDS if f not in meta]
    if missing:
        raise IngestError(f"Artifact missing IEF required fields: {', '.join(missing)}")
    if meta.get("category") != "directive":
        raise IngestError(f"Only category=directive is supported; got {meta.get('category')!r}")
    source = meta.get("source")
    if expected_producer and source != expected_producer:
        raise IngestError(f"Artifact source mismatch: {source}")
    if source != "product-lens":
        raise IngestError(f"Only product-lens source is supported in V1 (got {source!r})")
    # Directive extended fields (product-lens specific)
    intent = meta.get("intent")
    if intent not in INTENT_TO_NOTE_TYPE:
        raise IngestError(f"Unsupported intent: {intent}")
    if not meta.get("decision"):
        raise IngestError("Artifact decision is required")
    # Directive body sections (bold-label format per IEF directive template)
    for marker in ("**Context:**", "**Next actions:**", "**Evidence:**"):
        if marker not in artifact.body:
            raise IngestError(f"Artifact missing required directive section: {marker}")


def state_file_for(args: argparse.Namespace, vault_root: Path) -> Path:
    if args.state_file:
        return expand_path(args.state_file)  # type: ignore[return-value]
    return vault_root / ".state" / "exchange-ingest.yaml"


def note_type_for(artifact: Artifact) -> str:
    return INTENT_TO_NOTE_TYPE[artifact.meta["intent"]]


def normalize_project(meta: dict[str, Any]) -> str:
    if meta.get("project"):
        return str(meta["project"]).strip()
    targets = meta.get("targets") or []
    if isinstance(targets, list) and targets:
        return Path(str(targets[0]).rstrip("/")).name or "_Portfolio"
    return "_Portfolio"


def normalize_feature(meta: dict[str, Any]) -> str | None:
    feature = meta.get("feature")
    if feature:
        return slugify(str(feature))
    return None


def created_date_for(meta: dict[str, Any]) -> str:
    created = meta.get("created")
    if created:
        return str(created)
    return datetime.now().date().isoformat()


def target_note_path(vault_root: Path, artifact: Artifact) -> Path:
    note_type = note_type_for(artifact)
    project = normalize_project(artifact.meta)
    created = created_date_for(artifact.meta)
    feature_slug = normalize_feature(artifact.meta)

    if project == "_Portfolio":
        base_dir = vault_root / "30-Projects" / "_Portfolio"
    else:
        base_dir = vault_root / "30-Projects" / project / NOTE_TYPE_TO_DIR[note_type]

    if note_type == "signal":
        filename = f"{created}-{project}-signal.md"
    elif note_type == "verdict":
        filename = f"{created}-{project}-verdict.md"
    else:
        feature_slug = feature_slug or "feature-slice"
        filename = f"{created}-{project}-{feature_slug}-feature-review.md"
    return base_dir / filename


BOLD_LABEL_RE = re.compile(r"^\*\*([A-Za-z][A-Za-z ]+):\*\*\s*(.*)$")


def parse_sections(body: str) -> dict[str, list[str]]:
    """Parse IEF directive bold-label sections into {normalized_key: [lines...]}.

    Example input:
        **Context:**
        1. first reason
        2. second reason

        **Next actions:**
        1. do the thing

    Returns:
        {"context": ["1. first reason", "2. second reason"],
         "next_actions": ["1. do the thing"]}

    Single-line fields (Intent / Decision / Confidence / Biggest risk) are captured as a single-element list.
    """
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        match = BOLD_LABEL_RE.match(line)
        if match:
            current = match.group(1).strip().lower().replace(" ", "_")
            first_inline = match.group(2).strip()
            sections[current] = [first_inline] if first_inline else []
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def strip_blank_edges(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def extract_summary_fields(sections: dict[str, list[str]]) -> tuple[str | None, str | None]:
    """Pull decision and biggest_risk from parsed directive sections.

    Decision comes from the ``decision`` section (may be wrapped in backticks).
    Biggest risk comes from the ``biggest_risk`` section.
    """
    decision_lines = strip_blank_edges(sections.get("decision", []))
    decision = decision_lines[0].strip("` ") if decision_lines else None

    risk_lines = strip_blank_edges(sections.get("biggest_risk", []))
    biggest_risk = risk_lines[0] if risk_lines else None

    return decision, biggest_risk


def note_title(note_type: str, project: str, feature_slug: str | None) -> str:
    if note_type == "signal":
        return f"{project} Signal"
    if note_type == "verdict":
        return f"{project} Verdict"
    display = feature_slug.replace("-", " ").title() if feature_slug else "Feature Review"
    return f"{project} {display} Feature Review"


def normalize_tags(meta: dict[str, Any], note_type: str, project: str) -> list[str]:
    tags = meta.get("tags") or []
    if not isinstance(tags, list):
        tags = [str(tags)]
    normalized = [str(tag).strip() for tag in tags if str(tag).strip()]
    normalized.extend(["product-lens", note_type, slugify(project)])
    seen: set[str] = set()
    ordered: list[str] = []
    for tag in normalized:
        if tag not in seen:
            seen.add(tag)
            ordered.append(tag)
    return ordered


def discover_superseded_notes(target_path: Path, artifact: Artifact) -> list[Path]:
    note_type = note_type_for(artifact)
    if note_type == "signal":
        return []
    target_dir = target_path.parent
    if not target_dir.exists():
        return []

    candidates = sorted(target_dir.glob("*.md"))
    superseded: list[Path] = []
    feature_slug = normalize_feature(artifact.meta)
    for candidate in candidates:
        if candidate == target_path:
            continue
        name = candidate.name
        if note_type == "verdict" and name.endswith("-verdict.md"):
            superseded.append(candidate)
        if note_type == "feature-review" and feature_slug and name.endswith(f"-{feature_slug}-feature-review.md"):
            superseded.append(candidate)
    return superseded


def final_frontmatter(artifact: Artifact, target_path: Path, superseded: list[Path]) -> dict[str, Any]:
    meta = artifact.meta
    note_type = note_type_for(artifact)
    project = normalize_project(meta)
    feature_slug = normalize_feature(meta)
    frontmatter: dict[str, Any] = {
        "type": note_type,
        "source": "product-lens",
        "created": created_date_for(meta),
        "tags": normalize_tags(meta, note_type, project),
        "quality": 1 if note_type == "signal" else 2,
        "citations": 0,
        "related": [],
        "status": "fresh" if note_type == "signal" else "active",
        "producer_intent": meta["intent"],
        "decision": meta["decision"],
        "confidence": meta.get("confidence", "medium"),
        "project": project,
        "exchange_source": str(artifact.path),
    }
    if note_type == "feature-review" and feature_slug:
        frontmatter["feature"] = feature_slug
        if meta.get("window_days"):
            frontmatter["commit_window_days"] = meta["window_days"]
    if meta.get("notion_sync_requested"):
        frontmatter["projection_status"] = "pending"
    if superseded:
        frontmatter["replaces"] = [f"[[{path.stem}]]" for path in superseded]
    return frontmatter


def final_body(artifact: Artifact) -> str:
    note_type = note_type_for(artifact)
    project = normalize_project(artifact.meta)
    feature_slug = normalize_feature(artifact.meta)
    title = note_title(note_type, project, feature_slug)
    sections = parse_sections(artifact.body)
    reasons = strip_blank_edges(sections.get("context", []))
    actions = strip_blank_edges(sections.get("next_actions", []))
    evidence = strip_blank_edges(sections.get("evidence", []))
    _, biggest_risk = extract_summary_fields(sections)

    lines = [f"# {title}", ""]
    if note_type == "signal":
        lines.extend(["## Observable Signals"])
        lines.extend(reasons or ["- No context signals recorded"])
        lines.extend(["", "## Risks"])
        lines.append(f"- {biggest_risk}" if biggest_risk else "- No primary risk recorded")
        lines.extend(["", "## Suggested Follow-up"])
        lines.extend(actions or ["- No follow-up actions recorded"])
    elif note_type == "verdict":
        lines.extend(["## Recommendation", f"- {artifact.meta['decision']}", "", "## Why"])
        lines.extend(reasons or ["- No reasons recorded"])
        lines.extend(["", "## Biggest Risk"])
        lines.append(f"- {biggest_risk}" if biggest_risk else "- No primary risk recorded")
        lines.extend(["", "## Next Actions"])
        lines.extend(actions or ["- No next actions recorded"])
    else:
        lines.extend(["## Feature Slice"])
        lines.append(f"- {feature_slug.replace('-', ' ').title()}" if feature_slug else "- Recent feature slice")
        lines.extend(["", "## Recommendation", f"- {artifact.meta['decision']}", "", "## Why"])
        lines.extend(reasons or ["- No reasons recorded"])
        lines.extend(["", "## Biggest Risk"])
        lines.append(f"- {biggest_risk}" if biggest_risk else "- No primary risk recorded")
        lines.extend(["", "## Next Actions"])
        lines.extend(actions or ["- No next actions recorded"])

    lines.extend(["", "## Evidence"])
    lines.extend(evidence or ["- No evidence paths recorded"])
    return "\n".join(lines).rstrip() + "\n"


def render_markdown(frontmatter: dict[str, Any], body: str) -> str:
    yaml_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=False).strip()
    return f"---\n{yaml_text}\n---\n\n{body}"


def print_dry_run(
    artifact: Artifact,
    target_path: Path,
    note_type: str,
    superseded: list[Path],
    pending_projection: bool,
) -> None:
    print("PKOS Exchange Dry Run")
    print(f"  Artifact: {artifact.path}")
    print(f"  Producer: {artifact.meta.get('producer')}")
    print(f"  Intent: {artifact.meta.get('intent')}")
    print(f"  Note type: {note_type}")
    print(f"  Target: {target_path}")
    print(f"  Supersedes: {', '.join(str(path) for path in superseded) if superseded else 'none'}")
    print(f"  Projection: {'pending' if pending_projection else 'not-requested'}")


def run_notion_sync(
    note_path: Path,
    args: argparse.Namespace,
    vault_root: Path,
) -> int:
    sync_script = Path(__file__).with_name("sync_product_lens_notion.py")
    cmd = [
        "python3",
        str(sync_script),
        "--note",
        str(note_path),
        "--vault-root",
        str(vault_root),
    ]
    if args.notion_database_id:
        cmd.extend(["--database-id", args.notion_database_id])
    if args.notion_dry_run:
        cmd.append("--dry-run")
    elif args.sync_notion:
        cmd.append("--apply")
    else:
        return 0

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    return result.returncode


def archive_artifact(artifact_path: Path, archive_root: Path, created_date: str) -> Path:
    """Move the consumed artifact out of the producer's export dir into the consumer's archive.

    Destination: {archive_root}/{YYYY-MM}/{original_filename}. If a file with the same
    name already exists, suffix with the current epoch seconds to avoid collision.
    Implements the IEF 'consumer removes source files from producer directory' convention.
    """
    # YYYY-MM partition based on the artifact's stated date (falls back to today).
    try:
        year_month = created_date[:7]  # "2026-04"
    except Exception:  # noqa: BLE001
        year_month = datetime.now().strftime("%Y-%m")
    if not re.match(r"^\d{4}-\d{2}$", year_month):
        year_month = datetime.now().strftime("%Y-%m")

    dest_dir = archive_root / year_month
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / artifact_path.name
    if dest.exists():
        suffix = datetime.now().strftime("%Y%m%dT%H%M%S")
        dest = dest_dir / f"{artifact_path.stem}.{suffix}{artifact_path.suffix}"
    shutil.move(str(artifact_path), str(dest))
    return dest


def process_artifact(
    artifact_path: Path,
    args: argparse.Namespace,
    vault_root: Path,
    state: dict[str, Any],
    state_path: Path,
    archive_root: Path,
) -> int:
    artifact_key = str(artifact_path)
    artifacts_state = state.setdefault("artifacts", {})

    try:
        artifact = load_artifact(artifact_path)
        validate_artifact(artifact, args.producer)
        previous = artifacts_state.get(artifact_key, {})
        if previous.get("checksum") == artifact.checksum:
            previous.update({"status": "skipped_unchanged"})
            state["last_sync"] = datetime.now().isoformat(timespec="seconds")
            write_yaml_file(state_path, state)
            print(f"Skipped unchanged artifact: {artifact.path}")
            return 0

        target_path = target_note_path(vault_root, artifact)
        note_type = note_type_for(artifact)
        superseded = discover_superseded_notes(target_path, artifact)
        pending_projection = bool(artifact.meta.get("notion_sync_requested"))

        if args.dry_run:
            print_dry_run(artifact, target_path, note_type, superseded, pending_projection)
            return 0

        frontmatter = final_frontmatter(artifact, target_path, superseded)
        body = final_body(artifact)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(render_markdown(frontmatter, body), encoding="utf-8")

        # Archive consumed artifact out of the producer's export directory (IEF convention).
        archived_to: Path | None = None
        if not args.no_archive:
            archived_to = archive_artifact(artifact_path, archive_root, str(artifact.meta.get("date", "")))

        artifacts_state[artifact_key] = {
            "imported_at": datetime.now().isoformat(timespec="seconds"),
            "checksum": artifact.checksum,
            "status": "imported",
            "note_type": note_type,
            "note_path": str(target_path.relative_to(vault_root)),
            "superseded_notes": [str(path.relative_to(vault_root)) for path in superseded if path.exists()],
            "archived_to": str(archived_to) if archived_to else None,
        }
        state["last_sync"] = datetime.now().isoformat(timespec="seconds")
        write_yaml_file(state_path, state)
        if archived_to:
            print(f"Imported {artifact.path} -> {target_path} (archived to {archived_to})")
        else:
            print(f"Imported {artifact.path} -> {target_path}")
        if pending_projection and (args.sync_notion or args.notion_dry_run):
            sync_exit = run_notion_sync(target_path, args, vault_root)
            if sync_exit != 0:
                return sync_exit
        return 0
    except IngestError as exc:
        artifacts_state[artifact_key] = {
            "imported_at": datetime.now().isoformat(timespec="seconds"),
            "checksum": compute_checksum(artifact_path) if artifact_path.exists() else "",
            "status": "failed_validation",
            "note_type": "",
            "note_path": "",
            "superseded_notes": [],
        }
        state["last_sync"] = datetime.now().isoformat(timespec="seconds")
        write_yaml_file(state_path, state)
        print(f"Validation failed for {artifact_path}: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        artifacts_state[artifact_key] = {
            "imported_at": datetime.now().isoformat(timespec="seconds"),
            "checksum": compute_checksum(artifact_path) if artifact_path.exists() else "",
            "status": "failed_write",
            "note_type": "",
            "note_path": "",
            "superseded_notes": [],
        }
        state["last_sync"] = datetime.now().isoformat(timespec="seconds")
        write_yaml_file(state_path, state)
        print(f"Write failed for {artifact_path}: {exc}", file=sys.stderr)
        return 1


def main() -> int:
    args = parse_args()
    exchange_root = expand_path(args.exchange_root)
    vault_root = expand_path(args.vault_root)
    archive_root = expand_path(args.archive_root)
    if exchange_root is None or vault_root is None or archive_root is None:
        raise IngestError("Failed to resolve required paths")

    artifacts = discover_artifacts(args, exchange_root)
    if not artifacts:
        print("No exchange artifacts found.")
        return 0

    state_path = state_file_for(args, vault_root)
    state = load_yaml_file(state_path) if state_path.exists() else {"artifacts": {}, "last_sync": None}

    exit_code = 0
    for artifact_path in artifacts:
        exit_code = max(exit_code, process_artifact(artifact_path, args, vault_root, state, state_path, archive_root))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
