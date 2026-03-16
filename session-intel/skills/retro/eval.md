---
skill: retro
---

## Trigger Tests
- "retro"
- "daily retro"
- "show my daily retro"
- "retrospective"
- "复盘"
- "what did I work on yesterday"

## Negative Trigger Tests
- "search sessions"
- "show trends"
- "cost report"

## Output Assertions
- [ ] Output contains "Overview" section
- [ ] Output contains session count
- [ ] Output contains project breakdown
- [ ] Output contains session DNA distribution
- [ ] Output contains emotion analysis section (when signals detected)
- [ ] Error handling: "No sessions found" for empty date range
- [ ] Suggests /collect-lesson for notable findings
