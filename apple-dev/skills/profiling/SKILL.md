---
name: profiling
description: "Use when the user asks about performance profiling, os_signpost instrumentation, MetricKit integration, Instruments workflow, performance anti-patterns, hitch detection, or the user says 'profiling', 'performance analysis', '性能分析'. Provides interactive guidance on iOS/macOS profiling based on the reference guide."
compatibility: Requires macOS and Xcode
---

# Profiling Skill

Provide interactive guidance on iOS/macOS performance profiling based on `references/profiling-guide.md`.

## When to Use

- User asks about performance profiling or instrumentation
- Setting up os_signpost / OSSignposter in code
- Integrating MetricKit for production monitoring
- Writing XCTest performance tests (measure, XCTMetric)
- Scanning code for performance anti-patterns
- Using Instruments or xctrace CLI
- Connecting signpost → XCTest → MetricKit workflow

## Process

### 1. Identify Profiling Scenario

Determine what the user needs:
- Signpost instrumentation
- MetricKit setup
- Performance test writing
- Anti-pattern detection
- Instruments guidance
- End-to-end profiling workflow

### 2. Read Relevant Section of Reference Guide

Grep for section markers:

```
Grep("<!-- section:", "references/profiling-guide.md")
```

Read only the section matching the user's scenario:

```
Read("references/profiling-guide.md", offset=<marker_line + 1>, limit=<lines_to_next_marker>)
```

Section-to-need mapping:
- os_signpost / OSSignposter → section "1. OSSignposter 插桩"
- MetricKit / production metrics → section "2. MetricKit 集成"
- XCTest performance / measure / XCTMetric / hitch → section "3. XCTest 性能测试"
- Anti-pattern / performance issue scanning → section "4. 性能反模式扫描"
- Instruments / Time Profiler / xctrace → section "5. Instruments 工作流"
- Full workflow / integration → section "6. Signpost + MetricKit + XCTest 联动"

### 3. Provide Contextual Guidance

Based on user's specific scenario:

**For Signpost Instrumentation**:
- Show OSSignposter creation patterns from guide Section 1
- Demonstrate beginInterval/endInterval pairing
- Explain SignpostID for concurrent intervals
- Show animation-specific beginAnimationInterval

**For MetricKit Integration**:
- Show MXMetricManagerSubscriber implementation from guide Section 2
- Explain 24h metric report cycle vs immediate diagnostics (iOS 15+)
- Demonstrate MXSignpostMetric for custom metrics
- Show payload JSON export for backend reporting

**For Performance Tests**:
- Show measure {} and XCTMetric family from guide Section 3
- Demonstrate XCTOSSignpostMetric with custom signpost names
- Show built-in metrics (navigationTransitionMetric, scrollingAndDecelerationMetric)
- Explain XCTHitchMetric (iOS 26+) for hitch detection
- Guide baseline setup for CI regression detection

**For Anti-Pattern Scanning**:
- Read user's code and grep for patterns from guide Section 4
- Check for: main thread blocking, large body, DateFormatter in body, UIImage without downsample, N+1 fetch
- Provide fix suggestions with code examples

**For Instruments Workflow**:
- Show template selection guide from guide Section 5
- Demonstrate xctrace CLI commands
- Explain how to connect signposts to Instruments timeline

**For End-to-End Workflow**:
- Show three-stage cycle from guide Section 6
- Dev: signpost → Test: XCTOSSignpostMetric → Prod: MetricKit
- Provide complete example adapted to user's code

### 4. Generate Code

For signpost/MetricKit/XCTest scenarios, generate code adapted to the user's existing subsystem/category naming and project structure.

For anti-pattern scanning, scan the user's code and output findings with severity and fix suggestions.

### 5. Common Profiling Mistakes

- Using `os_signpost` without a subsystem/category (loses filtering ability)
- Forgetting to end a signpost interval (unpaired begin/end)
- Using `.exclusive` SignpostID when multiple intervals can overlap
- Not setting performance test baselines (no regression detection)
- Only profiling in Debug build (optimizer changes behavior significantly)

## Success Criteria

- User can instrument their code with signposts
- Performance tests detect regressions via CI
- Anti-patterns are identified with actionable fixes
- MetricKit is properly integrated for production monitoring

## 串联提示

- `/testing-guide` — Unit Test、Mock/DI、TDD 基础
- `/xc-ui-test` — XCUITest 高级用法（多屏幕旅程、网络 stub、snapshot）
