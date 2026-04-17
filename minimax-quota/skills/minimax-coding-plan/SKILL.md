---
name: minimax-coding-plan
description: "查询 MiniMax coding plan 剩余额度，使用官方 OpenAPI Bearer token (MINIMAX_API_KEY)。Use when the user asks to check MiniMax coding plan quota, remains, usage, or MiniMax API usage. Keywords: MiniMax, minimax, coding plan, remains, quota."
context: fork
model: haiku
allowed-tools: Bash(*skills/minimax-coding-plan/scripts/*)
---

# MiniMax Coding Plan

查询 MiniMax `coding_plan/remains` 接口，使用官方 OpenAPI `MINIMAX_API_KEY` 进行认证。

## 认证

- 需要有效的 `MINIMAX_API_KEY`（MiniMax 开放平台 API 密钥）
- 可选 `MINIMAX_GROUP_ID`（若不提供则使用 API KEY 关联的默认组）

## Path Setup

```bash
BASE="${CLAUDE_PLUGIN_ROOT:-${CODEX_HOME:-$HOME/.codex}}"
SKILLS_ROOT="$BASE/skills"
[ -d "$SKILLS_ROOT/minimax-coding-plan/scripts" ] || SKILLS_ROOT="$BASE/indie-toolkit/minimax-platform/skills"
```

## 工具

```bash
${SKILLS_ROOT}/minimax-coding-plan/scripts/minimax_coding_plan.sh
```

## 常用命令

### 查看额度摘要

```bash
MINIMAX_API_KEY='your-api-key' \
${SKILLS_ROOT}/minimax-coding-plan/scripts/minimax_coding_plan.sh
```

### 指定 GroupId

```bash
MINIMAX_API_KEY='your-api-key' \
MINIMAX_GROUP_ID='2036327615073096267' \
${SKILLS_ROOT}/minimax-coding-plan/scripts/minimax_coding_plan.sh
```

### 输出原始 JSON

```bash
MINIMAX_API_KEY='your-api-key' \
MINIMAX_OUTPUT=json \
${SKILLS_ROOT}/minimax-coding-plan/scripts/minimax_coding_plan.sh
```

## 错误处理

- `MINIMAX_API_KEY` 缺失时退出并提示
- API 返回错误时输出原始响应内容
- 网络问题导致请求失败时提示检查网络/代理/DNS
