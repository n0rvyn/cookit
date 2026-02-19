#!/usr/bin/env python3
"""
OmniFocus 4 操作工具
通过 AppleScript 与 OmniFocus 交互
"""

import subprocess
import sys
import re
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple


def parse_date(date_str: str) -> Optional[datetime]:
    """
    解析多种日期格式:
    - 自然语言: "今天", "明天", "后天", "下周"
    - 相对格式: "+3d", "+1w", "+2m"
    - 绝对格式: "2025-02-01", "02/01/2025"
    """
    if not date_str:
        return None

    date_str = date_str.strip().lower()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # 自然语言解析
    natural_map = {
        "今天": today,
        "明天": today + timedelta(days=1),
        "后天": today + timedelta(days=2),
        "下周": today + timedelta(weeks=1),
        "today": today,
        "tomorrow": today + timedelta(days=1),
        "next week": today + timedelta(weeks=1),
    }

    if date_str in natural_map:
        return natural_map[date_str]

    # 相对格式解析: +3d, +1w, +2m
    relative_pattern = r'^[\+]?(\d+)([dwmDWM])$'
    match = re.match(relative_pattern, date_str)
    if match:
        num = int(match.group(1))
        unit = match.group(2).lower()
        if unit == 'd':
            return today + timedelta(days=num)
        elif unit == 'w':
            return today + timedelta(weeks=num)
        elif unit == 'm':
            # 月份处理: 近似为30天
            return today + timedelta(days=num * 30)

    # 绝对日期解析
    date_formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%d-%m-%Y",
    ]

    for fmt in date_formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed
        except ValueError:
            continue

    # 尝试解析只有月日的格式（默认今年）
    short_formats = [
        "%m-%d",
        "%m/%d",
        "%d-%m",
        "%d/%m",
    ]

    for fmt in short_formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            # 设置为今年
            parsed = parsed.replace(year=today.year)
            return parsed
        except ValueError:
            continue

    return None


def format_date_for_applescript(dt: datetime) -> str:
    """
    将 datetime 转换为 AppleScript 可识别的日期格式
    返回格式: "date \"MM/DD/YYYY HH:MM:SS\""
    """
    return f'date "{dt.strftime("%m/%d/%Y %H:%M:%S")}"'


def parse_command_args() -> Tuple[List[str], Dict[str, str]]:
    """
    解析命令行参数
    返回: (位置参数列表, 关键字参数字典)
    支持: --option value 或 --flag
    """
    args = sys.argv[2:]
    kwargs = {}
    positional = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('--'):
            key = arg[2:].replace('-', '_')
            if i + 1 < len(args) and not args[i + 1].startswith('--'):
                kwargs[key] = args[i + 1]
                i += 2
            else:
                kwargs[key] = True
                i += 1
        else:
            positional.append(arg)
            i += 1

    return positional, kwargs


def escape_applescript_string(s: str) -> str:
    """
    转义 AppleScript 字符串中的特殊字符
    """
    if not s:
        return ""
    # 转义双引号和反斜杠
    return s.replace('\\', '\\\\').replace('"', '\\"')


def run_applescript(script: str) -> str:
    """执行 AppleScript 并返回结果"""
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: Script execution timed out"
    except Exception as e:
        return f"Error: {str(e)}"


def get_status() -> str:
    """获取 OmniFocus 状态概览"""
    script = '''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        set allTasks to every flattened task
        set incompleteTasks to every flattened task whose completed is false
        set flaggedTasks to every flattened task whose flagged is true and completed is false
        set completedTasks to every flattened task whose completed is true
        set allProjects to every flattened project
        set activeProjects to every flattened project whose status is active status

        return "OmniFocus Status Overview
========================

Task Statistics
---------------
Total:       " & (count of allTasks) & "
Incomplete:  " & (count of incompleteTasks) & "
Flagged:     " & (count of flaggedTasks) & "
Completed:   " & (count of completedTasks) & "

Project Statistics
------------------
Total:       " & (count of allProjects) & "
Active:      " & (count of activeProjects) & "
"
    end tell
end tell
'''
    return run_applescript(script)


def list_tasks(project_name: Optional[str] = None, limit: int = 20, context: Optional[str] = None) -> str:
    """列出任务，可按项目和上下文筛选"""
    project_str = escape_applescript_string(project_name) if project_name else ""
    context_str = escape_applescript_string(context) if context else ""

    if context:
        script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set targetContext to first flattened context whose name is "{context_str}"
            set contextTasks to every flattened task whose (completed is false) and (context is targetContext)
            set output to "Tasks in context '{context_str}' (" & (count of contextTasks) & ")
========================

"
            set taskCount to 0
            repeat with t in contextTasks
                try
                    set taskCount to taskCount + 1
                    if taskCount > {limit} then
                        set output to output & "
... and " & ((count of contextTasks) - {limit}) & " more tasks
"
                        exit repeat
                    end if
                    set taskName to name of t
                    set projName to ""
                    try
                        set projName to name of (containing project of t)
                    end try
                    set flagStr to ""
                    if flagged of t then set flagStr to "[Flagged] "
                    set output to output & taskCount & ". " & flagStr & taskName
                    if projName is not "" then
                        set output to output & " [" & projName & "]"
                    end if
                    set output to output & "
"
                end try
            end repeat
            return output
        on error
            return "Error: Context '{context_str}' not found"
        end try
    end tell
end tell
'''
        return run_applescript(script)

    if project_name:
        script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set targetProject to first flattened project whose name is "{project_str}"
            set projTasks to every task of targetProject whose completed is false
            set output to "Project: {project_str} (" & (count of projTasks) & " incomplete tasks)
========================

"
            set taskCount to 0
            repeat with t in projTasks
                try
                    set taskCount to taskCount + 1
                    if taskCount > {limit} then exit repeat
                    set taskName to name of t
                    set flagStr to ""
                    if flagged of t then set flagStr to "[Flagged] "
                    set output to output & taskCount & ". " & flagStr & taskName & "
"
                end try
            end repeat
            return output
        on error
            return "Error: Project '{project_str}' not found"
        end try
    end tell
end tell
'''
    else:
        script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        set incompleteTasks to every flattened task whose completed is false
        set output to "All Incomplete Tasks (" & (count of incompleteTasks) & ")
========================

"
        set taskCount to 0
        repeat with t in incompleteTasks
            try
                set taskCount to taskCount + 1
                if taskCount > {limit} then
                    set output to output & "
... and " & ((count of incompleteTasks) - {limit}) & " more tasks
"
                    exit repeat
                end if
                set taskName to name of t
                set projName to ""
                try
                    set projName to name of (containing project of t)
                end try
                set flagStr to ""
                if flagged of t then set flagStr to "[Flagged] "
                set output to output & taskCount & ". " & flagStr & taskName
                if projName is not "" then
                    set output to output & " [" & projName & "]"
                end if
                set output to output & "
"
            end try
        end repeat
        return output
    end tell
end tell
'''
    return run_applescript(script)


def list_inbox() -> str:
    """列出收件箱任务"""
    script = '''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        set inboxTasks to every inbox task whose completed is false
        set output to "Inbox Tasks (" & (count of inboxTasks) & ")
========================

"
        set taskCount to 0
        repeat with t in inboxTasks
            try
                set taskCount to taskCount + 1
                set taskName to name of t
                set flagStr to ""
                if flagged of t then set flagStr to "[Flagged] "
                set output to output & taskCount & ". " & flagStr & taskName & "
"
            end try
        end repeat
        return output
    end tell
end tell
'''
    return run_applescript(script)


def list_flagged() -> str:
    """列出已标记任务"""
    script = '''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        set flaggedTasks to every flattened task whose flagged is true and completed is false
        set output to "Flagged Tasks (" & (count of flaggedTasks) & ")
========================

"
        set taskCount to 0
        repeat with t in flaggedTasks
            try
                set taskCount to taskCount + 1
                set taskName to name of t
                set projName to ""
                try
                    set projName to name of (containing project of t)
                end try
                set output to output & taskCount & ". " & taskName
                if projName is not "" then
                    set output to output & " [" & projName & "]"
                end if
                set output to output & "
"
            end try
        end repeat
        return output
    end tell
end tell
'''
    return run_applescript(script)


def list_due(days: int = 7) -> str:
    """列出即将到期的任务"""
    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        set todayDate to current date
        set futureDate to todayDate + ({days} * days)
        set allIncompleteTasks to every flattened task whose completed is false
        set dueTasks to {{}}
        repeat with t in allIncompleteTasks
            try
                set dueDateVal to due date of t
                if dueDateVal is not missing value then
                    if dueDateVal <= futureDate then
                        set end of dueTasks to t
                    end if
                end if
            end try
        end repeat

        set output to "Due within {days} days (" & (count of dueTasks) & ")
========================

"
        set taskCount to 0
        repeat with t in dueTasks
            try
                set taskCount to taskCount + 1
                set taskName to name of t
                set dueDateVal to due date of t
                set dateStr to short date string of dueDateVal
                set projName to ""
                try
                    set projName to name of (containing project of t)
                end try
                set flagStr to ""
                if flagged of t then set flagStr to "[Flagged] "
                set output to output & taskCount & ". " & flagStr & taskName & "
"
                set output to output & "   Due: " & dateStr
                if projName is not "" then
                    set output to output & " | Project: " & projName
                end if
                set output to output & "

"
            end try
        end repeat
        return output
    end tell
end tell
'''
    return run_applescript(script)


def list_due_by_range(range_str: str) -> str:
    """
    按时间范围列出到期任务
    range_str: "today", "tomorrow", "week", "overdue"
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = None
    end_date = None
    title = ""

    if range_str == "today":
        start_date = today
        end_date = today + timedelta(days=1)
        title = "Due Today"
    elif range_str == "tomorrow":
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=2)
        title = "Due Tomorrow"
    elif range_str == "week":
        start_date = today
        end_date = today + timedelta(days=7)
        title = "Due This Week"
    elif range_str == "overdue":
        end_date = today
        title = "Overdue"
    else:
        return f"Error: Invalid range '{range_str}'. Use: today, tomorrow, week, overdue"

    start_str = format_date_for_applescript(start_date) if start_date else "missing value"
    end_str = format_date_for_applescript(end_date) if end_date else "missing value"

    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        set allIncompleteTasks to every flattened task whose completed is false
        set dueTasks to {{}}

        repeat with t in allIncompleteTasks
            try
                set dueDateVal to due date of t
                if dueDateVal is not missing value then
'''

    if range_str == "overdue":
        script += f'''
                    if dueDateVal < {end_str} then
                        set end of dueTasks to t
                    end if
'''
    elif start_date and end_date:
        script += f'''
                    if dueDateVal >= {start_str} and dueDateVal < {end_str} then
                        set end of dueTasks to t
                    end if
'''

    script += f'''
                end if
            end try
        end repeat

        set output to "{title} (" & (count of dueTasks) & ")
========================

"
        set taskCount to 0
        repeat with t in dueTasks
            try
                set taskCount to taskCount + 1
                set taskName to name of t
                set dueDateVal to due date of t
                set dateStr to short date string of dueDateVal
                set projName to ""
                try
                    set projName to name of (containing project of t)
                end try
                set flagStr to ""
                if flagged of t then set flagStr to "[Flagged] "
                set output to output & taskCount & ". " & flagStr & taskName & "
"
                set output to output & "   Due: " & dateStr
                if projName is not "" then
                    set output to output & " | Project: " & projName
                end if
                set output to output & "

"
            end try
        end repeat
        return output
    end tell
end tell
'''
    return run_applescript(script)


def list_projects() -> str:
    """列出所有项目"""
    script = '''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        set allProjects to every flattened project
        set activeProjects to every flattened project whose status is active status

        set output to "All Projects (" & (count of allProjects) & ")
========================

[Active Projects]
"
        repeat with proj in activeProjects
            try
                set projName to name of proj
                set projTasks to every task of proj whose completed is false
                set output to output & "- " & projName & " (" & (count of projTasks) & " tasks)
"
            end try
        end repeat

        return output
    end tell
end tell
'''
    return run_applescript(script)


def list_contexts() -> str:
    """列出所有上下文"""
    script = '''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        set allContexts to every flattened context
        set output to "All Contexts (" & (count of allContexts) & ")
========================

"
        repeat with ctx in allContexts
            try
                set ctxName to name of ctx
                set ctxTasks to every flattened task whose (completed is false) and (context is ctx)
                set output to output & "- " & ctxName & " (" & (count of ctxTasks) & " tasks)
"
            end try
        end repeat
        return output
    end tell
end tell
'''
    return run_applescript(script)


def list_folders() -> str:
    """列出所有文件夹"""
    script = '''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        set allFolders to every folder
        set output to "All Folders (" & (count of allFolders) & ")
========================

"
        repeat with f in allFolders
            try
                set fName to name of f
                set output to output & "- " & fName & "
"
            end try
        end repeat
        return output
    end tell
end tell
'''
    return run_applescript(script)


def list_perspectives() -> str:
    """列出所有透视"""
    script = '''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    set allPerspectives to every built-in perspective
    set output to "Built-in Perspectives (" & (count of allPerspectives) & ")
========================

"
    repeat with p in allPerspectives
        try
            set pName to name of p
            set output to output & "- " & pName & "
"
        end try
    end repeat
    return output
end tell
'''
    return run_applescript(script)


def add_task(name: str, project: Optional[str] = None, note: str = "",
             context: Optional[str] = None, due: Optional[str] = None,
             defer: Optional[str] = None, repeat_rule: Optional[str] = None) -> str:
    """创建新任务，支持上下文、截止日期、开始日期、重复规则"""
    name_str = escape_applescript_string(name)
    project_str = escape_applescript_string(project) if project else ""
    note_str = escape_applescript_string(note)
    context_str = escape_applescript_string(context) if context else ""

    # 构建任务属性
    properties = [f'name:"{name_str}"']
    if note_str:
        properties.append(f'note:"{note_str}"')

    # 处理截止日期
    due_str = ""
    if due:
        due_date = parse_date(due)
        if due_date:
            due_str = format_date_for_applescript(due_date)
            properties.append(f'due date:{due_str}')
        else:
            return f"Error: Invalid due date '{due}'"

    # 处理开始日期
    defer_str = ""
    if defer:
        defer_date = parse_date(defer)
        if defer_date:
            defer_str = format_date_for_applescript(defer_date)
            properties.append(f'defer date:{defer_str}')
        else:
            return f"Error: Invalid defer date '{defer}'"

    properties_dict = "{" + ", ".join(properties) + "}"

    # 构建上下文设置脚本
    context_script = ""
    if context_str:
        context_script = f'''
try
    set targetContext to first flattened context whose name is "{context_str}"
    set context of newTask to targetContext
on error
    -- Context not found, task created without context
end try
'''

    # 构建重复规则设置脚本
    repeat_script = ""
    if repeat_rule:
        repeat_rule_escaped = escape_applescript_string(repeat_rule)
        repeat_script = f'''
try
    set repetition rule of newTask to "{repeat_rule_escaped}"
on error
    -- Could not set repetition rule
end try
'''

    # 构建项目版本脚本
    if project:
        project_msg = f"Project: {project_str}" + (f'\nDue: {due}' if due else '')
        if context:
            project_msg += f'\nContext: {context}'

        script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set targetProject to first flattened project whose name is "{project_str}"
            tell targetProject
                set newTask to make new task with properties {properties_dict}
            end tell
            {context_script}
            {repeat_script}
            return "Task created
Name: {name_str}
{project_msg}"
        on error
            return "Error: Project \\"{project_str}\\" not found"
        end try
    end tell
end tell
'''
    else:
        # 构建收件箱版本脚本
        inbox_msg = f"Task created in inbox\nName: {name_str}" + (f'\nDue: {due}' if due else '')
        if context:
            inbox_msg += f'\nContext: {context}'

        script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        set newTask to make new inbox task with properties {properties_dict}
        {context_script}
        {repeat_script}
            return "{inbox_msg}"
    end tell
end tell
'''

    return run_applescript(script)


def set_task_context(task_name: str, context_name: str) -> str:
    """设置任务上下文"""
    task_name_escaped = escape_applescript_string(task_name)
    context_name_escaped = escape_applescript_string(context_name)

    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set matchingTasks to every flattened task whose name contains "{task_name_escaped}" and completed is false

            if (count of matchingTasks) = 0 then
                return "Error: No matching task found '{task_name_escaped}'"
            else if (count of matchingTasks) = 1 then
                set targetTask to first item of matchingTasks
                try
                    set targetContext to first flattened context whose name is "{context_name_escaped}"
                    set context of targetTask to targetContext
                    return "Task context set
Task: {task_name_escaped}
Context: {context_name_escaped}"
                on error
                    return "Error: Context '{context_name_escaped}' not found"
                end try
            else
                return "Multiple matching tasks found, please be more specific"
            end if
        on error errMsg
            return "Error: Failed to set task context - " & errMsg
        end try
    end tell
end tell
'''
    return run_applescript(script)


def clear_task_context(task_name: str) -> str:
    """清除任务上下文"""
    task_name_escaped = escape_applescript_string(task_name)

    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set matchingTasks to every flattened task whose name contains "{task_name_escaped}" and completed is false

            if (count of matchingTasks) = 0 then
                return "Error: No matching task found '{task_name_escaped}'"
            else if (count of matchingTasks) = 1 then
                set targetTask to first item of matchingTasks
                set context of targetTask to missing value
                return "Task context cleared
Task: {task_name_escaped}"
            else
                return "Multiple matching tasks found, please be more specific"
            end if
        on error errMsg
            return "Error: Failed to clear task context - " & errMsg
        end try
    end tell
end tell
'''
    return run_applescript(script)


def set_task_due(task_name: str, date_str: str) -> str:
    """设置任务截止日期"""
    task_name_escaped = escape_applescript_string(task_name)
    due_date = parse_date(date_str)

    if not due_date:
        return f"Error: Invalid due date '{date_str}'"

    due_formatted = format_date_for_applescript(due_date)
    due_display = due_date.strftime("%Y-%m-%d")

    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set matchingTasks to every flattened task whose name contains "{task_name_escaped}" and completed is false

            if (count of matchingTasks) = 0 then
                return "Error: No matching task found '{task_name_escaped}'"
            else if (count of matchingTasks) = 1 then
                set targetTask to first item of matchingTasks
                set due date of targetTask to {due_formatted}
                return "Task due date set
Task: {task_name_escaped}
Due: {due_display}"
            else
                return "Multiple matching tasks found, please be more specific"
            end if
        on error errMsg
            return "Error: Failed to set task due date - " & errMsg
        end try
    end tell
end tell
'''
    return run_applescript(script)


def clear_task_due(task_name: str) -> str:
    """清除任务截止日期"""
    task_name_escaped = escape_applescript_string(task_name)

    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set matchingTasks to every flattened task whose name contains "{task_name_escaped}" and completed is false

            if (count of matchingTasks) = 0 then
                return "Error: No matching task found '{task_name_escaped}'"
            else if (count of matchingTasks) = 1 then
                set targetTask to first item of matchingTasks
                set due date of targetTask to missing value
                return "Task due date cleared
Task: {task_name_escaped}"
            else
                return "Multiple matching tasks found, please be more specific"
            end if
        on error errMsg
            return "Error: Failed to clear task due date - " & errMsg
        end try
    end tell
end tell
'''
    return run_applescript(script)


def set_task_defer(task_name: str, date_str: str) -> str:
    """设置任务开始日期（defer date）"""
    task_name_escaped = escape_applescript_string(task_name)
    defer_date = parse_date(date_str)

    if not defer_date:
        return f"Error: Invalid defer date '{date_str}'"

    defer_formatted = format_date_for_applescript(defer_date)
    defer_display = defer_date.strftime("%Y-%m-%d")

    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set matchingTasks to every flattened task whose name contains "{task_name_escaped}" and completed is false

            if (count of matchingTasks) = 0 then
                return "Error: No matching task found '{task_name_escaped}'"
            else if (count of matchingTasks) = 1 then
                set targetTask to first item of matchingTasks
                set defer date of targetTask to {defer_formatted}
                return "Task defer date set
Task: {task_name_escaped}
Defer: {defer_display}"
            else
                return "Multiple matching tasks found, please be more specific"
            end if
        on error errMsg
            return "Error: Failed to set task defer date - " & errMsg
        end try
    end tell
end tell
'''
    return run_applescript(script)


def clear_task_defer(task_name: str) -> str:
    """清除任务开始日期"""
    task_name_escaped = escape_applescript_string(task_name)

    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set matchingTasks to every flattened task whose name contains "{task_name_escaped}" and completed is false

            if (count of matchingTasks) = 0 then
                return "Error: No matching task found '{task_name_escaped}'"
            else if (count of matchingTasks) = 1 then
                set targetTask to first item of matchingTasks
                set defer date of targetTask to missing value
                return "Task defer date cleared
Task: {task_name_escaped}"
            else
                return "Multiple matching tasks found, please be more specific"
            end if
        on error errMsg
            return "Error: Failed to clear task defer date - " & errMsg
        end try
    end tell
end tell
'''
    return run_applescript(script)


def set_task_repetition(task_name: str, recurrence: str) -> str:
    """设置任务重复规则"""
    task_name_escaped = escape_applescript_string(task_name)
    recurrence_escaped = escape_applescript_string(recurrence)

    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set matchingTasks to every flattened task whose name contains "{task_name_escaped}" and completed is false

            if (count of matchingTasks) = 0 then
                return "Error: No matching task found '{task_name_escaped}'"
            else if (count of matchingTasks) = 1 then
                set targetTask to first item of matchingTasks
                set repetition rule of targetTask to "{recurrence_escaped}"
                return "Task repetition rule set
Task: {task_name_escaped}
Rule: {recurrence_escaped}"
            else
                return "Multiple matching tasks found, please be more specific"
            end if
        on error errMsg
            return "Error: Failed to set task repetition - " & errMsg
        end try
    end tell
end tell
'''
    return run_applescript(script)


def clear_task_repetition(task_name: str) -> str:
    """清除任务重复规则"""
    task_name_escaped = escape_applescript_string(task_name)

    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set matchingTasks to every flattened task whose name contains "{task_name_escaped}" and completed is false

            if (count of matchingTasks) = 0 then
                return "Error: No matching task found '{task_name_escaped}'"
            else if (count of matchingTasks) = 1 then
                set targetTask to first item of matchingTasks
                set repetition rule of targetTask to ""
                return "Task repetition rule cleared
Task: {task_name_escaped}"
            else
                return "Multiple matching tasks found, please be more specific"
            end if
        on error errMsg
            return "Error: Failed to clear task repetition - " & errMsg
        end try
    end tell
end tell
'''
    return run_applescript(script)


def append_note(task_name: str, note: str) -> str:
    """追加任务备注"""
    task_name_escaped = escape_applescript_string(task_name)
    note_escaped = escape_applescript_string(note)

    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set matchingTasks to every flattened task whose name contains "{task_name_escaped}" and completed is false

            if (count of matchingTasks) = 0 then
                return "Error: No matching task found '{task_name_escaped}'"
            else if (count of matchingTasks) = 1 then
                set targetTask to first item of matchingTasks
                set existingNote to note of targetTask
                if existingNote is "" then
                    set note of targetTask to "{note_escaped}"
                else
                    set note of targetTask to existingNote & "\\n\\n" & "{note_escaped}"
                end if
                return "Note appended to task
Task: {task_name_escaped}"
            else
                return "Multiple matching tasks found, please be more specific"
            end if
        on error errMsg
            return "Error: Failed to append note - " & errMsg
        end try
    end tell
end tell
'''
    return run_applescript(script)


def show_project(project_name: str) -> str:
    """显示项目详情"""
    project_name_escaped = escape_applescript_string(project_name)

    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set targetProject to first flattened project whose name is "{project_name_escaped}"
            set allTasks to every task of targetProject
            set incompleteTasks to every task of targetProject whose completed is false
            set completedTasks to every task of targetProject whose completed is true

            set projectStatus to status of targetProject as string
            set projectNote to note of targetProject
            if projectNote is "" then
                set projectNote to "(no note)"
            end if

            set output to "Project: {project_name_escaped}
========================

Status: " & projectStatus & "
Total Tasks: " & (count of allTasks) & "
Incomplete: " & (count of incompleteTasks) & "
Completed: " & (count of completedTasks) & "

Note:
" & projectNote & "

[Tasks]
"
            set taskCount to 0
            repeat with t in incompleteTasks
                try
                    set taskCount to taskCount + 1
                    set taskName to name of t
                    set flagStr to ""
                    if flagged of t then set flagStr to "[Flagged] "
                    set output to output & taskCount & ". " & flagStr & taskName & "
"
                end try
            end repeat
            return output
        on error
            return "Error: Project '{project_name_escaped}' not found"
        end try
    end tell
end tell
'''
    return run_applescript(script)


def create_project(project_name: str, folder_name: Optional[str] = None) -> str:
    """创建新项目"""
    project_name_escaped = escape_applescript_string(project_name)
    folder_name_escaped = escape_applescript_string(folder_name) if folder_name else ""

    if folder_name:
        script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set targetFolder to first folder whose name is "{folder_name_escaped}"
            tell targetFolder
                set newProject to make new project with properties {{name:"{project_name_escaped}"}}
            end tell
            return "Project created
Name: {project_name_escaped}
Folder: {folder_name_escaped}"
        on error
            return "Error: Folder '{folder_name_escaped}' not found"
        end try
    end tell
end tell
'''
    else:
        script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        set newProject to make new project with properties {{name:"{project_name_escaped}"}}
        return "Project created in root
Name: {project_name_escaped}"
    end tell
end tell
'''
    return run_applescript(script)


def create_folder(folder_name: str) -> str:
    """创建新文件夹"""
    folder_name_escaped = escape_applescript_string(folder_name)

    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        set newFolder to make new folder with properties {{name:"{folder_name_escaped}"}}
        return "Folder created
Name: {folder_name_escaped}"
    end tell
end tell
'''
    return run_applescript(script)


def activate_perspective(perspective_name: str) -> str:
    """激活指定透视"""
    perspective_name_escaped = escape_applescript_string(perspective_name)

    script = f'''
tell application "OmniFocus"
    if not running then
        activate
    end if
    try
        set targetPerspective to first built-in perspective whose name is "{perspective_name_escaped}"
        activate perspective targetPerspective
        return "Perspective activated: {perspective_name_escaped}"
    on error
        return "Error: Perspective '{perspective_name_escaped}' not found"
    end try
end tell
'''
    return run_applescript(script)


def complete_task(name: str) -> str:
    """完成任务"""
    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set matchingTasks to every flattened task whose name contains "{name}" and completed is false

            if (count of matchingTasks) = 0 then
                return "Error: No matching task found '{name}'"
            else if (count of matchingTasks) = 1 then
                set targetTask to first item of matchingTasks
                set taskNameFull to name of targetTask
                set completed of targetTask to true
                return "Task completed
" & taskNameFull
            else
                set output to "Multiple matching tasks found, please be more specific:

"
                set i to 1
                repeat with t in matchingTasks
                    try
                        set n to name of t
                        set projName to ""
                        try
                            set projName to name of (containing project of t)
                        end try
                        set output to output & i & ". " & n
                        if projName is not "" then
                            set output to output & " [" & projName & "]"
                        end if
                        set output to output & "
"
                        set i to i + 1
                    end try
                end repeat
                return output
            end if
        on error errMsg
            return "Error: Failed to complete task - " & errMsg
        end try
    end tell
end tell
'''
    return run_applescript(script)


def toggle_flag(name: str) -> str:
    """切换任务标记状态"""
    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set matchingTasks to every flattened task whose name contains "{name}" and completed is false

            if (count of matchingTasks) = 0 then
                return "Error: No matching task found '{name}'"
            else if (count of matchingTasks) = 1 then
                set targetTask to first item of matchingTasks
                set taskNameFull to name of targetTask
                set currentFlag to flagged of targetTask
                set flagged of targetTask to (not currentFlag)

                if currentFlag then
                    return "Task unflagged
" & taskNameFull
                else
                    return "Task flagged
" & taskNameFull
                end if
            else
                return "Multiple matching tasks found, please be more specific"
            end if
        on error errMsg
            return "Error: Failed to flag task - " & errMsg
        end try
    end tell
end tell
'''
    return run_applescript(script)


def delete_task(name: str) -> str:
    """删除任务"""
    script = f'''
tell application "OmniFocus"
    if not running then return "OmniFocus is not running"
    tell front document
        try
            set matchingTasks to every flattened task whose name contains "{name}"

            if (count of matchingTasks) = 0 then
                return "Error: No matching task found '{name}'"
            else if (count of matchingTasks) = 1 then
                set targetTask to first item of matchingTasks
                set taskNameFull to name of targetTask
                delete targetTask
                return "Task deleted
" & taskNameFull
            else
                return "Multiple matching tasks found, please be more specific"
            end if
        on error errMsg
            return "Error: Failed to delete task - " & errMsg
        end try
    end tell
end tell
'''
    return run_applescript(script)


def print_usage():
    """打印使用说明"""
    print("""OmniFocus 4 CLI Tool

Usage: python3 omnifocus_cli.py <command> [args] [options]

Core Commands:
  status              - Show task statistics
  list [project]      - List tasks (optionally filter by project)
  inbox               - Show inbox tasks
  flagged             - Show flagged tasks
  due [days]          - Show tasks due within days (default 7)
  due today           - Show tasks due today
  due tomorrow        - Show tasks due tomorrow
  due week            - Show tasks due this week
  due overdue         - Show overdue tasks
  projects            - List all projects

Contexts:
  contexts            - List all contexts
  set-context <task> <context> - Set task context
  clear-context <task> - Clear task context

Task Operations:
  add <name> [options] - Create new task
    Options:
      --project <name>   Set project
      --context <name>   Set context
      --due <date>       Set due date
      --defer <date>     Set defer date
      --note <text>      Add note
      --repeat <rule>     Set repetition rule

  complete <name>     - Mark task as complete
  flag <name>         - Toggle flag status
  delete <name>        - Delete task

Due Date Operations:
  set-due <task> <date>  - Set task due date
  clear-due <task>        - Clear task due date

Defer Date Operations:
  set-defer <task> <date> - Set task defer date
  clear-defer <task>       - Clear task defer date

Repetition Operations:
  set-repeat <task> <rule> - Set task repetition rule
  clear-repeat <task>       - Clear task repetition rule

Note Operations:
  append-note <task> <text> - Append text to task note

Project Operations:
  show-project <name>  - Show project details
  create-project <name> [folder] - Create new project

Folder Operations:
  folders             - List all folders
  create-folder <name> - Create new folder

Perspective Operations:
  perspectives        - List all perspectives
  activate-perspective <name> - Activate perspective

Date Formats:
  Natural: "今天", "明天", "tomorrow", "next week"
  Relative: "+3d", "+1w", "+2m"
  Absolute: "2025-02-01", "02/01/2025"
  Short: "02-01", "02/01" (defaults to current year)

Repetition Rules (examples):
  FREQ=DAILY           - Daily
  FREQ=WEEKLY          - Weekly
  FREQ=WEEKLY;INTERVAL=2 - Every 2 weeks
  FREQ=MONTHLY         - Monthly

Examples:
  # List all contexts
  python3 omnifocus_cli.py contexts

  # Create task with context and due date
  python3 omnifocus_cli.py add "Buy groceries" --context "Errands" --due "tomorrow"

  # Set task context
  python3 omnifocus_cli.py set-context "Buy groceries" "Errands"

  # List tasks due today
  python3 omnifocus_cli.py due today

  # Set defer date
  python3 omnifocus_cli.py set-defer "Report" "+3d"

  # Create project
  python3 omnifocus_cli.py create-project "New Project" "Work"
""")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    cmd = sys.argv[1].lower()
    positional, kwargs = parse_command_args()

    # Core commands
    if cmd == "status":
        print(get_status())
    elif cmd == "list":
        project = positional[0] if positional else None
        context = kwargs.get('context')
        print(list_tasks(project, context=context))
    elif cmd == "inbox":
        print(list_inbox())
    elif cmd == "flagged":
        print(list_flagged())
    elif cmd == "due":
        if positional:
            range_val = positional[0].lower()
            if range_val in ('today', 'tomorrow', 'week', 'overdue'):
                print(list_due_by_range(range_val))
            else:
                try:
                    days = int(range_val)
                    print(list_due(days))
                except ValueError:
                    print(f"Error: Invalid due range '{range_val}'")
        else:
            print(list_due(7))
    elif cmd == "projects":
        print(list_projects())

    # Contexts
    elif cmd == "contexts":
        print(list_contexts())
    elif cmd == "set-context":
        if len(positional) < 2:
            print("Error: Please provide task name and context name")
            return
        print(set_task_context(positional[0], positional[1]))
    elif cmd == "clear-context":
        if not positional:
            print("Error: Please provide task name")
            return
        print(clear_task_context(positional[0]))

    # Task operations
    elif cmd == "add":
        if not positional:
            print("Error: Please provide task name")
            return
        name = positional[0]
        project = kwargs.get('project')
        context = kwargs.get('context')
        due = kwargs.get('due')
        defer = kwargs.get('defer')
        note = kwargs.get('note', '')
        repeat_rule = kwargs.get('repeat')
        print(add_task(name, project, note, context, due, defer, repeat_rule))
    elif cmd == "complete":
        if not positional:
            print("Error: Please provide task name")
            return
        print(complete_task(positional[0]))
    elif cmd == "flag":
        if not positional:
            print("Error: Please provide task name")
            return
        print(toggle_flag(positional[0]))
    elif cmd == "delete":
        if not positional:
            print("Error: Please provide task name")
            return
        print(delete_task(positional[0]))

    # Due date operations
    elif cmd == "set-due":
        if len(positional) < 2:
            print("Error: Please provide task name and date")
            return
        print(set_task_due(positional[0], positional[1]))
    elif cmd == "clear-due":
        if not positional:
            print("Error: Please provide task name")
            return
        print(clear_task_due(positional[0]))

    # Defer date operations
    elif cmd == "set-defer":
        if len(positional) < 2:
            print("Error: Please provide task name and date")
            return
        print(set_task_defer(positional[0], positional[1]))
    elif cmd == "clear-defer":
        if not positional:
            print("Error: Please provide task name")
            return
        print(clear_task_defer(positional[0]))

    # Repetition operations
    elif cmd == "set-repeat":
        if len(positional) < 2:
            print("Error: Please provide task name and repetition rule")
            return
        print(set_task_repetition(positional[0], positional[1]))
    elif cmd == "clear-repeat":
        if not positional:
            print("Error: Please provide task name")
            return
        print(clear_task_repetition(positional[0]))

    # Note operations
    elif cmd == "append-note":
        if len(positional) < 2:
            print("Error: Please provide task name and note text")
            return
        print(append_note(positional[0], positional[1]))

    # Project operations
    elif cmd == "show-project":
        if not positional:
            print("Error: Please provide project name")
            return
        print(show_project(positional[0]))
    elif cmd == "create-project":
        if not positional:
            print("Error: Please provide project name")
            return
        folder = positional[1] if len(positional) > 1 else None
        print(create_project(positional[0], folder))

    # Folder operations
    elif cmd == "folders":
        print(list_folders())
    elif cmd == "create-folder":
        if not positional:
            print("Error: Please provide folder name")
            return
        print(create_folder(positional[0]))

    # Perspective operations
    elif cmd == "perspectives":
        print(list_perspectives())
    elif cmd == "activate-perspective":
        if not positional:
            print("Error: Please provide perspective name")
            return
        print(activate_perspective(positional[0]))

    else:
        print(f"Unknown command: {cmd}")
        print_usage()


if __name__ == "__main__":
    main()
