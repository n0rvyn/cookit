---
name: generate-design-prompt
description: "Use when the user needs a design tool prompt (for Stitch, Figma, or similar) based on actual project functionality. Generates initial prompts from design docs/code, or refinement prompts from design analysis feedback."
disable-model-invocation: true
---

> **Note on `disable-model-invocation`:** This skill generates text for the user to paste into external design tools (Stitch/Figma). It does not invoke AI models itself; the AI reads project code/docs and assembles a prompt. Shared pattern with `apple-dev:generate-stitch-prompts`.

## 定位

从代码/文档中提取功能需求，翻译为设计工具能理解的 UI 描述语言。支持两种输出目标（Stitch / Figma）和两种模式（初始生成 / 迭代改进）。

基于 `apple-dev:generate-stitch-prompts` 的核心提取逻辑演进，增加 Figma 支持和 pipeline 集成。

## 参数

`$ARGUMENTS` 可选，格式：
- 空 → 生成主界面 prompt（auto-detect 目标工具）
- `stitch` / `figma` → 指定目标工具
- `all` → 生成主界面 + 所有后续屏幕的 follow-up prompts
- `refine` → 从 design analysis 文件读取迭代建议，生成改进 prompt
- `{屏幕名}` → 生成指定屏幕的 prompt

可组合：`stitch settings`、`figma all`、`refine stitch`

## 流程

### Mode A: 初始生成（默认）

#### 1. 目标工具检测

如果参数未指定工具：
1. 检查是否有 Stitch MCP 工具可用（`get_screen_code`）→ 建议 Stitch
2. 检查是否有 Figma MCP 工具可用（`get_design_context`）→ 建议 Figma
3. 都没有或都有 → 询问用户首选

#### 2. 项目信息采集

**自动执行，不问用户。** 按优先级依次读取，跳过不存在的：

| 优先级 | 来源 | 提取内容 |
|--------|------|----------|
| 1 | `CLAUDE.md` / `docs/00-AI-CONTEXT.md` / `README.md` | 产品定位、目标用户、核心功能、技术栈 |
| 2 | 设计文档（`docs/06-plans/*-design.md`） | 布局结构、页面层级、交互流程、信息架构、UX Assertions |
| 3 | UI 组件代码（Swift: `**/*View.swift`; Web: `src/components/`、`src/pages/`、`app/`） | 页面/组件列表、层级关系 |
| 4 | 类型/模型定义（Swift: `**/*.swift` with `struct/enum`; Web: `src/types/`、`src/models/`） | UI 展示的数据结构、枚举值、状态类型 |
| 5 | 样式/主题（`**/DesignTokens*`、`tailwind.config.*`、`**/theme.*`） | 当前配色、字体、间距体系（仅作参考） |
| 6 | 路由/导航定义 | 页面总数、导航结构 |

#### 3. 功能清单提取

**a) 屏幕清单**

列出所有独立页面/屏幕，每个标注：
- 名称
- 功能（一句话）
- 包含的 UI 区域（zones）
- 关键交互

**b) 每个屏幕的 UI 区域分解**

对目标屏幕逐区域提取：

| 区域 | 提取内容 |
|------|----------|
| 布局 | 排列方式（split pane / stack / grid / sidebar + content） |
| 数据展示 | 展示什么数据、数据的字段和值域、列表/卡片/表格形态 |
| 状态指示 | 有哪些状态、每个状态的视觉表达（颜色、图标、徽章） |
| 用户输入 | 输入方式（文本框 / 选择器 / 开关）、输入格式 |
| 操作按钮 | 按钮名称、触发行为描述 |
| 消息/反馈 | 消息类型、不同类型的视觉区分 |
| 导航 | Tab 切换、侧边栏、面包屑 |
| 可折叠/展开 | 哪些内容默认折叠、展开触发方式 |

**c) 交互关系**

提取区域间的联动：
- 点击 A 区域的元素 → B 区域如何响应
- 拖拽/缩放行为

#### 4. 信息转译

将技术描述转译为设计工具理解的 UI 语言：

| 技术概念 | UI 语言 |
|----------|---------|
| `DashMap<TabId, TabState>` | "a row of status cards, one per open session" |
| `enum Status { Idle, Running, Error }` | "a colored status dot (green=idle, blue=running, red=error)" |
| `Vec<ChatMessage>` with discriminated union | "a chronological feed with different message types: ..." |
| 后端实现（框架、并发模型、数据库） | 不出现 |
| API 调用方式 | 不出现 |
| 状态管理方案 | 不出现 |

规则：用户可见的数据和交互 → 必须出现；纯后端细节 → 过滤掉。

#### 5. Prompt 组装

根据目标工具选择格式：

**Stitch 格式：**

```
第1段：产品定位（1-2句）
  "Design a {platform} application UI for {name}, a {one-line description}."

第2段：平台约束（1句）
  "Platform: {desktop/mobile/responsive}. {theme preference}."

第3段起：逐区域描述（每区域一段，标题用 ── 分隔）

最后一段：设计方向指引
  - 目标用户画像
  - 设计优先级
  - 调性描述
```

术语规范：navbar, card, feed, badge, chip, modal, split pane, toggle, textarea（不用 container, indicator, popup 等泛称）

字符限制：主 prompt < 4000 字符。超出则拆分到 follow-up。不足 1500 字符则补充视觉细节。

**Figma 格式：**

```
第1段：产品定位 + 目标平台
  "Create a {platform} app prototype for {name}: {description}."

第2段：设计系统约束
  "Design system: {existing tokens summary or 'create a clean system'}.
   Color palette: {primary, secondary, accent}. Spacing scale: {base unit}."

第3段起：逐屏幕描述
  每屏幕包含：
  - 屏幕名称和用途
  - 组件列表（具体到每个元素的数据和交互）
  - 布局结构（columns, rows, grid）

最后一段：交互要求
  - 页面间导航方式
  - 关键交互流程（step by step）
  - 需要展示的状态变化
```

Figma 特有：可以引用现有组件库名称；可以指定 Auto Layout 方向；支持更长的 prompt（无严格字符限制）。

#### 6. 字符数检查（Stitch 格式时）

1. 估算总字符数
2. \> 4000 字符：移最不关键的区域到 follow-up
3. < 1500 字符：补充视觉细节

Figma 格式不做字符裁切，但每屏幕仍建议独立描述。

### Mode B: 迭代改进（参数包含 `refine`）

当参数包含 `refine` 时，从 design analysis 生成改进 prompt：

1. 搜索 `docs/06-plans/*-design-analysis.md` 找到最近的分析文件
2. 读取 `## Iteration Suggestions` 部分
3. 对每个 issue / missing state / alignment 条目：
   - 读取原始问题描述
   - 读取 design-analyzer 已生成的 follow-up prompt 文本
   - 如果 prompt 文本已存在且可直接使用 → 原样输出
   - 如果需要更多项目上下文 → 用步骤 2-4 的采集结果补充细节
4. 输出格式与初始模式相同，但标题为 `## Refinement Prompts`

## 输出

### 初始模式

````
## Design Prompt ({Stitch / Figma})

**项目**: {项目名称}
**屏幕**: {目标屏幕}
**目标工具**: {Stitch / Figma}
{Stitch 格式时} **字符数**: ~{N} chars

---

**复制以下内容粘贴到 {Stitch / Figma}：**

```
{生成的完整 prompt}
```

---

**使用建议**：
{根据目标工具不同}

Stitch:
- 先用 Standard Mode（Gemini Flash）测试，满意方向后切 Experimental Mode 精修
- 每次满意的结果截图保存，后续迭代时上传截图作为上下文
- 如需细化某个区域，描述时指明区域名称

Figma:
- 在 Figma Make 中粘贴，选择目标 frame 尺寸
- 生成后检查 Auto Layout 和组件命名
- 使用 Dev Mode 导出设计变量

**下一步**：
- 在设计工具中生成原型后，使用 `/understand-design` 将原型带回进行 AI 分析
````

### 参数为 `all` 时

主 prompt 之后额外输出 `## Follow-up Prompts` 部分，每屏幕一条。

### 迭代模式

````
## Refinement Prompts

**基于分析文件**: {design-analysis 路径}
**目标工具**: {Stitch / Figma}

### Issue 1: {问题描述}

```
{改进 prompt}
```

### Issue 2: {问题描述}

```
{改进 prompt}
```

### Missing State: {状态名}

```
{生成该状态的 prompt}
```
````

## 原则

1. **只描述用户可见的**：后端、API、状态管理方案不出现
2. **具体数据 > 抽象描述**：写 "a colored status dot (green=idle, blue=running, red=error)" 而不是 "a status indicator"
3. **一屏一 prompt**：主 prompt 只覆盖主界面，其他屏幕用 follow-up
4. **枚举值全列**：状态、类型、消息种类等枚举值逐一列出其视觉表达，不省略
5. **交互写完整链路**：不只写 "clickable"，写 "clicking a card switches the right pane to that terminal tab"
6. **英文输出**：prompt 始终用英文，即使项目文档是中文
7. **迭代 prompt 可直接粘贴**：不是对问题的描述，而是给设计工具的指令

## Pipeline 集成

在 dev-workflow pipeline 中的位置：

```
brainstorm（输出 design doc）
  → generate-design-prompt（本 skill）
  → [用户在 Stitch/Figma 中操作]
  → understand-design（分析原型）
  → generate-design-prompt refine（如需迭代）
  → [用户修改]
  → understand-design（再次分析）
  → write-plan
```
