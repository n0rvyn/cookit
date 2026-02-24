---
name: swiftdata-patterns
description: Provide SwiftData best practices and patterns guidance
---

# SwiftData Patterns Skill

Provide interactive guidance on SwiftData best practices based on `references/swiftdata-guide.md`.

## When to Use

- User asks about SwiftData usage
- Designing data models
- Questions about relationships, queries, or migrations
- Concurrency issues with SwiftData

## Process

### 1. Identify User's Need

Determine what aspect of SwiftData the user needs help with:
- @Model definition
- Relationships (one-to-many, many-to-many)
- Querying with @Query
- Data migration
- Concurrency safety

### 2. Read Relevant Section of Reference Guide

Grep for section markers:

```
Grep("<!-- section:", "references/swiftdata-guide.md")
```

Match the user's need to the section keywords, then read only that section:

```
Read("references/swiftdata-guide.md", offset=<marker_line + 1>, limit=<lines_to_next_marker>)
```

Section-to-need mapping:
- @Model definition → section "1. @Model 定义"
- Relationships → section "2. 关系定义"
- Querying → section "3. 查询"
- Migration → section "4. 数据迁移"
- Concurrency → section "5. 并发安全"
- Performance → section "6. 性能优化"
- Testing → section "7. 测试"

### 3. Provide Contextual Guidance

Based on user's specific scenario:

**For @Model definition**:
- Show basic pattern from guide Section 1
- Discuss optional vs required properties
- Explain @Transient and @Attribute modifiers

**For Relationships**:
- Show relationship patterns from guide Section 2
- Explain delete rules (.cascade, .nullify, .deny)
- Demonstrate inverse relationships

**For Querying**:
- Show @Query patterns from guide Section 3
- Demonstrate predicates for filtering
- Show sort descriptors
- Explain dynamic query initialization

**For Migration**:
- Explain versioned schemas from guide Section 4
- Show migration plan setup
- Discuss lightweight vs custom migrations

**For Concurrency**:
- Explain @MainActor usage from guide Section 5
- Show ModelContext thread safety
- Demonstrate background task patterns

### 4. Provide Code Examples

Extract relevant code examples from the guide and adapt to user's context.

### 5. Highlight Common Pitfalls

- Cross-thread ModelContext usage
- **Misunderstanding autosave behavior**
  - SwiftData autosaves automatically (triggered by run loop idle, app background, etc.)
  - Explicit `modelContext.save()` IS needed for:
    - Immediately before app enters background (AppDelegate/SceneDelegate lifecycle)
    - After batch imports where you need the data visible immediately
    - In tests that need synchronous state verification
  - Do NOT call save() after every individual insert — let autosave handle it
  - iOS 18+ (minimum deployment target): autosave behavior is stable and reliable
- Overusing relationships (performance)
- Not handling migration for schema changes

## Success Criteria

- User understands the SwiftData pattern for their scenario
- Code example is directly applicable
- Common mistakes are avoided
