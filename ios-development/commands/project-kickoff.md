---
name: project-kickoff
description: 新项目启动开题流程，完成需求澄清、范围收敛和执行建议。
---

# Project Kickoff - 项目开题

新项目启动前的可行性分析和定位。

## 输入

用户描述项目想法。可以是模糊概念，如"做一个记账 App"。

## 流程

### 1. 需求澄清

如果输入不够明确，追问：
- 解决什么问题？
- 目标用户是谁？
- 有什么独特切入点？

直到形成清晰的项目概念。不清晰就不进入下一步。

### 2. AI 时代前置检验

在搜索竞品之前，先回答：

**是否需要开发？**
- 这个需求能否用现有 AI 工具直接解决？（ChatGPT、Claude、专用 AI 工具）
- 是否用 No-Code 工具组合就够了？（Notion、Airtable、Zapier）
- "做成 App"比"用现有工具"好在哪里？

**AI 替代风险**
- 如果 AI 能力继续提升，这个产品还有价值吗？
- 什么是 AI 难以替代的部分？

如果结论是"不需要开发"或"很快会被 AI 替代"，直接告诉用户，不继续往下走。

### 3. 市场调研

使用 WebSearch 搜索相关产品：

**搜索来源**：
- GitHub：开源实现、技术方案
- Product Hunt：已发布产品、用户反馈
- App Store / Google Play：移动应用评分评论
- IndieHackers / HackerNews：独立开发者经验
- 通用搜索：测评文章、对比分析

**搜索策略**：
- `[产品类型]` 直接搜索
- `[产品类型] alternatives` 竞品列表
- `[产品类型] open source` 开源方案
- `[用户痛点]` 从问题角度搜索

每个来源至少搜索一次，汇总 5-10 个主要竞品。

### 4. 竞品分析

对每个竞品整理：

| 维度 | 内容 |
|------|------|
| 产品名称 | 名称 + 链接 |
| 核心功能 | 主要卖点 |
| 目标用户 | 面向谁 |
| 商业模式 | 免费/付费/订阅 |
| 优点 | 做得好的地方 |
| 缺点 | 用户抱怨的点 |
| 技术栈 | 如果是开源项目 |

### 5. 定位分析

基于调研结果，分析：

- **差异点**：与竞品的核心区别
- **护城河**：难以被复制的优势（特别关注数据护城河）
- **风险点**：潜在挑战和应对思路
- **市场机会**：为什么现在做这个

如果调研后发现"这个方向已经很卷，没有明显差异化空间"，直接告诉用户，不要硬凑。

### 6. 功能规划

- **完整功能列表**：要做的所有功能（不是 MVP，是完整版）
- **明确不做**：边界在哪里
- **技术选型**：推荐技术栈和理由
- **数据策略**：产品如何积累独特数据

### 6.5 AI Native 架构评估

如果项目涉及 AI 能力，评估 AI Native 架构需求：

#### 6.5.1 AI 集成深度

| 级别 | 描述 | 架构需求 |
|------|------|---------|
| **Level 0** | 无 AI | 跳过本章节 |
| **Level 1** | AI 辅助 | 单向 API 调用，无需 Agent |
| **Level 2** | AI 增强 | 需要 Tool Calling + 简单 Agent |
| **Level 3** | AI 原生 | 完整 Agent 框架 + 多 Tool + 上下文管理 |

#### 6.5.2 Tool-First 设计检查

如果 Level >= 2，评估：

- [ ] **Service 可 Tool 化**：现有 Service 能否暴露为 AI Tool？
- [ ] **Tool Schema 设计**：Tool 输入输出是否清晰、可验证？
- [ ] **幂等性**：Tool 是否幂等（可安全重试）？
- [ ] **权限控制**：敏感 Tool 是否需要用户确认？

#### 6.5.3 Agent 策略选择

| 策略 | 适用场景 | 复杂度 |
|------|---------|-------|
| **Simple** | 单次 Tool 调用 | 低 |
| **ReAct** | 多步推理、需要观察 Tool 结果 | 中 |
| **CoT** | 需要展示推理过程 | 中 |
| **Multi-Agent** | 复杂任务分解、专家协作 | 高 |

#### 6.5.4 上下文管理需求

- [ ] **对话历史**：是否需要跨消息上下文？
- [ ] **用户偏好学习**：是否需要长期记忆？
- [ ] **Token 预算**：如何处理超长对话？

#### 6.5.5 可观测性规划

- [ ] **Tracing**：是否需要完整调用链追踪？
- [ ] **Metrics**：需要监控哪些指标（Token、延迟、成本）？
- [ ] **Audit**：是否有合规审计需求？

#### 6.5.6 错误恢复策略

- Tool 执行失败如何处理？
- LLM 调用超时如何处理？
- 如何避免无限循环？

### 7. 输出文档

将分析结果写入项目文档：

**文件路径**：`docs/01-discovery/project-brief.md`

**文档结构**：

```markdown
# [项目名称]

> 一句话描述

## 背景

### 解决什么问题
### 目标用户
### 核心价值

## 可行性检验

### 为什么要开发（而非用现有工具）
### AI 替代风险评估

## 市场调研

### 竞品概览

| 产品 | 定位 | 优点 | 缺点 |
|------|------|------|------|
| ... | ... | ... | ... |

### 竞品详情

#### [竞品 1]
...

## 产品定位

### 差异化
### 护城河
### 风险与机会

## 功能规划

### 完整功能
1. ...
2. ...

### 明确不做
- ...

### 技术选型
...

### 数据策略
...

## 参考链接

- [产品名](URL) - 简述
```

### 8. 初始化项目结构（iOS/Swift 项目）

**仅适用于 iOS/Swift 项目**。其他类型项目跳过此步。

#### 8.1 创建 docs 目录结构

```bash
mkdir -p docs/{01-discovery,02-architecture,03-decisions,04-implementation,05-features,07-changelog,09-lessons-learned,10-app-store-connect}
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
| 07-changelog/ | 变更历史 |
| 09-lessons-learned/ | 踩坑记录 |
| 10-app-store-connect/ | ASC 提交文档（隐私政策、用户协议、支持页、营销文案） |

#### 8.2 创建 CLAUDE.md（项目根目录）

```markdown
# [项目名] - Claude Code 项目指令

> 通用规则见 ~/.claude/CLAUDE.md

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
| 变更历史 | `docs/07-changelog/` |
| 踩坑记录 | `docs/09-lessons-learned/` |

## 开发工作流

**Build 命令**：
\`\`\`bash
xcodebuild build -scheme [项目名] -destination 'platform=iOS Simulator,name=iPhone 17 Pro' -quiet 2>&1 | grep -E "error:|warning:|BUILD"
\`\`\`

### 修改代码后必须

1. 更新 `docs/04-implementation/file-structure.md`
2. 记录到 `docs/07-changelog/YYYY-MM-DD.md`
3. 架构级变更 -> 创建 ADR 到 `docs/03-decisions/`
4. 同样的坑可能再踩 -> 写入 `docs/09-lessons-learned/`

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

\`\`\`
禁止：[项目特定禁止项]

必须：[项目特定必须项]
必须：[由步骤 8.2.1 生成的平台 API 规则]
\`\`\`

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

## Plan Execution with Design References

When executing a plan task that contains design anchor fields:

| Field | Action |
|-------|--------|
| `Design ref:` | Read the referenced design doc sections before implementing |
| `Expected values:` | After implementing, verify each value matches |
| `Replaces:` | After implementing, Grep for old code references, confirm handled |
| `Data flow:` | After implementing, trace path end-to-end, confirm connectivity |
| `Quality markers:` | During implementation, use specified approach, do not simplify |
| `Verify after:` | After implementing, execute each checklist item |

Gray areas not covered by the plan: ask the user, do not improvise.
```

#### 8.2.1 平台 API 规则生成

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

#### 8.3 创建 docs/00-AI-CONTEXT.md

```markdown
# [项目名] - AI 上下文

> AI 助手必读的项目入口文档

## 一句话描述

[项目做什么，给谁用]

## 核心功能

### 功能 A

简述功能做什么。

**关键文件**：
- `路径/文件A.swift` - 职责
- `路径/文件B.swift` - 职责

### 功能 B

简述功能做什么。

**关键文件**：
- `路径/文件C.swift` - 职责

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| iOS | 18+ | 最低支持 |
| Swift | 6.2 | 主语言 |
| SwiftUI | - | UI 框架 |
| SwiftData | - | 本地存储 |

## 本地化

- 所有 UI 文本使用 `String(localized: "中文", table: "模块名")`
- table 按功能模块命名
- 翻译文件：`[项目名]/*.xcstrings`

## 关键路径

| 功能 | 入口文件 |
|------|---------|
| 主界面 | `ContentView.swift` |
| 数据模型 | `Models/` |
| 服务层 | `Services/` |
| 视图层 | `Views/` |

## 详细文档索引

- 项目调研：`docs/01-discovery/project-brief.md`
- 架构设计：`docs/02-architecture/`
- 功能行为：`docs/05-features/`
```

#### 8.4 创建 docs/02-architecture/README.md

简要描述：分层、数据流、模块依赖。后续可拆分为多个文件。

#### 8.5 创建 docs/05-features/README.md

参考模板：

```markdown
# 功能文档

记录功能的预期行为、关键代码位置、边界条件。

## 文件模板

每个功能一个文件，命名格式：`功能名.md`

\`\`\`markdown
# 功能名称

## 预期行为
用户视角描述功能做什么。

## 关键文件
| 文件 | 职责 |
|------|------|
| `路径/文件.swift` | 说明 |

## 边界条件/限制
- 条件 1

## 变更历史
| 日期 | 变更 |
|------|------|
| YYYY-MM-DD | 初始实现 |
\`\`\`
```

#### 8.6 Design System 初始化

> 完整设计原则参考 `~/.claude/docs/ui-design-principles.md`

新项目应在早期建立 Design System：

| 维度 | 建议 | 原则来源 |
|------|------|---------|
| 颜色 | 主色/辅色/强调色 | 色彩比例法则（原则 §3.1，按 App 类型选比例） |
| 间距 | 4xs~2xl（2pt~64pt） | 8pt 网格（原则 §2.1） |
| 字体 | headline/body/caption | Minor Third 阶梯（原则 §1.1） |
| 圆角 | small/medium/large | 嵌套递减（原则 §2.3） |
| 阴影 | subtle/medium | opacity ≤ 0.08（原则 §10.2） |
| 动效 | 200-500ms, spring | 原则 §9 |

初始化时读取 `~/.claude/docs/ui-design-principles.md` §2 间距系统和 §3 颜色系统确定具体值。

创建 `[项目名]/DesignSystem/DesignSystem.swift`，最小骨架：

```swift
import SwiftUI

// MARK: - Spacing

enum AppSpacing {
    /// 2pt - 极细微调整
    static let _4xs: CGFloat = 2
    /// 4pt - 图标与标签间距
    static let _3xs: CGFloat = 4
    /// 8pt - 同组元素间距
    static let _2xs: CGFloat = 8
    /// 12pt - 列表项间距、卡片内元素间距
    static let xs: CGFloat = 12
    /// 16pt - 页面水平边距、卡片内边距
    static let sm: CGFloat = 16
    /// 24pt - 区块间距、卡片之间间距
    static let md: CGFloat = 24
    /// 32pt - 大分组间距
    static let lg: CGFloat = 32
    /// 48pt - 页面板块间距
    static let xl: CGFloat = 48
    /// 64pt - 页面级大留白
    static let _2xl: CGFloat = 64
}

// MARK: - Corner Radius

enum AppCornerRadius {
    /// 8pt - 徽章、小元素
    static let small: CGFloat = 8
    /// 12pt - 内层卡片、按钮
    static let medium: CGFloat = 12
    /// 16pt - 外层卡片、容器
    static let large: CGFloat = 16
}

// MARK: - Shadow

enum AppShadow {
    static let subtle = ShadowStyle(color: .black.opacity(0.04), radius: 2, y: 1)
    static let medium = ShadowStyle(color: .black.opacity(0.08), radius: 4, y: 2)
}

struct ShadowStyle {
    let color: Color
    let radius: CGFloat
    let y: CGFloat
}

extension View {
    func appShadow(_ style: ShadowStyle) -> some View {
        self.shadow(color: style.color, radius: style.radius, y: style.y)
    }
}
```

根据项目品牌色补充 `Color` extensions（使用 Asset Catalog 定义 light/dark 变体）。

**询问用户：是否使用 Apple HIG Design Token 系统生成 DesignSystem.swift？**

如果选 Yes：
- 调用 `generate-design-system` skill
- 询问主题：sporty / diet / minimalist / custom
- 询问平台：iOS / macOS / 两者
- 生成完整的 DesignSystem.swift 到 `[项目名]/DesignSystem/`

#### 8.7 不要预建的目录

以下目录按需创建，不预建空目录：
- `06-prompts/` → 用户级规则已有
- `08-guidelines/` → 引用用户级全局规则

#### 8.8 App Store Connect 文档初始化

在 `docs/10-app-store-connect/` 下创建 4 个模板文件：

**privacy-policy.md** — 隐私政策模板：
```markdown
# [App 名称] - 隐私政策

最后更新日期：[日期]

生效日期：[日期]

[App 名称]（以下简称"我们"）重视你的隐私。本隐私政策说明我们在你使用 [App 名称] App 时如何收集、使用和保护你的信息。

## 一、我们收集的信息

（根据步骤 6 的功能列表，逐项列出数据收集类型）

## 二、我们不收集的信息

## 三、数据存储与安全

## 四、数据共享

## 五、你的权利

## 六、儿童隐私

## 七、隐私政策的变更

## 八、联系我们

## 九、适用法律
```

**terms-of-use.md** — 用户协议模板：
```markdown
# [App 名称] - 用户协议

最后更新日期：[日期]

（根据 App 功能填写：服务描述、使用限制、订阅条款、免责声明、知识产权、终止条款、适用法律）
```

**support-page.md** — 支持页面模板：
```markdown
# [App 名称] - 帮助与支持

## 常见问题

## 联系我们

- 邮箱：[support email]
```

**market.md** — App Store 描述模板：
```markdown
# [App 名称] - App Store 描述

## App Name / Subtitle

## Description

## Keywords

## What's New (v1.0)
```

#### 8.9 Notion 同步配置

如果用户计划使用 Notion 托管法律文档的 public URL：

创建 `.claude/notion-sync.local.md`（添加到 `.gitignore`）：
```yaml
---
token: ""
workspace: ""
parent_page_id: ""
pages: {}
---
```

提示用户：
1. 在 Notion 创建 Internal Integration 获取 token
2. 创建 "App Store Connect" 页面作为父页面
3. 将 token 和 parent_page_id 填入配置
4. 后续使用 `/update-asc-docs` 或 `/notion-page-sync` 同步

#### 8.10 CI/CD 配置初始化

**询问用户：是否配置 CI/CD（自动上传 TestFlight）？**

如果选 Yes：
- 调用 `setup-ci-cd` command
- 生成 `fastlane/Fastfile`
- 生成 `.github/workflows/release.yml`
- 说明需要配置的 GitHub Secrets

## 原则

1. **不编造**：所有竞品信息来自真实搜索，附链接
2. **客观分析**：不美化用户想法，指出真实风险
3. **可操作**：MVP 规划要具体，不泛泛而谈
4. **敢说不**：如果方向不可行，直接说
