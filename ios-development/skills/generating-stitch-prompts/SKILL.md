---
name: generating-stitch-prompts
description: "Use when the user wants to generate UI with Google Stitch for the current project, or needs a Stitch prompt based on actual project functionality."
disable-model-invocation: true
---

## 定位

从代码/文档中提取功能需求，翻译为 Stitch 能理解的 UI 描述语言。只描述"界面是什么、用户能做什么"，不涉及后端实现。

## 触发时机

- 想用 Stitch 给当前项目生成全新 UI
- 想用 Stitch 重新设计某个页面/组件
- 任何时候需要一条基于项目真实功能的 Stitch prompt

## 参数

`$ARGUMENTS` 可选，格式：
- 空 → 生成主界面（primary screen）prompt
- `settings` / `onboarding` / 任意屏幕名 → 生成该屏幕的 prompt
- `all` → 生成主界面 prompt + 后续屏幕的 follow-up prompts 列表

## 流程

### 1. 项目信息采集

**自动执行，不问用户。** 按优先级依次读取，跳过不存在的：

| 优先级 | 来源 | 提取内容 |
|--------|------|----------|
| 1 | `CLAUDE.md` / `docs/00-AI-CONTEXT.md` / `README.md` | 产品定位、目标用户、核心功能、技术栈 |
| 2 | 设计文档（`docs/plans/`、`docs/design/`） | 布局结构、页面层级、交互流程、信息架构 |
| 3 | UI 组件代码（`src/components/`、`src/pages/`、`src/views/`、`app/`） | 所有页面/组件列表、组件层级关系、props/state |
| 4 | 类型定义（`src/types/`、`src/models/`、`src/interfaces/`） | UI 中展示的数据结构、枚举值、状态类型 |
| 5 | 样式/主题（`src/styles/`、`src/design/`、`tailwind.config.*`） | 当前配色、字体、间距体系（仅作参考，Stitch 会重新设计） |
| 6 | 路由定义（`src/router/`、`src/App.tsx`、`app/layout.*`） | 页面总数、导航结构 |

### 2. 功能清单提取

从采集结果中提取：

**a) 屏幕清单**

列出所有独立页面/屏幕，每个标注：
- 名称
- 功能（一句话）
- 包含的 UI 区域（zones）
- 关键交互

**b) 每个屏幕的 UI 区域分解**

对目标屏幕（由参数决定），逐区域提取：

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
- 键盘快捷键（仅影响布局的，如分割线拖拽）

### 3. 信息转译

将技术描述转译为 Stitch 理解的 UI 语言：

| 技术概念 | Stitch 语言 |
|----------|-------------|
| `DashMap<TabId, TabState>` | "a row of status cards, one per open session" |
| `enum Status { Idle, Running, Error }` | "a colored status dot (green=idle, blue=running, red=error)" |
| `Vec<ChatMessage>` with discriminated union | "a chronological feed with different message types: ..." |
| `RingBuffer<u8>` | （不出现在 prompt 中，纯后端） |
| `tokio::spawn` / `async fn` | （不出现在 prompt 中） |
| `invoke("command")` / API calls | （不出现在 prompt 中） |
| `xterm.js` terminal | "a real terminal emulator area with monospace text, blinking cursor, and sample output" |

**过滤规则**：
- 后端实现细节（框架、并发模型、数据库）→ 不出现
- API 调用方式 → 不出现
- 状态管理方案（Redux / Context / Zustand）→ 不出现
- 用户可见的数据和交互 → 必须出现
- 数据的视觉形态（卡片/列表/表格）→ 必须出现

### 4. Prompt 组装

#### 结构（严格按此顺序）

```
第1段：产品定位（1-2句）
  "Design a {platform} application UI for {name}, a {one-line description}."

第2段：平台约束（1句）
  "Platform: {desktop/mobile/responsive}. {theme preference}."

第3段起：逐区域描述（每区域一段，标题用 ── 分隔）
  每段包含：
  - 布局方式
  - 包含哪些元素（逐一列出）
  - 每个元素显示什么数据
  - 用户可以做什么操作
  - 状态变化的视觉表达

最后一段：设计方向指引
  - 目标用户画像（开发者 / 普通用户 / 设计师）
  - 设计优先级（信息密度 / 留白 / 可玩性）
  - 调性描述（专业工具 / 消费产品 / 极简）
```

#### Stitch 限制适配

| 限制 | 适配策略 |
|------|----------|
| 长 prompt（>4000字符）丢失组件 | 主 prompt 只覆盖主界面；其他屏幕作为 follow-up |
| 多屏幕一次描述效果差 | 每个 follow-up 针对单屏幕 |
| 通用描述生成通用 UI | 每个元素必须写明具体数据和交互，不用"等"或"..." |
| Stitch 不理解技术术语 | 所有技术概念转译为视觉描述（见第3步转译表） |

#### 术语规范

在 prompt 中使用 Stitch 友好的 UI 术语：

| 用 | 不用 |
|----|------|
| navbar, tab bar, sidebar | navigation component |
| card, tile | container |
| status dot, badge | indicator |
| feed, timeline | message list |
| textarea, input field | text component |
| toggle, switch | boolean input |
| chip, tag | pill button |
| modal, dialog, overlay | popup |
| split pane, draggable divider | resizable layout |
| monospace, terminal area | code block |

### 5. 字符数检查

组装完成后：
1. 估算 prompt 总字符数
2. 如果 > 4000 字符：
   - 识别最不关键的区域描述
   - 将其移入 follow-up prompt
   - 在主 prompt 中标注 "[details in follow-up]"
3. 如果 < 1500 字符：
   - 检查是否遗漏了区域或交互
   - 补充更多视觉细节（间距暗示、对齐方式、响应式行为）

## 输出

### 参数为空或具体屏幕名时

````
## Stitch Prompt

**项目**: {项目名称}
**屏幕**: {目标屏幕}
**字符数**: ~{N} chars

---

**复制以下内容粘贴到 Stitch：**

```
{生成的完整 prompt}
```

---

**使用建议**：
- 先用 Standard Mode（Gemini Flash）测试，满意方向后切 Experimental Mode 精修
- 每次满意的结果截图保存，后续迭代时上传截图作为上下文
- 如需细化某个区域，描述时指明区域名称（如 "Refine the tab snapshots section..."）
````

### 参数为 `all` 时

主 prompt 之后额外输出：

````
---

## Follow-up Prompts

以下 prompt 在主界面生成满意后逐条使用。每条前先上传前一步的截图。

### Screen 2: {屏幕名}

```
{follow-up prompt}
```

### Screen 3: {屏幕名}

```
{follow-up prompt}
```

...
````

## 原则

1. **只描述用户可见的**：后端、API、状态管理方案不出现在 prompt 中
2. **具体数据 > 抽象描述**：写 "a colored status dot (green=idle, blue=running, red=error)" 而不是 "a status indicator"
3. **一屏一 prompt**：主 prompt 只覆盖主界面，复杂应用的其他屏幕用 follow-up
4. **保持在 4000 字符内**：超出则拆分，不硬塞
5. **用 Stitch 术语**：navbar, card, feed, badge, chip, modal；不用技术术语
6. **设计方向给范围不给答案**：写 "power-user developer tool, prioritize information density" 而不是 "use 12px font and 4px padding"
7. **枚举值全列**：状态、类型、消息种类等枚举值逐一列出其视觉表达，不省略
8. **交互写完整链路**：不只写 "clickable"，写 "clicking a card switches the right pane to that terminal tab"
9. **英文输出**：Stitch prompt 始终用英文，即使项目文档是中文
