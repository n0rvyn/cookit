---
name: inbox
description: "Internal skill — processes captured items from iOS (Reminders, Notes, voice memos). Reads from all PKOS input sources, classifies, routes to Obsidian/Notion, and triggers ripple compilation. Triggered by Adam cron or via /pkos ingest."
model: sonnet
---

## Overview

Process all pending items in the PKOS inbox. Reads from Reminders "PKOS Inbox" list, Notes "PKOS Inbox" folder, and iCloud voice files. Each item is classified, enriched, and routed to the appropriate destination.

## Arguments

Parse from user input:
- `--dry-run`: Show what would be processed without making changes
- `--source SOURCE`: Process only from specific source (reminders | notes | voice | all). Default: all

## Process

### Step 1: Collect

Collect pending items from all sources (or filtered by `--source`).

**Reminders:**
```bash
${CLAUDE_PLUGIN_ROOT}/../../mactools/1.0.1/skills/reminders/scripts/reminders.sh list "PKOS Inbox"
```
Parse output lines. Each reminder with title and notes becomes an inbox item with `source: reminder`, `raw_type: text` (or `url` if notes contain a URL).

**Notes:**
```bash
${CLAUDE_PLUGIN_ROOT}/../../mactools/1.0.1/skills/notes/scripts/notes.sh list "PKOS Inbox"
```
For each note found, read its full content:
```bash
${CLAUDE_PLUGIN_ROOT}/../../mactools/1.0.1/skills/notes/scripts/notes.sh read "Note Title"
```
Each note becomes an inbox item with `source: note`, `raw_type: text`.

**Voice files:**
```bash
ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/PKOS/voice/*.m4a 2>/dev/null | grep -v '/processed/'
```
Each unprocessed .m4a file becomes an inbox item with `source: voice_memo`, `raw_type: audio`.

Present a summary to the user:
```
📥 PKOS Inbox: {N} items pending
  🔔 Reminders: {count}
  📝 Notes: {count}
  🎤 Voice: {count}
  🌐 Web (cleaned): {count}
```

If zero items found, report "Inbox is empty." and stop.

### Step 1.5: Clean Web Content (URL items only)

For each inbox item where `raw_type` is `url` or `raw_content` contains a URL (http:// or https://):

1. Extract the URL from the content
2. Run defuddle to get clean markdown:
   ```bash
   defuddle parse "{url}" --md
   ```
3. If defuddle succeeds (exit code 0):
   - Replace `raw_content` with defuddle output
   - Set `raw_type` to `cleaned_web`
   - Preserve the original URL in a new field `source_url`
4. If defuddle fails (URL unreachable, timeout, etc.):
   - Keep original `raw_content` unchanged
   - Log: `[inbox] defuddle failed for {url}: {error}. Using raw content.`

> Defuddle removes navigation, ads, and boilerplate from web pages, reducing noise before classification. Install: `npm install -g defuddle`

### Step 2: Transcribe Voice Files

For each voice item (raw_type: audio):

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/voice-transcribe.sh "{file_path}"
```

- Update `raw_content` with the transcription text
- Update `raw_type` to `voice_transcript`
- If transcription fails, log warning and set `raw_content` to "(transcription failed)"

### Step 3: Classify and Extract (dispatch inbox-processor agent)

Dispatch the `pkos:inbox-processor` agent with all collected items. The agent receives the items and returns routing decisions for each:

```yaml
items:
  - id: "reminder-{title-slug}"
    source: reminder
    raw_content: "the reminder text and notes"
    raw_type: text
  - id: "voice-en-2026-03-22"
    source: voice_memo
    raw_content: "transcribed text..."
    raw_type: voice_transcript
```

The agent returns:
```yaml
decisions:
  - id: "reminder-{slug}"
    classification: knowledge
    title: "Generated Title"
    keywords: [k1, k2, k3]
    tags: [tag1, tag2]
    urgency: low
    related_notes: ["10-Knowledge/related-note.md"]
    obsidian_path: "10-Knowledge/generated-title.md"
```

Present classification results to user for review before routing.

If `--dry-run`: display results and stop here.

### Step 4: Route to Destinations

Route each item based on its classification. Different types go to different destinations.

**A. knowledge / idea / reference → Obsidian + Notion**

1. Write Obsidian note at `~/Obsidian/PKOS/{obsidian_path}`:
```yaml
---
type: {classification}
source: {source}
created: {today's date}
tags: [{tags}]
quality: 0
citations: 0
related: [{related_notes}]
status: seed               # OR needs-reconciliation if conflict detected (see below)
aliases: []
---

# {title}

> [!insight] Source
> Captured from {source} on {today's date}.

{raw_content}

## Connections

{For each item in related_notes, output: `- [[{note-title}]]` using just the filename without path or extension}
{If inbox-processor identified a matching MOC topic, add: `- See also: [[MOC-{topic}]]`}
```

> Format reference: see `references/obsidian-format.md` for wikilink and callout conventions.

**Conflict handling:** If the inbox-processor returned `conflict_status: needs-reconciliation` for this item:
- Set `status: needs-reconciliation` (instead of `seed`) in the frontmatter
- Add `conflicts_with: [{conflicts_with paths}]` to the frontmatter
- Add `conflict_description: "{conflict_description}"` to the frontmatter
- The note is still written and routed normally — conflicts flag for human review, they do not block ingest.

> [!warning] Conflict Detected
> Conflicts with [[{conflicts_with note title}]]: {conflict_description}

2. Create Notion Pipeline DB entry via Python API (token and proxy from env):
```bash
NO_PROXY="*" python3 ~/.claude/skills/notion/scripts/notion_api.py create-db-item \
  32a1bde4-ddac-81ff-8f82-f2d8d7a361d7 \
  "{title}" \
  --props '{"Status": "inbox", "Source": "{source}", "Type": "{classification}", "Topics": "{tags_csv}", "Priority": "{urgency}"}'
```
Note the returned page ID from output.

3. Update Notion status after Obsidian note written:
```bash
NO_PROXY="*" python3 ~/.claude/skills/notion/scripts/notion_api.py update-db-item-properties \
  {notion_page_id} \
  --props '{"Status": "processed", "Obsidian Link": "obsidian://open?vault=PKOS&file={obsidian_path_encoded}"}'
```

**B. task → Notion only (no Obsidian note)**

1. Create Notion Pipeline DB entry with Status "actionable":
```bash
NO_PROXY="*" python3 ~/.claude/skills/notion/scripts/notion_api.py create-db-item \
  32a1bde4-ddac-81ff-8f82-f2d8d7a361d7 \
  "{title}" \
  --props '{"Status": "actionable", "Source": "{source}", "Type": "task", "Topics": "{tags_csv}", "Priority": "{urgency}"}'
```

2. If urgency is high or a due date is mentioned, create a Reminder:
```bash
${CLAUDE_PLUGIN_ROOT}/../../mactools/1.0.1/skills/reminders/scripts/reminders.sh create "{title}" --list "Tasks" --due "{due_date}"
```

**C. feedback → .signals/ only (no Obsidian, no Notion)**

Write feedback signal to `.signals/` directory:
```bash
echo "- source: {source}
  content: \"{raw_content}\"
  timestamp: {today}T{now}" >> ~/Obsidian/PKOS/.signals/$(date +%Y-%m-%d)-feedback.yaml
```

### Step 5: Mark Source Items as Processed

**Reminders:**
```bash
${CLAUDE_PLUGIN_ROOT}/../../mactools/1.0.1/skills/reminders/scripts/reminders.sh complete "{title}" --list "PKOS Inbox"
```

**Notes:**
```bash
${CLAUDE_PLUGIN_ROOT}/../../mactools/1.0.1/skills/notes/scripts/notes.sh delete "{note_title}"
```

**Voice files:**
```bash
mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/PKOS/voice/processed/
mv "{voice_file_path}" ~/Library/Mobile\ Documents/com~apple~CloudDocs/PKOS/voice/processed/
```

### Step 5.5: Ripple Compilation

For each item that was routed to Obsidian (classification: knowledge, idea, or reference):

Dispatch `pkos:ripple-compiler` agent with:
```yaml
note_path: "{obsidian_path}"
title: "{title}"
tags: [{tags from inbox-processor decision}]
related_notes: [{related_notes from inbox-processor decision}]
```

If processing multiple items, dispatch ripple for each sequentially (not parallel) to avoid concurrent MOC edits.

If ripple fails for an item, log warning and continue — the source note is already saved, ripple can be retried later.

### Step 6: Report

Present final summary:
```
PKOS Inbox processed: {N} items
  knowledge: {count} → Obsidian 10-Knowledge/
  idea: {count} → Obsidian 20-Ideas/
  reference: {count} → Obsidian 50-References/
  task: {count} → Notion
  feedback: {count} → .signals/

Wiki compilation:
  MOCs updated: {count}
  MOCs created: {count}
  Cross-references added: {count}
  Conflicts flagged: {count} (need human reconciliation)

All items synced to Notion Pipeline DB.
```

## Error Handling

- If mactools scripts fail (Reminders/Notes not found), log warning and continue with other sources
- If Notion API fails, log error but keep the Obsidian note (data is not lost)
- If voice transcription fails, skip that file and log warning
- Never block the entire pipeline for a single item failure

## Notion Configuration

- Pipeline DB ID: `32a1bde4-ddac-81ff-8f82-f2d8d7a361d7`
- Access method: Python API (`~/.claude/skills/notion/scripts/notion_api.py`)
- Token + proxy: provided via Adam template env (`NOTION_TOKEN`, `NO_PROXY`)
- Topics multi_select: use existing options from DB schema
