# collect-lesson Eval

## Trigger Tests
<!-- Prompts that SHOULD trigger this skill -->
- "Collect a lesson from this session about the bug we fixed"
- "Save what we learned about SwiftData concurrency to the knowledge base"
- "Extract an error entry from this debugging session"
- "记录这个 bug 的教训到知识库"
- "把刚才发现的架构约束保存为 lesson"
- "Save this API gotcha as a note"
- "Record this architecture decision"

## Negative Trigger Tests
<!-- Prompts that should NOT trigger this skill -->
- "Fix this bug"
- "Write a plan for the new feature"
- "Review my code"
- "Search the knowledge base" (should trigger /kb instead)

## Output Assertions
<!-- What must be true in the skill's output -->
- [ ] Output extracts structured content from the session
- [ ] Output asks user to confirm draft before saving
- [ ] Output includes category slug and 3-6 keywords
- [ ] Output writes file directly via Write tool (no MCP dependency)
- [ ] Output reports saved file path after completion
- [ ] Dedup check uses Grep over ~/.claude/knowledge/ (not MCP search)
- [ ] Supports multiple content types (lesson, API note, architecture decision, reference)
- [ ] After saving, searches ~/.claude/knowledge/ for entries with >=2 overlapping keywords
- [ ] Adds mutual `related:` frontmatter fields to both new and matched entries
- [ ] Reports cross-reference count (related found, links added, contradictions flagged) after saving
- [ ] Contradiction detection is best-effort and only flags obvious specific conflicts
- [ ] Ripple step is skipped for project-local saves (docs/09-lessons-learned/)

## Redundancy Risk
Baseline comparison: Base model can summarize sessions but lacks structured extraction, duplicate checking, and knowledge base conventions
Last tested model: Opus 4.6
Last tested date: 2026-03-10
Verdict: essential
