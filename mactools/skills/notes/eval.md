# notes Eval

## Trigger Tests
<!-- Prompts that SHOULD trigger this skill -->
- "List my notes"
- "Create a new note titled 'Meeting Notes'"
- "Search for notes about 'project'"
- "查找关于会议的备忘录"
- "Append text to my existing note"

## Negative Trigger Tests
<!-- Prompts that should NOT trigger this skill -->
- "Send an email"
- "Create a reminder"
- "Fix this bug"

## Output Assertions
<!-- What must be true in the skill's output -->
- [ ] Output uses notes.sh script from skills/notes/scripts/
- [ ] Output supports folders, list, read, create, append, search commands
- [ ] Output handles folder filtering and result limits (-n flag)
- [ ] Output presents notes with title, folder, creation/modification date
- [ ] Create command creates note in default folder if not specified
- [ ] Append command adds text to existing note content

## Redundancy Risk
Baseline comparison: Base model cannot access local macOS Notes.app data; this skill provides AppleScript integration
Last tested model: Opus 4.6
Last tested date: 2026-03-08
Verdict: essential
