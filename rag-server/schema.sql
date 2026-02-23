-- RAG Phase 1 schema

CREATE TABLE IF NOT EXISTS chunks (
    id          TEXT    PRIMARY KEY,
    source_type TEXT    NOT NULL,
    source_path TEXT    NOT NULL,
    section     TEXT    NOT NULL DEFAULT '',
    content     TEXT    NOT NULL,
    line_start  INTEGER,
    line_end    INTEGER,
    keywords    TEXT    NOT NULL DEFAULT '',
    updated_at  TEXT    NOT NULL
);

-- Content-table-backed FTS5 (unicode61 handles ASCII + CJK codepoints;
-- Chinese is pre-tokenized by jieba before insertion so spaces separate tokens)
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    content,
    keywords,
    section,
    content="chunks",
    content_rowid="rowid",
    tokenize="unicode61"
);

CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
    INSERT INTO chunks_fts(rowid, content, keywords, section)
    VALUES (new.rowid, new.content, new.keywords, new.section);
END;

CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, content, keywords, section)
    VALUES ('delete', old.rowid, old.content, old.keywords, old.section);
END;

CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, content, keywords, section)
    VALUES ('delete', old.rowid, old.content, old.keywords, old.section);
    INSERT INTO chunks_fts(rowid, content, keywords, section)
    VALUES (new.rowid, new.content, new.keywords, new.section);
END;

-- sqlite-vec virtual tables are created at runtime in db.py after loading the
-- extension (CREATE VIRTUAL TABLE USING vec0 requires the extension to be loaded).
