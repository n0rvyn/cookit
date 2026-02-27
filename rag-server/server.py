"""
RAG MCP Server — Phase 1

Four tools: search, add_entry, reindex, status

Registration in ~/.claude.json:
{
  "mcpServers": {
    "rag": {
      "command": "/absolute/path/to/rag-server/.venv/bin/python3",
      "args": ["/absolute/path/to/rag-server/server.py"],
      "env": {
        "RAG_DEFAULT_PROJECT": "/absolute/path/to/your-project"
      }
    }
  }
}
"""
from __future__ import annotations
import datetime
import os
import re
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

import db
import search as search_module
import indexer

mcp = FastMCP("rag")

_DEFAULT_PROJECT: str | None = os.environ.get("RAG_DEFAULT_PROJECT") or None

_DIRTY_FLAG_NAME = ".dirty"


def _check_and_clear_dirty(project_root: str | None) -> None:
    """
    If a .dirty flag exists in the project's .claude/rag/ directory, run
    incremental reindex and remove the flag. Silently skips if the embed
    binary is missing, sqlite-vec is unavailable, or project_root is None.
    """
    if not project_root:
        return
    flag = Path(project_root) / ".claude" / "rag" / _DIRTY_FLAG_NAME
    if not flag.exists():
        return
    embed_bin = Path(__file__).parent / "embed" / "embed"
    if not embed_bin.exists() or not db.SQLITE_VEC_AVAILABLE:
        return
    try:
        indexer.reindex_incremental(project_root)
        flag.unlink(missing_ok=True)
    except Exception:
        # Never block search due to background reindex failure
        pass


@mcp.tool()
def search(
    query: str,
    project_root: str | None = None,
    source_type: list[str] | None = None,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Hybrid BM25 + cosine similarity search over indexed documents.

    query: Natural language query, English, Chinese, or mixed
    project_root: Absolute path to project root — Claude should fill from cwd.
                  Falls back to server RAG_DEFAULT_PROJECT env var if omitted.
    source_type: Filter list, e.g. ["error","lesson"]. Omit to search all types.
    top_k: Number of results (default 5)

    Each result: {source_path, section, content, score, line_range}
    Returns empty list if index is empty or no matches found.
    """
    effective_root = project_root or _DEFAULT_PROJECT
    _check_and_clear_dirty(effective_root)
    db_path = db.db_path_for(effective_root)
    if not db_path.exists():
        return [{
            "error": "index.db not found — index has not been built yet.",
            "remediation": (
                f"Run: rag-server/.venv/bin/python3 rag-server/cli.py build "
                f"--project {effective_root or '<project-root>'}"
            ),
        }]
    try:
        results = search_module.search(
            query=query,
            project_root=effective_root,
            source_type=source_type,
            top_k=top_k,
        )
        if not results:
            return [{
                "result_count": 0,
                "message": "No results found in RAG index.",
                "fallback": (
                    "Invoke the spotlight-search agent with the same query "
                    "to search local files via Spotlight: "
                    f'spotlight_query="{query}"'
                ),
            }]
        return results
    except FileNotFoundError as e:
        return [{"error": str(e),
                 "remediation": f"Run: bash {Path(__file__).parent}/embed/build.sh"}]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def add_entry(
    title: str,
    category: str,
    scope: str,
    content: str,
    keywords: list[str],
    source_type: str = "lesson",
    project_root: str | None = None,
) -> dict[str, str]:
    """
    Write a new lesson or error entry and index it immediately.

    title: Short descriptive title
    category: Category slug, e.g. "value-domain", "swiftdata", "swift-concurrency"
    scope: "project" to write to docs/09-lessons-learned/ inside project_root,
           "global" to write to ~/.claude/rag/lessons/
    content: Markdown body of the entry
    keywords: Extra keyword strings for FTS5 boosting
    source_type: Entry type for indexing — "lesson", "error", or "api-ref" (default "lesson")
    project_root: Required when scope is "project"

    Returns {id, path, message}
    """
    effective_root = project_root or _DEFAULT_PROJECT

    if scope == "project":
        if not effective_root:
            return {"error": "project_root is required for scope='project'"}
        base = Path(effective_root) / "docs" / "09-lessons-learned"
    else:
        base = Path.home() / ".claude" / "rag" / "lessons"

    base.mkdir(parents=True, exist_ok=True)

    existing = sorted(base.glob("E[0-9][0-9][0-9]-*.md"))
    next_num = max((int(f.name[1:4]) for f in existing), default=0) + 1
    entry_id = f"E{next_num:03d}"

    slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:40].strip('-')
    filename = f"{entry_id}-{slug}.md"
    file_path = base / filename

    now = datetime.datetime.utcnow().isoformat() + "Z"
    kw_str = " ".join(keywords)
    md = f"""---
id: {entry_id}
title: {title}
category: {category}
source_type: {source_type}
keywords: {kw_str}
created: {now}
---

{content}
"""
    file_path.write_text(md, encoding="utf-8")

    conn = db.open_db(effective_root if scope == "project" else None)
    indexer.load_jieba_dict()
    root_for_idx = effective_root or str(Path.home() / ".claude" / "rag")
    indexer.index_file(conn, file_path, source_type, root_for_idx)
    conn.close()

    return {"id": entry_id, "path": str(file_path), "message": f"Saved and indexed as {entry_id}"}


@mcp.tool()
def reindex(
    project_root: str | None = None,
    source_type: str = "doc",
    incremental: bool = False,
) -> dict[str, Any]:
    """
    Re-index docs/**/*.md files for the given project root.

    project_root: Absolute path to project. Uses RAG_DEFAULT_PROJECT if omitted.
    source_type: Source type label for indexed chunks (default "doc")
    incremental: If True, only re-index files changed since the last indexed commit.
                 Falls back to full reindex if config.json has no last_commit yet.

    Returns {files_scanned, chunks_written, mode} on success, or {error, remediation}.
    """
    effective_root = project_root or _DEFAULT_PROJECT
    if not effective_root:
        return {
            "error": "project_root is required",
            "remediation": "Pass project_root or set RAG_DEFAULT_PROJECT in server env",
        }

    embed_bin = Path(__file__).parent / "embed" / "embed"
    if not embed_bin.exists():
        return {
            "error": "embed binary not found",
            "remediation": f"Run: bash {embed_bin.parent}/build.sh",
        }

    if not db.SQLITE_VEC_AVAILABLE:
        return {
            "error": "sqlite-vec extension not available",
            "remediation": "Run: pip install sqlite-vec (inside the rag-server venv)",
        }

    try:
        if incremental:
            return indexer.reindex_incremental(effective_root, source_type=source_type)
        result = indexer.reindex_project(effective_root, source_type=source_type)
        # Store current HEAD so future incremental runs have a baseline
        import subprocess as _sp
        try:
            head = _sp.run(
                ["git", "-C", effective_root, "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=10,
            )
            if head.returncode == 0:
                db.write_config(effective_root, {"last_commit": head.stdout.strip()})
        except Exception:
            pass
        return result
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def status(project_root: str | None = None) -> dict[str, Any]:
    """
    Return index statistics.

    project_root: Absolute path to project. Uses RAG_DEFAULT_PROJECT if omitted.

    Returns {status, db_path, total_chunks, by_source_type, db_size_kb,
             sqlite_vec_available} or {status: "no_index", ...} with remediation.
    """
    effective_root = project_root or _DEFAULT_PROJECT
    db_path = db.db_path_for(effective_root)

    if not db_path.exists():
        return {
            "status": "no_index",
            "db_path": str(db_path),
            "message": (
                f"No index found. "
                f"Run: reindex(project_root='{effective_root}')"
            ),
        }

    conn = db.open_db(effective_root)
    total = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    by_type = dict(
        conn.execute(
            "SELECT source_type, COUNT(*) FROM chunks GROUP BY source_type"
        ).fetchall()
    )
    conn.close()

    size_kb = db_path.stat().st_size // 1024
    return {
        "status": "ok",
        "db_path": str(db_path),
        "total_chunks": total,
        "by_source_type": by_type,
        "db_size_kb": size_kb,
        "sqlite_vec_available": db.SQLITE_VEC_AVAILABLE,
    }


if __name__ == "__main__":
    mcp.run()
