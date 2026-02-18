---
name: ios-swift-context
description: "Use when working on Swift, iOS, macOS, iPadOS, SwiftUI, or SwiftData code, editing .swift files, planning Apple platform features, fixing Swift bugs, or reviewing Swift code. Provides essential development rules including build cycle, constraints, concurrency, UI rules, and plan execution principles."
user-invocable: false
---

Read and follow the plugin's `references/ios-swift-rules.md`. It contains mandatory rules for Swift/Apple platform development:

- Build-Check-Fix cycle and timing
- Hard constraints (no hardcoded UI values, no main-thread blocking, no direct .pbxproj editing)
- Swift 6 concurrency principles (@Model, @MainActor, Sendable)
- .foregroundColor migration strategy
- iOS UI rules (layered enforcement)
- Plan-phase architecture review triggers
- Plan self-check (M&M test)
- Plan execution principles (ambiguity check, interruption handling)
- Error fix, code deletion, and dead code disposal principles
