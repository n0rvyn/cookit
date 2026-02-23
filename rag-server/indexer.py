"""
Indexing pipeline: reads docs/**/*.md, chunks by markdown heading,
pre-tokenizes Chinese with jieba, generates dual embeddings via Swift CLI,
writes to index.db.
"""
from __future__ import annotations
import datetime
import hashlib
import re
import subprocess
from pathlib import Path

import jieba

import db

EMBED_BIN = Path(__file__).parent / "embed" / "embed"
CHUNK_CHAR_BUDGET = 800  # ~200 tokens for mixed CJK+ASCII (1 token ~= 4 chars)
_JIEBA_LOADED = False


def load_jieba_dict() -> None:
    global _JIEBA_LOADED
    if _JIEBA_LOADED:
        return
    dict_path = Path(__file__).parent / "tech-terms.txt"
    if dict_path.exists():
        jieba.load_userdict(str(dict_path))
    _JIEBA_LOADED = True


def jieba_tokenize(text: str) -> str:
    """Return space-separated tokens for FTS5 keywords field."""
    load_jieba_dict()
    return " ".join(jieba.cut(text))


def split_by_heading(content: str, default_section: str) -> list[dict]:
    """
    Split markdown content into chunks at heading boundaries.
    Heading levels 1-3 trigger a new chunk.
    Large sections are further split at paragraph boundaries.

    Returns list of {section, content, line_start, line_end}.
    """
    lines = content.splitlines(keepends=True)
    chunks: list[dict] = []
    current_section = default_section
    current_body: list[str] = []
    current_start = 1

    def flush(section: str, body: list[str], start: int) -> None:
        text = "".join(body).strip()
        if not text:
            return
        if len(text) <= CHUNK_CHAR_BUDGET:
            chunks.append({
                "section": section,
                "content": text,
                "line_start": start,
                "line_end": start + len(body) - 1,
            })
            return
        # Split large sections at paragraph boundaries
        paras = re.split(r'\n{2,}', text)
        sub_buf: list[str] = []
        sub_chars = 0
        sub_start = start
        for para in paras:
            if sub_chars + len(para) > CHUNK_CHAR_BUDGET and sub_buf:
                sub_text = "\n\n".join(sub_buf)
                chunks.append({
                    "section": section,
                    "content": sub_text,
                    "line_start": sub_start,
                    "line_end": sub_start + sub_text.count('\n'),
                })
                sub_start += sub_text.count('\n') + 2
                sub_buf = [para]
                sub_chars = len(para)
            else:
                sub_buf.append(para)
                sub_chars += len(para)
        if sub_buf:
            sub_text = "\n\n".join(sub_buf)
            chunks.append({
                "section": section,
                "content": sub_text,
                "line_start": sub_start,
                "line_end": sub_start + sub_text.count('\n'),
            })

    for i, line in enumerate(lines, start=1):
        if re.match(r'^#{1,3}\s+', line):
            flush(current_section, current_body, current_start)
            current_section = line.strip().lstrip('#').strip()
            current_body = []
            current_start = i
        else:
            current_body.append(line)

    flush(current_section, current_body, current_start)
    return chunks


def get_embeddings(text: str) -> tuple[list[float], list[float]] | None:
    """
    Call the Swift embed binary with text as argument.
    Returns (latin_vec, cjk_vec) where each is a list of 512 floats.
    Returns None if the binary is missing, crashes, or produces unexpected output.
    """
    if not EMBED_BIN.exists():
        raise FileNotFoundError(
            f"embed binary not found at {EMBED_BIN}. "
            f"Run: bash {EMBED_BIN.parent}/build.sh"
        )
    try:
        result = subprocess.run(
            [str(EMBED_BIN), text],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return None

    if result.returncode != 0:
        return None

    output_lines = result.stdout.strip().splitlines()
    if len(output_lines) < 2:
        return None

    try:
        latin_vec = [float(x) for x in output_lines[0].split(",")]
        cjk_vec = [float(x) for x in output_lines[1].split(",")]
    except ValueError:
        return None

    if len(latin_vec) != 512 or len(cjk_vec) != 512:
        return None

    return latin_vec, cjk_vec


def _chunk_id(source_path: str, section: str, line_start: int) -> str:
    raw = f"{source_path}::{section}::{line_start}"
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


def index_file(
    conn,
    filepath: Path,
    source_type: str,
    project_root: str,
) -> int:
    """
    Index a single markdown file into the open database connection.
    Returns the number of chunks written.
    """
    load_jieba_dict()
    content = filepath.read_text(encoding="utf-8", errors="replace")
    chunks = split_by_heading(content, filepath.stem)

    try:
        rel_path = str(filepath.relative_to(project_root))
    except ValueError:
        rel_path = str(filepath)

    # Delete stale chunks for this file before re-indexing (prevents accumulation
    # when line numbers shift). FTS5 triggers handle chunks_fts cleanup automatically.
    stale_rowids = [r[0] for r in conn.execute(
        "SELECT rowid FROM chunks WHERE source_path = ?", (rel_path,)
    ).fetchall()]
    if stale_rowids:
        conn.execute("DELETE FROM chunks WHERE source_path = ?", (rel_path,))
        if db.SQLITE_VEC_AVAILABLE:
            placeholders = ",".join("?" * len(stale_rowids))
            conn.execute(f"DELETE FROM chunks_vec_latin WHERE rowid IN ({placeholders})", stale_rowids)
            conn.execute(f"DELETE FROM chunks_vec_cjk WHERE rowid IN ({placeholders})", stale_rowids)

    now = datetime.datetime.utcnow().isoformat() + "Z"
    written = 0

    for chunk in chunks:
        cid = _chunk_id(rel_path, chunk["section"], chunk["line_start"])
        keywords = jieba_tokenize(chunk["content"])

        emb = get_embeddings(chunk["content"])
        if emb is None:
            continue
        latin_vec, cjk_vec = emb

        # Upsert into chunks table (triggers keep chunks_fts in sync)
        conn.execute(
            """
            INSERT OR REPLACE INTO chunks
              (id, source_type, source_path, section, content,
               line_start, line_end, keywords, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cid, source_type, rel_path, chunk["section"],
                chunk["content"], chunk["line_start"], chunk["line_end"],
                keywords, now,
            ),
        )

        rowid = conn.execute(
            "SELECT rowid FROM chunks WHERE id = ?", (cid,)
        ).fetchone()[0]

        if db.SQLITE_VEC_AVAILABLE:
            conn.execute(
                "INSERT OR REPLACE INTO chunks_vec_latin(rowid, embedding) VALUES (?, ?)",
                (rowid, db.serialize_vec(latin_vec)),
            )
            conn.execute(
                "INSERT OR REPLACE INTO chunks_vec_cjk(rowid, embedding) VALUES (?, ?)",
                (rowid, db.serialize_vec(cjk_vec)),
            )

        written += 1

    conn.commit()
    return written


def reindex_project(project_root: str, source_type: str = "doc") -> dict:
    """
    Index all docs/**/*.md files under project_root.
    Returns {files_scanned, chunks_written}.
    """
    conn = db.open_db(project_root)
    md_files = list(Path(project_root).glob("docs/**/*.md"))
    total = 0
    for f in md_files:
        total += index_file(conn, f, source_type, project_root)
    conn.close()
    return {"files_scanned": len(md_files), "chunks_written": total, "mode": "full"}


def reindex_incremental(project_root: str, source_type: str = "doc") -> dict:
    """
    Re-index only files that changed since the last indexed commit.

    Reads last_commit from config.json, runs `git diff --name-only <hash> HEAD`,
    re-chunks only the changed docs/**/*.md files, deletes chunks for deleted files,
    and writes the new HEAD commit hash back to config.json.

    Falls back to full reindex if:
    - config.json has no last_commit (first run)
    - git is not available
    - last_commit hash is not in the repo (history rewrite)

    Returns {files_scanned, chunks_written, mode} where mode is "incremental" or "full".
    """
    cfg = db.read_config(project_root)
    last_commit = cfg.get("last_commit")

    # Get current HEAD commit hash
    try:
        head_result = subprocess.run(
            ["git", "-C", project_root, "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        if head_result.returncode != 0:
            raise RuntimeError("git rev-parse HEAD failed")
        head_commit = head_result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired, RuntimeError):
        # git not available — fall back to full reindex
        result = reindex_project(project_root, source_type)
        result["mode"] = "full"
        return result

    if not last_commit or last_commit == head_commit:
        if not last_commit:
            # First run — full reindex
            result = reindex_project(project_root, source_type)
            result["mode"] = "full"
            db.write_config(project_root, {"last_commit": head_commit})
            return result
        # Already up to date
        db.write_config(project_root, {"last_commit": head_commit})
        return {"files_scanned": 0, "chunks_written": 0, "mode": "incremental"}

    # Get list of changed files between last_commit and HEAD
    try:
        diff_result = subprocess.run(
            ["git", "-C", project_root, "diff", "--name-only", last_commit, "HEAD"],
            capture_output=True, text=True, timeout=30,
        )
        if diff_result.returncode != 0:
            # last_commit not in history (e.g. after rebase) — full reindex
            result = reindex_project(project_root, source_type)
            result["mode"] = "full"
            db.write_config(project_root, {"last_commit": head_commit})
            return result
        changed_paths = diff_result.stdout.strip().splitlines()
    except (OSError, subprocess.TimeoutExpired):
        result = reindex_project(project_root, source_type)
        result["mode"] = "full"
        db.write_config(project_root, {"last_commit": head_commit})
        return result

    # Filter to docs/**/*.md files only
    root = Path(project_root)
    changed_md: list[Path] = []
    deleted_rel: list[str] = []
    for rel in changed_paths:
        if not rel.startswith("docs/") or not rel.endswith(".md"):
            continue
        abs_path = root / rel
        if abs_path.exists():
            changed_md.append(abs_path)
        else:
            # File was deleted — remove its chunks from the index
            deleted_rel.append(rel)

    conn = db.open_db(project_root)

    # Remove chunks for deleted files (collect rowids first for vec table cleanup)
    for rel in deleted_rel:
        stale_rowids = [r[0] for r in conn.execute(
            "SELECT rowid FROM chunks WHERE source_path = ?", (rel,)
        ).fetchall()]
        conn.execute("DELETE FROM chunks WHERE source_path = ?", (rel,))
        if stale_rowids and db.SQLITE_VEC_AVAILABLE:
            placeholders = ",".join("?" * len(stale_rowids))
            conn.execute(f"DELETE FROM chunks_vec_latin WHERE rowid IN ({placeholders})", stale_rowids)
            conn.execute(f"DELETE FROM chunks_vec_cjk WHERE rowid IN ({placeholders})", stale_rowids)
    if deleted_rel:
        conn.commit()

    # Re-index changed files
    total = 0
    for f in changed_md:
        total += index_file(conn, f, source_type, project_root)

    conn.close()
    db.write_config(project_root, {"last_commit": head_commit})

    return {
        "files_scanned": len(changed_md),
        "chunks_written": total,
        "deleted_files": len(deleted_rel),
        "mode": "incremental",
    }
