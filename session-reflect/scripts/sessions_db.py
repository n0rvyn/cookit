#!/usr/bin/env python3
"""
session-reflect sessions.db management script.
Zero dependencies (uses Python's built-in sqlite3 module).
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

DB_PATH = Path("~/.claude/session-reflect/sessions.db").expanduser()


def init_db():
    """Create all tables if not exist. Run on first use."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    schema_path = Path(__file__).parent / "sessions-schema.sql"
    conn = sqlite3.connect(DB_PATH)
    with open(schema_path) as f:
        conn.executescript(f.read())
    conn.close()


def _get_conn(read_only=False):
    """Get a database connection. For read-only access during active sessions,
    use file:{path}?mode=ro URI to prevent locking. For writes use regular connect."""
    if read_only:
        return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    return sqlite3.connect(DB_PATH)


def upsert_session(session_id: str, session_data: dict):
    """Insert or replace a parsed+enriched session into sessions.db."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT OR REPLACE INTO sessions (
            session_id, source, project, project_path, branch, model,
            time_start, time_end, duration_min, turns_user, turns_asst,
            tokens_in, tokens_out, cache_read, cache_create, cache_hit_rate,
            session_dna, task_summary, analyzed_at, outcome
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        session_data.get("source"),
        session_data.get("project"),
        session_data.get("project_path"),
        session_data.get("branch"),
        session_data.get("model"),
        session_data.get("time_start"),
        session_data.get("time_end"),
        session_data.get("duration_min"),
        session_data.get("turns_user"),
        session_data.get("turns_asst"),
        session_data.get("tokens_in"),
        session_data.get("tokens_out"),
        session_data.get("cache_read"),
        session_data.get("cache_create"),
        session_data.get("cache_hit_rate"),
        session_data.get("session_dna"),
        session_data.get("task_summary"),
        session_data.get("analyzed_at") or datetime.now().isoformat(),
        session_data.get("outcome"),
    ))
    conn.commit()
    conn.close()


def update_session_dna(session_id: str, session_dna: str):
    """Update session_dna for an existing session after enrichment."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "UPDATE sessions SET session_dna = ? WHERE session_id = ?",
            (session_dna, session_id),
        )
        conn.commit()
    finally:
        conn.close()


def upsert_tool_calls(session_id: str, tool_calls: list):
    """Insert tool call sequence into tool_calls table."""
    conn = sqlite3.connect(DB_PATH)
    # Delete existing tool calls for this session (upsert behavior)
    conn.execute("DELETE FROM tool_calls WHERE session_id = ?", (session_id,))
    for idx, tc in enumerate(tool_calls):
        conn.execute("""
            INSERT INTO tool_calls (session_id, seq_idx, tool_name, file_path, is_error)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            idx,
            tc.get("tool_name"),
            tc.get("file_path"),
            tc.get("is_error", 0),
        ))
    conn.commit()
    conn.close()


def query_sessions(project=None, days=None, dimension=None, limit=100):
    """OLAP query across sessions. Returns list of session dicts."""
    conn = _get_conn(read_only=True)
    query = "SELECT * FROM sessions WHERE 1=1"
    params = []

    if project:
        query += " AND project = ?"
        params.append(project)

    if days:
        cutoff = datetime.now().timestamp() - (days * 86400)
        query += " AND analyzed_at >= ?"
        params.append(datetime.fromtimestamp(cutoff).isoformat())

    query += f" LIMIT {limit}"

    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description] if rows else []
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


def query_sessions_by_dimension(dimension, threshold=None, project=None, days=None, limit=50):
    """OLAP query across sessions by dimension."""
    conn = _get_conn(read_only=True)
    dim_table_map = {
        "token_audit": ("token_audit", "ta", "ta.total_tokens, ta.cache_hit_rate, ta.efficiency_score"),
        "session_outcomes": ("session_outcomes", "so", "so.outcome, so.end_trigger, so.last_tool"),
        "session_features": ("session_features", "sf", "sf.dna, sf.tool_density, sf.project_complexity"),
        "context_gaps": ("context_gaps", "cg", "COUNT(*) as gap_count"),
        "rhythm_stats": ("rhythm_stats", "rs", "rs.avg_response_interval_s, rs.long_pause_count"),
        "skill_invocations": ("skill_invocations", "si", "si.skill_name, si.invoked"),
        "corrections": ("corrections", "c", "COUNT(*) as correction_count"),
    }
    if dimension not in dim_table_map:
        conn.close()
        return []
    table, alias, select_cols = dim_table_map[dimension]
    query = f"""
        SELECT s.session_id, s.project, s.time_start, s.duration_min,
               s.session_dna, s.outcome, {select_cols}
        FROM sessions s
        JOIN {table} {alias} ON s.session_id = {alias}.session_id
        WHERE 1=1
    """
    params = []
    if project:
        query += " AND s.project = ?"
        params.append(project)
    if days:
        cutoff = datetime.now().timestamp() - (days * 86400)
        query += " AND s.analyzed_at >= ?"
        params.append(datetime.fromtimestamp(cutoff).isoformat())
    if threshold is not None and dimension in ("token_audit", "session_features"):
        query += f" AND {alias}.efficiency_score >= ?"
        params.append(threshold)
    query += f" LIMIT {limit}"
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description] if rows else []
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


def query_sessions_by_outcome(outcome, project=None, days=None, limit=50):
    """Query sessions by outcome field."""
    conn = _get_conn(read_only=True)
    query = """
        SELECT s.session_id, s.project, s.time_start, s.duration_min,
               s.session_dna, s.outcome, s.model,
               so.end_trigger, so.last_tool, so.satisfaction_signal
        FROM sessions s
        LEFT JOIN session_outcomes so ON s.session_id = so.session_id
        WHERE s.outcome = ?
    """
    params = [outcome]
    if project:
        query += " AND s.project = ?"
        params.append(project)
    if days:
        cutoff = datetime.now().timestamp() - (days * 86400)
        query += " AND s.analyzed_at >= ?"
        params.append(datetime.fromtimestamp(cutoff).isoformat())
    query += f" LIMIT {limit}"
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description] if rows else []
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


def query_sessions_by_complexity(op, value, project=None, days=None, limit=50):
    """Query sessions by project_complexity with operator."""
    ops = {"gt": ">", "lt": "<", "eq": "="}
    if op not in ops:
        return []
    conn = _get_conn(read_only=True)
    query = f"""
        SELECT s.session_id, s.project, s.time_start, s.duration_min,
               s.session_dna, s.outcome,
               sf.project_complexity, sf.tool_density, sf.token_per_turn
        FROM sessions s
        LEFT JOIN session_features sf ON s.session_id = sf.session_id
        WHERE sf.project_complexity IS NOT NULL AND sf.project_complexity {ops[op]} ?
    """
    params = [value]
    if project:
        query += " AND s.project = ?"
        params.append(project)
    if days:
        cutoff = datetime.now().timestamp() - (days * 86400)
        query += " AND s.analyzed_at >= ?"
        params.append(datetime.fromtimestamp(cutoff).isoformat())
    query += f" ORDER BY sf.project_complexity DESC LIMIT {limit}"
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description] if rows else []
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


def query_significance_above(threshold, project=None, days=None, limit=50):
    """Query sessions with significance (analysis_meta.parsed_fields) >= threshold."""
    conn = _get_conn(read_only=True)
    query = """
        SELECT s.session_id, s.project, s.time_start, s.session_dna,
               s.outcome, am.parsed_fields as significance
        FROM sessions s
        JOIN analysis_meta am ON s.session_id = am.session_id
        WHERE COALESCE(am.parsed_fields, 0) >= ?
    """
    params = [threshold]
    if project:
        query += " AND s.project = ?"
        params.append(project)
    if days:
        cutoff = datetime.now().timestamp() - (days * 86400)
        query += " AND s.analyzed_at >= ?"
        params.append(datetime.fromtimestamp(cutoff).isoformat())
    query += " ORDER BY am.parsed_fields DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    cols = [desc[0] for desc in conn.cursor().description] if rows else []
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


def get_session_ids(exclude_analyzed=False):
    """Return all session_ids currently in db."""
    conn = _get_conn(read_only=True)
    rows = conn.execute("SELECT session_id FROM sessions").fetchall()
    conn.close()
    return [r[0] for r in rows]


def mark_analyzed(session_ids: list):
    """Mark sessions as analyzed (idempotent)."""
    conn = sqlite3.connect(DB_PATH)
    for sid in session_ids:
        conn.execute("""
            INSERT OR IGNORE INTO sessions (session_id, analyzed_at)
            VALUES (?, ?)
        """, (sid, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_ief_insights(significance_min=3, limit=20, session_ids=None):
    """Query sessions with significance >= threshold for IEF export."""
    conn = _get_conn(read_only=True)
    if session_ids:
        placeholders = ",".join("?" * len(session_ids))
        query = f"""
            SELECT s.session_id, s.project, s.session_dna, s.outcome,
                   sf.dna, sf.tool_density, sf.correction_ratio,
                   sf.token_per_turn, sf.project_complexity,
                   am.parsed_fields as significance, am.analyzer_version
            FROM sessions s
            LEFT JOIN session_features sf ON s.session_id = sf.session_id
            LEFT JOIN analysis_meta am ON s.session_id = am.session_id
            WHERE COALESCE(am.parsed_fields, 0) >= ? AND s.session_id IN ({placeholders})
            ORDER BY am.parsed_fields DESC
            LIMIT ?
        """
        rows = conn.execute(query, [significance_min] + list(session_ids) + [limit]).fetchall()
    else:
        query = """
            SELECT s.session_id, s.project, s.session_dna, s.outcome,
                   sf.dna, sf.tool_density, sf.correction_ratio,
                   sf.token_per_turn, sf.project_complexity,
                   am.parsed_fields as significance, am.analyzer_version
            FROM sessions s
            LEFT JOIN session_features sf ON s.session_id = sf.session_id
            LEFT JOIN analysis_meta am ON s.session_id = am.session_id
            WHERE COALESCE(am.parsed_fields, 0) >= ?
            ORDER BY am.parsed_fields DESC
            LIMIT ?
        """
        rows = conn.execute(query, [significance_min, limit]).fetchall()
    conn.close()
    cols = ["session_id", "project", "session_dna", "outcome",
            "dna", "tool_density", "correction_ratio", "token_per_turn",
            "project_complexity", "significance", "analyzer_version"]
    return [dict(zip(cols, row)) for row in rows]


def migrate_from_analyzed_sessions():
    """One-time migration: read analyzed_sessions.json and upsert all sessions into sessions.db."""
    json_path = Path("~/.claude/session-reflect/analyzed_sessions.json")
    if not json_path.exists():
        return 0, "skipped"
    with open(json_path) as f:
        data = json.load(f)  # {session_id: "YYYY-MM-DD", ...}
    if not data:
        return 0, "empty"
    count = 0
    for session_id, date_str in data.items():
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT OR IGNORE INTO sessions (session_id, analyzed_at)
            VALUES (?, ?)
        """, (session_id, date_str))
        conn.commit()
        count += 1
    conn.close()
    return count, None


def upsert_session_features(session_id: str, data: dict, conn=None):
    """Upsert per-session feature snapshot. significance stored in analysis_meta."""
    _conn = conn if conn else sqlite3.connect(DB_PATH)
    _close = not bool(conn)
    try:
        _conn.execute("""
            INSERT OR REPLACE INTO session_features
                (session_id, dna, tool_density, correction_ratio, token_per_turn, project_complexity, predicted_outcome, actual_outcome)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            data.get("dna"),
            data.get("tool_density"),
            data.get("correction_ratio"),
            data.get("token_per_turn"),
            data.get("project_complexity"),
            data.get("predicted_outcome"),
            data.get("actual_outcome"),
        ))
        # Store significance in analysis_meta (parsed_fields carries significance as integer bitmask)
        significance = data.get("significance", 0)
        version = data.get("analyzer_version", "1.0")
        _conn.execute("""
            INSERT OR REPLACE INTO analysis_meta (session_id, analyzer_version, parsed_fields)
            VALUES (?, ?, ?)
        """, (session_id, version, significance))
        if _close:
            _conn.commit()
    finally:
        if _close:
            _conn.close()


def upsert_context_gaps(session_id: str, gaps: list, conn=None):
    """Delete existing then insert new context gaps for a session."""
    if not gaps:
        return
    _conn = conn if conn else sqlite3.connect(DB_PATH)
    _close = not bool(conn)
    try:
        _conn.execute("DELETE FROM context_gaps WHERE session_id = ?", (session_id,))
        for g in gaps:
            _conn.execute("""
                INSERT INTO context_gaps (session_id, gap_turn, missing_info, described_turn)
                VALUES (?, ?, ?, ?)
            """, (session_id, g.get("gap_turn"), g.get("missing_info"), g.get("described_turn")))
        if _close:
            _conn.commit()
    finally:
        if _close:
            _conn.close()


def upsert_token_audit(session_id: str, data: dict, conn=None):
    """Upsert token efficiency audit for a session."""
    _conn = conn if conn else sqlite3.connect(DB_PATH)
    _close = not bool(conn)
    try:
        _conn.execute("""
            INSERT OR REPLACE INTO token_audit (session_id, total_tokens, cache_hit_rate, wasted_tokens, efficiency_score)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            data.get("total_tokens"),
            data.get("cache_hit_rate"),
            data.get("wasted_tokens"),
            data.get("efficiency_score"),
        ))
        if _close:
            _conn.commit()
    finally:
        if _close:
            _conn.close()


def upsert_session_outcomes(session_id: str, data: dict, conn=None):
    """Upsert session outcome record."""
    _conn = conn if conn else sqlite3.connect(DB_PATH)
    _close = not bool(conn)
    try:
        _conn.execute("""
            INSERT OR REPLACE INTO session_outcomes (session_id, outcome, end_trigger, last_tool, satisfaction_signal)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            data.get("outcome"),
            data.get("end_trigger"),
            data.get("last_tool"),
            data.get("satisfaction_signal"),
        ))
        if _close:
            _conn.commit()
    finally:
        if _close:
            _conn.close()


def upsert_skill_invocations(session_id: str, invocations: list, conn=None):
    """Delete existing then insert skill invocation records."""
    if not invocations:
        return
    _conn = conn if conn else sqlite3.connect(DB_PATH)
    _close = not bool(conn)
    try:
        _conn.execute("DELETE FROM skill_invocations WHERE session_id = ?", (session_id,))
        for inv in invocations:
            _conn.execute("""
                INSERT INTO skill_invocations (session_id, skill_name, invoked)
                VALUES (?, ?, ?)
            """, (session_id, inv.get("skill_name"), inv.get("invoked")))
        if _close:
            _conn.commit()
    finally:
        if _close:
            _conn.close()


def upsert_error_patterns(data: dict, conn=None):
    """Upsert a global error pattern entry. Called once per unique pattern."""
    _conn = conn if conn else sqlite3.connect(DB_PATH)
    _close = not bool(conn)
    try:
        _conn.execute("""
            INSERT OR REPLACE INTO error_patterns (pattern_id, description, bash_sample, resolution, frequency, projects, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("pattern_id"),
            data.get("description"),
            data.get("bash_sample"),
            data.get("resolution"),
            data.get("frequency", 1),
            data.get("projects"),
            data.get("last_seen"),
        ))
        if _close:
            _conn.commit()
    finally:
        if _close:
            _conn.close()


def upsert_file_graph(entries: list, conn=None):
    """Upsert file graph entries. Uses ON CONFLICT DO UPDATE for incremental counts."""
    if not entries:
        return
    _conn = conn if conn else sqlite3.connect(DB_PATH)
    _close = not bool(conn)
    try:
        for e in entries:
            _conn.execute("""
                INSERT INTO file_graph (file_path, read_count, edit_count, last_session_id, project, last_read_at, last_edited_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    read_count = read_count + excluded.read_count,
                    edit_count = edit_count + excluded.edit_count,
                    last_session_id = excluded.last_session_id,
                    last_read_at = COALESCE(excluded.last_read_at, file_graph.last_read_at),
                    last_edited_at = COALESCE(excluded.last_edited_at, file_graph.last_edited_at)
            """, (
                e.get("file_path"),
                e.get("read_count", 0),
                e.get("edit_count", 0),
                e.get("last_session_id"),
                e.get("project"),
                e.get("last_read_at"),
                e.get("last_edited_at"),
            ))
        if _close:
            _conn.commit()
    finally:
        if _close:
            _conn.close()


def upsert_rhythm_stats(session_id: str, data: dict, conn=None):
    """Upsert session rhythm statistics."""
    _conn = conn if conn else sqlite3.connect(DB_PATH)
    _close = not bool(conn)
    try:
        _conn.execute("""
            INSERT OR REPLACE INTO rhythm_stats (session_id, avg_response_interval_s, long_pause_count, turn_count)
            VALUES (?, ?, ?, ?)
        """, (
            session_id,
            data.get("avg_response_interval_s"),
            data.get("long_pause_count"),
            data.get("turn_count"),
        ))
        if _close:
            _conn.commit()
    finally:
        if _close:
            _conn.close()


def enrich_session(session_id: str, enrichment: dict):
    """Bulk upsert all dimension data for a session in a single transaction. Call after upsert_session."""
    conn = sqlite3.connect(DB_PATH)
    try:
        if "session_features" in enrichment:
            _d = dict(enrichment["session_features"])
            _d["significance"] = enrichment.get("significance", 0)
            upsert_session_features(session_id, _d, conn=conn)
        if "context_gaps" in enrichment:
            upsert_context_gaps(session_id, enrichment["context_gaps"], conn=conn)
        if "token_audit" in enrichment:
            upsert_token_audit(session_id, enrichment["token_audit"], conn=conn)
        if "session_outcomes" in enrichment:
            upsert_session_outcomes(session_id, enrichment["session_outcomes"], conn=conn)
        if "skill_invocations" in enrichment:
            upsert_skill_invocations(session_id, enrichment["skill_invocations"], conn=conn)
        if "error_patterns" in enrichment:
            for ep in enrichment["error_patterns"]:
                upsert_error_patterns(ep, conn=conn)
        if "file_graph" in enrichment:
            upsert_file_graph(enrichment["file_graph"], conn=conn)
        if "rhythm_stats" in enrichment:
            upsert_rhythm_stats(session_id, enrichment["rhythm_stats"], conn=conn)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="session-reflect sessions.db management")
    parser.add_argument("--init", action="store_true", help="Initialize sessions.db schema")
    parser.add_argument("--migrate", action="store_true", help="Migrate from analyzed_sessions.json")
    parser.add_argument("--query-ids", action="store_true", help="List all session IDs in db")
    parser.add_argument("--query-insights", action="store_true", help="Query high-significance sessions for IEF export")
    parser.add_argument("--limit", type=int, default=20, help="Max results")
    parser.add_argument("--query", choices=["dimension", "outcomes", "complexity", "significance"], help="OLAP query mode")
    parser.add_argument("--dimension", help="Dimension to query (token_audit, session_outcomes, session_features, context_gaps, rhythm_stats, skill_invocations, corrections)")
    parser.add_argument("--outcome", help="Outcome value (completed|interrupted|failed)")
    parser.add_argument("--op", choices=["gt", "lt", "eq"], help="Comparison operator for complexity query")
    parser.add_argument("--value", type=float, help="Threshold value")
    parser.add_argument("--min-sig", "--min-significance", type=int, default=3, dest="min_sig", help="Minimum significance")
    parser.add_argument("--project", help="Filter by project name")
    parser.add_argument("--days", type=int, help="Lookback in days")
    args = parser.parse_args()

    if args.init:
        init_db()
        print("sessions.db initialized")
    elif args.migrate:
        n, reason = migrate_from_analyzed_sessions()
        if reason:
            print(f"Migration {reason}: {n} sessions")
        else:
            print(f"Migrated {n} sessions")
    elif args.query_ids:
        ids = get_session_ids()
        print("\n".join(ids))
    elif args.query_insights:
        insights = get_ief_insights(significance_min=args.min_sig, limit=args.limit)
        print(json.dumps(insights, indent=2))
    elif args.query == "dimension":
        if not args.dimension:
            print("--dimension required for dimension query", file=sys.stderr)
            sys.exit(1)
        rows = query_sessions_by_dimension(args.dimension, project=args.project, days=args.days)
        print(json.dumps(rows, indent=2, default=str))
    elif args.query == "outcomes":
        outcome = args.outcome or "interrupted"
        rows = query_sessions_by_outcome(outcome, project=args.project, days=args.days)
        print(json.dumps(rows, indent=2, default=str))
    elif args.query == "complexity":
        if not args.op or args.value is None:
            print("--op and --value required for complexity query", file=sys.stderr)
            sys.exit(1)
        rows = query_sessions_by_complexity(args.op, args.value, project=args.project, days=args.days)
        print(json.dumps(rows, indent=2, default=str))
    elif args.query == "significance":
        rows = query_significance_above(args.min_sig, project=args.project, days=args.days)
        print(json.dumps(rows, indent=2, default=str))
    else:
        parser.print_help()
