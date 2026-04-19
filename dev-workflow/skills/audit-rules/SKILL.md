---
name: audit-rules
description: "Use when Claude exhibited unexpected behavior, for periodic rule health checks, or after adding new rules. Audits CLAUDE.md rules from the AI execution perspective for conflicts, loopholes, gaps, and redundancies."
disable-model-invocation: true
---

## Overview

This skill dispatches the `dev-workflow:rules-auditor` agent to audit CLAUDE.md rules in a separate context so it starts with a fresh, unbiased perspective.

## Process

### Step 1: Gather Context

Collect the following before dispatching:

1. **Deviation description** — from the user's message (e.g., "Claude added animations without asking"). Set to "periodic check" if none provided
2. **Global CLAUDE.md path** — `~/.claude/CLAUDE.md`
3. **Project CLAUDE.md path** — check for `CLAUDE.md` in project root (may not exist)
4. **Installed plugin behaviors** — discover installed plugins and collect their behavioral surface:
   - Glob `~/.claude/plugins/*/*/.claude-plugin/plugin.json` to find installed plugins
   - For each plugin found:
     - Read `hooks/hooks.json` (if exists) — extract hook events, matchers, and script paths
     - Read each hook shell script to extract the behavioral description (first comment line after shebang)
     - Glob `skills/*/SKILL.md` — extract frontmatter `description` field from each
   - Compile into a structured summary per plugin:
     ```
     Plugin: {name}
     Hooks:
     - {Event}({Matcher}): {description from script comment}
     - ...
     Skills:
     - {name}: "{description from frontmatter}"
     - ...
     ```
   - If no plugins found: pass "No plugins installed" to agent

### Step 2: Dispatch Agent

Use the Agent tool to launch the `dev-workflow:rules-auditor` agent with all gathered context. Structure the task prompt as:

```
Audit CLAUDE.md rules with the following inputs:

Deviation description: {description or "periodic check"}
Global CLAUDE.md: ~/.claude/CLAUDE.md
Project CLAUDE.md: {path or "none"}
Installed plugin behaviors:
{compiled plugin behavior summary, or "No plugins installed"}
```

### Step 3: Present Results

When the agent completes:

1. **Validate DP count**: Parse the `Decisions:` line for N+M total, count actual `DP-\d+` entries in headings. If mismatch, prepend warning to report: `⚠️ 报告声称 {N+M} 个决策点，实际只列了 {actual} 个。以实际条目为准。`
2. Present the Rules Review Report returned by the agent
3. **Decision Points:** Check the agent's return for `Decisions:` count.
   - If Decisions > 0:
     - First time this session: Read `${CLAUDE_PLUGIN_ROOT}/references/decision-points.md`
     - Apply the rules with parameters:
       - Source file: the audit report
       - Mode: `mixed`
       - Recording: `conversation-only`
4. If fix recommendations were made:
   - List each recommendation
   - Ask the user: "Execute these fixes?"
5. If user approves: apply the recommended changes to the CLAUDE.md files
6. If user declines: done

## Completion Criteria

- Audit report presented to user
- If fixes recommended: user has approved or declined each recommendation
- If approved: changes applied to CLAUDE.md files
