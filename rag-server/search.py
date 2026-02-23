"""
Hybrid search: BM25 (FTS5) + cosine (sqlite-vec), merged with RRF.
"""
from __future__ import annotations
import sqlite3
from typing import Any

import db
from indexer import get_embeddings, jieba_tokenize, load_jieba_dict

RRF_K = 60
DEFAULT_TOP_K = 5


def _rrf(ranks: list[int]) -> float:
    return sum(1.0 / (RRF_K + r) for r in ranks)


def _escape_fts5(query_tokens: str) -> str:
    """Wrap each token in double quotes to escape FTS5 operators (-, *, OR, NOT, NEAR)."""
    tokens = query_tokens.split()
    return " ".join(f'"{t}"' for t in tokens if t.strip())


def _bm25_search(
    conn: sqlite3.Connection, query: str, top_k: int
) -> list[dict]:
    load_jieba_dict()
    tok = _escape_fts5(jieba_tokenize(query))
    try:
        rows = conn.execute(
            """
            SELECT c.rowid, c.id, c.source_type, c.source_path, c.section,
                   c.content, c.line_start, c.line_end,
                   bm25(chunks_fts) AS bm25_score
            FROM chunks_fts
            JOIN chunks c ON c.rowid = chunks_fts.rowid
            WHERE chunks_fts MATCH ?
            ORDER BY bm25_score
            LIMIT ?
            """,
            (tok, top_k * 3),
        ).fetchall()
    except sqlite3.OperationalError:
        # Graceful degradation on malformed FTS5 query
        rows = []
    return [dict(r) for r in rows]


def _vec_search(
    conn: sqlite3.Connection,
    table: str,
    query_vec: list[float],
    top_k: int,
) -> list[dict]:
    blob = db.serialize_vec(query_vec)
    rows = conn.execute(
        f"""
        SELECT v.rowid, v.distance,
               c.id, c.source_type, c.source_path, c.section,
               c.content, c.line_start, c.line_end
        FROM {table} v
        JOIN chunks c ON c.rowid = v.rowid
        WHERE v.embedding MATCH ? AND k = ?
        ORDER BY v.distance
        """,
        (blob, top_k * 3),
    ).fetchall()
    return [dict(r) for r in rows]


def search(
    query: str,
    project_root: str | None = None,
    source_type: list[str] | None = None,
    top_k: int = DEFAULT_TOP_K,
) -> list[dict[str, Any]]:
    """
    Hybrid BM25 + cosine search with RRF merge.

    Returns up to top_k dicts, each with:
        source_path, section, content, score, line_range
    Returns empty list if index is empty or query matches nothing.
    """
    conn = db.open_db(project_root)

    # BM25
    bm25_rows = _bm25_search(conn, query, top_k)
    bm25_rank: dict[str, int] = {r["id"]: i + 1 for i, r in enumerate(bm25_rows)}

    # Vector (only if extension is loaded)
    latin_rank: dict[str, int] = {}
    cjk_rank: dict[str, int] = {}
    latin_rows: list[dict] = []
    cjk_rows: list[dict] = []

    if db.SQLITE_VEC_AVAILABLE:
        emb = get_embeddings(query)
        if emb is not None:
            latin_vec, cjk_vec = emb
            latin_rows = _vec_search(conn, "chunks_vec_latin", latin_vec, top_k)
            cjk_rows = _vec_search(conn, "chunks_vec_cjk", cjk_vec, top_k)
            latin_rank = {r["id"]: i + 1 for i, r in enumerate(latin_rows)}
            cjk_rank = {r["id"]: i + 1 for i, r in enumerate(cjk_rows)}

    # Collect all candidate IDs and build id->row lookup
    all_ids: set[str] = set(bm25_rank) | set(latin_rank) | set(cjk_rank)
    id_to_row: dict[str, dict] = {}
    for r in bm25_rows + latin_rows + cjk_rows:
        id_to_row.setdefault(r["id"], r)

    # Score with RRF; take the better of the two vec ranks
    max_rank = top_k * 3 + 1  # penalty for "not in this list"
    scored: list[tuple[float, str]] = []
    for cid in all_ids:
        br = bm25_rank.get(cid, max_rank)
        lr = latin_rank.get(cid, max_rank)
        cr = cjk_rank.get(cid, max_rank)
        best_vec = min(lr, cr)
        scored.append((_rrf([br, best_vec]), cid))

    scored.sort(reverse=True)

    # Build output, applying optional source_type filter
    results: list[dict[str, Any]] = []
    for score, cid in scored:
        row = id_to_row.get(cid)
        if not row:
            continue
        if source_type and row["source_type"] not in source_type:
            continue
        results.append({
            "source_type": row["source_type"],
            "source_path": row["source_path"],
            "section": row["section"],
            "content": row["content"],
            "score": round(score, 6),
            "line_range": [row["line_start"], row["line_end"]],
        })
        if len(results) >= top_k:
            break

    conn.close()
    return results
