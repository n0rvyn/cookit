---
name: serendipity
description: "Internal skill — discovers cross-domain connections via topic similarity. Triggered by Adam cron (weekly Sunday 10am)."
model: sonnet
---

## Overview

Discover surprising cross-domain connections in the Obsidian PKOS vault using metadata similarity (DP-003 Chosen B).

## Arguments

- `--count N`: Number of discoveries to generate (default: 5)
- `--min-age DAYS`: Minimum age for temporal discoveries (default: 90)

## Process

### Step 1: Build Note Index

Dispatch `pkos:graph-analyzer` agent to scan the vault and build a note index with topics and link structure.

Alternatively, scan directly:

```bash
# Find all notes with frontmatter
find ~/Obsidian/PKOS/{10-Knowledge,20-Ideas,50-References} -name "*.md" 2>/dev/null
```

For each note, extract:
- File path
- `topics` array from frontmatter
- `created` date from frontmatter
- Wikilinks (`[[note-name]]`) in body

### Step 2: Compute Topic Similarity

For each pair of notes (A, B):
- Compute Jaccard coefficient: `|topics_A ∩ topics_B| / |topics_A ∪ topics_B|`
- Only consider pairs where Jaccard > 0.3 (at least 30% topic overlap)

### Step 3: Filter for Surprise

A pair is "surprising" if:

**Structural distance**: Notes A and B share topics but are NOT directly linked (no `[[A]]` in B or `[[B]]` in A). The more topic overlap WITHOUT a direct link = more surprising.

**Temporal distance** (bonus): One note created within last 7 days, the other created > `--min-age` days ago. This catches "old idea meets new information" connections.

### Step 4: Rank and Select

Score each surprising pair:
```
surprise_score = jaccard_coefficient * (1 + temporal_bonus)
```
Where `temporal_bonus = 0.5` if temporal distance > min-age days, else 0.

Sort by surprise_score descending. Select top `--count` pairs.

### Step 5: Generate Explanations

For each selected pair, generate a one-paragraph explanation:
- What topics they share
- Why they're not obviously connected (different directories, different time periods)
- What the connection might imply (potential insight, action item, or new research direction)

### Step 6: Output

```
🔮 PKOS Serendipity Discoveries

1. **{note_A_title}** ↔ **{note_B_title}**
   Shared: {topic1, topic2} | Distance: {no direct link, {N} months apart}
   💡 {explanation}

2. **{note_C_title}** ↔ **{note_D_title}**
   ...

{count} discoveries generated. Consider:
- Creating links between these notes
- Exploring the connections in a Canvas board
- Adding to this week's digest
```

Write discoveries to `~/Obsidian/PKOS/70-Reviews/serendipity-{date}.md` for the weekly digest to pick up.

## Algorithm Notes

- Current: Metadata similarity (Jaccard on topics). Fast, uses existing frontmatter.
- Future upgrade path: Embedding-based similarity for deeper semantic connections (issue #2).
