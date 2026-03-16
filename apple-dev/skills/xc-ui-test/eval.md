# xc-ui-test Eval

## Trigger Tests
<!-- Prompts that SHOULD trigger this skill -->
- "How do I write E2E tests for my login-to-checkout flow?"
- "Set up network stubbing for my UI tests"
- "How to do snapshot testing in Swift?"
- "Help me set up visual regression testing"
- "Run accessibility audit in my UI tests"
- "How to run UI tests in parallel on CI?"
- "Set up test data factories for my XCUITests"
- "How do I test deep links in my app?"
- "无障碍测试怎么做"
- "How to isolate app state between UI tests?"

## Negative Trigger Tests
<!-- Prompts that should NOT trigger this skill -->
- "Write a unit test for my ViewModel" (→ testing-guide)
- "How do I mock a network service for unit tests?" (→ testing-guide)
- "Profile my app's scroll performance" (→ profiling)
- "Add os_signpost to my code" (→ profiling)
- "Set up basic Page Object pattern for UI tests" (→ testing-guide, Section 2)

## Output Assertions
<!-- What must be true in the skill's output -->
- [ ] Output identifies the XCUITest scenario (flow / network stub / data factory / snapshot / a11y / CI)
- [ ] Output greps section markers from references/xc-ui-test-guide.md
- [ ] Output reads only the relevant section based on scenario mapping
- [ ] Flow test examples use Flow Object pattern (not raw XCUIElement chains)
- [ ] Network stub examples use URLProtocol (not third-party mock servers)
- [ ] Snapshot examples reference swift-snapshot-testing library
- [ ] Accessibility examples use performAccessibilityAudit API
- [ ] CI examples include xcodebuild and xcresulttool commands
- [ ] Output provides interactive guidance rather than static documentation dump

## Redundancy Risk
Baseline comparison: Base model knows XCUITest basics but lacks Flow Object pattern, URLProtocol stubbing details, performAccessibilityAudit API, xcresulttool usage, and multi-matrix snapshot testing patterns
Last tested model: claude-sonnet-4-6
Last tested date: 2026-03-16
Verdict: essential
