---
name: apple-swift-context
description: "Use when working on Swift, iOS, macOS, iPadOS, SwiftUI, or SwiftData code, editing .swift files, planning Apple platform features, fixing Swift bugs, or reviewing Swift code. Provides essential development rules including build cycle, constraints, concurrency, UI rules, and plan execution principles."
compatibility: Requires macOS and Xcode
user-invocable: false
---

## Purpose

Load the relevant sections of `references/apple-swift-rules.md` based on the current task. Do not read the entire file unless the task requires rules from every section.

## Section-Targeted Reading Process

### Step 1: Identify relevant sections

Grep for section markers in the file:

```
Grep("<!-- section:", "references/apple-swift-rules.md")
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
| Working with iOS 18 APIs (@Entry, Tab, MeshGradient, @Previewable) | swift-api-changes-ios18 |
| Working with iOS 26 APIs (glassEffect, FoundationModels) | swift-api-changes-ios26 |
| Seeing deprecation warnings in Xcode | swift-api-changes-ios18 (migration), validate-design-tokens |
| Using TabView | swift-api-changes-ios18 → TabView Architecture |
| Adding LLM/AI features | swift-api-changes-ios26 → Foundation Models |
| macOS window, WindowGroup, MenuBarExtra, Settings scene | macOS Window Management |
| macOS menu, commands, CommandMenu, toolbar customization | macOS Menu & Toolbar |
| Keyboard shortcut on macOS, keyboardShortcut | macOS Keyboard Shortcuts |
| NSViewRepresentable, macOS SwiftUI, pasteboard, onHover | macOS SwiftUI Patterns |
| macOS distribution, notarization, Developer ID | macos-distribution-guide |
| macOS sandbox, entitlements, file access permissions | macos-distribution-guide → Sandboxing & Entitlements |
| macOS auto-update, Sparkle | macos-distribution-guide → Auto-Update |

### Step 2.5: Platform-aware section filtering

Section markers may include a `platform:` attribute (e.g., `platform: iOS`, `platform: macOS`). Sections without a `platform:` tag apply to all platforms (shared).

The target platform is determined by which rows matched in Step 2:

- If Step 2 matched any **macOS keyword row** (rows 50-56: WindowGroup, MenuBarExtra, CommandMenu, keyboardShortcut, NSViewRepresentable, notarization, Sparkle) → the task involves macOS. When grepping `apple-swift-rules.md`, also include sections with `platform: macOS`.
- If Step 2 matched any **iOS keyword row** (rows 45-48: iOS 18/26 APIs, TabView, glassEffect) → the task involves iOS. When grepping reference files, also include sections with `platform: iOS`.
- If Step 2 matched **only shared rows** (rows 33-44: build cycle, concurrency, plan rules, bug fix) → load only sections without a `platform:` tag.
- Both platforms can be active simultaneously (e.g., a multiplatform project).

### Step 3: Read only the matched sections

For each matched section in `apple-swift-rules.md`, use the line number from the Grep result as
`offset` and read until the next section marker or approximately 60 lines (whichever comes first):

```
Read("references/apple-swift-rules.md", offset=<section_line>, limit=<next_section_line - section_line>)
```

For `swift-api-changes-*` and `macos-distribution-guide.md` files: search for the specific section
keyword rather than reading the entire file. Example:

```
Grep("glassEffect", "references/swift-api-changes-ios26.md")
→ Read("references/swift-api-changes-ios26.md", offset=<section_line>, limit=<lines_to_next_section>)

Grep("notarytool", "references/macos-distribution-guide.md")
→ Read("references/macos-distribution-guide.md", offset=<section_line>, limit=<lines_to_next_section>)
```

If the task is not clearly scoped (e.g., the task description is very broad or covers the whole codebase), read `通用约束` and `Swift 6 并发原则` at minimum — these two sections apply to all Swift work.

### Step 4: Apply the loaded rules

Follow the rules from the loaded sections strictly. Do not infer rules from memory about sections that were not read.
