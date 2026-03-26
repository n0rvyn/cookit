---
name: project-kickoff
description: "Use when starting a new iOS/macOS project, or the user says 'kickoff', 'new project setup'. Runs the project kickoff flow to clarify requirements, converge scope, and produce execution recommendations."
disable-model-invocation: true
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

### CP1: 项目概念确认

**展示内容**（控制在 20 行内）：

| 维度 | 内容 |
|------|------|
| 项目名称 | {name} |
| 解决的问题 | {problem} |
| 目标用户 | {users} |
| 独特切入点 | {angle} |
| AI 时代判定 | 值得开发 / 不需要开发 / AI 替代风险高 |
| AI 难以替代的部分 | {irreplaceable} |

**询问用户**（使用 AskUserQuestion）：

> 以上是项目概念和 AI 时代可行性判定。
>
> - **继续** — 进入市场调研
> - **定制项目** — 客户已确认需求，跳过市场调研，直接进入功能规划
> - **调整** — 修改概念或切入点后重新评估
> - **放弃** — 终止开题流程

等待用户回复。选择「调整」则回到步骤 1 重新澄清需求；选择「放弃」则终止流程。

选择「定制项目」时：
- 跳过步骤 3（市场调研）、4（竞品分析）、5（定位分析）、CP2
- 直接进入步骤 6（功能规划）
- 步骤 2 的 AI 时代前置检验调整为：不问「是否需要开发」（客户已确认），保留「AI 能力评估」（帮客户识别哪些功能可用 AI 更高效地做）
- project-brief.md 中「市场调研」章节写入：「定制项目，客户已确认需求，跳过市场调研」
- 后续步骤中涉及「差异化」「护城河」「竞品」的分析内容，替换为客户需求对齐分析

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

### CP2: 差异化方向确认

**展示内容**（控制在 40 行内）：

**竞品概览**：

| 竞品 | 定位 | 商业模式 | 优点 | 缺点 |
|------|------|---------|------|------|
| {name1} | {positioning} | {model} | {strength} | {weakness} |
| ... | ... | ... | ... | ... |

**关键发现**（3 条以内）：

1. {finding1}
2. {finding2}
3. {finding3}

**推荐差异化方向**：{direction}

**询问用户**（使用 AskUserQuestion）：

> 以上是竞品分析和推荐的差异化方向。
>
> - **确认方向** — 按此方向进入定位分析和功能规划
> - **调整方向** — 指定不同的差异化方向
> - **补充调研** — 补充特定竞品或来源的调研

等待用户回复。选择「调整方向」则根据用户指定的方向重新分析；选择「补充调研」则回到步骤 3 补充搜索。

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

#### 6.5.7 AI 推断功能设计原则

如果项目功能涉及机器推断/分析（智能分类、自动标签、行为预测等），设计时遵守：

- **宁漏勿误**：阈值宁严勿松，错误推断比没有推断更糟
- **明确告知**：UI 中标注这是机器推断，不是确定结果
- **保留覆盖入口**：用户能修正机器判断

#### 6.5.8 架构原型决策

在确定 AI 集成深度后，判断项目属于哪个架构原型：

| 原型 | 描述 | 典型特征 | 推荐技术栈 |
|------|------|---------|-----------|
| **Simple Skill** | 单命令完成单任务 | 无状态、单次输入输出、无 UI | Claude Code skill / CLI |
| **Multi-Skill Workflow** | 多步骤编排、有状态流转 | 步骤间依赖、需要上下文传递 | Agent + Tool chain |
| **Content Studio** | 内容生产/编辑为核心 | 需要预览、迭代、版本管理 | UI + AI backend |
| **Data + MCP Tool** | 数据查询/操作为核心 | 外部数据源集成、结构化输出 | MCP server + Tool schema |

**判定流程**：
1. 用户需求可以用一句话 prompt 完成 → Simple Skill
2. 需要多步骤但不需要 UI → Multi-Skill Workflow
3. 核心价值是内容创建/编辑 → Content Studio
4. 核心价值是连接/查询外部数据 → Data + MCP Tool
5. 混合型：列出主原型 + 辅原型，主原型决定架构骨架

#### 6.5.9 Terminal-First 默认检查

在决定构建 UI 之前，回答：

- [ ] **这个功能必须有 UI 吗？** 如果 terminal 命令 + 文本输出就能满足 80% 的使用场景，先做 CLI 版本
- [ ] **UI 的不可替代价值是什么？** 列出 terminal 无法提供的具体能力（实时预览、拖拽操作、可视化图表等）
- [ ] **成本对比**：CLI 开发量 vs UI 开发量，维护成本差异

如果无法列出 UI 的不可替代价值 → 先做 CLI，用户反馈确认需要 UI 后再加。

#### 6.5.10 三次法则（Three Times Rule）

评估自动化时机：

- 第一次手动做 → 记录过程
- 第二次手动做 → 提取模式，写成文档
- 第三次手动做 → 自动化

在 MVP 规划中标记哪些功能适用三次法则：先手动/半自动验证价值，再投入自动化开发。避免过早自动化尚未验证的流程。

#### 6.5.11 AI 反模式目录

检查项目设计是否包含以下反模式：

| 反模式 | 检测信号 | 问题 | 替代方案 |
|--------|---------|------|---------|
| **Prompt Spaghetti** | 单个 prompt > 2000 字，混合多种指令 | 不可维护、难以调试 | 拆分为多个 skill，每个 < 500 字 |
| **God Agent** | 一个 agent 处理所有任务 | 上下文污染、精度下降 | 按职责拆分专用 agent |
| **Invisible AI** | AI 做了决策但用户看不到推理过程 | 信任问题、调试困难 | 输出推理链、标注置信度 |
| **Token Waste Loop** | 每次调用传递完整历史 | 成本高、延迟大 | 摘要压缩、选择性上下文 |
| **Hallucination Amplifier** | AI 输出直接作为下一步 AI 输入 | 错误级联放大 | 中间加验证/人工检查点 |
| **UI-First Trap** | 先做 UI 再考虑 AI 能力边界 | UI 承诺了 AI 做不到的事 | 先验证 AI 能力，再设计 UI |

对每个匹配的反模式，在 project-brief 中记录缓解措施。

### 6.6 平台 API 可行性验证

在确认功能范围之前，验证架构依赖的关键平台 API 和能力是否真的能按设计方式使用。

#### 6.6.1 提取关键依赖

从步骤 6 的功能列表和技术选型中，列出架构成立所依赖的关键 API/能力点。重点关注：

- **跨 target 数据流**：Extension ↔ Main App、Widget ↔ Main App 之间传递的每种数据类型
- **受限框架**：HealthKit、CallKit、Messages、SMS、Push Notification、NFC 等 Apple 管控较严的框架
- **需要特殊 Entitlement 的能力**：App Groups、Keychain Sharing、Associated Domains 等
- **Extension 中使用的 API**：Extension 对可用 API 有独立限制

输出格式：

```
[关键依赖清单]
1. {API/能力} — 用于 {什么功能} — 架构中的角色：{做什么}
2. ...
```

#### 6.6.2 逐项查官方文档验证

对清单中每一项，用 WebFetch 访问 Apple Developer Documentation 对应页面，确认：

- 该 API 在目标 target 类型中是否可用
- 数据是否允许在设计的路径上流转（特别是跨进程/跨 target）
- 有无明确的使用限制或禁止事项
- 需要哪些 Entitlement，Entitlement 是否对个人/组织开发者开放

**搜索策略**：
- 直接访问框架文档页：`https://developer.apple.com/documentation/{框架名}`
- 访问对应 Extension 类型的文档：`https://developer.apple.com/documentation/{extension类型}`
- 如果文档中未明确说明限制，补充搜索：WebSearch `"{API名}" "{Extension类型}" restrictions site:developer.apple.com`

输出格式：

```
[API 验证结果]
1. {API/能力} — ✅ 可行 — 文档确认：{关键原文摘录}
2. {API/能力} — ❌ 不可行 — 文档原文：{限制描述} — 来源：{URL}
3. {API/能力} — ⚠️ 文档未明确 — 需要 spike 验证
```

#### 6.6.3 处理验证结果

- **全部 ✅**：进入 CP3
- **有 ❌**：停止流程，向用户报告硬限制，讨论替代架构方案。调整架构后重新从 6.6.1 验证
- **有 ⚠️**：告知用户哪些点文档未明确，建议在正式开发前用最小工程 spike 验证。用户决定是否现在验证还是接受风险继续

### 6.7 事前验尸（Pre-mortem）

假设项目已上线 6 个月后失败。从以下维度推演最可能的失败原因：

**推演维度**：

- **技术风险**：架构假设不成立、关键 API 限制未发现、性能瓶颈、平台版本兼容性
- **产品风险**：用户不买账、需求理解偏差、核心体验不够好、竞品先行（定制项目跳过竞品相关）
- **执行风险**：范围蔓延、关键路径单点依赖、独立开发者精力分配、技术债累积
- **数据风险**：冷启动问题、数据质量不可控、隐私合规障碍

**输出格式**：

| 失败场景 | 维度 | 可能性 | 影响 | 缓解措施 | 计划应覆盖 |
|----------|------|--------|------|----------|-----------|
| {scenario} | 技术/产品/执行/数据 | 高/中/低 | 致命/严重/可控 | {mitigation} | ✅ 写入 dev-guide / ⚠️ 需 spike 验证 |

**处理规则**：

- 可能性「高」+ 影响「致命」或「严重」的项：必须在 project-brief.md 的「风险与缓解」章节记录，且标记「计划应覆盖」= ✅ 的条目传递给后续 `/write-dev-guide`
- 如果发现致命级风险且无可行缓解措施：暂停流程，向用户报告风险详情，询问是否继续
- 定制项目：跳过「竞品先行」相关风险项

### CP3: 功能范围确认

**展示内容**（控制在 60 行内）：

**产品定位摘要**：

- 差异点：{differentiation}
- 护城河：{moat}
- 目标用户：{users}

**功能列表**：

| 功能 | 描述 | 优先级 |
|------|------|--------|
| {feature1} | {desc} | 核心 |
| {feature2} | {desc} | 核心 |
| ... | ... | ... |

**明确不做**：

- {not_doing_1}
- {not_doing_2}

**技术选型**：

| 技术 | 选择 | 理由 |
|------|------|------|
| {category} | {choice} | {reason} |

**AI Native 级别**：Level {N} — {description}

**平台 API 验证结果**：

| API/能力 | 用途 | 状态 | 说明 |
|----------|------|------|------|
| {api1} | {usage} | ✅/❌/⚠️ | {detail} |
| ... | ... | ... | ... |

**关键风险（事前验尸）**：

仅列出可能性「高」且影响「致命」或「严重」的条目：

| 失败场景 | 缓解措施 | 计划应覆盖 |
|----------|----------|-----------|
| {scenario} | {mitigation} | ✅/⚠️ |

**询问用户**（使用 AskUserQuestion）：

> 以上是产品定位、功能范围、技术选型、AI 集成评估、平台 API 验证和关键风险。
>
> - **确认范围** — 按此范围进入设计生成
> - **调整功能** — 增删功能或调整优先级
> - **调整技术选型** — 修改技术方案

等待用户回复。选择「调整功能」或「调整技术选型」则修改后重新展示本检查点。

### 7. 设计生成

基于步骤 1-6 的分析结果，使用 Stitch 生成 UI 设计稿。

1. 提示用户运行 `/generate-stitch-prompts all`，为项目生成主界面及各屏幕的 Stitch prompt
2. 对每个包含列表/内容区域的屏幕，标记需要空状态设计。空状态是新用户首次看到的界面，优先级不低于填充态
3. 从 skill 输出中提取：屏幕清单（名称 + 功能一句话）、每个屏幕的核心 UI 区域列表、需要空状态的屏幕标记
4. 将提取结果填入 CP4 展示模板

### CP4: 视觉方向确认

**展示内容**（控制在 40 行内）：

**屏幕清单**：

| 屏幕 | 功能 | 核心 UI 区域 | 空状态 |
|------|------|-------------|--------|
| {screen1} | {function} | {zones} | 需要 / — |
| {screen2} | {function} | {zones} | 需要 / — |
| ... | ... | ... | ... |

**Stitch prompt 数量**：主 prompt 1 条 + follow-up {N} 条

**询问用户**（使用 AskUserQuestion）：

> Stitch prompt 已生成。选择后续方式：
>
> - **用 Stitch 生成设计** — 将 prompt 粘贴到 Stitch 生成 UI，完成后提供设计文件路径继续流程
> - **已有设计稿** — 提供设计文件目录路径
> - **跳过设计** — 不使用设计稿，后续使用默认 Design System 值

等待用户回复。选择「用 Stitch 生成设计」则暂停流程，用户在 Stitch 中完成设计后回来提供文件路径；选择「已有设计稿」则记录路径；选择「跳过设计」则标记无设计输入，跳过 7.5，直接进入 CP5。设计文件路径将在步骤 7.5 和 9.6 中使用。

### 7.5 设计评审

**前置条件**：CP4 中用户提供了设计文件目录路径。如果选择了「跳过设计」，跳过本步。

读取设计目录下的全部文件，以顶尖视觉设计师视角完成评审。

**文件类型处理**：
- **HTML/CSS + DESIGN.md**：可读取精确的间距、颜色、字体值，评审结论引用具体数值
- **纯图片（PNG/JPG/PDF）**：只能做视觉观察，间距和颜色值标注为 `~近似值`，不做精确度量声称
- 优先读取 HTML/CSS 和 Markdown 文件；图片文件作为视觉参照补充

#### 7.5.1 逐屏点评

对每个屏幕/页面评价：

- **评级**：✅✅ 最佳 / ✅ 优 / ➖ 可用但有瑕疵 / ⚠️ 需调整
- **信息层次**：内容组织是否清晰、扫一眼能否抓到重点
- **交互合理性**：操作入口是否明确、操作流是否顺畅
- **视觉细节**：间距、颜色、对比度、一致性
- **亮点**：值得保留的设计决策
- **问题**：需要在实现中修正或调整的点

#### 7.5.2 跨屏一致性检查

检查全部屏幕之间的一致性问题：

| 检查维度 | 说明 |
|----------|------|
| 色彩一致性 | 同一 token 在不同屏幕上是否一致 |
| 导航风格 | 标题位置、返回按钮、tab bar 在各屏幕是否统一 |
| 组件风格 | 按钮、卡片、列表项等在各屏幕是否一致 |
| 间距节奏 | 各屏幕的间距系统是否统一 |
| 图标风格 | 线条粗细、填充风格、尺寸是否一致 |

#### 7.5.3 生成 REVIEW.md

在设计文件目录下创建 `REVIEW.md`，结构如下：

```markdown
# {项目名} Design Review

> 评审日期：{date}
> 目的：记录设计稿已知问题和刻意偏离，供后续开发对照。
> 规则：如果 UI 实现与设计稿不一致，先查本文档。在此列出的 = 已知偏差，不是 bug。

## 整体评价

{一段话总结}

---

## 已知问题（实现时需修正）

### P{N} — {问题标题}
- **位置**：{屏幕名}
- **问题**：{描述}
- **处理**：{实现时如何修正}

---

## 刻意不采纳的设计元素

### D{N} — {元素标题}
- **位置**：{屏幕名}
- **设计稿**：{设计稿中的做法}
- **不采纳原因**：{为什么不用}
- **决策人**：产品评审 / 工程评审

---

## 采纳且需要重点保留的设计亮点

| 编号 | 位置 | 亮点 | 说明 |
|------|------|------|------|
| H{N} | {屏幕名} | {亮点描述} | {为什么必须保留} |
```

**P 条目来源**：Stitch/工具限制导致的问题（如 Web 字体、静态图片替代相机）、跨屏一致性问题、对比度/间距等视觉问题。

**D 条目来源**：设计稿中的做法与 iOS 平台惯例冲突、与 Apple HIG 不协调、增加维护成本但收益不明确。每条必须写明不采纳原因，让后续开发者理解这是刻意决策而非遗漏。

**H 条目来源**：体现产品核心逻辑的 UI 细节、解决真实用户矛盾的交互方案、有辨识度的视觉设计。这些是实现时不能丢失的设计意图。

**空 section 处理**：如果某个 section 没有条目，在 section 标题下写 `无`。不要为了填充而发明问题。

#### 7.5.4 用户确认

**D 条目需逐条确认**：D 条目是 AI 判断的"不采纳"建议，用户可能有不同意见。在 AskUserQuestion 中逐条列出 D 项摘要，让用户明确知道哪些设计元素将被跳过。

**询问用户**（使用 AskUserQuestion）：

> 设计评审完成，REVIEW.md 已创建。
>
> 以下设计元素建议不采纳：
> - D1: {摘要}
> - D2: {摘要}
> - ...
>
> - **确认继续** — 按评审结论进入文档生成
> - **调整评审** — 修改已知问题或不采纳项的判定
> - **重新设计** — 问题过多，回到 CP4 提供新设计

等待用户回复。选择「调整评审」则根据用户反馈修改 REVIEW.md 后重新确认；选择「重新设计」则回到 CP4（不重新生成 Stitch prompts，用户可直接提供新设计文件）。

### CP5: 文档与初始化确认

**展示内容**（控制在 30 行内）：

即将创建以下内容：

| 文件/目录 | 说明 |
|-----------|------|
| `docs/01-discovery/project-brief.md` | 项目概要（含调研、定位、功能规划） |
| `docs/` 目录结构 | 10 个标准子目录 |
| `CLAUDE.md` | AI 助手项目规则（需先运行 /init） |
| `docs/00-AI-CONTEXT.md` | AI 上下文入口文档 |
| `docs/02-architecture/README.md` | 架构文档骨架 |
| `docs/05-features/README.md` | 功能文档模板 |
| `[项目名]/DesignSystem/DesignSystem.swift` | Design System 代码 |
| `docs/10-app-store-connect/` | ASC 文档模板（4 个文件） |
| `.github/ISSUE_TEMPLATE/` | GitHub Issue 模板和自定义 labels（如选择初始化） |

**询问用户**（使用 AskUserQuestion）：

> 以上是将要创建的文档和项目结构。
>
> - **确认执行** — 创建全部文件
> - **调整内容** — 修改文件列表或内容后执行
> - **仅创建 project-brief** — 只创建项目概要文档，跳过项目初始化

等待用户回复。选择「仅创建 project-brief」则跳过步骤 9（初始化项目结构），直接进入步骤 10（下一步）。

### 8. 输出文档

将分析结果写入项目文档：

**文件路径**：`docs/01-discovery/project-brief.md`

Read `references/doc-templates.md` 的「project-brief.md 模板」段，按模板结构创建，根据步骤 1-6 的分析结果填充内容。

### 9. 初始化项目结构（iOS/Swift 项目）

**仅适用于 iOS/Swift 项目**。其他类型项目跳过此步。

模板内容在 references/ 目录中，按需加载。

#### 9.1 创建 docs 目录结构

Read `references/project-init-templates.md` 的「docs 目录结构」段，按模板创建 10 个标准子目录。

#### 9.2 创建 CLAUDE.md

**步骤 A**：提示用户运行 `/init` 生成基础 CLAUDE.md，等待完成。

**步骤 B**：Read `references/project-init-templates.md` 的「CLAUDE.md 追加模板」段，在 /init 生成的 CLAUDE.md 末尾追加项目特定内容（不替换 /init 生成的部分）。根据项目实际信息填充模板中的占位符。

#### 9.2.1 平台 API 规则生成

Read `references/project-init-templates.md` 的「平台 API 规则表」段。根据步骤 6 识别的功能列表查表匹配，将匹配到的「项目规则」写入 CLAUDE.md 的「项目特定约束」`必须：` 部分。

#### 9.2.2 Build Environment 信息采集

**前置条件**：项目根目录存在 `.xcodeproj` 或 `.xcworkspace` 文件。如果都不存在（新建项目尚未创建 Xcode 工程），跳过本步。

**检测方式**：

```bash
# 优先使用 workspace（CocoaPods/SPM workspace）
workspace=$(find . -maxdepth 2 -name "*.xcworkspace" -not -path "*/DerivedData/*" | head -1)
project=$(find . -maxdepth 2 -name "*.xcodeproj" -not -path "*/DerivedData/*" | head -1)
```

如果找到 workspace 或 project：

1. 获取 scheme 列表：`xcodebuild -list -quiet 2>/dev/null`
2. 选择主 scheme（排除含 `Tests`/`UI` 后缀的 scheme；仅一个 scheme 时直接使用；多个且无法判断时用 AskUserQuestion 让用户选择）
3. 采集 build settings：`xcodebuild -showBuildSettings -scheme "{scheme}" -quiet 2>/dev/null`
4. 从输出中提取以下字段：
   - `IPHONEOS_DEPLOYMENT_TARGET` 或 `MACOSX_DEPLOYMENT_TARGET`
   - `PRODUCT_BUNDLE_IDENTIFIER`
   - `DEVELOPMENT_TEAM`
   - `SWIFT_VERSION`
   - `TARGETED_DEVICE_FAMILY`（1=iPhone, 2=iPad, 1,2=Universal）
5. 在 CLAUDE.md 末尾追加：

```markdown
## Build Environment

| Setting | Value |
|---------|-------|
| Deployment Target | iOS {version} / macOS {version} |
| Bundle ID | {identifier} |
| Development Team | {team_id} |
| Swift Version | {version} |
| Device Family | iPhone / iPad / Universal |
| Scheme | {scheme_name} |
```

**错误处理**：
- `xcodebuild` 命令失败（返回非零）：跳过本步，不写入 Build Environment 段。不中断 kickoff 流程。
- 某个字段为空：该行写 `(not set)`。

#### 9.3 创建 docs/00-AI-CONTEXT.md

Read `references/doc-templates.md` 的「docs/00-AI-CONTEXT.md 模板」段，按模板创建，根据步骤 1-6 的分析结果填充内容。

#### 9.4 创建 docs/02-architecture/README.md

简要描述：分层、数据流、模块依赖。后续可拆分为多个文件。

#### 9.5 创建 docs/05-features/README.md

Read `references/doc-templates.md` 的「docs/05-features/README.md 模板」段，按模板创建。

#### 9.6 Design System 初始化

Read `references/doc-templates.md` 的「Design System 初始化」段，按指引创建 DesignSystem.swift。如果 CP4 中用户提供了设计文件，优先从设计文件提取 token 值；否则使用默认模板值。

询问用户是否生成完整版 Design System。如果用户确认，直接调用 `Skill("apple-dev:generate-design-system")` 执行，不中断流程。

#### 9.7 不要预建的目录

以下目录按需创建，不预建空目录：`06-prompts/`、`08-guidelines/`

#### 9.8 App Store Connect 文档初始化

Read `references/doc-templates.md` 的「App Store Connect 文档初始化」段，在 `docs/10-app-store-connect/` 下创建 4 个模板文件（privacy-policy、terms-of-use、support-page、market）。

#### 9.9 Notion 同步配置

Read `references/doc-templates.md` 的「Notion 同步配置」段。如果用户计划使用 Notion，按指引创建配置文件。

#### 9.10 CI/CD 配置初始化

询问用户是否配置 CI/CD（Xcode Cloud + GitHub Actions 自动版本管理）。如果选 Yes，提示用户运行 `/setup-ci-cd`。

`/setup-ci-cd` 会：
- 统一所有 target 的版本号
- 启用 Apple Generic versioning
- 创建 GitHub Actions auto-version workflow（conventional commit → semver bump）
- 创建 Xcode Cloud ci_post_clone.sh（自动设置 build number）
- 输出 Xcode Cloud workflow 配置指引

#### 9.11 GitHub Issue 基础设施初始化

询问用户是否初始化 GitHub Issue 跟踪。如果选 No，跳过。

如果选 Yes：

1. Read `references/project-init-templates.md` 的「GitHub Issue Templates」段
2. 提取 owner/repo：`gh repo view --json owner,name -q '.owner.login + "/" + .name'`
3. 创建 `.github/ISSUE_TEMPLATE/bug.md` 和 `feature.md`（按模板内容）
4. 创建自定义 labels：`deferred`、`blocked`
5. 如果 dev-guide 已存在（`docs/06-plans/*-dev-guide.md`），为每个 phase 创建 label（`phase-N`）和 milestone
6. 如果 dev-guide 不存在，跳过 phase labels 和 milestones，提示用户：
   > Phase labels 和 milestones 需要 dev-guide。完成 `/write-dev-guide` 后，手动运行：
   > ```
   > gh label create "phase-1" --color "0E8A16" --description "Phase 1"
   > gh api repos/{owner}/{repo}/milestones -f title="Phase 1: {name}" -f description="{scope}"
   > ```
   > （具体命令见 `references/project-init-templates.md`「Milestones」段）

### 10. 下一步

项目初始化完成。根据项目复杂度选择：

- **需要深度设计探索** → `/brainstorm` → `/write-dev-guide` → `/run-phase`
- **设计已明确，直接开始** → `/write-dev-guide` → `/run-phase`
- **简单项目，直接做** → `/plan`

## 原则

1. **不编造**：所有竞品信息来自真实搜索，附链接
2. **客观分析**：不美化用户想法，指出真实风险
3. **可操作**：MVP 规划要具体，不泛泛而谈
4. **敢说不**：如果方向不可行，直接说
