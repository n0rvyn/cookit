# Unified Session Summary Schema

Both `parse_claude_session.py` and `parse_codex_session.py` produce this identical JSON structure.

## Schema

```json
{
  "session_id": "string — unique session identifier",
  "source": "claude-code | codex",
  "project": "string — basename of cwd (e.g. 'indie-toolkit')",
  "project_path": "string — full working directory path",
  "branch": "string | null — git branch name",
  "model": "string | null — model identifier (e.g. 'claude-opus-4-6', 'gpt-5.4')",
  "time": {
    "start": "ISO 8601 timestamp — first record in session",
    "end": "ISO 8601 timestamp — last record in session",
    "duration_min": "number | null — session duration in minutes"
  },
  "turns": {
    "user": "int — count of user messages",
    "assistant": "int — count of unique assistant messages (by message ID for Claude Code)"
  },
  "tokens": {
    "input": "int | null — total input tokens",
    "output": "int | null — total output tokens (includes reasoning tokens for Codex)",
    "cache_read": "int | null — cached input tokens read",
    "cache_create": "int | null — cache creation input tokens",
    "cache_hit_rate": "float (0-1) | null — cache_read / (input + cache_read)"
  },
  "tools": {
    "distribution": "object — {tool_name: call_count}",
    "total_calls": "int — sum of all tool calls",
    "sequence": "string[] — ordered list of tool names as called"
  },
  "files": {
    "read": "string[] — sorted file paths passed to Read tool",
    "edited": "string[] — sorted file paths passed to Edit tool",
    "created": "string[] — sorted file paths passed to Write tool"
  },
  "quality": {
    "repeated_edits": "object — {file_path: count} where count > 2",
    "bash_errors": "int — count of Bash tool calls with non-zero exit",
    "build_attempts": "int — count of build/compile commands detected",
    "build_failures": "int — count of failed build commands"
  },
  "session_dna": "explore | build | fix | chat | mixed — placeholder, set by LLM agent in Phase 2",
  "user_prompts": "string[] — first N user message texts (truncated to 500 chars each)",
  "task_summary": "string — placeholder, set by LLM agent in Phase 2",
  "corrections": "array — placeholder, populated by LLM agent in Phase 2",
  "emotion_signals": "array — [{turn, type, trigger, text}], placeholder filled by session-parser agent",
  "prompt_assessments": "array — [{turn, original, issues, rewrite, improvement_note}], placeholder filled by session-parser agent",
  "process_gaps": "array — [{type, evidence, suggestion}], placeholder filled by session-parser agent"
}
```

## Source Field Mapping

### Claude Code → Unified

| Unified Field | Claude Code Source |
|---------------|-------------------|
| session_id | `record.sessionId` or filename stem |
| source | hardcoded `"claude-code"` |
| project | `basename(record.cwd)` |
| project_path | `record.cwd` |
| branch | `record.gitBranch` |
| model | `record.message.model` |
| time.start/end | `record.timestamp` (first/last) |
| turns.user | count of `type=user` records |
| turns.assistant | count of unique `message.id` in `type=assistant` records |
| tokens.input | sum of `message.usage.input_tokens` |
| tokens.output | sum of `message.usage.output_tokens` |
| tokens.cache_read | sum of `message.usage.cache_read_input_tokens` |
| tokens.cache_create | sum of `message.usage.cache_creation_input_tokens` |
| tools | from `tool_use` content blocks: `block.name`, `block.input` |
| files | from tool inputs: Read(`file_path`), Edit(`file_path`), Write(`file_path`) |

### Codex → Unified

| Unified Field | Codex Source |
|---------------|-------------|
| session_id | `session_meta.payload.id` |
| source | hardcoded `"codex"` |
| project | `basename(session_meta.payload.cwd)` |
| project_path | `session_meta.payload.cwd` |
| branch | `session_meta.payload.git.branch` |
| model | `turn_context.payload.model` |
| time.start/end | `record.timestamp` (first/last) |
| turns.user | count of `response_item` with `payload.role=user` |
| turns.assistant | count of `response_item` with `payload.role=assistant` |
| tokens.input | `event_msg[token_count].info.total_token_usage.input_tokens` (last event, cumulative) |
| tokens.output | `output_tokens + reasoning_output_tokens` (last event) |
| tokens.cache_read | `cached_input_tokens` (last event) |
| tokens.cache_create | `input_tokens - cached_input_tokens` (last event) |
| tools | from `response_item` with `payload.type=function_call`: `payload.name` |
| files | limited; extracted from `exec_command` arguments when file paths detectable |

## Placeholder Fields

These fields are set to default values by the Python scripts and populated by LLM agents in Phase 2:

| Field | Default | Populated By |
|-------|---------|-------------|
| session_dna | `"mixed"` | session-parser agent (classifies by tool pattern) |
| task_summary | `""` | session-parser agent (generates from content) |
| corrections | `[]` | session-parser agent (identifies user corrections) |
| emotion_signals | `[]` | session-parser agent (detects frustration, impatience, satisfaction, etc.) |
| prompt_assessments | `[]` | session-parser agent (assesses prompt quality: issues, rewrites) |
| process_gaps | `[]` | session-parser agent (detects workflow anti-patterns: skipped exploration, no verification, etc.) |

## Tool Name Differences

| Claude Code Tool | Codex Equivalent |
|-----------------|------------------|
| Read | (part of exec_command: `cat`, `head`) |
| Edit | apply_patch |
| Write | (part of exec_command: `cat >`) |
| Bash | exec_command |
| Grep | (part of exec_command: `grep`, `rg`) |
| Glob | (part of exec_command: `find`, `ls`) |
| Agent | (no equivalent) |
| — | write_stdin (Codex-specific) |
