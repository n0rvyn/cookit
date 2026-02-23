# UI 设计原则（专业级参考）
<!-- SECTION MARKERS: Each "section" comment line immediately precedes the ##
     heading it labels. Use Grep("<!-- section:", file) to find sections, then
     Read(file, offset, limit) to fetch only the relevant lines. -->

> 目标：让 AI 辅助开发的 UI 达到专业设计师 90 分水准。
> 适用平台：iOS/macOS（SwiftUI 优先）、Web App
> 来源：Refactoring UI、Apple HIG、Laws of UX、WCAG 2.1、Gestalt 心理学、Bringhurst 排版原理

---

<!-- section: 1. 字体系统（Typography） keywords: typography, font scale, type scale, line height, font weight, Dynamic Type -->
## 1. 字体系统（Typography）

### 1.1 字号阶梯（Type Scale）

使用数学比例生成字号阶梯，不要随意选择字号。

| 比例名 | 比值 | 适用场景 | 示例（base 16px / iOS 17pt body） |
|--------|------|---------|----------------------------------|
| Minor Second | 1.067 | 极紧凑 | 15, 16, 17, 18 |
| Major Second | 1.125 | 紧凑信息密集型 | 14, 16, 18, 20 |
| Minor Third | 1.200 | **移动端推荐** | 12, 14, 17, 20, 24 |
| Major Third | 1.250 | 移动/Web 通用 | 11, 14, 17, 22, 27 |
| Perfect Fourth | 1.333 | **Web 推荐** | 10, 13, 17, 23, 31 |
| Golden Ratio | 1.618 | 海报/展示 | 10, 16, 26, 42 |

**iOS Dynamic Type 精确值**（默认/"Large" 用户设置下）：

| Text Style | 默认字号 | 字重 |
|---|---|---|
| `.largeTitle` | 34pt | Regular |
| `.title` | 28pt | Regular |
| `.title2` | 22pt | Regular |
| `.title3` | 20pt | Regular |
| `.headline` | 17pt | Semibold |
| `.body` | 17pt | Regular |
| `.callout` | 16pt | Regular |
| `.subheadline` | 15pt | Regular |
| `.footnote` | 13pt | Regular |
| `.caption` | 12pt | Regular |
| `.caption2` | 11pt | Regular |

Apple 推荐正文最小 17pt，绝对最小 11pt。

**判断标准**：
- ✅ 相邻层级字号差 ≥ 2pt
- ✅ 标题与正文差异 ≥ 4pt 或 字重差 ≥ 2 级
- ❌ 页面中存在仅差 1pt 的两种字号（视觉无法区分）

### 1.2 行高（Line Height）

| 用途 | 行高倍数 | iOS 参考 |
|------|---------|---------|
| 大标题（28pt+） | 1.1 - 1.2 | `.largeTitle` 行高 ≈ 1.18 |
| 标题（20-27pt） | 1.2 - 1.3 | `.title` 行高 ≈ 1.25 |
| 正文（15-19pt） | 1.4 - 1.6 | `.body` 行高 ≈ 1.47 |
| 小字（11-14pt） | 1.3 - 1.5 | `.caption` 行高 ≈ 1.36 |

**核心规则**：字号越大，行高倍数越小。大标题不需要 1.5 倍行高。

### 1.3 字重层级

一个页面最多使用 **2-3 种字重**：

| 层级 | 推荐字重 | SwiftUI | 用途 |
|------|---------|---------|------|
| 强调 | Semibold / Bold | `.semibold` / `.bold` | 标题、CTA、关键数字 |
| 常规 | Regular | `.regular`（默认） | 正文 |
| 弱化 | Regular + 降低色彩 | `.regular` + `.secondary` | 辅助信息、时间戳 |

**判断标准**：
- ✅ 层级区分同时使用字重 + 颜色（不只靠一种）
- ❌ 使用 4 种以上字重（Thin + Light + Regular + Medium + Bold = 混乱）

### 1.4 字符宽度

**最佳阅读行宽**：45-75 字符（英文），20-40 字符（中文）。最佳值约 66 字符（英文）。

| 场景 | 推荐宽度 |
|------|---------|
| 手机竖屏正文 | 自然宽度（约 40-50 字符），无需额外限制 |
| 平板/桌面正文 | 使用 `readableContentGuide`（iOS 自动计算最佳行宽） |
| Web 正文 | `max-width: 680px`（约 65 字符） |
| 卡片内文字 | 受卡片宽度约束，通常满足 |

**iOS 实践**：UIKit 中使用 `UIView.readableContentGuide` 自动计算最佳行宽（见 §11.6）。SwiftUI 中 `List`/`Form` 已内置 readable width；自定义布局用 `.frame(maxWidth: 672)` 近似。

**Baymard Institute 研究**：行宽 > 80 字符时，内容跳过率增加 41%。

### 1.5 字间距（Letter Spacing / Tracking）

| 字号范围 | 字间距调整 | SF Pro 已内置 |
|---------|----------|--------------|
| 大标题 36pt+ | 收紧 -0.02em ~ -0.04em | ✅ Optical sizing 自动处理 |
| 正文 14-20pt | 默认 0 | ✅ |
| 全大写文字 | 加宽 +0.05em ~ +0.1em | 手动：`.tracking(1.5)` |
| 小字 11pt 以下 | 略加宽 +0.01em | ✅ |

**iOS 实践**：SF Pro 的 Optical Sizing 已处理大部分情况。只在全大写标签、等宽数字、自定义字体时手动调整。

---

<!-- section: 2. 间距系统（Spacing） keywords: spacing, padding, margin, whitespace, 8pt grid, density -->
## 2. 间距系统（Spacing）

### 2.1 8pt 网格

所有间距值基于 **4pt 的倍数，优先选择 8pt 的倍数**。4pt 和 12pt 用于紧凑场景（图标与文字间距、列表项间距、卡片内元素间距）。

**间距阶梯**：

| Token | 值 | 用途 |
|-------|------|------|
| 4xs | 2pt | 极细微调整（罕用） |
| 3xs | 4pt | 图标与标签间距、紧凑元素内间距 |
| 2xs | 8pt | 同组元素间距、小组件内边距 |
| xs | 12pt | 列表项间距、卡片内元素间距 |
| sm | 16pt | **页面水平边距**、卡片内边距、段落间距 |
| md | 24pt | 区块间距、卡片之间间距 |
| lg | 32pt | 大分组间距 |
| xl | 48pt | 页面板块间距 |
| 2xl | 64pt | 页面级大留白 |

### 2.2 间距关系规则

**内边距 < 外间距**（Refactoring UI 核心原则之一）

```
┌─────────────────────────────────────────┐
│ 容器                                      │
│   ┌──────────────┐  24pt  ┌──────────────┐│
│   │  卡片 A       │ ←────→ │  卡片 B       ││
│   │  padding:16pt │        │  padding:16pt ││
│   └──────────────┘        └──────────────┘│
└─────────────────────────────────────────┘

卡片内边距 (16pt) < 卡片间距 (24pt)  ✅
卡片内边距 (16pt) > 卡片间距 (12pt)  ❌  内容看起来属于不同卡片
```

**同级一致**：同层级的间距值必须相同。

**判断标准**：
- ✅ 所有卡片使用相同 padding
- ✅ 所有列表项使用相同 spacing
- ❌ 同级卡片有的 padding 16pt，有的 12pt

### 2.3 嵌套圆角公式

**内层圆角 = 外层圆角 − 外层与内层的间距**

```
外层 cornerRadius = 16pt
外层 padding = 8pt
→ 内层 cornerRadius = 16 - 8 = 8pt

如果 padding ≥ 外层 cornerRadius：
→ 内层 cornerRadius = 0（直角）
```

**iOS 实践**：
```
外层容器: 16pt → 内层卡片: 12pt → 内层徽章: 8pt
```

**判断标准**：
- ✅ 嵌套层级的圆角递减
- ❌ 外层 12pt 内层 16pt（内层圆角比外层大 = 视觉不协调）

### 2.4 留白策略

**留白不是浪费空间，是信息结构的一部分。**

| 原则 | 说明 |
|------|------|
| 组间距 > 组内距 | 分组用间距而非分隔线 |
| 首屏不塞满 | 留出呼吸空间，宁缺毋滥 |
| 对称留白 | 上下左右边距保持一致或有意的不对称 |
| 焦点留白 | 重要元素周围留更多空白，拉开与周围的距离 |

**Refactoring UI 原则**：如果界面看起来设计感不够，先试试加大留白，而非加装饰。

### 2.5 信息密度层级

不同场景需要不同密度，不是一律"多留白"：

| 密度 | 行高倍数 | 间距 | 适用场景 |
|------|---------|------|---------|
| 紧凑（Compact） | 1.2-1.4x | 组内 4pt，组间 8-12pt | 设置页、数据表格、选择列表 |
| 标准（Standard） | 1.4-1.6x | 组内 8pt，组间 16-24pt | 表单、内容列表、对话 |
| 宽松（Comfortable） | 1.5-1.8x | 组内 16pt，组间 32-48pt | 引导页、展示页、空状态 |

**选择原则**：
- 信息量大 + 用户需要快速扫描 → 紧凑
- 常规交互 → 标准
- 内容少 + 需要引导注意力 → 宽松
- 同一页面可以混合密度：列表区域紧凑，操作区域标准

---

<!-- section: 3. 颜色系统（Color） keywords: color, OKLCH, contrast, palette, semantic color, dark mode -->
## 3. 颜色系统（Color）

### 3.1 色彩比例法则

| App 类型 | 背景 | 辅助 | 强调 | 示例 |
|---------|------|------|------|------|
| 工具型 | ~80% | ~15% | ~5% | 设置、计算器、记事本 |
| 内容型 | ~60% | ~30% | ~10% | 社交、新闻、电商 |
| 展示型 | ~50% | ~35% | ~15% | 营销页、着陆页 |

60/30/10 源自室内设计，适用于内容型 App；iOS 工具型 App 背景占比远高于 60%，中性色主导，强调色只在可交互元素上出现。

**判断标准**：
- ✅ 眯眼看界面，背景占绝对主体，只有少量色块跳出
- ❌ 多个颜色竞争注意力、背景色和强调色比例接近

### 3.2 中性色层级

**iOS 优先使用系统语义颜色**（自动适配深色模式）：

| 层级 | 文字颜色 | 背景颜色 | 用途 |
|------|---------|---------|------|
| 最强 | `.primary` | — | 标题、关键信息 |
| 次强 | `.secondary` | `.secondarySystemBackground` | 正文、卡片背景 |
| 弱化 | `.tertiary` | `.tertiarySystemBackground` | 辅助信息、嵌套背景 |
| 最弱 | `.quaternary` | — | 占位符、禁用状态 |
| 分隔 | — | `Color(uiColor: .separator)` | 分隔线 |

只有在语义颜色无法满足需求时（如品牌定制灰色），才建立自定义灰阶：

```
                         用途（Web/自定义场景）
   50 ░░░░░░░░░░░░░░  页面背景
  100 ░░░░░░░░░░░░░░  卡片/次要背景
  200 ░░░░░░░░░░░░░░  边框、分隔线
  300 ░░░░░░░░░░░░░░  禁用状态
  400 ████████████     辅助文字
  500 ████████████     次要文字
  600 ████████████     正文
  700 ████████████████ 标题
  800 ████████████████ 强调标题
  900 ████████████████ 极深（慎用）
```

### 3.3 色彩和谐

| 方法 | 色轮关系 | 适用场景 |
|------|---------|---------|
| 单色（Monochromatic） | 同色相，不同明度/饱和度 | 最安全，适合大多数 App |
| 类似（Analogous） | 色轮相邻 30° 内 | 和谐温暖，适合内容型 App |
| 互补（Complementary） | 色轮对面 180° | 高对比，用于强调（小面积）|
| 分裂互补（Split-complementary） | 主色 + 互补色两侧各偏 30° | 对比但不刺激 |

**实操建议**：
- 大多数 App 用**单色方案** + 一个强调色即可
- 不要同时使用 2 个以上高饱和色
- 页面颜色种类 ≤ 5（含语义色红/黄/绿）

### 3.4 HSB 调色技巧

**Refactoring UI 核心技巧**：

1. **亮度增加时，色相向暖色偏移（黄 60°）**
2. **亮度降低时，色相向冷色偏移（蓝 240°）**

这让浅色和深色变体看起来更自然，而非简单地加白或加黑。

3. **饱和度与亮度反向**：浅色降饱和，深色降亮度但保持饱和度
4. **深色模式**：高饱和色需降低饱和度 + 降低亮度，避免在暗背景上刺眼
5. **深色模式 opacity 阈值**：`Color.X.opacity(n)` 做有色背景时，n < 0.15 在深色模式下几乎不可见（与纯黑背景无法区分）。
   - 需要区分层级的有色背景：浅色模式 opacity 0.08-0.12，深色模式 0.15-0.20
   - 实现方式：根据 `colorScheme` 动态调整（参考模式：`Color.X.opacity(scheme == .dark ? 0.15 : 0.08)`）

### 3.5 对比度标准（WCAG 2.1）

| 级别 | 正文文字 | 大字（18pt+ 粗体，或 24pt+） | UI 组件/图形 |
|------|---------|---------------------------|-------------|
| AA（最低要求） | 4.5 : 1 | 3 : 1 | 3 : 1 |
| AAA（推荐） | 7 : 1 | 4.5 : 1 | — |

**常见违反**：
- 浅灰文字 `#999` 在白底 `#FFF` 上 = 对比度 2.85:1 ❌
- 深灰文字 `#666` 在白底 `#FFF` 上 = 对比度 5.74:1 ✅
- 白色文字在品牌蓝 `#4A90D9` 上 = 需验证（可能不够）

**iOS 实践**：使用 `.primary`（对比度最高）、`.secondary`（已验证 AA）、`.tertiary`（仅用于最次要信息）。

### 3.6 品牌色应用

品牌色 = App 的强调色（`.tint` / `accentColor`），贯穿整个 App。

**使用场景**：可交互元素（按钮、链接）、选中态（Tab Bar、Segment）、进度指示器、空状态 CTA

**禁止场景**：大面积背景（工具型 App 背景应为中性色）、非交互文字、纯装饰

**与语义色的关系**：语义色（红/黄/绿）优先于品牌色；同一元素不同时用品牌色和语义色

**深色模式**：品牌色对比度不足时，提供深色变体（降亮度、保色相；参见 §3.4 第 4 点）

---

<!-- section: 4. 视觉层级（Visual Hierarchy） keywords: visual hierarchy, emphasis, weight, scale, prominence -->
## 4. 视觉层级（Visual Hierarchy）

### 4.1 三种工具建立层级

视觉层级不只靠字号。**同时使用三种工具**：

| 工具 | 强调 | 弱化 |
|------|------|------|
| 字号 | 放大 | 缩小 |
| 字重 | 加粗 | 不变（不要用 Light） |
| 颜色 | 深色/强调色 | 浅灰/.secondary |

**Refactoring UI 核心理念**：弱化不重要的信息，比放大重要信息更有效。

```
❌ 业余做法：放大标题来强调
┌─────────────────────┐
│ 【28pt Bold 黑色】标题  │
│ 【16pt Regular 黑色】正文│
│ 【14pt Regular 黑色】辅助│
└─────────────────────┘

✅ 专业做法：弱化次要信息来强调
┌─────────────────────┐
│ 【20pt Semibold 深灰】标题│
│ 【16pt Regular 中灰】正文 │
│ 【14pt Regular 浅灰】辅助 │
└─────────────────────┘
```

### 4.2 一屏一焦点

每个页面/屏幕只有 **一个主要操作焦点**：
- 主 CTA 按钮用实心 + 强调色
- 次要操作用轮廓/文字按钮
- 一屏内不要有两个同等视觉权重的按钮

### 4.3 页面层级模板

```
Level 1: 页面标题     → .title (28pt) / .title2 (22pt) + .semibold + .primary
Level 2: 区块标题     → .title3 (20pt) + .semibold + .primary
Level 3: 内容正文     → .body (17pt) + .regular + .primary
Level 4: 辅助信息     → .subheadline / .footnote + .regular + .secondary
Level 5: 最弱信息     → .caption + .regular + .tertiary
```

**注意**：
- `.headline`（17pt Semibold）与 `.body`（17pt Regular）字号相同，仅差字重。`.headline` 适用于列表项标题等"同行内的强调"，不适合跨区块的分组标题
- Level 1 选 `.title2`(22pt) 时，与 Level 2 `.title3`(20pt) 仅差 2pt，低于 §1.1 的 ≥ 4pt 阈值。此时 Level 2 应改用 `.headline`（靠字重区分），或 Level 1 用 `.title`(28pt) 拉开差距

**判断标准**：
- ✅ 眯眼测试（Squint Test）：半闭眼看界面，仍能分辨 3 个层级
- ❌ 所有文字同一视觉权重 → 无层级 → 用户不知道先看哪里

### 4.4 数字与标签的层级

卡片中常见的数字 + 标签组合：

```
❌ 业余：标签和数字同等权重
┌──────────┐
│ 收入        │
│ ¥12,500    │
└──────────┘

✅ 专业：数字是焦点，标签是辅助
┌──────────┐
│ 收入 (.caption .secondary)  │
│ ¥12,500 (.title2 .semibold) │
└──────────┘
```

---

<!-- section: 5. 布局原则（Layout） keywords: layout, alignment, grid, columns, containment -->
## 5. 布局原则（Layout）

### 5.1 对齐

**一切对齐到网格线**。视觉对齐比数学对齐更重要。

| 规则 | 说明 |
|------|------|
| 左对齐统一 | 同一容器内所有元素左边缘对齐到同一条线 |
| 不混用对齐 | 同一列表不同时出现左对齐和居中对齐 |
| 数字右对齐 | 金额、统计数字右对齐便于比较 |
| 图标光学对齐 | 三角形/播放按钮需视觉居中（偏右 1-2pt） |

### 5.2 黄金比例（1 : 1.618）

实际应用方式（不是万能公式，是参考比例）：

| 场景 | 应用 |
|------|------|
| 两栏布局（Web/iPad） | 主内容 : 侧边栏 ≈ 5 : 3（接近 1.618） |
| 卡片宽高比 | 5:8 或 3:5（接近黄金比例） |
| 字号跳级 | Golden Ratio scale 1.618（仅用于展示型设计） |

**iOS 行动按钮位置**：不用黄金分割点（62% 高度），而是遵循拇指热区人体工学：
- 主操作按钮放在屏幕底部（底部安全区上方），单手拇指自然可达
- 底部固定按钮用 `.safeAreaInset(edge: .bottom)` 或 toolbar `.bottomBar`
- 次要操作放在导航栏（右上角）或内容区域内

**实操**：黄金比例更适合作为"直觉校准"而非严格公式。适用于静态构图（卡片比例、两栏布局），不适用于交互元素的位置决策。

### 5.3 三分法（Rule of Thirds）

将页面分为 3×3 网格，关键元素放在交叉点附近：

```
┌───┬───┬───┐
│   │   │   │
├───┼───┼───┤  ← 关键内容放在
│   │ ◉ │   │    四个交叉点
├───┼───┼───┤
│   │   │   │
└───┴───┴───┘
```

**移动端应用**：主要内容区域放在上 1/3 到中 1/3 之间；底部 1/3 留给操作区和 Tab Bar。

### 5.4 视觉重量与平衡

| 增加视觉重量 | 减少视觉重量 |
|-------------|-------------|
| 深色 | 浅色 |
| 大尺寸 | 小尺寸 |
| 密集纹理/图案 | 大面积留白 |
| 靠近中心 | 远离中心 |
| 规则形状 | 不规则形状 |

**对称平衡**：安全、正式、稳定（适合工具类 App）
**非对称平衡**：动态、现代、有活力（适合社交/创意类 App）

---

<!-- section: 6. 视觉流（Visual Flow） keywords: visual flow, reading order, F-pattern, Z-pattern -->
## 6. 视觉流（Visual Flow）

### 6.1 阅读模式

| 模式 | 适用场景 | 布局策略 |
|------|---------|---------|
| **单列流** | **iOS/移动端（首选）** | 自上而下线性滚动，关键信息在首屏 |
| F 型 | Web 文字密集型、iPad 多列 | 重要信息放左上；标题吸引横扫 |
| Z 型 | Web 着陆页、营销页 | 左上 Logo → 右上 CTA → 左下内容 → 右下按钮 |

**iOS 说明**：移动端是单列纵向滚动，视觉流本质上是线性的。F/Z 型来自 Web 大屏多列布局的眼动追踪研究，对 iPhone 单列布局参考价值有限。iPad 多列布局可参考 F 型。

### 6.2 引导视线

1. **大到小**：大元素先被看到，引导到小元素
2. **亮到暗**：高对比/高饱和色先被看到
3. **孤立优先**：留白多的元素比拥挤区域的元素更先被注意
4. **方向暗示**：箭头、人物视线方向、渐变方向

### 6.3 首屏规则

- **0.05 秒**：用户形成第一印象（整洁？混乱？专业？廉价？）
- **3 秒内**：用户判断"这个页面能帮我解决什么"
- 首屏必须回答：**这是什么 + 我该做什么**

---

<!-- section: 7. Gestalt 原则（感知分组） keywords: Gestalt, grouping, proximity, similarity, closure -->
## 7. Gestalt 原则（感知分组）

### 7.1 接近性（Proximity）

**距离近 = 有关系**。所有 Gestalt 原则中最强的分组信号（冲突时，接近性优先于相似性）。

```
❌ 均匀间距 = 无分组
A  B  C  D  E  F

✅ 差异间距 = 清晰分组
A B C    D E F
```

**实操**：组内间距 : 组间间距 ≥ 1:2（如组内 8pt，组间 16pt+）

### 7.2 相似性（Similarity）

外观相同 = 功能/类别相同。

- 同类按钮统一样式
- 同级信息统一字体/颜色
- 可点击元素统一颜色（强调色）

### 7.3 连续性（Continuity）

沿线或曲线排列的元素被感知为一组。

- 列表项垂直排列 → 自然连续
- 水平标签页 → 连续性引导左右浏览
- 进度条 → 连续性暗示流程

### 7.4 闭合（Closure）

大脑会补完不完整的形状。

- 卡片不需要完整边框，阴影或背景色即可暗示容器
- Tab 选中指示器不需要包围整个 Tab，底部线条即可

### 7.5 共同区域（Common Region）

同一个背景色/边框内的元素被视为一组。

- 卡片把相关信息框在一起
- Section header + 背景色分隔不同区块
- **不要过度使用**：太多卡片/框 = 视觉噪音

### 7.6 图形-背景（Figure-Ground）

前景元素必须清晰地从背景中分离。

- 弹窗/Sheet 需要遮罩层或阴影
- 浮动按钮需要阴影
- 深色模式下卡片用微妙的亮度差区分层级（而非阴影）

---

<!-- section: 8. UX 法则（Laws of UX） keywords: UX laws, Fitts, Hick, Miller, affordance -->
## 8. UX 法则（Laws of UX）

### 8.1 菲茨定律（Fitts's Law）

**目标越大、越近，点击越快。**

| 规则 | iOS 值 |
|------|--------|
| 最小触摸目标 | 44 × 44pt（Apple HIG 标准） |
| 关键操作按钮 | 宽度占屏幕 > 50%，或使用 `.buttonStyle(.borderedProminent)` |
| 紧邻元素间距 | ≥ 8pt（防止误触） |
| Web/Android 参考 | 48 × 48dp（Material Design），不用于 iOS |

**常见违反**：图标按钮视觉 24pt 但触摸区域也是 24pt → 增加 `.frame(minWidth: 44, minHeight: 44)`

### 8.2 希克定律（Hick's Law）

**选项越多，决策越慢。**

| 阈值 | 建议 |
|------|------|
| 同屏选项 | ≤ 5-7 个（超过则分组或分页） |
| 导航 Tab | ≤ 5 个（Apple HIG 硬限制） |
| 表单字段 | 每屏 ≤ 5 个（多了分步） |
| 操作菜单 | ≤ 5 个常用 + "更多"收纳其余 |

### 8.3 米勒定律（Miller's Law）

**短期记忆容量 7 ± 2。** 信息分块（chunking）帮助记忆。

- 电话号码分段：138-0000-0000 ✅，13800000000 ❌
- 长列表分组显示
- 步骤类流程分 3-5 步

### 8.4 雅各布定律（Jakob's Law）

**用户期望你的产品和他们用过的产品一样运作。**

- iOS App 遵循 iOS 设计规范（导航在顶部，Tab 在底部）
- 常见图标含义不要改（齿轮=设置，放大镜=搜索）
- 返回手势、下拉刷新等系统行为不覆盖

### 8.5 冯·雷斯托夫效应（Von Restorff Effect）

**在一组相似元素中，视觉上独特的那个最容易被记住。**

- 主 CTA 必须在视觉上与其他按钮明显不同（支撑"一屏一焦点"原则）
- 推荐方案用独特样式高亮（定价页常见）
- **注意**：过度使用（多个元素都"独特"）会互相抵消效果

### 8.6 审美可用性效应（Aesthetic-Usability Effect）

**用户认为好看的设计更好用，即使客观可用性相同。**

视觉打磨不是装饰；它直接影响用户对可用性的感知和对小问题的容忍度。

### 8.7 多尔蒂阈值（Doherty Threshold）

**系统响应 < 400ms，用户感知为"即时"。**

| 响应时间 | 用户感知 | 处理方式 |
|---------|---------|---------|
| < 100ms | 即时 | 无需任何反馈 |
| 100-400ms | 快速 | 简单的视觉变化（按钮按下效果） |
| 400ms-1s | 可感知延迟 | 轻量动画、骨架屏 |
| 1s-10s | 等待 | 进度指示器 + 可取消 |
| > 10s | 流失风险 | 后台处理 + 通知完成 |

---

<!-- section: 9. 动效原则（Motion） keywords: motion, animation, transition, easing, duration -->
## 9. 动效原则（Motion）

### 9.1 时长

| 类型 | 推荐时长 | iOS 参考 |
|------|---------|---------|
| 微交互（按钮按下、颜色/透明度变化） | 80-150ms | `.easeInOut(duration: 0.1)` |
| 状态切换（Toggle、选中/取消） | 150-250ms | `.snappy` |
| 小元素过渡（淡入、滑入） | 200-300ms | `.default`（约 250ms） |
| 页面转场 | 300-500ms | NavigationStack 默认 ~350ms |
| 复杂动画（展开/收起） | 300-500ms | `.spring(duration: 0.4)` |

**核心规则**：
- 状态变化（颜色、透明度、缩放）：80-200ms，快速响应不拖沓
- 空间位移（滑入、展开、转场）：200-500ms，需要时间让用户跟踪运动轨迹
- > 500ms = 感觉迟缓
- 永远 **不超过 700ms**
- **区分**：微交互 100ms 不是"突然"，而是"即时"；空间位移 100ms 才是"看不清"

### 9.2 缓动函数

| 场景 | 缓动 | SwiftUI |
|------|------|---------|
| 元素进入 | Ease Out（快入慢出） | `.easeOut` |
| 元素退出 | Ease In（慢入快出） | `.easeIn` |
| 状态变化 | Ease In-Out | `.easeInOut` |
| iOS 原生感 | Spring | `.spring`（推荐默认） |
| 弹性反馈 | Bouncy Spring | `.spring(response: 0.4, dampingFraction: 0.6)` |

**iOS Spring 预设**（iOS 17+，优先使用）：

| 预设 | 特性 | 适用场景 |
|------|------|---------|
| `.smooth` | 无弹跳，干净收敛 | 大部分 UI 过渡的默认选择 |
| `.snappy` | 快速，极微弹跳 | 按钮/开关响应 |
| `.bouncy` | 可见弹跳，活泼感 | 吸引注意力、趣味交互 |

**iOS 推荐**：优先使用 Spring 而非 `.easeInOut`，Spring 动画更自然（来源：WWDC23 "Animate with springs"）。

### 9.3 动效原则

| 原则 | 说明 |
|------|------|
| 有因必有果 | 每个动画必须对应用户操作或状态变化 |
| 方向暗示关系 | 进入方向 = 来源方向；退出方向 = 去向方向 |
| 退出快于进入 | 退出动画比进入动画短 15-20%（Material Design 原则） |
| 重要的先动 | 主角元素先动，配角跟随 |
| 减少运动 | 尊重 `accessibilityReduceMotion`，提供替代方案 |

### 9.4 禁止的动效

- ❌ 纯装饰性循环动画（分散注意力）
- ❌ 弹跳超过 2 次的 Spring（幼稚感）
- ❌ 延迟超过 200ms 才开始的动画（用户以为没响应）
- ❌ 同时有 5 个以上元素在动（认知过载）

### 9.5 触觉反馈（Haptic Feedback）— iOS 独有

触觉反馈是区分专业与业余 iOS App 的重要维度。

**SwiftUI（iOS 17+，首选）**：

| 类型 | SwiftUI modifier | 适用场景 |
|------|-----------------|---------|
| Impact（碰撞） | `.sensoryFeedback(.impact(style: .light/.medium/.heavy), trigger:)` | UI 元素"到位"：吸附、对齐、卡片放下 |
| Selection（选择） | `.sensoryFeedback(.selection, trigger:)` | 滚动选择器值变化、Picker 切换 |
| Notification（通知） | `.sensoryFeedback(.success/.warning/.error, trigger:)` | 操作结果反馈：保存成功、错误提示 |

**UIKit 等价**：`UIImpactFeedbackGenerator`、`UISelectionFeedbackGenerator`、`UINotificationFeedbackGenerator`。

**使用原则**：

| 规则 | 说明 |
|------|------|
| 与视觉反馈配对 | 触觉不能替代视觉，只是增强。没有对应视觉变化的触觉 = 困惑 |
| 频率克制 | 列表滚动不需要每行触发；高频操作（打字）不加触觉 |
| 强度匹配动作 | 轻量操作用 `.light`，确认/完成用 `.medium`，破坏性操作用 `.heavy` |
| 系统一致性 | Toggle 切换用 `.impact(.light)`，删除确认用 `.warning` |

**常见场景**：
- ✅ Toggle 切换：`.sensoryFeedback(.impact(style: .light), trigger: isOn)`
- ✅ 操作成功：`.sensoryFeedback(.success, trigger: saveCompleted)`
- ✅ 长按触发菜单：`.sensoryFeedback(.impact(style: .medium), trigger: showMenu)`
- ✅ 滑动到阈值时（如下拉刷新触发点）：`.impact(style: .medium)`
- ❌ 普通按钮点击（按钮自带视觉反馈，不需要额外触觉）
- ❌ 每次滚动列表行
- ❌ 输入文字时

---

<!-- section: 10. 组件规范（Component Standards） keywords: components, button, card, input, modal, list -->
## 10. 组件规范（Component Standards）

### 10.1 按钮层级

一个页面的按钮必须有明确的层级：

| 层级 | 样式 | SwiftUI | 用途 |
|------|------|---------|------|
| 主要（Primary） | 实心 + 强调色 | `.borderedProminent` | 主操作（一个可见视觉区域内最多 1 个） |
| 次要（Secondary） | 轮廓/浅底 | `.bordered` | 次要操作 |
| 最弱（Tertiary） | 纯文字 | `.borderless` / `Button` | 取消、辅助链接 |
| 危险（Destructive） | 红色文字/红底 | `.destructive` role | 删除、退出 |

**按钮内边距比例**：水平 padding = 垂直 padding × 2~3

| 尺寸 | 垂直 | 水平 |
|------|------|------|
| Small | 8pt | 16pt |
| Medium | 12pt | 24pt |
| Large | 16pt | 32pt |

**判断标准**：
- ✅ 一个可见视觉区域内只有 1 个 Primary 按钮
- ✅ 列表中每行有一个行级主操作（尺寸小于页面级 Primary，视觉权重自然降低）
- ❌ 同一可见区域内两个同等视觉权重的实心按钮并排

### 10.2 卡片规范

| 属性 | 推荐值 | 说明 |
|------|--------|------|
| 内边距 | 16pt | 最小 12pt，不能贴边 |
| 圆角 | 12-16pt | 与页面圆角保持层级关系 |
| 阴影（浅色模式） | opacity 0.04-0.08, radius 2-4, y 1-2 | 克制！微妙即可 |
| 深色模式替代 | 微妙亮度差（+4-8%） | 深色模式不用阴影，用背景色层级 |
| 同类卡片 | 统一所有属性 | 圆角、阴影、内边距全部一致 |

### 10.3 图标规范

| 规则 | 说明 |
|------|------|
| 风格统一 | 全用 SF Symbols，不混用第三方图标 |
| 粗细统一 | 同屏图标用同一 weight（`.regular` 或 `.medium`） |
| 渲染模式统一 | 同上下文用同一 rendering mode |
| 尺寸统一 | 同级元素的图标尺寸一致（如列表项图标全部 24pt） |
| 光学对齐 | 非对称图标（如播放、向右箭头）视觉居中 |

### 10.4 输入框规范

| 属性 | 推荐值 |
|------|--------|
| 高度 | 44pt（iOS 标准触摸高度） |
| 内边距 | 水平 12-16pt，垂直居中 |
| 圆角 | 8-12pt |
| 标签位置 | 输入框上方（浮动标签也可） |
| 错误提示位置 | 输入框正下方，红色小字 |
| 聚焦状态（Web） | 边框颜色变为强调色 |
| 聚焦状态（iOS） | 光标闪烁 + 键盘弹出（iOS 原生无 focus ring，不要添加边框变色） |

---

<!-- section: 11. iOS / macOS 平台特定（Apple HIG） keywords: Apple HIG, iOS, macOS, platform guidelines, navigation bar -->
## 11. iOS / macOS 平台特定（Apple HIG）

### 11.1 iOS 页面边距

| 设备 | 水平边距 |
|------|---------|
| iPhone SE / Mini | 16pt |
| iPhone 标准/Plus | 16pt（20pt 也可） |
| iPad | 20-24pt（紧凑模式 16pt） |

### 11.2 导航栏

| 属性 | 值 |
|------|-----|
| 大标题高度 | 约 96pt（系统管理） |
| 小标题高度 | 约 44pt |
| 大标题用于 | 顶级页面（Tab 根视图） |
| 小标题用于 | 详情页、二级页面 |

### 11.3 Tab Bar

| 规则 | 值 |
|------|-----|
| Tab 数量 | 3-5 个（最多 5 个） |
| 图标 + 文字 | 必须同时有（不能只有图标） |
| 选中颜色 | 强调色（`.tint`） |
| 未选中颜色 | `.secondary` |

### 11.4 安全区域

| 区域 | 处理 |
|------|------|
| 顶部（刘海/动态岛） | 内容不可侵入 |
| 底部（Home Indicator） | 底部按钮留足间距 |
| 键盘 | 输入区域自动上推 `.ignoresSafeArea(.keyboard)` |

### 11.5 Dynamic Type 适配

| 级别 | 建议 |
|------|------|
| 必须适配 | 所有用户可见文本 |
| 测试范围 | xSmall → AX5（无障碍最大） |
| 布局策略 | 大字号时允许换行、滚动，不截断 |

### 11.6 readableContentGuide

Apple 提供的 `readableContentGuide` 根据设备宽度和字号自动调整内容最大宽度至最佳阅读行宽。

- iPad 横屏：自动收窄内容区域，避免行宽过长
- 大字号：自动调整行宽适配更大的字符
- 优于手动 `.frame(maxWidth:)` — 自适应性更强

**UIKit**：直接约束到 `view.readableContentGuide`，最准确。

**SwiftUI**：目前无原生 readableContentGuide modifier。替代方案：
- 简单场景：`.frame(maxWidth: 672)` + `.dynamicTypeSize` 响应（近似值，iPhone 上无影响，iPad 上生效）
- 精确场景：通过 `UIViewRepresentable` 桥接 UIKit 的 `readableContentGuide`
- `List` / `Form` 在 iPad 上已内置 readable width 行为，无需额外处理

---

## 12. Web App 补充原则

### 12.1 响应式断点

| 断点 | 宽度 | 布局 |
|------|------|------|
| Mobile | < 640px | 单列 |
| Tablet | 640-1024px | 可选侧边栏 |
| Desktop | 1024-1440px | 多列 |
| Wide | > 1440px | 内容居中，max-width 限制 |

### 12.2 正文 max-width

正文区域 `max-width: 680px`（约 65 字符），超宽屏时居中。

### 12.3 Web 字号基准

`html { font-size: 16px }`，所有字号用 rem 单位：

| 层级 | rem | px |
|------|-----|-----|
| Display | 2.5rem | 40px |
| H1 | 2rem | 32px |
| H2 | 1.5rem | 24px |
| H3 | 1.25rem | 20px |
| Body | 1rem | 16px |
| Small | 0.875rem | 14px |
| Caption | 0.75rem | 12px |

---

## 13. 检查清单（Quick Checklist）

供 `/design-review` 和 `/ui-review` 快速引用。

### 通过/不通过判断

| # | 检查项 | 通过标准 | 常见违反 |
|---|--------|---------|---------|
| 1 | 字号阶梯 | 相邻层级差 ≥ 2pt，页面内无仅差 1pt 的字号 | 14pt 和 15pt 同时出现 |
| 2 | 字重层级 | ≤ 3 种字重，层级用字重+颜色共同区分 | 5 种字重混用 |
| 3 | 行高 | 正文 1.4-1.6x，标题 1.1-1.3x | 标题用 1.5x 行高（太松散） |
| 4 | 间距网格 | 所有间距为 4/8 的倍数 | 出现 15pt、22pt 等非网格值 |
| 5 | 内外间距 | 组件内 padding ≤ 组件间 spacing | 卡片 padding 24pt 但卡片间距 16pt |
| 6 | 嵌套圆角 | 内层 = 外层 − 间距 | 内外圆角相同或内层更大 |
| 7 | 颜色数量 | 页面 ≤ 5 种颜色（含语义色） | 7+ 种颜色竞争 |
| 8 | 色彩比例 | 背景占绝对主体（工具型 ≥ 80%），强调色仅用于可交互元素 | 多个高饱和色竞争注意力 |
| 9 | 对比度 | 正文 ≥ 4.5:1，大字 ≥ 3:1 | 浅灰文字 #999 在白底上 |
| 10 | 一屏一焦点 | 同一可见区域内只有一个 Primary 按钮 | 同一区域两个同等权重的实心按钮 |
| 11 | 触摸目标 | ≥ 44pt | 图标按钮 24pt 无扩展 |
| 12 | 对齐一致 | 同容器内元素对齐到同一条线 | 混用左对齐和居中 |
| 13 | 留白充足 | 内容有呼吸空间，分组清晰 | 所有元素紧贴 |
| 14 | 动效时长 | 微交互 80-200ms，空间位移 200-500ms | 微交互 > 200ms（拖沓）或位移 > 700ms |
| 15 | 图标统一 | 同风格、同粗细、同渲染模式 | SF Symbols 混 outline 和 filled |
| 16 | 深色模式 opacity | 有色背景 opacity ≥ 0.15（深色模式下） | `Color.purple.opacity(0.1)` 在深色模式下不可见 |

---

## 14. 业余 vs 专业：常见差异总结

| 维度 | 业余 / AI 默认 | 专业做法 |
|------|---------|---------|
| 层级 | 所有文字同大小、同颜色 | 3+ 级层级，弱化次要信息 |
| 间距 | 随意数值（13pt、17pt） | 8pt 网格，系统化 |
| 颜色 | 高饱和色到处用 | 大面积低饱和 + 小面积强调 |
| 留白 | 害怕空白，塞满内容 | 充足留白，让内容呼吸 |
| 对齐 | 差 1-2px 的错位随处可见 | 严格网格对齐 |
| 阴影 | 高 opacity 重阴影 | opacity ≤ 0.08 的微妙阴影 |
| 按钮 | 所有按钮同等权重 | 明确的 Primary/Secondary/Tertiary 层级 |
| 圆角 | 随意值、嵌套不递减 | 系统化圆角，嵌套递减 |
| 字体 | 3+ 种字体混用 | 1 种字体 + 字重/字号变化 |
| 分隔 | 到处加分隔线/边框来理清布局 | 用间距和背景色差区分，边框仅用于结构边界 |
| 动效 | 无动效或过度弹跳 | 微交互 80-200ms + 空间位移 200-500ms，Spring 优先 |
| 深色模式 | 简单反色 | 独立配色方案，降低饱和度 |
| 透明度 | 浅色深色用同一个 opacity 值 | 根据 colorScheme 调整 opacity，深色模式 ≥ 0.15 |
| 图标 | 大小/风格不统一 | SF Symbols 统一风格 |
| AI 千篇一律：卡片 | 所有卡片同大小同间距 | 重点卡片更大或更多留白；次要卡片紧凑排列 |
| AI 千篇一律：列表 | 纯文字列表无节奏变化 | 关键数据大字号突出；列表穿插摘要/图表打破单调 |
| AI 千篇一律：布局 | 所有页面同一布局模板 | 不同页面不同密度（§2.5）；首页宽松，设置紧凑 |
| AI 千篇一律：颜色 | 颜色均匀分布 | 大面积中性色 + 品牌色只在交互点 |

---

<!-- section: 15. iOS 26 Liquid Glass keywords: Liquid Glass, iOS 26, material, blur, frosted glass -->
## 15. iOS 26 Liquid Glass

> iOS 26 已发布（2025 年 9 月）。使用 iOS 26 SDK 编译的 App 自动获得 Liquid Glass。项目最低部署目标 iOS 18 时，需用 `#available(iOS 26, *)` 包裹 Glass-only API。

Liquid Glass 是 iOS 7 以来最大的视觉变革，核心理念是「透光材质 + 内容即界面」。

### 15.1 核心原则

Liquid Glass = 导航/控制层的透光材质，**不用于内容层**。

五大设计原则：
- **Lensing**：折射聚光，Glass 元素像透镜一样折射下方内容
- **Materialization**：从内容中浮现，而非悬浮于内容之上
- **Fluidity**：流动变形响应触摸，触摸时材质形态随手指变化
- **Morphing**：跨状态平滑变形，元素在不同状态间连续过渡
- **Adaptivity**：根据背景内容自动调整色调、阴影、动态范围

使用 iOS 26 SDK 编译 → 系统组件（NavigationStack, TabView, Sheet）自动获得 Glass。
临时退出：`UIDesignRequiresCompatibility = YES`（Xcode 27 移除此选项）。

### 15.2 新增 API 速查表

| API | 用途 | 注意 |
|-----|------|------|
| `.glassEffect(.regular)` | 自定义控件的标准 Glass | 默认 capsule 形状 |
| `.glassEffect(.clear)` | 高透 Glass（媒体背景上） | 仅当背景是图片/视频时 |
| `GlassEffectContainer` | Glass 元素共享容器 | Glass 不能采样其他 Glass，必须用容器包裹。注：SDK 中 init 参数待实现时确认 |
| `glassEffectID(_:in:)` | 跨状态 morphing | 配合 Namespace + withAnimation |
| `.buttonStyle(.glass)` | 次要玻璃按钮 | iOS 26 替代 `.bordered` |
| `.buttonStyle(.glassProminent)` | 主要玻璃按钮 | iOS 26 替代 `.borderedProminent` |
| `tabBarMinimizeBehavior(.onScrollDown)` | Tab Bar 滚动收缩 | 仅当 Tab Bar 覆盖在 scrollable 内容上时生效 |
| `Tab(role: .search)` | 搜索 Tab | 选中时变形为搜索框 |
| `tabViewBottomAccessory` | Tab Bar 上方附件 | 持续可见，收缩时跟随 |
| `navigationSubtitle(_:)` | 导航栏副标题 | |
| `ToolbarSpacer(.fixed)` | 工具栏间距控制 | |
| `scrollEdgeEffectStyle(.soft)` | 滚动边缘淡化 | 替代手写渐变遮罩 |
| `.backgroundExtensionEffect()` | 内容延伸到安全区 | |

### 15.3 组件行为变化

- **Tab Bar**：默认浮动 + Glass；滚动自动收缩为胶囊；搜索 Tab 变形为搜索框
- **Navigation Bar**：大标题/inline 标题获得 Glass 背景；toolbar items 自动分组到共享 Glass 背景
- **Sheet**：半高 Sheet 自动获得 Glass 背景（需至少指定一个部分高度 detent）；全高 Sheet 过渡到不透明；**禁止** iOS 26 上用 `presentationBackground()` 覆盖 Glass
- **Button**：`.glassProminent` 替代 `.borderedProminent`；`.glass` 替代 `.bordered`；capsule 形状主导
- **控件**：Toggle/Slider/Picker 获得 Glass 质感；新增 `.controlSize(.extraLarge)`

### 15.4 颜色与阴影规则

- Glass 材质自动适应背景色调，开发者不设置 Glass 颜色
- Tinting（`.glassEffect(.regular.tint(.blue))`）仅用于语义含义（主操作=蓝、错误=红），不用于装饰
- 阴影由系统自适应管理（暗背景上加深、亮背景上减弱）→ **开发者不要手动给 Glass 元素加 `.shadow()`**
- 文字在 Glass 上自动获得 vibrant treatment → 用高对比前景色（`.primary`）确保可读性

### 15.5 对现有原则的影响索引

| 现有章节 | 影响 | 调整 |
|---------|------|------|
| §3.1 色彩比例 | Glass 层不计入色彩比例 | 内容区域规则不变 |
| §10.1 按钮层级 | iOS 26 上 Primary = `.glassProminent` | `#available(iOS 26, *)` 分支 |
| §10.2 卡片规范 | 卡片属于内容层，不使用 Glass | 阴影规则不变 |
| §11.3 Tab Bar | 浮动+自动收缩是新默认 | 数量限制（3-5）不变 |
| §9.2 缓动函数 | Glass morphing 使用系统管理的弹簧动画 | 自定义 Glass 动画无需手指定 |

---

## 16. 页面构成模板（Page Composition）

### 16.1 工具型 App 页面节奏

三种页面骨架及对应的密度/间距/层级指引：

**1. 列表页**（设置、数据列表）

```
┌─────────────────────────┐
│ Navigation Bar (large)   │
├─────────────────────────┤
│ Section Header           │
│ ┌─────────────────────┐ │
│ │ Row                  │ │
│ │ Row                  │ │
│ │ Row                  │ │
│ └─────────────────────┘ │
│         24pt             │
│ Section Header           │
│ ┌─────────────────────┐ │
│ │ Row                  │ │
│ └─────────────────────┘ │
├─────────────────────────┤
│ Tab Bar                  │
└─────────────────────────┘
```

- SwiftUI：`NavigationStack > List > Section` groups
- 密度：紧凑（§2.5）
- 间距：Section 间 24pt，行间由 List 默认管理
- 操作：inline 行级操作 or swipe action
- 视觉层级：§4.3 Level 2-4
- 按钮层级：§10.1 Tertiary 为主

**2. 卡片页**（仪表盘、摘要）

```
┌─────────────────────────┐
│ Navigation Bar           │
├─────────────────────────┤
│                          │
│ ┌─────────────────────┐ │
│ │  摘要卡片 (宽松)      │ │
│ │  大字号 + 多留白      │ │
│ └─────────────────────┘ │
│         16pt             │
│ ┌──────────┐┌──────────┐│
│ │ 次要卡片  ││ 次要卡片  ││
│ └──────────┘└──────────┘│
│         16pt             │
│ ┌─────────────────────┐ │
│ │  详情卡片            │ │
│ └─────────────────────┘ │
│                          │
├─────────────────────────┤
│ Tab Bar                  │
└─────────────────────────┘
```

- SwiftUI：`ScrollView > LazyVStack(spacing: 16)` > 卡片组
- 密度：标准
- 间距：卡片间 16pt，卡片内 padding 16pt，Section 间 32pt
- 焦点：首个卡片或顶部摘要区域使用更大字号/更多留白（宽松密度）
- 视觉层级：§4.3 Level 1-3
- 按钮层级：§10.1 首个卡片内可有 1 个 Primary

**3. 表单页**（输入、配置）

```
┌─────────────────────────┐
│ Navigation Bar (inline)  │
├─────────────────────────┤
│ Section Header           │
│ ┌─────────────────────┐ │
│ │ TextField            │ │
│ │ TextField            │ │
│ │ Picker               │ │
│ └─────────────────────┘ │
│ Section Header           │
│ ┌─────────────────────┐ │
│ │ Toggle               │ │
│ └─────────────────────┘ │
│                          │
├─────────────────────────┤
│ [ 提交按钮 - Primary ]   │
└─────────────────────────┘
```

- SwiftUI：`NavigationStack > Form > Section` groups
- 密度：标准
- 间距：Form 自动管理
- 操作：底部固定 CTA（`.safeAreaInset(edge: .bottom)` or toolbar `.bottomBar`）
- 视觉层级：§4.3 Level 2-4
- 按钮层级：§10.1 底部 Primary

### 16.2 "做对"检查（正面质量指标）

规则体系中唯一的"正面清单"（对应快速自检的"负面清单"）：

1. 首屏 3 秒内传达"这是什么 + 该做什么"
2. 文字 ≥ 3 级层级且通过眯眼测试
3. 背景色占绝对主体，强调色只在可交互元素
4. 分组通过间距差异实现，不依赖分隔线
5. 主操作视觉权重 > 所有其他按钮
6. 不同页面有不同密度节奏（设置=紧凑，引导=宽松）

---

## 引用来源

| 来源 | 贡献领域 |
|------|---------|
| Refactoring UI (Wathan & Schoger) | 间距系统、视觉层级、颜色技巧、实操建议 |
| Apple Human Interface Guidelines | iOS/macOS 平台规范、间距、触摸目标 |
| Laws of UX (Jon Yablonski) | Fitts、Hick、Miller、Jakob、Doherty |
| WCAG 2.1 | 对比度标准、无障碍 |
| Gestalt Psychology | 感知分组原则 |
| Elements of Typographic Style (Bringhurst) | 行高、行宽、字间距 |
| Material Design | 动效原则、缓动曲线、elevation |
| Modular Scale (Tim Brown) | 字号阶梯数学比例 |
