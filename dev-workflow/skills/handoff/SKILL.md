---
name: handoff
description: "Use when the session is running low on context, the user says 'handoff', or a complex task needs to continue in a new session. Generates a cold-start prompt for session transfer."
context: fork
model: haiku
---

## 使用场景

- 会话窗口即将用完（<15%）
- 任务未完成需要续接
- 复杂问题需要跨会话追踪

## 输出格式

```markdown
## 上下文恢复

项目：[项目名称和简述]
当前任务：[一句话描述]

### 执行计划（如有）
来源：[docs/06-plans/xxx.md | ~/.claude/plans/xxx.md | "用户消息内联提供" | 无]
状态：[全部完成 | 进行中(N/M) | 中断 | 无计划]
Crystal file：[docs/11-crystals/xxx-crystal.md | 无]

（dev-workflow:write-plan 计划文件在 docs/06-plans/，内置 /plan 计划文件在 ~/.claude/plans/，新会话可直接 Read）

### 问题
[遇到的核心问题，包含具体报错/现象]

### 已完成
1. [已完成项 1]
2. [已完成项 2]
...

### 当前状态
[刚做完什么，卡在哪里]

### 关键文件
- `path/to/file1` - 说明
- `path/to/file2` - 说明

### 下一步
1. [待做项 1]
2. [待做项 2]

### 关键代码/配置（如有）
[粘贴关键代码片段或配置，避免新会话重新查找]
```

## 执行指令

读取当前会话上下文，生成上述格式的 markdown。要求：
1. 信息密度高，去掉废话
2. 包含具体文件路径（绝对路径）
3. 包含具体错误信息/日志（如有）
4. 关键代码片段直接粘贴，不要说"见某文件"
5. 输出为 markdown 代码块，方便用户复制
6. 如果当前会话是按计划执行的，必须包含计划来源（文件路径或 transcript 路径）
7. 如果项目有 crystal 文件（`docs/11-crystals/*-crystal.md`），在关键文件中列出路径
