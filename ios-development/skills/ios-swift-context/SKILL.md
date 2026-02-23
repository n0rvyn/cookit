---
name: ios-swift-context
description: "Use when working on Swift, iOS, macOS, iPadOS, SwiftUI, or SwiftData code, editing .swift files, planning Apple platform features, fixing Swift bugs, or reviewing Swift code. Provides essential development rules including build cycle, constraints, concurrency, UI rules, and plan execution principles."
user-invocable: false
---

## Purpose

Load the relevant sections of `references/ios-swift-rules.md` based on the current task. Do not read the entire file unless the task requires rules from every section.

## Section-Targeted Reading Process

### Step 1: Identify relevant sections

Grep for section markers in the file:

```
Grep("<!-- section:", "references/ios-swift-rules.md")
```

This returns lines like:
```
3:<!-- section: Build-Check-Fix Cycle keywords: build, xcodebuild, check, fix -->
```

### Step 2: Match sections to current task

From the current task description, identify which keyword sets are relevant:

| Task involves | Read section(s) |
|---|---|
| Running builds, checking errors | Build-Check-Fix Cycle |
| Any Swift code (always apply) | 通用约束 |
| async/await, actors, @Model, Sendable | Swift 6 并发原则 |
| Existing foregroundColor calls | .foregroundColor 迁移策略 |
| Creating new UI, layout changes | iOS UI 规则（分层生效） |
| New triggers, data paths, schedulers | 计划阶段架构审查（条件触发） |
| Plan with ≥3 file changes | 计划自检（M&M 测试） |
| Writing a plan | 计划编写原则 |
| Starting execution of a plan | 计划执行原则 |
| Interruption during execution | 计划执行中断处理（必须遵守） |
| User reported a behavior bug | 错误修复原则 |
| Deleting code or variables | 删除代码原则, 死代码/未接入代码处置原则 |

### Step 3: Read only the matched sections

For each matched section, use the line number from the Grep result as `offset` and read until the next section marker or approximately 60 lines (whichever comes first):

```
Read("references/ios-swift-rules.md", offset=<section_line>, limit=<next_section_line - section_line>)
```

If the task is not clearly scoped (e.g., the task description is very broad or covers the whole codebase), read `通用约束` and `Swift 6 并发原则` at minimum — these two sections apply to all Swift work.

### Step 4: Apply the loaded rules

Follow the rules from the loaded sections strictly. Do not infer rules from memory about sections that were not read.
