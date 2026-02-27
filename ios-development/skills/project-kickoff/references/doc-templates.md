# 文档模板

## docs/00-AI-CONTEXT.md 模板

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
- 开发指南/计划：`docs/06-plans/`
- 功能行为：`docs/05-features/`
- 产品评估：`docs/08-product-evaluation/`
```

## docs/02-architecture/README.md

简要描述：分层、数据流、模块依赖。后续可拆分为多个文件。

## docs/05-features/README.md 模板

```markdown
# 功能文档

记录功能的预期行为、关键代码位置、边界条件。

## 文件模板

每个功能一个文件，命名格式：`功能名.md`

\```markdown
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
\```
```

## Design System 初始化

**设计输入处理**：如果 CP4 中用户提供了设计文件（Stitch 生成或已有设计稿），先读取设计文件提取颜色、字体、间距等 token 值，以提取值为准初始化 DesignSystem.swift。如果 CP4 选择了「跳过设计」，使用下方默认模板值。

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

## 不要预建的目录

以下目录按需创建，不预建空目录：
- `06-prompts/` → 用户级规则已有
- `08-guidelines/` → 引用用户级全局规则

## App Store Connect 文档初始化

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

## Notion 同步配置

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

## CI/CD 配置初始化

**询问用户：是否配置 CI/CD（自动上传 TestFlight）？**

如果选 Yes：
- 调用 `setup-ci-cd` skill
- 生成 `fastlane/Fastfile`
- 生成 `.github/workflows/release.yml`
- 说明需要配置的 GitHub Secrets
