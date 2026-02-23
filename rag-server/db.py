"""
Database connection helpers.

Requires a Python with SQLite extension loading support (system Python does not).
Install deps: rag-server/.venv/bin/pip install sqlite-vec
"""
from __future__ import annotations
import json
import sqlite3
import struct
from pathlib import Path

try:
    import sqlite_vec
    SQLITE_VEC_AVAILABLE = True
except ImportError:
    SQLITE_VEC_AVAILABLE = False


def db_path_for(project_root: str | None) -> Path:
    """Return path to index.db for the given project root (or user-level if None)."""
    if project_root:
        return Path(project_root) / ".claude" / "rag" / "index.db"
    return Path.home() / ".claude" / "rag" / "index.db"


def open_db(project_root: str | None = None) -> sqlite3.Connection:
    """
    Open (and initialize if needed) the SQLite database.
    Loads sqlite-vec extension and ensures all tables exist.
    """
    path = db_path_for(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row

    if SQLITE_VEC_AVAILABLE:
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)

    schema = (Path(__file__).parent / "schema.sql").read_text()
    conn.executescript(schema)
    _ensure_vec_tables(conn)
    conn.commit()
    return conn


def _ensure_vec_tables(conn: sqlite3.Connection) -> None:
    if not SQLITE_VEC_AVAILABLE:
        return
    conn.executescript("""
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec_latin USING vec0(
            rowid INTEGER PRIMARY KEY,
            embedding float[512] distance_metric=cosine
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec_cjk USING vec0(
            rowid INTEGER PRIMARY KEY,
            embedding float[512] distance_metric=cosine
        );
    """)


def serialize_vec(floats: list[float]) -> bytes:
    """Pack floats into sqlite-vec binary format (little-endian float32)."""
    return struct.pack(f"{len(floats)}f", *floats)


def config_path_for(project_root: str | None) -> Path:
    """Return path to config.json for the given project root (or user-level if None)."""
    if project_root:
        return Path(project_root) / ".claude" / "rag" / "config.json"
    return Path.home() / ".claude" / "rag" / "config.json"


def read_config(project_root: str | None) -> dict:
    """Read config.json, returning {} if it does not exist."""
    path = config_path_for(project_root)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def write_config(project_root: str | None, data: dict) -> None:
    """Write data to config.json, merging with existing keys."""
    path = config_path_for(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = read_config(project_root)
    existing.update(data)
    path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
