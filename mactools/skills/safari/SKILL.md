---
name: safari
description: 查询 Safari 浏览历史和书签。当用户需要回顾浏览过的网页、查找书签、查看阅读列表时使用。关键词：Safari、浏览历史、书签、阅读列表、网页记录、browsing history、bookmarks、reading list。
context: fork
model: haiku
compatibility: Requires macOS
allowed-tools: Bash(*skills/safari/scripts/*)
---

# Safari History & Bookmarks

Query Safari browsing history, bookmarks, and reading list. All operations are read-only.

## Prerequisites

- macOS with Safari
- Full Disk Access granted to the terminal app running Claude Code (System Settings > Privacy & Security > Full Disk Access). Without this, sqlite3 and plistlib cannot read Safari's data files.

## Path Setup

```bash
BASE="${CLAUDE_PLUGIN_ROOT:-${CODEX_HOME:-$HOME/.codex}}"
SKILLS_ROOT="$BASE/skills"
[ -d "$SKILLS_ROOT/safari/scripts" ] || SKILLS_ROOT="$BASE/cookit/mactools/skills"
```

## Tool

```
${SKILLS_ROOT}/safari/scripts/safari.sh
```

## Subcommands

### Browsing History

```bash
# Recent history (default: 7 days, 20 results)
${SKILLS_ROOT}/safari/scripts/safari.sh history

# History from last 30 days
${SKILLS_ROOT}/safari/scripts/safari.sh history 30

# History from last 3 days, max 10 results
${SKILLS_ROOT}/safari/scripts/safari.sh history 3 -n 10
```

### Search History

```bash
# Search by URL or title
${SKILLS_ROOT}/safari/scripts/safari.sh search "apple developer"

# Search with result limit
${SKILLS_ROOT}/safari/scripts/safari.sh search "swift" -n 50
```

### Most Visited Sites

```bash
# Top 20 most visited sites
${SKILLS_ROOT}/safari/scripts/safari.sh top

# Top 10
${SKILLS_ROOT}/safari/scripts/safari.sh top -n 10
```

### List Bookmarks

```bash
# List bookmarks (title, URL, folder)
${SKILLS_ROOT}/safari/scripts/safari.sh bookmarks

# Limit results
${SKILLS_ROOT}/safari/scripts/safari.sh bookmarks -n 50
```

### Search Bookmarks

```bash
# Search bookmarks by title or URL
${SKILLS_ROOT}/safari/scripts/safari.sh search-bookmarks "github"
```

### Reading List

```bash
# Show reading list items
${SKILLS_ROOT}/safari/scripts/safari.sh reading-list

# Limit results
${SKILLS_ROOT}/safari/scripts/safari.sh reading-list -n 10
```

## Output Format

### History / Search

```
1. How to use Swift Concurrency - Apple Developer
   URL: https://developer.apple.com/...
   Visited: 2026-02-10 14:30 | Visits: 5
```

### Top Sites

```
1. GitHub
   URL: https://github.com/
   Total visits: 342 | Last visit: 2026-02-10 15:00
```

### Bookmarks

```
1. Swift Documentation
   URL: https://docs.swift.org/
   Folder: Development/Apple
```

### Reading List

```
1. Understanding async/await in Swift
   URL: https://example.com/article
   Added: 2026-02-08 10:30
   Preview: This article explains how async/await works...
```

## Options

| Option | Description | Default |
|--------|------------|---------|
| `-n <count>` | Maximum number of results | 20 |

## Common Workflows

### Recall a page visited recently

```bash
# What did I browse in the last 3 days?
${SKILLS_ROOT}/safari/scripts/safari.sh history 3

# Search for a specific topic
${SKILLS_ROOT}/safari/scripts/safari.sh search "SwiftUI"
```

### Find saved resources

```bash
# List all bookmarks
${SKILLS_ROOT}/safari/scripts/safari.sh bookmarks -n 100

# Search bookmarks for a keyword
${SKILLS_ROOT}/safari/scripts/safari.sh search-bookmarks "reference"

# Check reading list
${SKILLS_ROOT}/safari/scripts/safari.sh reading-list
```

### Browsing analytics

```bash
# Which sites do I visit most?
${SKILLS_ROOT}/safari/scripts/safari.sh top -n 20
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot read Safari history database" | Grant Full Disk Access to your terminal app: System Settings > Privacy & Security > Full Disk Access |
| "Cannot read Safari bookmarks plist" | Same as above: grant Full Disk Access |
| "No results found" for history | Try increasing the days parameter, or check that Safari has history |
| Empty bookmark results | Bookmarks may be synced via iCloud; ensure Safari has local bookmarks |

## Data Sources

| Data | Location | Access Method |
|------|----------|---------------|
| History | `~/Library/Safari/History.db` | sqlite3 (read-only copy) |
| Bookmarks | `~/Library/Safari/Bookmarks.plist` | python3 plistlib |
| Reading List | `~/Library/Safari/Bookmarks.plist` | python3 plistlib (ReadingList entries) |

## Limitations

- Read-only: this tool never modifies Safari data
- History database is queried via a temporary copy to avoid locking conflicts with Safari
- Bookmarks stored in iCloud-only sync may not appear in the local plist
- CoreData timestamps in History.db use seconds since 2001-01-01 (offset 978307200)
