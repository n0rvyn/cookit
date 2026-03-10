# plugin-review Eval

## Trigger Tests
- "review skill"
- "audit plugin"
- "Check my agent for logic bugs"

## Negative Trigger Tests
- "Review my code"
- "Design review"

## Output Assertions
- [ ] Output covers 9 dimensions regardless of strategy (structural, reference integrity, workflow logic, execution feasibility, trigger/routing, edge cases, spec compliance, metadata & docs, trigger quality review)
- [ ] If plugin-dev available (Strategy A): dispatches plugin-dev:plugin-validator + plugin-dev:skill-reviewer + skill-audit:plugin-reviewer in parallel
- [ ] If plugin-dev not available (Strategy B): dispatches skill-audit:plugin-reviewer with supporting files (structural-validation.md, trigger-baseline.md)
- [ ] Report format is identical between Strategy A and Strategy B
- [ ] Output is from AI executor perspective (not end-user)
- [ ] Output flags trigger mechanism issues and execution feasibility problems

## Redundancy Risk
Baseline comparison: Base model can review code but lacks plugin-specific review framework from executor perspective
Last tested model: Opus 4.6
Last tested date: 2026-03-08
Verdict: essential
