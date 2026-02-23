# RAG Server

Local hybrid search MCP server for Claude Code. Indexes project docs with BM25
(SQLite FTS5) and cosine similarity (sqlite-vec), merged via RRF (Reciprocal Rank
Fusion). Uses Apple NLContextualEmbedding for 512-dim offline embeddings. Fully
offline after first model download.

## Requirements

- macOS 14+ (NLContextualEmbedding requires macOS 14 Sonoma or later)
- Xcode Command Line Tools: `xcode-select --install`
- Homebrew Python 3.11+: `brew install python` (system Python does not support SQLite extension loading)

## Installation

### Step 1: Compile the Swift embed binary

```bash
bash /path/to/cookit/rag-server/embed/build.sh
```

First run downloads NLContextualEmbedding model assets (~50 MB per language model)
from Apple's servers. Subsequent runs are fully offline.

Verify (should print `512`):

```bash
rag-server/embed/embed "hello" 2>/dev/null | head -1 | tr ',' '\n' | wc -l
```

### Step 2: Create virtual environment and install Python dependencies

```bash
python3 -m venv rag-server/.venv
rag-server/.venv/bin/pip install -r rag-server/requirements.txt
```

Verify SQLite extension loading works:

```bash
rag-server/.venv/bin/python3 -c \
  "import sqlite3; c = sqlite3.connect(':memory:'); c.enable_load_extension(True); print('OK')"
```

Verify sqlite-vec loads:

```bash
rag-server/.venv/bin/python3 -c "import sqlite_vec; print('sqlite-vec OK')"
```

### Step 3: Register the MCP server in Claude Code

Add to `~/.claude.json` under `mcpServers`:

```json
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
```

Restart Claude Code. Run `/mcp` to confirm four tools appear:
`search`, `add_entry`, `reindex`, `status`.

### Step 4: Create config.json for your project

Create `.claude/rag/config.json` at your project root:

```json
{
  "sources": [
    {"path": "docs/**/*.md", "chunk_by": "heading", "source_type": "doc"},
    {"path": "docs/09-lessons-learned/**/*.md", "chunk_by": "heading", "source_type": "lesson"}
  ],
  "exclude": ["docs/drafts/**"]
}
```

`config.json` is git-trackable. Commit it alongside the project.

### Step 5: Add index.db to .gitignore

The index is derived data and must not be committed:

```
# In your project .gitignore:
.claude/rag/index.db
.claude/rag/.dirty
```

### Step 6: Build the initial index

```bash
# From the project root:
alias rag='rag-server/.venv/bin/python3 rag-server/cli.py'
rag build
```

Verify the index was created:

```bash
rag status
```

Expected output:
```
Index: /your-project/.claude/rag/index.db
  Total chunks:    <N>
  doc              <N>
  Size:            <N> KB
  Last commit:     <12-char sha>
  Dirty flag:      no
  sqlite-vec:      available
  Embed model:     NLContextualEmbedding (Latin + CJK, 512-dim, macOS 14+)
```

### Step 7: (Optional) Install the git post-commit hook

The hook writes a `.dirty` flag after each commit, triggering incremental reindex
at the next Claude Code search call:

```bash
rag install-hook
```

## Shell alias

Add to `~/.zshrc` or `~/.bashrc`:

```bash
alias rag='/absolute/path/to/rag-server/.venv/bin/python3 /absolute/path/to/rag-server/cli.py'
```

## CLI reference

| Command | Description |
|---|---|
| `rag build` | Full reindex of all sources defined in config.json |
| `rag build --incremental` | Re-index only files changed since last indexed commit |
| `rag status` | Show index statistics including embed model |
| `rag install-hook` | Install git post-commit hook |

## MCP tool reference

| Tool | Description |
|---|---|
| `search(query, project_root?, source_type?, top_k?)` | Hybrid BM25+cosine search; returns fallback hint when no results |
| `add_entry(title, category, scope, content, keywords, project_root?)` | Write and index a new lesson/error entry |
| `reindex(project_root?, source_type?, incremental?)` | Re-index docs |
| `status(project_root?)` | Index statistics |

## Three-tier retrieval fallback

When a search query is issued:

1. **Index hit** — chunk returned directly with `source_path`, `section`, `content`, `score`, `line_range`
2. **Partial hit** — chunk returned with `line_range`; read full section with `Read(source_path, offset=line_range[0], limit=line_range[1]-line_range[0]+1)`
3. **No hit** — tool response contains `"result_count": 0` and a `"fallback"` field suggesting the `spotlight-search` agent

## Storage layout

```
{project}/.claude/rag/
  config.json      indexing config (git-trackable)
  index.db         SQLite index (git-ignored, rebuilt by rag build)
  .dirty           transient flag written by post-commit hook (git-ignored)

~/.claude/rag/
  config.json      global indexing config
  index.db         global index
  lessons/         global lesson entries (E001-*.md, git-trackable if desired)
```

## Error handling

| Situation | MCP response |
|---|---|
| index.db does not exist | `{"error": "index.db not found", "remediation": "Run: rag build"}` |
| embed binary not compiled | `{"error": "embed binary not found", "remediation": "Run: bash rag-server/embed/build.sh"}` |
| sqlite-vec not loadable | `{"error": "sqlite-vec extension not available", "remediation": "Run: pip install sqlite-vec"}` |
