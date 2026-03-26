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

## project-brief.md 模板

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

> 定制项目写入：「定制项目，客户已确认需求，跳过市场调研」

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

## 风险与缓解（事前验尸）

| 失败场景 | 维度 | 可能性 | 影响 | 缓解措施 |
|----------|------|--------|------|----------|
| ... | ... | ... | ... | ... |

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
| 阴影 | 5 级（flat/subtle/small/medium/large） | z 轴语义分层（原则 §10.2） |
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

// MARK: - Layout

/// 页面级布局约束 — 非节奏值，由平台和 size class 驱动
enum AppLayout {
    /// 16pt — iPhone 内容边距 (compact size class)
    static let marginCompact: CGFloat = 16
    /// 20pt — iPad/Mac 内容边距 (regular size class)
    static let marginRegular: CGFloat = 20
    /// 672pt — regular size class 最大内容宽度
    static let maxContentWidth: CGFloat = 672
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
    /// 基面元素，无阴影
    static let flat = ShadowStyle(color: .clear, radius: 0, y: 0)
    /// 轻微浮起：卡片默认态
    static let subtle = ShadowStyle(color: .black.opacity(0.04), radius: 2, y: 1)
    /// 中度浮起：悬停态卡片、下拉菜单
    static let small = ShadowStyle(color: .black.opacity(0.06), radius: 4, y: 2)
    /// 明显浮起：弹出面板、浮动按钮
    static let medium = ShadowStyle(color: .black.opacity(0.08), radius: 8, y: 4)
    /// 最高层级：模态弹窗、拖拽中元素
    static let large = ShadowStyle(color: .black.opacity(0.12), radius: 16, y: 8)
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

颜色阶梯结构（在 DesignSystem.swift 中追加）：

```swift
// MARK: - Color Scale

/// 颜色阶梯：每色 9 级，500 为基准色，向上变浅向下变深。
/// 值来自 Asset Catalog（支持 light/dark 变体），不硬编码 hex。
/// 灰色阶梯的饱和度建议 S 值 5-12%，避免在不同显示器上偏色。
enum AppColor {
    // -- Primary（替换为项目主色名） --
    static let primary50  = Color("Primary50")   // 最浅，背景/高亮底
    static let primary100 = Color("Primary100")
    static let primary200 = Color("Primary200")
    static let primary300 = Color("Primary300")
    static let primary400 = Color("Primary400")
    static let primary500 = Color("Primary500")  // 基准色：按钮、链接
    static let primary600 = Color("Primary600")
    static let primary700 = Color("Primary700")
    static let primary800 = Color("Primary800")
    static let primary900 = Color("Primary900")  // 最深，深色文本/标题

    // -- Gray（带微饱和的中性灰） --
    static let gray50  = Color("Gray50")
    static let gray100 = Color("Gray100")
    static let gray200 = Color("Gray200")
    static let gray300 = Color("Gray300")
    static let gray400 = Color("Gray400")
    static let gray500 = Color("Gray500")
    static let gray600 = Color("Gray600")
    static let gray700 = Color("Gray700")
    static let gray800 = Color("Gray800")
    static let gray900 = Color("Gray900")

    // -- 按需添加 Accent / Success / Warning / Danger 阶梯 --
}
```

根据项目品牌色补充 `Color` extensions（使用 Asset Catalog 定义 light/dark 变体）。

**颜色定义指引**：定义颜色时以 HSL 维度思考（色相/饱和度/亮度独立调整），调色时只改一个维度。Asset Catalog 中使用 Display P3 色彩空间。代码中避免硬编码 hex 字符串，使用 Asset Catalog 命名颜色引用。

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

**询问用户：是否配置 CI/CD（Xcode Cloud + 自动版本管理）？**

如果选 Yes：
- 调用 `setup-ci-cd` skill
- 统一所有 target 版本号 + 启用 Apple Generic versioning
- 生成 `.github/workflows/auto-version.yml`（conventional commit → semver bump，ubuntu-latest）
- 生成 `ci_scripts/ci_post_clone.sh`（Xcode Cloud 构建号自动设置）
- 输出 Xcode Cloud workflow 配置指引（Dev to TestFlight / Main to App Store）
- 零 GitHub Secret 配置
