---
name: collect-lesson
description: "Use after resolving a bug, completing a task with notable pitfalls, or discovering an important architecture constraint. Extracts a structured entry from the session and saves it to the knowledge base."
---

## Overview

This skill extracts a structured knowledge entry from the current session and writes it to the central knowledge base at `~/.claude/knowledge/` or the project-local `docs/09-lessons-learned/`. It checks for near-duplicates before creating, and asks the user to confirm the draft.

## Supported Content Types

| Type | When to use | Suggested body structure |
|------|-------------|------------------------|
| **Lesson / Error** | Bug fixed, pitfall discovered | Symptom / Root Cause / Prevention |
| **API Note** | API quirk, undocumented behavior, version diff | Behavior / Gotcha / Example |
| **Architecture Decision** | Cross-project reusable pattern or constraint | Context / Decision / Consequences |
| **Reference** | WWDC note, framework learning, article summary | Summary / Key Points / Links |

The body format is flexible; the YAML frontmatter is mandatory.

## Process

### Step 1: Extract Entry from Session

Review the current conversation to identify:

1. **Title** — 5-8 words, action-oriented (e.g., "Actor dispatch blocks main context synchronously")
2. **Body** — Markdown content following the appropriate structure for the content type
3. **Keywords** — 3-6 keywords for search (error type, component name, API name, pattern name)
4. **Category** — Pick the most fitting slug: `api-usage`, `bug-postmortem`, `architecture`, `platform-constraints`, `stability-audit`, `data-research`, `workflow`, `reference`, or a new slug if none fit

### Step 2: Check for Near-Duplicates

Search the central knowledge base for similar entries:

1. `Grep(pattern="<keywords joined by |>", path="~/.claude/knowledge/", output_mode="files_with_matches")`
2. For each matching file, read its frontmatter `keywords:` line and title
3. If any file has significant keyword overlap (3+ shared keywords): present it to the user as "Similar entry already in knowledge base:" and ask whether to create a new entry, update the existing one, or skip

If `~/.claude/knowledge/` does not exist yet, skip this step.

### Step 2.5: Reject Drafts with Unresolved Gaps

A lesson must describe a settled conclusion, not work-in-progress. Before drafting, check whether the claim has unresolved follow-ups (pending fixes, unverified assumptions, "TODO: confirm X" notes from the session).

If gaps exist, stop and report them to the user. Do not proceed to Step 3 until either:
- The user resolves the gap, or
- The user explicitly scopes the lesson to exclude the unresolved part

### Step 3: Ask User to Confirm

Present the draft entry:

```
Draft knowledge entry:

Title:     {suggested title}
Category:  {category}
Keywords:  {keyword1}, {keyword2}, ...
Scope:     global (saves to ~/.claude/knowledge/{category}/)
           OR project (saves to docs/09-lessons-learned/)

---
{markdown body}
---

Options:
- Save as-is (global or project scope?)
- Edit (specify what to change)
- Skip
```

Wait for user response. Apply any edits before saving.

### Step 4: Save Entry

Once the user confirms:

1. Determine the target directory:
   - **Global scope**: `~/.claude/knowledge/{category}/`
   - **Project scope**: `docs/09-lessons-learned/`

2. Generate filename: `YYYY-MM-DD-{slug}.md` where slug is the title lowercased, spaces replaced with hyphens, non-alphanumeric removed, truncated to 40 chars

3. Create directory if needed: `Bash("mkdir -p {target_directory}")`

4. Write the file using the `Write` tool:

```yaml
---
category: {category}
keywords: [{kw1}, {kw2}, ...]
date: {YYYY-MM-DD}
source_project: {current project name, optional}
---
# {Title}

{body}
```

5. Report back: `Saved to {file_path}`

### Step 5: Ripple (Cross-Reference)

After saving, propagate links to related entries in `~/.claude/knowledge/`. Skip this step if the entry was saved to project-local `docs/09-lessons-learned/`.

#### 5a. Find Related Entries

Search for entries sharing keywords with the new entry:

1. Join the new entry's keywords with `|` into a single regex: `Grep(pattern="{kw1}|{kw2}|{kw3}", path="~/.claude/knowledge/", glob="*.md", output_mode="files_with_matches")`
2. For each matched file (excluding the new entry itself), read its frontmatter `keywords:` line
3. Count how many of the new entry's keywords appear in the matched file's keywords
4. Filter to files with >=2 keyword overlaps. Keep at most 5 related entries (sorted by overlap count descending).

If no related entries found, skip to Step 5d.

#### 5b. Add Cross-References

For each related entry:

1. Read the related entry's frontmatter
2. If the related entry does NOT have a `related:` field:
   - `Edit` the file to insert `related: [{new-entry-filename}]` after the `date:` line in frontmatter
3. If the related entry already HAS a `related:` field and the new entry is not listed:
   - `Edit` the file to append the new entry's filename to the existing `related:` array
4. Collect all related entry filenames for the new entry

After processing all related entries, `Edit` the new entry's frontmatter to add `related: [{list of related filenames}]` after the `date:` line.

Related entries are referenced by filename only (e.g., `2026-04-07-some-slug.md`), not full paths, since category directories may differ.

#### 5c. Contradiction Flag (best-effort)

For each related entry with >=3 keyword overlaps:

1. Read both entries' body content (below the frontmatter)
2. If the new entry's core claim or recommendation directly contradicts the related entry (e.g., "use X" vs "avoid X", conflicting root causes for the same symptom):
   - Append to the new entry's body: `> ⚠️ Potential conflict with [[{related-filename}]] — review both entries.`
   - Append the same note to the related entry's body (at the end)
3. Only flag obvious, specific contradictions. Do not flag stylistic differences or different-scope advice.

#### 5d. Report Ripple Results

After the "Saved to {file_path}" message from Step 4, append:

```
Cross-references: {N} related entries found, {M} mutual links added, {C} contradictions flagged
```

If no related entries: `Cross-references: no related entries (< 2 keyword overlap)`

### Step 6: Next Steps

After saving, inform the user:

```
Optional: Run `/generate-bases-views --target lessons` to update the Obsidian Bases lessons dashboard.
```

## Completion Criteria

- Entry saved to `~/.claude/knowledge/{category}/` or `docs/09-lessons-learned/` with correct frontmatter
- User confirmed the draft before saving
- Related entries (>=2 keyword overlap) have mutual `related:` cross-references in frontmatter
