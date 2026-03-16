---
skill: session-search
---

## Trigger Tests
- "search sessions"
- "find session"
- "session search"
- "find session about caching"
- "find my session on March 10"
- "find that session where I fixed"

## Negative Trigger Tests
- "search code"
- "grep for"
- "commit"

## Output Assertions
- [ ] Returns ranked session list for keyword queries
- [ ] Each result shows session_id, project, date, summary
- [ ] --semantic flag enables LLM ranking
- [ ] Cross-project search works
- [ ] Error handling: "No sessions match" for empty results
- [ ] Suggests /kb and /session-replay
