---
name: mail
description: 读取、搜索、整理 macOS 邮件。支持查看收件箱、读取邮件内容、标记、移动、删除（移废纸篓）。当用户需要整理邮件、查找邮件、清理收件箱时使用。关键词：邮件、Mail、收件箱、整理邮件、清理邮件。
context: fork
model: haiku
compatibility: Requires macOS
allowed-tools: Bash(*skills/mail/scripts/*)
---

# Mail.app 邮件操作

通过 AppleScript 操作 macOS Mail.app，支持查看、搜索、标记、移动、清理邮件。

## 前提条件

- Mail.app 必须已打开并运行
- 需要 macOS 辅助功能/自动化权限

## Path Setup

```bash
BASE="${CLAUDE_PLUGIN_ROOT:-${CODEX_HOME:-$HOME/.codex}}"
SKILLS_ROOT="$BASE/skills"
[ -d "$SKILLS_ROOT/mail/scripts" ] || SKILLS_ROOT="$BASE/indie-toolkit/mactools/skills"
```

## 工具

```
${SKILLS_ROOT}/mail/scripts/mail.sh
```

## 命令

### 列出邮件账户

```bash
${SKILLS_ROOT}/mail/scripts/mail.sh accounts
```

### 列出邮箱

```bash
# 列出所有账户的邮箱
${SKILLS_ROOT}/mail/scripts/mail.sh mailboxes

# 列出指定账户的邮箱
${SKILLS_ROOT}/mail/scripts/mail.sh mailboxes "iCloud"
```

### 查看收件箱

```bash
# 查看所有账户的收件箱（默认 20 条）
${SKILLS_ROOT}/mail/scripts/mail.sh inbox

# 查看指定账户的收件箱
${SKILLS_ROOT}/mail/scripts/mail.sh inbox "iCloud"

# 指定数量
${SKILLS_ROOT}/mail/scripts/mail.sh inbox "iCloud" -n 50
${SKILLS_ROOT}/mail/scripts/mail.sh inbox -n 10
```

输出格式：
```
1. [unread] 服务器巡检报告 - 2026年1月
   From: zhang@example.com | Date: 2026-01-15 09:30
2. [read] Re: 项目周报
   From: li@example.com | Date: 2026-01-14 16:20
```

### 读取邮件全文

```bash
${SKILLS_ROOT}/mail/scripts/mail.sh read "iCloud" "INBOX" 1
```

输出包含：Subject、From、To、CC、Date、Status（read/unread, flagged）、正文。

### 查看未读邮件

```bash
# 所有账户的未读邮件
${SKILLS_ROOT}/mail/scripts/mail.sh unread

# 指定账户
${SKILLS_ROOT}/mail/scripts/mail.sh unread "iCloud"

# 指定数量
${SKILLS_ROOT}/mail/scripts/mail.sh unread "iCloud" -n 50
```

输出中包含 `(index N)` 标注该邮件在邮箱中的实际索引，用于后续 read/flag/trash 等操作。

### 搜索邮件

```bash
# 在所有账户中搜索
${SKILLS_ROOT}/mail/scripts/mail.sh search "发票"

# 在指定账户中搜索
${SKILLS_ROOT}/mail/scripts/mail.sh search "发票" "iCloud"

# 限制结果数
${SKILLS_ROOT}/mail/scripts/mail.sh search "发票" -n 10
```

搜索范围：主题、发件人、正文内容。输出中包含 `(index N)` 用于后续操作。

### 标记/取消标记邮件

```bash
${SKILLS_ROOT}/mail/scripts/mail.sh flag "iCloud" "INBOX" 3
```

切换邮件的旗标状态（已标记 -> 取消标记，未标记 -> 标记）。

### 标记为已读

```bash
${SKILLS_ROOT}/mail/scripts/mail.sh mark-read "iCloud" "INBOX" 3
```

### 移动邮件

```bash
${SKILLS_ROOT}/mail/scripts/mail.sh move "iCloud" "INBOX" 3 "Archive"
```

将邮件从一个邮箱移到同账户的另一个邮箱。目标邮箱名称需与 `mailboxes` 命令输出中的名称一致。

### 移到废纸篓（单条）

```bash
${SKILLS_ROOT}/mail/scripts/mail.sh trash "iCloud" "INBOX" 5
```

**trash = 移到废纸篓，可恢复。不会永久删除。**

### 批量移到废纸篓

```bash
${SKILLS_ROOT}/mail/scripts/mail.sh batch-trash "iCloud" "INBOX" 10 20
```

将索引 10 到 20 的邮件全部移到废纸篓。内部从高索引向低索引处理，避免索引偏移。

**batch-trash = 批量移到废纸篓，可恢复。不会永久删除。**

## 安全说明

- `trash` 和 `batch-trash` 调用 Mail.app 的 `delete` 命令，该命令将邮件移到废纸篓
- 废纸篓中的邮件可手动恢复
- 本工具不提供永久删除功能
- 批量操作前建议先用 `inbox` 或 `search` 确认目标邮件

## 邮件整理工作流

整理邮件的推荐流程：

### Step 1: 查看收件箱

```bash
# 先看有多少未读
${SKILLS_ROOT}/mail/scripts/mail.sh unread "账户名"

# 或查看全部收件箱
${SKILLS_ROOT}/mail/scripts/mail.sh inbox "账户名" -n 50
```

### Step 2: 逐条阅读和分类

对每封邮件用 `read` 查看内容，然后分类：

| 分类 | 处理方式 |
|------|---------|
| 有用（含待办事项） | 提取 TODO，通过 mactools:omnifocus 创建任务 |
| 参考资料（需留存） | 总结要点，通过 mactools:notes 创建笔记 |
| 垃圾/过期/无用 | 移到废纸篓 |

### Step 3: 创建整理摘要

通过 mactools:notes 创建一条笔记，记录本次整理结果：
- 处理了多少封邮件
- 提取了哪些待办事项
- 保存了哪些参考资料
- 清理了多少封垃圾邮件

### Step 4: 清理

将已处理的无用邮件批量移到废纸篓：

```bash
${SKILLS_ROOT}/mail/scripts/mail.sh trash "账户名" "INBOX" <index>
# 或批量
${SKILLS_ROOT}/mail/scripts/mail.sh batch-trash "账户名" "INBOX" <start> <end>
```

## 注意事项

- Mail.app 必须处于运行状态，否则脚本会报错提示
- 邮件索引从 1 开始，按 Mail.app 的默认排序（通常是最新在前）
- 搜索和未读列表输出中的 `(index N)` 是该邮件在邮箱中的实际索引，操作时使用该索引
- 移动/删除邮件后，同邮箱中后续邮件的索引会发生变化；批量操作时注意
- `batch-trash` 已内置从高到低索引的处理顺序，避免索引偏移问题
- 账户名和邮箱名需与 Mail.app 中显示的名称完全一致

## 故障排查

| 问题 | 解决方法 |
|------|---------|
| "Mail.app is not running" | 先启动 Mail.app |
| "account not found" | 用 `accounts` 命令确认账户名称 |
| "mailbox not found" | 用 `mailboxes "账户名"` 确认邮箱名称 |
| "index out of range" | 用 `inbox` 确认邮件总数和索引范围 |
| 权限弹窗 | macOS 首次运行需授权终端访问 Mail.app |
