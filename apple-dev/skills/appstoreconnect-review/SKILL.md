---
name: appstoreconnect-review
description: "Use when preparing for App Store submission, or the user says 'ASC review', 'prepare submission'. Performs item-by-item App Store Connect submission material check and guidance. Keywords: ASC, App Store Connect, submission, privacy labels, screenshots, review."
---

# App Store Connect 上架审查

逐项指导 App Store Connect 中 iOS/macOS App 上架需要填写的内容，或执行提交前审计。

参考资料在 `appstoreconnect-review/references/` 目录中（相对于 skills 目录），按需加载。

## Process

### Step 1: 确定审查模式

从用户消息判断：

**模式 A — 全量填写指导**：用户首次上架或说"帮我填 ASC"。按顺序引导所有字段。

**模式 B — 隐私标签**：用户专门问隐私标签。聚焦 App Privacy 部分。

**模式 C — 提交前审计**：用户说"提交前检查"或"pre-submit audit"。执行代码 + 文档合规检查。

**模式 D — 特定部分**：用户问某个具体字段或部分。加载对应 reference 段落回答。

### Step 2: 加载参考资料

根据模式加载对应 reference：

| 模式 | 加载文件 |
|------|---------|
| A | `references/asc-fields-guide.md` → `references/asc-version-and-review.md` → `references/asc-audit-checklist.md`（准备清单部分） |
| B | `references/asc-fields-guide.md`（第二部分：App Privacy） |
| C | `references/asc-audit-checklist.md` |
| D | 根据用户问题定位对应 reference 的具体段落 |

### Step 3: 执行审查

**模式 A**：按 reference 中的字段顺序，逐项向用户解释并确认填写内容。每完成一个大部分（App Information / Privacy / Version），确认再进入下一部分。

**模式 B**：读取项目代码（import 语句、网络请求、数据存储），帮用户判断每个数据类型是否需要声明。输出格式：

```
[隐私标签审查]
| 数据类型 | 是否收集 | 证据 | 建议 |
|---------|---------|------|------|
| Health | ✅ | import HealthKit in ... | 声明，关联用户，App Functionality |
| Location | ❌ | 无相关 import/API | 不声明 |
```

**模式 C**：按 `references/asc-audit-checklist.md` 执行：
1. 素材准备清单 → 逐项检查
2. 代码审计命令 → 逐个运行 Grep 检查
3. ASC 文档一致性 → 对比隐私政策与代码
4. 输出审计报告

**模式 D**：直接回答用户问题，引用 reference 中的具体指引。

### Step 4: 输出报告

**模式 A/B**：输出已确认的字段值汇总，标注待用户补充的项。

**模式 C**：输出审计报告：

```
## ASC 提交前审计报告

### 素材检查
- [ ] / [x] 逐项结果

### 代码合规
| 检查项 | 状态 | 说明 |
|--------|------|------|
| 框架残留 | ✅/❌ | 详情 |
| Consent Flow | ✅/❌ | 详情 |
| 法律链接 | ✅/❌ | 详情 |

### 文档一致性
| 项目 | 状态 | 说明 |
|------|------|------|

### 需要修复
1. {issue + fix}
```

## Completion Criteria

- 用户确认的模式已完成
- 所有检查项有明确结果（通过/不通过/待确认）
- 不通过的项有具体修复建议
