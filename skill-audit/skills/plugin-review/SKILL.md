---
name: plugin-review
description: "Use when the user says 'review skill', 'review agent', 'review plugin', 'audit plugin', or after creating/modifying skills and agents. Reviews Claude Code plugin artifacts (skills, agents, hooks, commands) from the AI executor perspective for logic bugs, trigger issues, and execution feasibility."
---

# Plugin Review

以 Claude Code 执行者视角审查 plugin 产物（skills, agents, hooks, commands），发现逻辑 bug、触发机制问题和执行可行性缺陷。

> **DEPRECATED:** This skill has been absorbed into `skill-master:master`.
> Use `/master` with review intent instead. This skill remains functional
> but will not receive updates.

## Overview

This skill orchestrates plugin review across 9 dimensions. It detects whether the optional `plugin-dev` plugin is installed and routes accordingly:

- **Strategy A** (plugin-dev available): dispatches `plugin-dev:plugin-validator` + `plugin-dev:skill-reviewer` + own `plugin-reviewer` in parallel, then merges results
- **Strategy B** (plugin-dev not installed): dispatches own `plugin-reviewer` with supporting files to cover all 9 dimensions

## Process

### Step 1: Determine Scope

从用户消息判断审查范围：

**Scope A — 指定文件**：用户给出具体 skill/agent 文件路径。

**Scope B — 指定 plugin**：用户指定 plugin 名称或目录。收集该 plugin 下所有 skills 和 agents：
- Glob `{plugin}/skills/*/SKILL.md` → all skills
- Glob `{plugin}/agents/*.md` → all agents

**Scope C — 最近变更**：用户说"review my changes"或无明确指定。用 `git diff --name-only HEAD` 找到最近修改的 skill/agent 文件。如果 working tree 是 clean 的（已 commit），改用用户指定的范围（commit hash、`HEAD~N`、`--since` 等），或默认 `git log --name-only -1 --pretty=format:""` 获取最后一次 commit 的变更文件。

**Scope D — 全量审查**：用户说"review all"或"audit everything"。收集所有已安装 plugin 的 skills 和 agents。

在审查范围确定后，列出将被审查的文件清单，让用户确认。

### Step 2: Gather Context

对审查范围内的每个 plugin，收集：

1. **Plugin manifest** — `.claude-plugin/plugin.json`
2. **All skill files** — `skills/*/SKILL.md`
3. **All agent files** — `agents/*.md`
4. **Marketplace registration** — 检查 `.claude-plugin/marketplace.json` 是否包含该 plugin
5. **Eval files** — 对每个 skill 目录，检查是否存在 `skills/{name}/eval.md`

构建文件清单传递给 agent。

### Step 2.5: Detect plugin-dev Availability

Check whether the `plugin-dev` plugin is installed:
- Glob for `~/.claude/plugins/*/plugin-dev/.claude-plugin/plugin.json` or `.claude/plugins/cache/*/plugin-dev/*/.claude-plugin/plugin.json`
- If found: use **Strategy A**
- If not found: use **Strategy B**

Record the strategy choice for Step 4.

### Step 3: Dispatch (Strategy A or B)

**Strategy A — plugin-dev available (3 parallel dispatches in a single message):**

1. `plugin-dev:plugin-validator` agent:
```
Validate this Claude Code plugin's structure.
Plugin manifest: {path}
Skills: {comma-separated paths}
Agents: {comma-separated paths}
```

2. `plugin-dev:skill-reviewer` agent:
```
Review these skill descriptions for trigger quality and routing clarity.
Skills: {comma-separated paths}
```

3. `skill-audit:plugin-reviewer` agent with `model: "opus"`:
```
Review these Claude Code plugin artifacts from the AI executor perspective.

Scope: {A: specific files | B: plugin | C: recent changes | D: all}
Files to review:
- Skills: {comma-separated paths}
- Agents: {comma-separated paths}
- Plugin manifest: {path}

Also read these for cross-reference checking:
- Other skills in same plugin(s): {paths, for trigger conflict detection}
- Other agents in same plugin(s): {paths, for reference integrity}
- Eval files: {comma-separated paths or "none"} — for trigger plausibility checking

Supporting files to load: none
Plugin agents dir: !`echo "${CLAUDE_PLUGIN_ROOT}/agents"`
(D1/D2 structural checks and baseline trigger/description checks are handled by plugin-dev agents.)

Focus on: workflow logic, execution feasibility, edge cases, dispatch loops, spec compliance, metadata & docs, eval.md consumption, deep trigger conflict detection, and Trigger Health Score.
Do NOT review code style or formatting — only functional correctness.
```

**Strategy B — plugin-dev not available (1 dispatch):**

`skill-audit:plugin-reviewer` agent with `model: "opus"`:
```
Review these Claude Code plugin artifacts from the AI executor perspective.

Scope: {A: specific files | B: plugin | C: recent changes | D: all}
Files to review:
- Skills: {comma-separated paths}
- Agents: {comma-separated paths}
- Plugin manifest: {path}

Also read these for cross-reference checking:
- Other skills in same plugin(s): {paths, for trigger conflict detection}
- Other agents in same plugin(s): {paths, for reference integrity}
- Eval files: {comma-separated paths or "none"} — for trigger plausibility checking

Supporting files to load: structural-validation.md, trigger-baseline.md
Plugin agents dir: !`echo "${CLAUDE_PLUGIN_ROOT}/agents"`

Focus on: logic bugs, trigger mechanism issues, execution feasibility, and edge cases.
Do NOT review code style or formatting — only functional correctness.
```

### Step 4: Present Results

When all dispatched agents complete:

**Strategy A — merge results:**
1. If any agent dispatch failed or timed out: mark its dimensions as "Error: agent did not return results" in the Dimension Summary and proceed with available results
2. Collect all findings from the 3 agents, tagging each finding with its source agent
3. Deduplicate: if multiple agents flag the same issue (same file + same location), keep the more specific finding
4. Map findings to the 9-dimension Dimension Summary table. Use finding content to determine the appropriate dimension row — do not rely on dimension IDs from external agents' output format
5. Assemble into the unified Plugin Review Report format (same structure as Strategy B output)

**Strategy B — direct presentation:**
Present the `plugin-reviewer` output directly.

**Both strategies:**
1. Group findings by severity:
   - **Bug** — will cause incorrect behavior or execution failure
   - **Logic** — won't fail but reduces effectiveness or produces misleading results
   - **Minor** — cosmetic or low-impact concerns
2. For each Bug-severity finding, include the suggested fix inline
3. If fixes exist: ask user "Apply suggested fixes?" and apply if approved

## Completion Criteria

- Review report presented with findings grouped by severity
- Every finding has a file:line reference and specific description
- Bug-severity findings include actionable fix suggestions
- If user approved fixes: changes applied
