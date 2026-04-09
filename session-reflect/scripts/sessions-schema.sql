-- session-reflect SQLite schema
-- 17 tables covering all 15 analysis dimensions

-- Core sessions table
CREATE TABLE IF NOT EXISTS sessions (
    session_id   TEXT PRIMARY KEY,
    source       TEXT NOT NULL,          -- 'claude-code' | 'codex'
    project      TEXT,
    project_path TEXT,
    branch       TEXT,
    model        TEXT,
    time_start   TEXT,
    time_end     TEXT,
    duration_min REAL,
    turns_user   INTEGER,
    turns_asst   INTEGER,
    tokens_in    INTEGER,
    tokens_out   INTEGER,
    cache_read   INTEGER,
    cache_create INTEGER,
    cache_hit_rate REAL,
    session_dna  TEXT,                  -- 'explore'|'build'|'fix'|'chat'|'mixed'
    task_summary TEXT,
    analyzed_at  TEXT,
    outcome      TEXT                   -- 'completed'|'interrupted'|'failed'
);

-- tool_calls: tool invocation sequence
CREATE TABLE IF NOT EXISTS tool_calls (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    seq_idx     INTEGER NOT NULL,
    tool_name   TEXT NOT NULL,
    file_path   TEXT,                   -- for Read/Edit/Write
    is_error    INTEGER DEFAULT 0,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- corrections (dimension 1 of 5 original)
CREATE TABLE IF NOT EXISTS corrections (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    turn       INTEGER,
    type       TEXT NOT NULL,           -- 'scope'|'direction'|'approach'|'factual'
    text       TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- emotion_signals (dimension 2 of 5 original)
CREATE TABLE IF NOT EXISTS emotion_signals (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    turn       INTEGER,
    type       TEXT NOT NULL,           -- 'frustration'|'impatience'|'satisfaction'|'resignation'|'sarcasm'
    trigger    TEXT,
    text       TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- prompt_assessments (dimension 3 of 5 original)
CREATE TABLE IF NOT EXISTS prompt_assessments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL,
    turn            INTEGER,
    original        TEXT,
    issues          TEXT,               -- JSON array stored as text
    rewrite         TEXT,
    improvement_note TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- process_gaps (dimension 4 of 5 original)
CREATE TABLE IF NOT EXISTS process_gaps (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    type       TEXT NOT NULL,           -- 'skipped_exploration'|'no_verification'|'excessive_correction_loop'|'blind_acceptance'|'context_drip_feeding'
    evidence   TEXT,
    suggestion TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- project_stats (dimension 6: aggregated per project)
CREATE TABLE IF NOT EXISTS project_stats (
    project           TEXT PRIMARY KEY,
    avg_duration_min  REAL,
    total_sessions    INTEGER,
    avg_tool_count    REAL,
    build_failure_rate REAL,
    avg_corrections   REAL,
    last_session_at   TEXT
);

-- tool_mastery (dimension 7: aggregated per tool)
CREATE TABLE IF NOT EXISTS tool_mastery (
    tool_name          TEXT PRIMARY KEY,
    total_calls        INTEGER,
    error_count        INTEGER,
    error_rate         REAL,
    last_used          TEXT,
    recent_avg_daily_calls REAL  -- rolling 30-day average
);

-- session_features (dimension 8: per-session feature snapshot)
CREATE TABLE IF NOT EXISTS session_features (
    session_id         TEXT PRIMARY KEY,
    dna                TEXT,
    tool_density       REAL,
    correction_ratio   REAL,
    token_per_turn     REAL,
    project_complexity REAL,
    predicted_outcome  TEXT,
    actual_outcome     TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- context_gaps (dimension 9)
CREATE TABLE IF NOT EXISTS context_gaps (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id     TEXT NOT NULL,
    gap_turn       INTEGER,
    missing_info   TEXT,                  -- 'error_msg'|'file_context'|'goal_detail'|'constraint'
    described_turn INTEGER,               -- turn where info was provided
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- token_audit (dimension 10)
CREATE TABLE IF NOT EXISTS token_audit (
    session_id        TEXT PRIMARY KEY,
    total_tokens      INTEGER,
    cache_hit_rate    REAL,
    wasted_tokens     INTEGER,            -- estimated from repeated context
    efficiency_score  REAL,               -- 0-1 computed score
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- session_outcomes (dimension 11)
CREATE TABLE IF NOT EXISTS session_outcomes (
    session_id          TEXT PRIMARY KEY,
    outcome             TEXT NOT NULL,   -- 'completed'|'interrupted'|'failed'
    end_trigger         TEXT,            -- 'user_abrupt'|'goal_achieved'|'build_failure_loop'|'max_turns'
    last_tool           TEXT,
    satisfaction_signal INTEGER,         -- 1 if satisfaction emotion detected
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- skill_invocations (dimension 12)
CREATE TABLE IF NOT EXISTS skill_invocations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    skill_name  TEXT,
    invoked     INTEGER NOT NULL,         -- 1 if skill was used, 0 if direct tool used instead
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- error_patterns (dimension 13: global shared table)
CREATE TABLE IF NOT EXISTS error_patterns (
    pattern_id   TEXT PRIMARY KEY,
    description  TEXT,
    bash_sample  TEXT,                   -- sample error text
    resolution   TEXT,                   -- common fix
    frequency    INTEGER,
    projects     TEXT,                   -- comma-separated affected projects
    last_seen    TEXT
);

-- file_graph (dimension 14)
CREATE TABLE IF NOT EXISTS file_graph (
    file_path       TEXT PRIMARY KEY,
    read_count      INTEGER,
    edit_count      INTEGER,
    last_session_id TEXT,
    project         TEXT,
    last_read_at    TEXT,
    last_edited_at  TEXT
);

-- rhythm_stats (dimension 15)
CREATE TABLE IF NOT EXISTS rhythm_stats (
    session_id              TEXT PRIMARY KEY,
    avg_response_interval_s REAL,        -- avg seconds between user turns
    long_pause_count        INTEGER,    -- pauses >60s
    turn_count              INTEGER,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- analysis_meta (metadata table)
CREATE TABLE IF NOT EXISTS analysis_meta (
    session_id        TEXT PRIMARY KEY,
    analyzer_version  TEXT,             -- e.g. '2.1.0'
    parsed_fields     INTEGER,          -- significance score (3-5), pre-computed by session-parser
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_tool_calls_session ON tool_calls(session_id);
CREATE INDEX IF NOT EXISTS idx_corrections_session ON corrections(session_id);
CREATE INDEX IF NOT EXISTS idx_emotion_signals_session ON emotion_signals(session_id);
CREATE INDEX IF NOT EXISTS idx_prompt_assessments_session ON prompt_assessments(session_id);
CREATE INDEX IF NOT EXISTS idx_process_gaps_session ON process_gaps(session_id);
CREATE INDEX IF NOT EXISTS idx_context_gaps_session ON context_gaps(session_id);
CREATE INDEX IF NOT EXISTS idx_skill_invocations_session ON skill_invocations(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_analyzed_at ON sessions(analyzed_at);
CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project);
CREATE INDEX IF NOT EXISTS idx_sessions_outcome ON sessions(outcome);
