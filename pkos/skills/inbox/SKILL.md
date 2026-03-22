---
name: inbox
description: "Use when the user says 'inbox', 'process inbox', '处理收件箱', or wants to process captured items from iOS (Reminders, Notes, voice memos). Reads from all PKOS input sources, classifies, and routes to Obsidian/Notion."
user_invocable: true
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
${CLAUDE_PLUGIN_ROOT}/../mactools/skills/reminders/scripts/reminders.sh list "PKOS Inbox"
```
Parse output lines. Each reminder with title and notes becomes an inbox item with `source: reminder`, `raw_type: text` (or `url` if notes contain a URL).

**Notes:**
```bash
${CLAUDE_PLUGIN_ROOT}/../mactools/skills/notes/scripts/notes.sh list "PKOS Inbox"
```
For each note found, read its full content:
```bash
${CLAUDE_PLUGIN_ROOT}/../mactools/skills/notes/scripts/notes.sh read "Note Title"
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
```

If zero items found, report "Inbox is empty." and stop.

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
    topics: [topic1, topic2]
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
topics: [{topics}]
quality: 0
citations: 0
related: [{related_notes}]
status: seed
---

# {title}

{raw_content}
```

2. Create Notion Pipeline DB entry via MCP:
```
mcp__claude_ai_Notion__notion-create-pages(
  parent: {"data_source_id": "32a1bde4-ddac-8182-830b-000bbcbf077d"},
  pages: [{"properties": {
    "Title": "{title}",
    "Status": "inbox",
    "Source": "{source}",
    "Type": "{classification}",
    "Topics": "[{topics_json_array}]",
    "Priority": "{urgency}",
    "date:Created:start": "{today}",
    "date:Created:is_datetime": 0
  }}]
)
```
Note the returned page ID.

3. Update Notion status after Obsidian note written via MCP:
```
mcp__claude_ai_Notion__notion-update-page(
  page_id: "{notion_page_id}",
  command: "update_properties",
  properties: {
    "Status": "processed",
    "Obsidian Link": "obsidian://open?vault=PKOS&file={obsidian_path_encoded}",
    "date:Processed:start": "{today}",
    "date:Processed:is_datetime": 0
  }
)
```

**B. task → Notion only (no Obsidian note)**

1. Create Notion Pipeline DB entry with Status "actionable" via MCP:
```
mcp__claude_ai_Notion__notion-create-pages(
  parent: {"data_source_id": "32a1bde4-ddac-8182-830b-000bbcbf077d"},
  pages: [{"properties": {
    "Title": "{title}",
    "Status": "actionable",
    "Source": "{source}",
    "Type": "task",
    "Topics": "[{topics_json_array}]",
    "Priority": "{urgency}",
    "date:Created:start": "{today}",
    "date:Created:is_datetime": 0
  }}]
)
```

2. If urgency is high or a due date is mentioned, create a Reminder:
```bash
${CLAUDE_PLUGIN_ROOT}/../mactools/skills/reminders/scripts/reminders.sh create "{title}" --list "Tasks" --due "{due_date}"
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
${CLAUDE_PLUGIN_ROOT}/../mactools/skills/reminders/scripts/reminders.sh complete "{title}" --list "PKOS Inbox"
```

**Notes:**
```bash
${CLAUDE_PLUGIN_ROOT}/../mactools/skills/notes/scripts/notes.sh delete "{note_title}"
```

**Voice files:**
```bash
mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/PKOS/voice/processed/
mv "{voice_file_path}" ~/Library/Mobile\ Documents/com~apple~CloudDocs/PKOS/voice/processed/
```

### Step 6: Report

Present final summary:
```
✅ PKOS Inbox processed: {N} items
  📋 knowledge: {count} → Obsidian 10-Knowledge/
  💡 idea: {count} → Obsidian 20-Ideas/
  📎 reference: {count} → Obsidian 50-References/
  ✅ task: {count} → Notion
  💬 feedback: {count} → .signals/

All items synced to Notion Pipeline DB.
```

## Error Handling

- If mactools scripts fail (Reminders/Notes not found), log warning and continue with other sources
- If Notion API fails, log error but keep the Obsidian note (data is not lost)
- If voice transcription fails, skip that file and log warning
- Never block the entire pipeline for a single item failure

## Notion Configuration

- Pipeline DB data source ID: `32a1bde4-ddac-8182-830b-000bbcbf077d`
- Access method: Notion MCP (built-in, no token/proxy needed)
- MCP tools: `mcp__claude_ai_Notion__notion-create-pages`, `mcp__claude_ai_Notion__notion-update-page`
- Topics multi_select: only use existing options; to add new topics, update data source schema first
