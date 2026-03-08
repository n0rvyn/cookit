# plugin-review Eval

## Trigger Tests
- "review skill"
- "audit plugin"
- "Check my agent for logic bugs"

## Negative Trigger Tests
- "Review my code"
- "Design review"

## Output Assertions
- [ ] Output covers 7 dimensions: structural, reference integrity, workflow logic, execution feasibility, trigger/routing, edge cases, spec compliance
- [ ] Output is from AI executor perspective (not end-user)
- [ ] Output flags trigger mechanism issues and execution feasibility problems

## Redundancy Risk
Baseline comparison: Base model can review code but lacks plugin-specific review framework from executor perspective
Last tested model: Opus 4.6
Last tested date: 2026-03-08
Verdict: essential
