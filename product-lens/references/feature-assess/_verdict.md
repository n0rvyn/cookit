# Verdict Computation

> Used by the skill orchestrator to compute the final GO / DEFER / KILL verdict. Not needed by individual dimension evaluators.

## Verdict Rules

### KILL

Triggered if ANY of:
- Any dimension has signal=Negative AND confidence=High
- Two or more dimensions have signal=Negative (regardless of confidence)

### GO

Triggered if ALL of:
- No dimension has signal=Negative with confidence=High
- At most one dimension has signal=Negative (with confidence Medium or Low)
- At least two dimensions have signal=Positive

### DEFER

Everything else. Additionally:
- List all conditions that, if resolved, could change the verdict
- Identify which signals have Low confidence (most likely to flip with more information)

## Conditional Follow-up

| Verdict | Follow-up Module |
|---------|-----------------|
| GO | Integration Map -- code-level integration points, reusable infrastructure, modification scope |
| DEFER | Alternative Directions -- lower-cost variants, complementary features, signal clarification paths |
| KILL | Alternative Directions -- same module as DEFER |

## Verdict Override

If the user explicitly requests a GO follow-up on a DEFER/KILL verdict (or vice versa), honor the request. The verdict is advisory.
