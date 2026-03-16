---
skill: session-replay
---

## Trigger Tests
- "replay session"
- "show session"
- "show me abc123"
- "session replay abc123"

## Negative Trigger Tests
- "search sessions"
- "retro"
- "show trends"

## Output Assertions
- [ ] Shows session header (id, project, model, duration)
- [ ] Turn timeline with timestamps
- [ ] Tool sequence displayed
- [ ] File changes table
- [ ] --detail levels work (summary/standard/verbose)
- [ ] Error handling: "Session not found" for invalid id
