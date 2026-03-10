# ui-review Eval

## Trigger Tests
<!-- Prompts that SHOULD trigger this skill -->
- "Review my UI code for compliance"
- "Check accessibility and state completeness"
- "审查一下我的 UI 代码"
- "UI review before I submit this PR"
- "Check if my UI follows platform conventions"

## Negative Trigger Tests
<!-- Prompts that should NOT trigger this skill -->
- "Design review for visual quality"
- "Feature review for user journey"
- "Fix this bug"

## Output Assertions
<!-- What must be true in the skill's output -->
- [ ] Output loads apple-ui-checklist.md and ui-design-principles.md references
- [ ] Output checks spacing uses 8pt multiples and Design System tokens
- [ ] Output validates semantic color usage over hardcoded colors
- [ ] Output verifies dynamic type support and monospaced digits for numbers
- [ ] Output checks accessibility labels, hints, and trait groups
- [ ] Output validates all state coverage: loading, empty, error, success
- [ ] Output verifies interaction guards: disabled states, haptic feedback, undo support
- [ ] Output complements design-review (visual quality) and feature-review (user journey)

## Redundancy Risk
Baseline comparison: Base model can review UI code but lacks systematic checklist-based compliance verification
Last tested model: Opus 4.6
Last tested date: 2026-03-08
Verdict: essential
