---
name: updating-asc-docs
description: "Use when preparing for App Store submission or the user says 'update ASC docs'. Audits codebase for privacy frameworks, permissions, third-party services, then updates legal and marketing documents."
disable-model-invocation: true
---

## 4 种文档

| 文件 | 内容 | 审计重点 |
|------|------|---------|
| `privacy-policy.md` | 隐私政策 | 数据收集类型、第三方服务、权限使用 |
| `terms-of-use.md` | 用户协议/EULA | 订阅条款、使用限制、免责条款 |
| `support-page.md` | 用户支持页面 | 联系方式、FAQ、功能说明 |
| `market.md` | App Store 描述/营销文案 | 功能列表、卖点、关键词 |

文件位置：`docs/10-app-store-connect/`

## 执行流程

### 1. 代码审计

根据 `$ARGUMENTS` 决定审计范围（无参数则审计全部）。

#### privacy-policy.md 审计

扫描代码库，收集以下信息：

```
[数据收集]
- Grep "import HealthKit|import CoreLocation|import Contacts" → 使用了哪些敏感框架
- Grep "NSCamera|NSMicrophone|NSLocation|NSHealth|NSReminders" → Info.plist 中声明了哪些权限
- Grep "UserDefaults|@AppStorage|SwiftData|CoreData" → 本地存储了什么数据
- Grep "URLSession|URLRequest|API" → 哪些数据发送到服务器

[第三方服务]
- 检查后端服务调用（API 端点、SDK 导入）
- 识别数据处理方（如 AI 大模型服务、语音识别服务）

[用户同意]
- Grep "consent|agree|同意" → 是否有同意流程
```

将审计结果与当前 `privacy-policy.md` 内容对比，列出差异：
- 代码中有但文档中未提及的数据收集
- 文档中提及但代码中已移除的数据收集
- 第三方服务名称是否一致

#### terms-of-use.md 审计

- 检查订阅相关代码（StoreKit、产品 ID、订阅层级）
- 检查 AI 功能是否有免责声明
- 检查用户内容处理（存储、删除、导出）

#### support-page.md 审计

- 检查联系方式是否有效
- 核心功能列表是否与 App 现状一致

#### market.md 审计

- 功能列表是否与 App 现状一致
- 是否提及已移除的功能

### 2. 输出审计报告

```
[审计结果] privacy-policy.md
- ✅ 语音数据描述与代码一致
- ❌ 文档仍提及"健康数据"，但 HealthKit 已移除
- ⚠️ 新增了图片 OCR 功能，文档未提及

建议修改：
1. 删除第 X 行"健康数据"相关段落
2. 在"我们收集的信息"章节新增图片识别说明
```

### 3. 用户确认后更新文档

将审计发现的差异逐项修改到 `.md` 文件中。修改前必须让用户确认修改方案。

### 4. 同步到 Notion

使用 `/notion-page-sync` 的逻辑同步更新后的文件：

1. 读取 `.claude/notion-sync.local.md` 获取 token 和配置
2. 对每个更新的文件，调用：
```bash
NOTION_TOKEN="<token>" python3 ~/.claude/skills/notion/scripts/notion_api.py update-page --file <filepath> <page_id>
```
3. 输出同步结果汇总表

### 5. 输出 App Store Connect 操作清单

列出需要用户在 ASC 后台手动执行的操作：
- Privacy Policy URL 字段是否已填写
- App Description 末尾是否有法律链接
- Privacy Labels 是否需要更新
- EULA 是否需要更新

## 注意事项

- 隐私政策的修改必须与代码实际行为一致，不能凭猜测编写
- 审计结果必须附带代码证据（文件:行号），不能凭记忆列举
- 营销文案可以比代码功能更抽象，但不能承诺不存在的功能
