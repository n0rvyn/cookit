# verify-plan Eval

## Trigger Tests
- "Verify this plan before I start coding"
- "Check the plan for issues"
- "review plan 检查计划"

## Negative Trigger Tests
- "Write a new plan for this feature"
- "Execute the plan now"

## Output Assertions
- [ ] Output includes verdict: Approved | Must-revise
- [ ] Output includes falsifiable error candidates tested
- [ ] Must-revise items include specific revision instructions
- [ ] Previously resolved decisions (Chosen: in plan) are not re-asked

## Redundancy Risk
Baseline comparison: Base model can review plans but lacks Verification-First methodology with falsifiable assertions
Last tested model: Opus 4.6
Last tested date: 2026-03-08
Verdict: essential
