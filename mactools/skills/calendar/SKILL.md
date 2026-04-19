---
name: calendar
description: "查询、创建、修改、删除 macOS 日历事件。当用户需要查看日程、创建会议、搜索日历事件时使用。Use when the user needs to view schedules, create meetings, or search calendar events. Keywords: 日历, Calendar, 日程, 会议, 事件, 安排."
context: fork
model: haiku
compatibility: Requires macOS
allowed-tools: Bash(*skills/calendar/scripts/*)
---

# Calendar 日历操作

通过 EventKit 框架连接 macOS Calendar，执行日历事件的查看、搜索、创建、删除操作。使用编译的 Swift 二进制，首次运行自动编译。

## 前提条件

- macOS Calendar 必须可用
- 首次运行需授权终端访问 Calendar（System Settings > Privacy & Security > Calendars）

## 工具

```
${CLAUDE_SKILL_DIR}/scripts/calendar.sh
```

## Core Commands

### Today's Events

```bash
${CLAUDE_SKILL_DIR}/scripts/calendar.sh today
${CLAUDE_SKILL_DIR}/scripts/calendar.sh today -n 10
```

### Upcoming Events

```bash
# Next 7 days (default)
${CLAUDE_SKILL_DIR}/scripts/calendar.sh upcoming

# Next 14 days
${CLAUDE_SKILL_DIR}/scripts/calendar.sh upcoming 14

# Next 3 days, max 5 results
${CLAUDE_SKILL_DIR}/scripts/calendar.sh upcoming 3 -n 5
```

### Search Events

```bash
${CLAUDE_SKILL_DIR}/scripts/calendar.sh search "Team Meeting"
${CLAUDE_SKILL_DIR}/scripts/calendar.sh search "Standup" -n 5
```

Search scope: event title, location, and notes within 1 year back to 1 year ahead. Case-insensitive.

### List Calendars

```bash
${CLAUDE_SKILL_DIR}/scripts/calendar.sh calendars
```

### Create Event

```bash
# Timed event
${CLAUDE_SKILL_DIR}/scripts/calendar.sh create "Team Meeting" "2026-02-10 09:00" "2026-02-10 10:00"

# Timed event with options
${CLAUDE_SKILL_DIR}/scripts/calendar.sh create "Lunch" "2026-02-10 12:00" "2026-02-10 13:00" --calendar "Personal" --location "Restaurant" --notes "Bring gift"

# All-day event
${CLAUDE_SKILL_DIR}/scripts/calendar.sh create "Vacation" "2026-02-15" "2026-02-16"

# All-day event on specific calendar
${CLAUDE_SKILL_DIR}/scripts/calendar.sh create "Conference" "2026-03-01" "2026-03-03" --calendar "Work"
```

### Delete Event

```bash
${CLAUDE_SKILL_DIR}/scripts/calendar.sh delete "Team Meeting" "2026-02-10"
```

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `-n <count>` | Max results (default: 20) | `-n 10` |
| `--calendar "Name"` | Target calendar (create only) | `--calendar "Work"` |
| `--location "Place"` | Event location (create only) | `--location "Room A"` |
| `--notes "Text"` | Event notes (create only) | `--notes "Bring laptop"` |

## Date Formats

| Format | Usage | Example |
|--------|-------|---------|
| `YYYY-MM-DD HH:MM` | Timed event start/end | `"2026-02-10 09:00"` |
| `YYYY-MM-DD` | All-day event start/end | `"2026-02-10"` |

When both start and end use `YYYY-MM-DD` format (no time), the event is created as all-day.

## Output Format

Events are displayed as:

```
1. Event Title
   Calendar: Work | Date: 2026-02-10 09:00 - 2026-02-10 10:00 | Location: Room A

2. Day Off
   Calendar: Personal | Date: 2026-02-15 (all-day)
```

## Common Workflows

### Morning Check

```bash
# What's on today?
${CLAUDE_SKILL_DIR}/scripts/calendar.sh today

# What's coming this week?
${CLAUDE_SKILL_DIR}/scripts/calendar.sh upcoming 7
```

### Schedule a Meeting

```bash
# First check available calendars
${CLAUDE_SKILL_DIR}/scripts/calendar.sh calendars

# Create the event
${CLAUDE_SKILL_DIR}/scripts/calendar.sh create "Project Review" "2026-02-12 14:00" "2026-02-12 15:00" --calendar "Work" --location "Conference Room B" --notes "Q1 progress review"
```

### Find and Remove an Event

```bash
# Search for the event
${CLAUDE_SKILL_DIR}/scripts/calendar.sh search "Project Review"

# Delete it
${CLAUDE_SKILL_DIR}/scripts/calendar.sh delete "Project Review" "2026-02-12"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Calendar access not granted` | Enable in System Settings > Privacy & Security > Calendars |
| `Calendar "X" not found` | Check exact calendar name with `calendars` command |
| `No matching event found` | Event title must match exactly; verify with `search` first |
| `Invalid date format` | Use `YYYY-MM-DD HH:MM` or `YYYY-MM-DD` |

## Limitations

- Cannot modify existing events (delete and recreate instead)
- Event title match for delete is exact (case-sensitive)
- Read-only calendars (subscribed/birthday) cannot be written to
- Recurring event deletion deletes only the instance on the specified date
- First run requires Xcode Command Line Tools for compilation
