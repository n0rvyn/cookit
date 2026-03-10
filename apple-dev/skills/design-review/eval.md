# design-review Eval

## Trigger Tests
<!-- Prompts that SHOULD trigger this skill -->
- "Review the visual design of this page"
- "Check the visual hierarchy and color strategy"
- "审查一下这个页面的设计感"
- "Does this UI look polished?"
- "Review design before I optimize visuals"

## Negative Trigger Tests
<!-- Prompts that should NOT trigger this skill -->
- "Review my code for bugs"
- "Check if this matches the design doc"
- "Write a plan for this feature"

## Output Assertions
<!-- What must be true in the skill's output -->
- [ ] Output loads ui-design-principles.md and apple-ui-checklist.md references
- [ ] Output checks visual hierarchy with 3-level font weight/size gradient
- [ ] Output verifies color strategy uses semantic colors not hardcoded values
- [ ] Output checks spacing rhythm follows consistent scale
- [ ] Output provides per-page design quality findings with specific code references
- [ ] Output complements ui-review (code compliance) rather than duplicating

## Redundancy Risk
Baseline comparison: Base model can give subjective design feedback but lacks systematic rule-based design quality checks
Last tested model: Opus 4.6
Last tested date: 2026-03-08
Verdict: essential
