---
name: collect-lesson
description: "Use after resolving a bug, completing a task with notable pitfalls, or discovering an important architecture constraint. Extracts a structured lesson entry from the session and saves it to the knowledge base."
user-invocable: false
---

## Overview

This skill extracts a structured lesson or error entry from the current session and writes it to the knowledge base via `add_entry`. It checks for near-duplicates before creating, and asks the user to confirm the draft.

## Process

### Step 1: Extract Entry from Session

Review the current conversation to identify:

1. **Symptom** — What went wrong or what was the key observation? (1-2 sentences)
2. **Root cause** — Why did it happen? (1-2 sentences)
3. **Prevention** — What rule or check prevents this in the future? (1-2 sentences)
4. **Keywords** — 3-6 keywords for FTS search (error type, component name, API name, pattern name)
5. **Category** — Pick the most fitting slug: `value-domain`, `concurrency`, `swiftdata`, `swift-concurrency`, `architecture`, `tooling`, `testing`, `ux`, `api-misuse`, or a new slug if none fit
6. **Source type** — `error` for bugs and pitfalls, `lesson` for best practices and architecture decisions

Compose a draft markdown body:

```markdown
## Symptom

{symptom — 1-2 sentences}

## Root Cause

{root-cause — 1-2 sentences}

## Prevention

{prevention — 1-2 sentences}
```

### Step 2: Check for Near-Duplicates (if search tool available)

1. Call `search(query="<keywords joined by space>", source_type=["error", "lesson"], project_root="<cwd>")`
2. If results score > 0.5: present them to the user as "Similar entries already in knowledge base:" and ask whether to continue creating a new entry or update the existing one
3. If no results or search unavailable: skip and continue

### Step 3: Ask User for Title and Scope

Present the draft entry to the user:

```
Draft lesson entry:

Title:     {suggested title — 5-8 words, action-oriented}
Category:  {category}
Keywords:  {keyword1}, {keyword2}, ...
Scope:     project (saves to docs/09-lessons-learned/) OR global (saves to ~/.claude/rag/lessons/)

---
{markdown body}
---

Confirm: save as-is, edit, or skip?
If saving: project or global scope?
```

Wait for user response. Apply any edits the user requests before calling `add_entry`.

### Step 4: Save Entry

Once the user confirms:

Call `add_entry` with:
- `title`: confirmed title
- `category`: category slug
- `scope`: user-chosen scope ("project" or "global")
- `content`: the markdown body
- `keywords`: list of keyword strings
- `source_type`: "error" or "lesson"
- `project_root`: current working directory (required when scope is "project")

Report back: `Saved as {id} at {path}`

### Graceful Degradation

If `add_entry` tool is unavailable: print the draft entry and tell the user to copy it manually to `docs/09-lessons-learned/E{NNN}-{slug}.md` with the front-matter format shown in the entry.
