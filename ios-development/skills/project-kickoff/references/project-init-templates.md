# 项目初始化模板

## docs 目录结构

```bash
mkdir -p docs/{01-discovery,02-architecture,03-decisions,04-implementation,05-features,06-plans,07-changelog,08-product-evaluation,09-lessons-learned,10-app-store-connect,11-crystals,_discussions}
```

目录说明：
| 目录 | 用途 |
|------|------|
| 00-AI-CONTEXT.md | AI 助手入口文档（文件，非目录） |
| 01-discovery/ | 项目调研、project-brief |
| 02-architecture/ | 架构设计、数据模型 |
| 03-decisions/ | 架构决策记录 (ADR) |
| 04-implementation/ | 实现细节、文件结构 |
| 05-features/ | 功能预期行为、关键代码位置 |
| 06-plans/ | 开发指南、设计文档、实施计划 |
| 07-changelog/ | 变更历史 |
| 08-product-evaluation/ | product-lens 评估报告 |
| 09-lessons-learned/ | 踩坑记录 |
| 10-app-store-connect/ | ASC 提交文档（隐私政策、用户协议、支持页、营销文案） |
| 11-crystals/ | 决策结晶（crystallize / distill-discussion 输出） |
| _discussions/ | 原始讨论存档（AI 对话导出、探索性笔记，非检索目标） |

## CLAUDE.md 追加模板

在 /init 生成的 CLAUDE.md 末尾追加以下内容（不替换 /init 生成的部分）：

```markdown
## 文档真相源

所有项目文档以 `docs/00-AI-CONTEXT.md` 为唯一真源。本文件只负责引导。

### 快速定位

| 需要... | 查看 |
|--------|------|
| 项目概览 | `docs/00-AI-CONTEXT.md` |
| 项目调研 | `docs/01-discovery/` |
| 架构设计 | `docs/02-architecture/` |
| 决策原因 | `docs/03-decisions/` |
| 实现细节 | `docs/04-implementation/` |
| 功能行为 | `docs/05-features/` |
| 开发指南/计划 | `docs/06-plans/` |
| 变更历史 | `docs/07-changelog/` |
| 产品评估 | `docs/08-product-evaluation/` |
| 踩坑记录 | `docs/09-lessons-learned/` |
| 决策结晶 | `docs/11-crystals/` |

## 文档搜索约定

搜索 `docs/` 下的结构化文档时，使用 glob pattern `[0-9]*/**/*.md`。此 pattern 匹配所有编号目录（01-discovery 到 11-crystals），自动排除 `_discussions/`（原始讨论存档，不宜直接检索——中间决策过程断章取义会产生误导）。

需要提炼讨论文档时，使用 `/distill-discussion`。

## 计划执行规则

当执行的计划 task 包含以下字段时：

| 字段 | 动作 |
|------|------|
| `Design ref:` | 实现前读取引用的设计文档段落 |
| `Expected values:` | 实现后逐个验证值是否匹配 |
| `Replaces:` | 实现后 Grep 旧代码引用，确认已处理 |
| `Data flow:` | 实现后端到端追踪路径，确认连通 |
| `Quality markers:` | 实现时使用指定的算法/数据结构，不简化 |
| `Verify after:` | 实现后逐项执行检查 |

遇到计划未覆盖的灰色地带：**问用户，不自行发挥**。

### 完成功能后留档

**触发条件**：
- 完成涉及多文件的功能实现
- 修复需要理解上下文的 bug
- 做了有 trade-off 的设计决策

**留档位置**：`docs/05-features/功能名.md`

**留档内容**：
- 功能预期行为（用户视角）
- 关键文件位置
- 边界条件/限制
- 相关决策（可链接到 03-decisions/）

**触发方式**：完成后用 `/handoff` 或主动询问用户

## 项目特定约束

\```
禁止：[项目特定禁止项]

必须：[项目特定必须项]
必须：[由步骤 9.2.1 生成的平台 API 规则]
\```

## Swift 6 并发（本项目）

**本项目 @Model 类型**：
- `ModelA`, `ModelB`, ...

**本项目 Service 单例**（均为 `@MainActor final class`）：
- `ServiceA.shared`, `ServiceB.shared`, ...

## 编码规范

通用规范见 `~/.claude/CLAUDE.md`

**项目 Design System**：
| 类型 | Token | 示例 |
|------|-------|------|
| 间距 | `AppSpacing.xs/sm/md/lg/xl` | 4/8/16/24/32 |
| 圆角 | `AppCornerRadius.small/medium/large` | 8/12/16 |
| 颜色 | `Color.appPrimary/appSecondary/...` | 见 DesignSystem.swift |

## 遇到困惑时

1. 查 `docs/00-AI-CONTEXT.md` - 项目概览包含完整技术方案
2. 查 `docs/03-decisions/` - 可能已有决策
3. 查 `docs/05-features/` - 功能的预期行为和关键代码位置
4. 查 `docs/09-lessons-learned/` - 可能是已知坑
```

## 平台 API 规则表

根据步骤 6 识别的功能列表，查下表生成项目级平台 API 约束，写入 CLAUDE.md 的「项目特定约束」`必须：` 部分。

| 功能类型 | 推荐平台 API | 项目规则 |
|---------|-------------|---------|
| 订阅/IAP | `SubscriptionStoreView`, StoreKit 2 | 订阅购买 UI 使用 `SubscriptionStoreView`，不手写付费墙 |
| 登录 | `SignInWithAppleButton`, `ASWebAuthenticationSession` | 登录使用 AuthenticationServices 声明式 API |
| 分享 | `ShareLink` | 分享使用 `ShareLink`，不桥接 UIActivityViewController |
| 照片选择 | `PhotosPicker` | 照片选择使用 `PhotosPicker`，不桥接 UIImagePickerController |
| 文件选择 | `.fileImporter()` / `.fileExporter()` | 文件操作使用 SwiftUI modifier，不桥接 UIDocumentPickerViewController |
| 设置/偏好 | `@AppStorage`, `AppIntents` | 用户设置使用 AppStorage；系统设置集成使用 AppIntents |
| 地图 | `Map` (MapKit for SwiftUI) | 地图使用 SwiftUI `Map` 视图 |
| 搜索 | `.searchable()`, `CoreSpotlight` | 应用内搜索使用 `.searchable()` modifier；系统搜索使用 CoreSpotlight 索引 |
| Widgets | `WidgetKit`, `AppIntents` | Widget 使用 WidgetKit + AppIntents |
| 快捷指令 | `AppIntents` | 快捷指令使用 AppIntents 框架 |
| 生物识别 | `LAContext` | 生物识别使用 LocalAuthentication |
| 后台任务 | `BGTaskScheduler` | 后台任务使用 BGTaskScheduler |
| 剪贴板 | `PasteButton` | 粘贴操作使用 `PasteButton`，不直接读 UIPasteboard |

**使用方式**：
- 步骤 6 中识别的每项功能，查表匹配
- 匹配到的行 → 将「项目规则」写入 CLAUDE.md「项目特定约束」
- 未匹配的功能 → 搜索 Apple Developer Documentation 确认是否有声明式 API，有则补充
- 此表随项目经验持续扩充

## GitHub Issue Templates

项目初始化时在 `.github/ISSUE_TEMPLATE/` 下创建 issue 模板，规范 issue 格式。

### .github/ISSUE_TEMPLATE/bug.md

```markdown
---
name: Bug
about: 已定位的 bug 报告
labels: ["bug"]
---

### 现象

<!-- 用户可见的异常行为 -->

### 根因

<!-- 代码层面的原因，附文件:行号 -->

### 相关文件

<!-- 涉及的文件列表 -->

### 修复策略

<!-- 推荐的修复方式，或"Phase N 迁移后自然消失" -->

### 备注

<!-- 其他上下文，如截图、日志 -->
```

### .github/ISSUE_TEMPLATE/feature.md

```markdown
---
name: Feature
about: 功能需求或改进
labels: ["enhancement"]
---

### 需求描述

<!-- 要解决什么问题 -->

### 预期行为

<!-- 完成后用户看到什么 -->

### 相关文件

<!-- 可能涉及的文件，如果已知 -->

### 备注

```

### 自定义 Labels

除 GitHub 默认 labels 外，创建以下 labels：

```bash
gh label create "deferred" --color "FBCA04" --description "已定位，推迟处理"
gh label create "blocked"  --color "D93F0B" --description "被其他事项阻塞"
# phase labels 根据 dev-guide phase 数量动态生成：
# gh label create "phase-1" --color "0E8A16" --description "Phase 1"
# gh label create "phase-2" --color "1D76DB" --description "Phase 2"
# ...
```

### Milestones

如果 dev-guide 已存在，为每个 phase 创建 milestone：

```bash
# 从 dev-guide 提取 phase 名称，逐个创建：
# gh api repos/{owner}/{repo}/milestones -f title="Phase 1: {name}" -f description="{scope}"
```
