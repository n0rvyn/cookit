#!/usr/bin/env python3
"""
RAG CLI — manual index management.

Usage:
  rag build                    Full reindex of docs/**/*.md
  rag build --incremental      Re-index only changed files since last commit
  rag status                   Show index statistics
  rag install-hook             Install post-commit hook into .git/hooks/

Run with the rag-server venv:
  rag-server/.venv/bin/python3 rag-server/cli.py <command> [options]

Or install as a script alias in your shell:
  alias rag='rag-server/.venv/bin/python3 rag-server/cli.py'
"""
from __future__ import annotations
import argparse
import os
import shutil
import sys
from pathlib import Path

# Ensure rag-server package is importable when run from repo root
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))

import db
import indexer


def _get_project_root(args) -> str:
    """Return project root from --project arg, env var, or cwd."""
    if hasattr(args, "project") and args.project:
        return args.project
    env = os.environ.get("RAG_DEFAULT_PROJECT")
    if env:
        return env
    return os.getcwd()


def cmd_build(args) -> None:
    project_root = _get_project_root(args)
    embed_bin = _HERE / "embed" / "embed"
    if not embed_bin.exists():
        print(f"ERROR: embed binary not found. Run: bash {embed_bin.parent}/build.sh", file=sys.stderr)
        sys.exit(1)
    if not db.SQLITE_VEC_AVAILABLE:
        print("ERROR: sqlite-vec not available. Run: pip install sqlite-vec", file=sys.stderr)
        sys.exit(1)

    if args.incremental:
        print(f"Incremental reindex: {project_root}")
        result = indexer.reindex_incremental(project_root)
        # Record embedding model info
        db.write_config(project_root, {
            "embed_model": "NLContextualEmbedding (Latin + CJK, 512-dim, macOS 14+)"
        })
    else:
        print(f"Full reindex: {project_root}")
        result = indexer.reindex_project(project_root)
        # Store current HEAD after full build
        import subprocess
        try:
            head = subprocess.run(
                ["git", "-C", project_root, "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=10,
            )
            if head.returncode == 0:
                db.write_config(project_root, {"last_commit": head.stdout.strip()})
        except Exception:
            pass
        # Record embedding model info
        db.write_config(project_root, {
            "embed_model": "NLContextualEmbedding (Latin + CJK, 512-dim, macOS 14+)"
        })

    mode = result.get("mode", "full" if not args.incremental else "incremental")
    print(f"Done ({mode}): {result.get('files_scanned', 0)} files scanned, "
          f"{result.get('chunks_written', 0)} chunks written")
    if result.get("deleted_files"):
        print(f"  Deleted chunks for {result['deleted_files']} removed files")


def cmd_status(args) -> None:
    project_root = _get_project_root(args)
    db_path = db.db_path_for(project_root)
    cfg = db.read_config(project_root)
    dirty_flag = Path(project_root) / ".claude" / "rag" / ".dirty"

    if not db_path.exists():
        print(f"No index found at {db_path}")
        print(f"Run: rag build --project {project_root}")
        return

    conn = db.open_db(project_root)
    total = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    by_type = dict(
        conn.execute(
            "SELECT source_type, COUNT(*) FROM chunks GROUP BY source_type"
        ).fetchall()
    )
    conn.close()

    size_kb = db_path.stat().st_size // 1024
    last_commit = cfg.get("last_commit", "unknown")
    dirty = dirty_flag.exists()

    print(f"Index: {db_path}")
    print(f"  Total chunks:    {total}")
    for st, count in sorted(by_type.items()):
        print(f"  {st:<16} {count}")
    print(f"  Size:            {size_kb} KB")
    print(f"  Last commit:     {last_commit[:12] if last_commit != 'unknown' else 'unknown'}")
    print(f"  Dirty flag:      {'yes (reindex pending)' if dirty else 'no'}")
    print(f"  sqlite-vec:      {'available' if db.SQLITE_VEC_AVAILABLE else 'NOT available'}")
    embed_model = cfg.get("embed_model", "NLContextualEmbedding (Latin + CJK, 512-dim) — run 'rag build' to confirm")
    print(f"  Embed model:     {embed_model}")


def cmd_install_hook(args) -> None:
    project_root = _get_project_root(args)
    src = _HERE / "hooks" / "post-commit"
    git_hooks_dir = Path(project_root) / ".git" / "hooks"

    if not git_hooks_dir.exists():
        print(f"ERROR: {git_hooks_dir} not found. Is {project_root} a git repo?", file=sys.stderr)
        sys.exit(1)

    if not src.exists():
        print(f"ERROR: hook source not found at {src}", file=sys.stderr)
        sys.exit(1)

    dst = git_hooks_dir / "post-commit"
    if dst.exists():
        print(f"WARNING: {dst} already exists. Overwriting.")

    shutil.copy2(src, dst)
    dst.chmod(0o755)
    print(f"Installed post-commit hook to {dst}")
    print("The hook will write .claude/rag/.dirty after each commit,")
    print("triggering an incremental reindex at the next MCP search call.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="rag",
        description="RAG index management CLI",
    )
    parser.add_argument(
        "--project", metavar="PATH",
        help="Project root path (default: RAG_DEFAULT_PROJECT env var or cwd)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # build
    p_build = sub.add_parser("build", help="Index docs/**/*.md files")
    p_build.add_argument(
        "--incremental", action="store_true",
        help="Re-index only files changed since last indexed commit",
    )
    p_build.set_defaults(func=cmd_build)

    # status
    p_status = sub.add_parser("status", help="Show index statistics")
    p_status.set_defaults(func=cmd_status)

    # install-hook
    p_hook = sub.add_parser("install-hook", help="Install git post-commit hook")
    p_hook.set_defaults(func=cmd_install_hook)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
