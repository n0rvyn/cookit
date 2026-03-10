# execution-review Eval

## Trigger Tests
<!-- Prompts that SHOULD trigger this skill -->
- "Review the implementation against the plan"
- "Check if I completed everything in the plan"
- "审查计划执行情况"
- "Did I miss anything after executing the plan?"
- "Execution review for this phase"

## Negative Trigger Tests
<!-- Prompts that should NOT trigger this skill -->
- "Write a plan"
- "Design review"
- "Fix this bug"

## Output Assertions
<!-- What must be true in the skill's output -->
- [ ] Output searches for known issues from knowledge base before invoking agent
- [ ] Output dispatches dev-workflow:implementation-reviewer agent
- [ ] Output performs Swift-specific code scan: localization (String(localized:)), concurrency (@MainActor), abstraction (protocols), error handling
- [ ] Output verifies doc updates: file-structure.md, changelog, ADRs
- [ ] Output combines agent summary with Swift-specific findings
- [ ] Output presents plan vs code gaps with file:line references

## Redundancy Risk
Baseline comparison: Base model can compare plan vs code manually but lacks systematic Swift-specific checks and known issue integration
Last tested model: Opus 4.6
Last tested date: 2026-03-08
Verdict: essential
