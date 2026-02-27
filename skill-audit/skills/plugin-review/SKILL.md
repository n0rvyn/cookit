---
name: plugin-review
description: "Use when the user says 'review skill', 'review agent', 'review plugin', 'audit plugin', or after creating/modifying skills and agents. Reviews Claude Code plugin artifacts (skills, agents, hooks, commands) from the AI executor perspective for logic bugs, trigger issues, and execution feasibility."
---

# Plugin Review

以 Claude Code 执行者视角审查 plugin 产物（skills, agents, hooks, commands），发现逻辑 bug、触发机制问题和执行可行性缺陷。

## Overview

This skill dispatches the `plugin-reviewer` agent to systematically review plugin artifacts. The review covers 7 dimensions: structural validation, reference integrity, workflow logic, execution feasibility, trigger/routing conflicts, edge case analysis, and spec compliance (Agent Skills Spec field conventions).

## Process

### Step 1: Determine Scope

从用户消息判断审查范围：

**Scope A — 指定文件**：用户给出具体 skill/agent 文件路径。

**Scope B — 指定 plugin**：用户指定 plugin 名称或目录。收集该 plugin 下所有 skills 和 agents：
- Glob `{plugin}/skills/*/SKILL.md` → all skills
- Glob `{plugin}/agents/*.md` → all agents

**Scope C — 最近变更**：用户说"review my changes"或无明确指定。用 `git diff --name-only HEAD` 找到最近修改的 skill/agent 文件。

**Scope D — 全量审查**：用户说"review all"或"audit everything"。收集所有已安装 plugin 的 skills 和 agents。

在审查范围确定后，列出将被审查的文件清单，让用户确认。

### Step 2: Gather Context

对审查范围内的每个 plugin，收集：

1. **Plugin manifest** — `.claude-plugin/plugin.json`
2. **All skill files** — `skills/*/SKILL.md`
3. **All agent files** — `agents/*.md`
4. **Marketplace registration** — 检查 `.claude-plugin/marketplace.json` 是否包含该 plugin

构建文件清单传递给 agent。

### Step 3: Dispatch plugin-reviewer Agent

Use the Task tool to launch the `plugin-reviewer` agent with `model: "opus"`:

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

Focus on: logic bugs, trigger mechanism issues, execution feasibility, and edge cases.
Do NOT review code style or formatting — only functional correctness.
```

### Step 4: Present Results

When the agent completes:

1. Present the Plugin Review Report
2. Group findings by severity:
   - **Bug** — will cause incorrect behavior or execution failure
   - **Logic** — won't fail but reduces effectiveness or produces misleading results
   - **Minor** — cosmetic or low-impact concerns
3. For each Bug-severity finding, include the suggested fix inline
4. If fixes exist: ask user "Apply suggested fixes?" and apply if approved

## Completion Criteria

- Review report presented with findings grouped by severity
- Every finding has a file:line reference and specific description
- Bug-severity findings include actionable fix suggestions
- If user approved fixes: changes applied
