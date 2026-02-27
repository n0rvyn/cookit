---
name: project-kickoff
description: 新项目启动开题流程，完成需求澄清、范围收敛和执行建议。
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
> - **调整** — 修改概念或切入点后重新评估
> - **放弃** — 终止开题流程

等待用户回复。选择「调整」则回到步骤 1 重新澄清需求；选择「放弃」则终止流程。

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

**询问用户**（使用 AskUserQuestion）：

> 以上是产品定位、功能范围、技术选型、AI 集成评估和平台 API 验证结果。
>
> - **确认范围** — 按此范围进入设计生成
> - **调整功能** — 增删功能或调整优先级
> - **调整技术选型** — 修改技术方案

等待用户回复。选择「调整功能」或「调整技术选型」则修改后重新展示本检查点。

### 7. 设计生成

基于步骤 1-6 的分析结果，使用 Stitch 生成 UI 设计稿。

1. 调用 `/generate-stitch-prompts all`，为项目生成主界面及各屏幕的 Stitch prompt
2. 从 skill 输出中提取：屏幕清单（名称 + 功能一句话）、每个屏幕的核心 UI 区域列表
3. 将提取结果填入 CP4 展示模板

### CP4: 视觉方向确认

**展示内容**（控制在 40 行内）：

**屏幕清单**：

| 屏幕 | 功能 | 核心 UI 区域 |
|------|------|-------------|
| {screen1} | {function} | {zones} |
| {screen2} | {function} | {zones} |
| ... | ... | ... |

**Stitch prompt 数量**：主 prompt 1 条 + follow-up {N} 条

**询问用户**（使用 AskUserQuestion）：

> Stitch prompt 已生成。选择后续方式：
>
> - **用 Stitch 生成设计** — 将 prompt 粘贴到 Stitch 生成 UI，完成后提供设计文件路径继续流程
> - **已有设计稿** — 提供设计文件目录路径
> - **跳过设计** — 不使用设计稿，后续使用默认 Design System 值

等待用户回复。选择「用 Stitch 生成设计」则暂停流程，用户在 Stitch 中完成设计后回来提供文件路径；选择「已有设计稿」则记录路径；选择「跳过设计」则标记无设计输入。设计文件路径将在步骤 9.6 中用于提取 Design Token。

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

#### 9.3 创建 docs/00-AI-CONTEXT.md

Read `references/doc-templates.md` 的「docs/00-AI-CONTEXT.md 模板」段，按模板创建，根据步骤 1-6 的分析结果填充内容。

#### 9.4 创建 docs/02-architecture/README.md

简要描述：分层、数据流、模块依赖。后续可拆分为多个文件。

#### 9.5 创建 docs/05-features/README.md

Read `references/doc-templates.md` 的「docs/05-features/README.md 模板」段，按模板创建。

#### 9.6 Design System 初始化

Read `references/doc-templates.md` 的「Design System 初始化」段，按指引创建 DesignSystem.swift。如果 CP4 中用户提供了设计文件，优先从设计文件提取 token 值；否则使用默认模板值。

询问用户是否使用 `generate-design-system` skill 生成完整版。

#### 9.7 不要预建的目录

以下目录按需创建，不预建空目录：`06-prompts/`、`08-guidelines/`

#### 9.8 App Store Connect 文档初始化

Read `references/doc-templates.md` 的「App Store Connect 文档初始化」段，在 `docs/10-app-store-connect/` 下创建 4 个模板文件（privacy-policy、terms-of-use、support-page、market）。

#### 9.9 Notion 同步配置

Read `references/doc-templates.md` 的「Notion 同步配置」段。如果用户计划使用 Notion，按指引创建配置文件。

#### 9.10 CI/CD 配置初始化

询问用户是否配置 CI/CD。如果选 Yes，调用 `setup-ci-cd` skill。

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
