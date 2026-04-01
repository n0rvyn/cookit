# fix-bug Eval

## Trigger Tests
- "I'm getting this error: [stack trace]"
- "The app crashes when I tap save, here's a screenshot"
- "Build fails with 'ambiguous reference' after my changes"

## Negative Trigger Tests
- "Add a new feature to export data"
- "Refactor this code to be cleaner"

## Output Assertions
- [ ] Step 7 gate: simple fix enters native plan mode (EnterPlanMode), complex fix invokes /write-plan
- [ ] No assertion confirmation gate blocks diagnosis (Step 3 flows directly to Step 4)
- [ ] Output includes Step 10 tradeoff report for the proposed fix
- [ ] Root cause includes code evidence (file:line references)

## Redundancy Risk
Baseline comparison: Base model can diagnose errors but lacks systematic value-domain tracing and parallel path detection methodology
Last tested model: Opus 4.6
Last tested date: 2026-03-08
Verdict: essential
