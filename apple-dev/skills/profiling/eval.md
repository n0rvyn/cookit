# profiling Eval

## Trigger Tests
<!-- Prompts that SHOULD trigger this skill -->
- "How do I add os_signpost to my networking code?"
- "Set up MetricKit to collect crash diagnostics"
- "Write a performance test for my app launch time"
- "Scan my code for performance anti-patterns"
- "How to use Instruments Time Profiler?"
- "性能分析怎么做"
- "Help me profile my SwiftUI scroll performance"
- "What's the best way to detect UI hitches in tests?"
- "Set up end-to-end performance monitoring from dev to production"
- "How do I use xctrace from the command line?"

## Negative Trigger Tests
<!-- Prompts that should NOT trigger this skill -->
- "Write a unit test for my ViewModel" (→ testing-guide)
- "Set up UI tests with Page Object pattern" (→ xc-ui-test)
- "How do I mock a network service?" (→ testing-guide)
- "Review my app for App Store submission" (→ submission-preview)
- "Optimize my SwiftData query" (→ swiftdata-patterns)

## Output Assertions
<!-- What must be true in the skill's output -->
- [ ] Output identifies the profiling scenario (signpost / MetricKit / perf test / anti-pattern / Instruments / workflow)
- [ ] Output greps section markers from references/profiling-guide.md
- [ ] Output reads only the relevant section based on scenario mapping
- [ ] Code examples use correct OSSignposter API (not legacy os_signpost functions)
- [ ] MetricKit examples include both didReceive metrics and diagnostics callbacks
- [ ] XCTest performance examples show XCTMetric protocol usage
- [ ] Anti-pattern scanning references user's actual code, not generic examples
- [ ] Output provides interactive guidance rather than static documentation dump

## Redundancy Risk
Baseline comparison: Base model knows os_signpost basics but lacks OSSignposter struct API details, XCTHitchMetric (iOS 26), and the signpost→XCTest→MetricKit integration pattern
Last tested model: claude-sonnet-4-6
Last tested date: 2026-03-16
Verdict: essential
