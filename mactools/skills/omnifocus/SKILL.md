---
name: omnifocus
description: "查询、创建、完成 OmniFocus 4 任务和项目。仅当用户明确提及 OmniFocus 或 OmniFocus 特有概念（项目、透视、上下文）时使用。Use only when the user explicitly mentions OmniFocus or OmniFocus-specific concepts (projects, perspectives, contexts). Keywords: OmniFocus, 项目, inbox, flagged, perspectives."
context: fork
model: haiku
compatibility: Requires macOS
allowed-tools: Bash(*skills/omnifocus/scripts/*)
---

# OmniFocus 4 Operations

Connect to OmniFocus 4 on macOS and perform authorized operations: list tasks, create tasks, complete tasks, check inbox, view flagged tasks, manage projects, contexts, perspectives, and more.

## Prerequisites

- OmniFocus 4 must be installed on macOS
- OmniFocus must be running (the skill will prompt to launch if not)

## Core Commands

### Status Overview

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py status
```

### List Tasks

```bash
# List all incomplete tasks (limit 20)
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py list

# List tasks in specific project
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py list "Project Name"
```

### Inbox Tasks

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py inbox
```

### Flagged Tasks

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py flagged
```

### Due Tasks

```bash
# Due within 7 days (default)
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py due

# Due within custom days
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py due 14

# Due today
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py due today

# Due tomorrow
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py due tomorrow

# Due this week
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py due week

# Overdue tasks
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py due overdue
```

### List Projects

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py projects
```

## Contexts 上下文

### List All Contexts

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py contexts
```

### Set Task Context

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py set-context "Task Name" "Context Name"
```

### Clear Task Context

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py clear-context "Task Name"
```

## Due Dates 截止日期

### Set Task Due Date

```bash
# Set with natural language
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py set-due "Task Name" "tomorrow"

# Set with relative format
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py set-due "Task Name" "+3d"

# Set with absolute date
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py set-due "Task Name" "2025-02-01"
```

### Clear Task Due Date

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py clear-due "Task Name"
```

## Defer Dates 开始日期

### Set Task Defer Date

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py set-defer "Task Name" "+3d"
```

### Clear Task Defer Date

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py clear-defer "Task Name"
```

## Repetition Rules 重复规则

### Set Task Repetition

```bash
# Daily
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py set-repeat "Task Name" "FREQ=DAILY"

# Weekly
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py set-repeat "Task Name" "FREQ=WEEKLY"

# Every 2 weeks
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py set-repeat "Task Name" "FREQ=WEEKLY;INTERVAL=2"

# Monthly
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py set-repeat "Task Name" "FREQ=MONTHLY"
```

### Clear Task Repetition

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py clear-repeat "Task Name"
```

## Note Operations 备注

### Append Note to Task

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py append-note "Task Name" "Additional note text"
```

## Task Operations

### Create Task

```bash
# Create task in inbox
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py add "Task Name"

# Create task with options
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py add "Task Name" --project "Project" --context "Context" --due "tomorrow" --defer "+1d" --note "Task note"

# Create task with repetition
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py add "Daily Task" --repeat "FREQ=DAILY"
```

### Complete Task

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py complete "Task Name"
```

### Toggle Flag

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py flag "Task Name"
```

### Delete Task

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py delete "Task Name"
```

## Project Operations

### Show Project Details

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py show-project "Project Name"
```

### Create Project

```bash
# Create project in root
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py create-project "Project Name"

# Create project in folder
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py create-project "Project Name" "Folder Name"
```

## Folder Operations

### List All Folders

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py folders
```

### Create Folder

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py create-folder "Folder Name"
```

## Perspective Operations 透视

### List All Perspectives

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py perspectives
```

### Activate Perspective

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py activate-perspective "Perspective Name"
```

## Date Formats 日期格式

### Natural Language 自然语言
- `今天` / `today` - Today
- `明天` / `tomorrow` - Tomorrow
- `后天` - Day after tomorrow
- `下周` / `next week` - Next week

### Relative Formats 相对格式
- `+3d` - 3 days from now
- `+1w` - 1 week from now
- `+2m` - 2 months from now (approx. 60 days)

### Absolute Formats 绝对格式
- `2025-02-01` - ISO format
- `02/01/2025` - MM/DD/YYYY

> ⚠️ 仅支持 MM/DD/YYYY 格式，避免 DD/MM 歧义。遇到模糊日期（如 `01/02`）时，向用户确认。

### Short Formats 短格式
- `02-01` - February 1st (current year, MM-DD)
- `02/01` - February 1st (current year, MM/DD)

## Common Workflows

### Daily Review
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py status
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py inbox
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py flagged
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py due today
```

### Weekly Review
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py projects
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py contexts
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py due week
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py due overdue
```

### Quick Capture
```bash
# Quick add to inbox
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py add "Buy milk"

# Add with context and due date
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py add "Call John" --context "Phone" --due "tomorrow"

# Add recurring task
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py add "Daily standup" --project "Work" --repeat "FREQ=DAILY"
```

### Context-Based Work
```bash
# List all contexts
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py contexts

# Start working in a context
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py activate-perspective "Context: Errands"

# Assign context to task
python3 ${CLAUDE_SKILL_DIR}/scripts/omnifocus_cli.py set-context "Buy groceries" "Errands"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "OmniFocus is not running" | Launch OmniFocus first |
| "Project not found" | Check exact project name with `projects` command |
| "Context not found" | Check exact context name with `contexts` command |
| "Multiple matching tasks" | Use more specific task name |
| Task not found | Task may already be completed or deleted |
| "Invalid date" | Check date format against Date Formats section |
| "Invalid range" | Use: today, tomorrow, week, overdue |

## Limitations

- Requires OmniFocus 4 running on macOS
- Cannot modify completed tasks
- Project and context names must match exactly
- Task matching is case-insensitive but uses substring matching
- Repetition rules use OmniFocus's iCalendar syntax
