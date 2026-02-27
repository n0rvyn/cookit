---
name: notes
description: 读取、搜索、创建、编辑 Apple Notes 备忘录。当用户需要查看备忘录内容、搜索笔记、创建新备忘录、或向已有备忘录追加内容时使用。关键词：备忘录、Notes、笔记、记录、Apple Notes。
compatibility: Requires macOS
allowed-tools: Bash(*skills/notes/scripts/*)
---

# Apple Notes 备忘录操作

通过 AppleScript 连接 macOS Notes.app，执行备忘录的查看、搜索、创建、编辑、删除操作。

## Path Setup

```bash
BASE="${CLAUDE_PLUGIN_ROOT:-${CODEX_HOME:-$HOME/.codex}}"
SKILLS_ROOT="$BASE/skills"
[ -d "$SKILLS_ROOT/notes/scripts" ] || SKILLS_ROOT="$BASE/cookit/mactools/skills"
```

## 工具

```
${SKILLS_ROOT}/notes/scripts/notes.sh
```

## 命令

### 列出所有文件夹

```bash
${SKILLS_ROOT}/notes/scripts/notes.sh folders
```

### 列出备忘录

```bash
# 列出所有备忘录（默认最多 20 条）
${SKILLS_ROOT}/notes/scripts/notes.sh list

# 列出指定文件夹中的备忘录
${SKILLS_ROOT}/notes/scripts/notes.sh list "工作"

# 限制结果数量
${SKILLS_ROOT}/notes/scripts/notes.sh list -n 10

# 限制结果数量 + 指定文件夹
${SKILLS_ROOT}/notes/scripts/notes.sh list -n 5 "工作"
```

输出格式：序号、备忘录名称、所属文件夹、修改日期、正文前 100 字预览。

### 读取备忘录内容

```bash
${SKILLS_ROOT}/notes/scripts/notes.sh read "备忘录标题"
```

返回纯文本内容（HTML 标签已剥离）。输出包含标题、文件夹、修改日期和正文。

### 搜索备忘录

```bash
# 按关键词搜索（匹配标题和正文，不区分大小写）
${SKILLS_ROOT}/notes/scripts/notes.sh search "关键词"

# 限制搜索结果数量
${SKILLS_ROOT}/notes/scripts/notes.sh search -n 10 "关键词"
```

### 创建备忘录

```bash
# 在默认文件夹创建
${SKILLS_ROOT}/notes/scripts/notes.sh create "标题" "正文内容"

# 在指定文件夹创建
${SKILLS_ROOT}/notes/scripts/notes.sh create "标题" "正文内容" "工作"

# 多行正文（使用 $'...' 语法传入换行符）
${SKILLS_ROOT}/notes/scripts/notes.sh create "会议记录" $'第一行\n第二行\n第三行'
```

### 追加内容到备忘录

```bash
${SKILLS_ROOT}/notes/scripts/notes.sh append "备忘录标题" "要追加的文本"

# 追加多行
${SKILLS_ROOT}/notes/scripts/notes.sh append "备忘录标题" $'第一行\n第二行'
```

### 删除备忘录

```bash
${SKILLS_ROOT}/notes/scripts/notes.sh delete "备忘录标题"
```

移至"最近删除"，非永久删除。用户可在 Notes.app 中恢复。

## 参数

| 参数 | 说明 | 适用命令 | 默认值 |
|------|------|---------|--------|
| `-n <count>` | 最大结果数 | list, search | 20 |

## 工作流程

### 查看备忘录

1. 先用 `folders` 查看文件夹结构
2. 用 `list` 或 `list "文件夹名"` 浏览备忘录列表
3. 用 `read "标题"` 读取具体内容

### 搜索备忘录

1. 用 `search "关键词"` 按关键词搜索
2. 从结果中选择目标备忘录
3. 用 `read "标题"` 读取完整内容

### 创建和编辑

1. 用 `create` 创建新备忘录
2. 用 `append` 向已有备忘录追加内容
3. 用 `read` 确认内容已写入

## 集成说明

- 其他 skill（如 mail）可通过 `create` 命令将处理结果保存为备忘录
- 搜索结果可与 Spotlight skill 互补：Spotlight 搜索文件系统，notes skill 搜索 Notes.app 内容

## 错误处理

| 错误信息 | 原因 | 处理方式 |
|---------|------|---------|
| `Error: Note "X" not found.` | 备忘录名称不匹配 | 用 `list` 或 `search` 确认准确名称 |
| `Error: Folder "X" not found.` | 文件夹名称不匹配 | 用 `folders` 确认文件夹名称 |
| `No notes found.` | 无备忘录或文件夹为空 | 确认 Notes.app 中有备忘录 |

## 注意事项

- Notes.app 需要在系统中可用（macOS 内置，无需额外安装）
- 备忘录名称匹配为精确匹配（`read`、`append`、`delete`），搜索为模糊匹配（`search`）
- `read` 返回纯文本，Notes.app 中的富文本格式（粗体、列表等）会被简化
- `create` 的正文支持多行，通过 shell 的 `$'...\n...'` 语法传入
- `delete` 将备忘录移至"最近删除"，30 天后自动永久删除
