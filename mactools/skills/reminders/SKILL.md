---
name: reminders
description: 查询、创建、完成、删除 macOS 提醒事项。当用户需要查看待办提醒、创建提醒、标记完成、搜索提醒事项时使用。关键词：提醒事项、Reminders、提醒、待办、remind、reminder。
compatibility: Requires macOS
allowed-tools: Bash(*skills/reminders/scripts/*)
---

# Reminders.app 提醒事项操作

通过 EventKit 框架连接 macOS Reminders，执行提醒事项的查看、搜索、创建、完成、删除操作。使用编译的 Swift 二进制，首次运行自动编译。

## 前提条件

- macOS Reminders 必须可用
- 首次运行需授权终端访问 Reminders（System Settings > Privacy & Security > Reminders）

## Path Setup

```bash
BASE="${CLAUDE_PLUGIN_ROOT:-${CODEX_HOME:-$HOME/.codex}}"
SKILLS_ROOT="$BASE/skills"
[ -d "$SKILLS_ROOT/reminders/scripts" ] || SKILLS_ROOT="$BASE/cookit/mactools/skills"
```

## 工具

```
${SKILLS_ROOT}/reminders/scripts/reminders.sh
```

## 命令

### 列出所有提醒列表

```bash
${SKILLS_ROOT}/reminders/scripts/reminders.sh lists
```

输出每个列表的名称和未完成提醒数量。

### 列出提醒事项

```bash
# 列出所有列表中的未完成提醒（默认最多 20 条）
${SKILLS_ROOT}/reminders/scripts/reminders.sh list

# 列出指定列表中的未完成提醒
${SKILLS_ROOT}/reminders/scripts/reminders.sh list "Work"

# 限制结果数量
${SKILLS_ROOT}/reminders/scripts/reminders.sh list -n 10
${SKILLS_ROOT}/reminders/scripts/reminders.sh list "Work" -n 5
```

### 今日到期

```bash
${SKILLS_ROOT}/reminders/scripts/reminders.sh today
${SKILLS_ROOT}/reminders/scripts/reminders.sh today -n 10
```

### 即将到期

```bash
# 未来 7 天（默认）
${SKILLS_ROOT}/reminders/scripts/reminders.sh upcoming

# 未来 14 天
${SKILLS_ROOT}/reminders/scripts/reminders.sh upcoming 14

# 未来 3 天，最多 5 条
${SKILLS_ROOT}/reminders/scripts/reminders.sh upcoming 3 -n 5
```

### 已过期未完成

```bash
${SKILLS_ROOT}/reminders/scripts/reminders.sh overdue
${SKILLS_ROOT}/reminders/scripts/reminders.sh overdue -n 10
```

### 搜索提醒

```bash
${SKILLS_ROOT}/reminders/scripts/reminders.sh search "keyword"
${SKILLS_ROOT}/reminders/scripts/reminders.sh search "keyword" -n 10
```

搜索范围：提醒名称和备注内容，不区分大小写。

### 创建提醒

```bash
# 基本创建（添加到默认列表）
${SKILLS_ROOT}/reminders/scripts/reminders.sh create "Buy milk"

# 指定列表和到期日
${SKILLS_ROOT}/reminders/scripts/reminders.sh create "Submit report" --list "Work" --due "2026-02-15"

# 带时间的到期日 + 提醒时间
${SKILLS_ROOT}/reminders/scripts/reminders.sh create "Meeting" --list "Work" --due "2026-02-12 14:00" --remind "2026-02-12 13:50"

# 完整选项
${SKILLS_ROOT}/reminders/scripts/reminders.sh create "Release v1.1" --list "Work" --due "2026-02-20" --notes "Includes new features" --priority 1
```

### 标记完成

```bash
# 在所有列表中查找并完成
${SKILLS_ROOT}/reminders/scripts/reminders.sh complete "Buy milk"

# 在指定列表中完成
${SKILLS_ROOT}/reminders/scripts/reminders.sh complete "Submit report" --list "Work"
```

### 删除提醒

```bash
# 在所有列表中查找并删除
${SKILLS_ROOT}/reminders/scripts/reminders.sh delete "Expired reminder"

# 在指定列表中删除
${SKILLS_ROOT}/reminders/scripts/reminders.sh delete "Expired reminder" --list "Work"
```

## 参数

| 参数 | 说明 | 适用命令 | 默认值 |
|------|------|---------|--------|
| `-n <count>` | 最大结果数 | list, today, upcoming, overdue, search | 20 |
| `--list "Name"` | 目标列表 | create, complete, delete | 默认列表 |
| `--due "Date"` | 到期日期 | create | 无 |
| `--remind "DateTime"` | 提醒时间（触发通知） | create | 无 |
| `--notes "Text"` | 备注 | create | 无 |
| `--priority <0-9>` | 优先级 | create | 0 (无) |

## 日期格式

| 格式 | 用途 | 示例 |
|------|------|------|
| `YYYY-MM-DD` | 仅日期（到期日） | `"2026-02-15"` |
| `YYYY-MM-DD HH:MM` | 日期+时间 | `"2026-02-15 14:00"` |

## 优先级值

| 值 | 含义 |
|----|------|
| 0 | 无优先级 |
| 1-4 | 高 |
| 5 | 中 |
| 6-9 | 低 |

## 输出格式

```
1. Submit report
   List: Work | Due: 2026-02-15 00:00 | Priority: high

2. Meeting
   List: Work | Due: 2026-02-12 14:00
   Discuss Q1 progress
```

## 常用工作流

### 每日检查

```bash
# 查看过期未完成
${SKILLS_ROOT}/reminders/scripts/reminders.sh overdue

# 查看今日到期
${SKILLS_ROOT}/reminders/scripts/reminders.sh today

# 查看本周待办
${SKILLS_ROOT}/reminders/scripts/reminders.sh upcoming 7
```

### 快速创建和完成

```bash
# 创建
${SKILLS_ROOT}/reminders/scripts/reminders.sh create "Reply to email" --list "Work" --due "2026-02-10 17:00"

# 完成
${SKILLS_ROOT}/reminders/scripts/reminders.sh complete "Reply to email" --list "Work"
```

## 错误处理

| 错误信息 | 原因 | 处理方式 |
|---------|------|---------|
| `Reminders access not granted` | 未授权 | System Settings > Privacy & Security > Reminders |
| `Error: List "X" not found.` | 列表名称不匹配 | 用 `lists` 确认列表名称 |
| `No incomplete reminder found` | 提醒已完成或名称不匹配 | 用 `search` 或 `list` 确认 |
| `No matching reminder found` | 名称不匹配 | 用 `search` 确认准确名称 |

## 注意事项

- 仅操作未完成的提醒事项（`list`、`search`、`complete`、`delete` 均过滤已完成项）
- 提醒名称匹配为精确匹配（`complete`、`delete`），搜索为模糊匹配（`search`）
- `delete` 永久删除提醒，不可恢复
- 优先级值遵循 Apple Reminders 标准：1-4=高，5=中，6-9=低，0=无
- 首次运行会自动编译 Swift 源码，需要 Xcode Command Line Tools
