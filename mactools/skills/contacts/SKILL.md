---
name: contacts
description: 搜索和查看 macOS 通讯录中的联系人信息。当用户需要查找联系人电话、邮箱、地址等信息时使用。关键词：通讯录、Contacts、联系人、电话、邮箱。
context: fork
model: haiku
compatibility: Requires macOS
allowed-tools: Bash(*skills/contacts/scripts/*)
---

# Contacts 通讯录查询

通过 macOS Contacts.app 搜索和查看联系人信息。

## Path Setup

```bash
BASE="${CLAUDE_PLUGIN_ROOT:-${CODEX_HOME:-$HOME/.codex}}"
SKILLS_ROOT="$BASE/skills"
[ -d "$SKILLS_ROOT/contacts/scripts" ] || SKILLS_ROOT="$BASE/cookit/mactools/skills"
```

## 工具

```
${SKILLS_ROOT}/contacts/scripts/contacts.sh
```

## 命令

### 搜索联系人

按名称模糊搜索，返回匹配的联系人及其电话、邮箱摘要。

```bash
${SKILLS_ROOT}/contacts/scripts/contacts.sh search "张三"
${SKILLS_ROOT}/contacts/scripts/contacts.sh search -n 10 "Zhang"
```

### 查看联系人详情

显示完整联系人信息：电话、邮箱、地址、公司、职位、生日、备注。

```bash
${SKILLS_ROOT}/contacts/scripts/contacts.sh show "张三"
```

### 列出所有联系人

仅显示姓名列表。

```bash
${SKILLS_ROOT}/contacts/scripts/contacts.sh list
${SKILLS_ROOT}/contacts/scripts/contacts.sh list -n 50
```

### 列出所有群组

```bash
${SKILLS_ROOT}/contacts/scripts/contacts.sh groups
```

### 查看群组成员

```bash
${SKILLS_ROOT}/contacts/scripts/contacts.sh group "同事"
${SKILLS_ROOT}/contacts/scripts/contacts.sh group -n 50 "家人"
```

## 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-n <count>` | 最大结果数 | 20 |

## 工作流程

### Step 1: 分析意图

从用户问题中判断：
- 是搜索联系人（模糊）还是查看特定联系人详情（精确）
- 是否按群组查找
- 需要什么信息（电话、邮箱、地址等）

### Step 2: 执行查询

- 不确定全名时，先用 `search` 模糊搜索
- 确定全名后，用 `show` 获取完整信息
- 按群组查找时，先用 `groups` 列出群组，再用 `group` 查看成员

### Step 3: 返回结果

从返回的联系人信息中提取用户需要的部分。如果用户只问电话号码，只返回电话相关信息即可。

## 注意事项

- 首次使用时 macOS 会弹出权限请求对话框，需用户授权访问通讯录
- 搜索为名称模糊匹配（contains），不区分姓/名
- `show` 命令优先精确匹配全名，无结果时回退到模糊匹配
- 联系人数据来自本地 Contacts.app，包含 iCloud 同步的联系人
