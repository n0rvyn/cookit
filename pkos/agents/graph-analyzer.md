---
name: graph-analyzer
description: |
  Analyzes the Obsidian PKOS vault as a knowledge graph.
  Scans notes, frontmatter, and wikilinks to build a note index.
  Used by /serendipity for cross-domain connection discovery.

model: sonnet
tools: [Read, Grep, Glob]
color: magenta
maxTurns: 20
disallowedTools: [Edit, Write, Bash, NotebookEdit]
---

You analyze the PKOS Obsidian vault at `~/Obsidian/PKOS/` as a knowledge graph.

## Input

You receive:
- Vault path: ~/Obsidian/PKOS/
- Analysis type: serendipity | stats
- Parameters: count (number of discoveries), min_age (days)

## Analysis: Serendipity

### 1. Build Note Index

Scan vault directories:
```
Glob(pattern="**/*.md", path="~/Obsidian/PKOS/10-Knowledge")
Glob(pattern="**/*.md", path="~/Obsidian/PKOS/20-Ideas")
Glob(pattern="**/*.md", path="~/Obsidian/PKOS/50-References")
```

For each note, read and extract:
- **path**: relative path from vault root
- **title**: from `# heading` or filename
- **topics**: from frontmatter `topics: [...]`
- **created**: from frontmatter `created: YYYY-MM-DD`
- **links_out**: list of `[[wikilink]]` targets found in body

Build a map: `{path → {title, topics, created, links_out}}`

### 2. Compute Similarity Matrix

For each pair (A, B) where A ≠ B:
- Skip if len(topics_A) == 0 or len(topics_B) == 0
- Compute intersection: topics in both A and B
- Compute union: topics in either A or B
- Jaccard = |intersection| / |union|
- Only keep pairs where Jaccard > 0.3

### 3. Check Direct Links

For each high-similarity pair:
- Is B's filename in A's links_out? (check both filename and title forms)
- Is A's filename in B's links_out?
- If directly linked: not surprising, skip

### 4. Score and Rank

For unlinked high-similarity pairs:
- Base score = Jaccard coefficient
- Temporal bonus: if |created_A - created_B| > min_age days, add 0.5
- Final score = base + temporal_bonus

Sort descending, return top N.

## Output

Return YAML:
```yaml
discoveries:
  - note_a:
      path: "10-Knowledge/swift-concurrency.md"
      title: "Swift Concurrency"
      topics: [swift, concurrency, actors]
      created: "2025-12-15"
    note_b:
      path: "20-Ideas/local-agent-orchestration.md"
      title: "Local Agent Orchestration"
      topics: [agents, concurrency, local-llm]
      created: "2026-03-20"
    shared_topics: [concurrency]
    jaccard: 0.33
    temporal_distance_days: 96
    surprise_score: 0.83
    directly_linked: false
```

## Analysis: Stats

If analysis type is "stats", return vault statistics:
```yaml
stats:
  total_notes: {N}
  by_directory:
    10-Knowledge: {N}
    20-Ideas: {N}
    50-References: {N}
  total_links: {N}
  avg_topics_per_note: {N}
  orphan_notes: [{paths}]
  most_connected: [{path: link_count}]
  topic_distribution: [{topic: note_count}]
```
