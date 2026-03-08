# parallel-agents Eval

## Trigger Tests
- "I have 3 independent issues to fix"
- "Multiple unrelated test failures"
- "Run these tasks in parallel"

## Negative Trigger Tests
- "Do this step by step"
- "Investigate this single issue"

## Output Assertions
- [ ] Output verifies tasks are independent (no shared state)
- [ ] Output dispatches multiple agents in single message
- [ ] Output consolidates results from all agents

## Redundancy Risk
Baseline comparison: Base model understands parallelism but lacks explicit agent dispatch mechanism for concurrent execution
Last tested model: Opus 4.6
Last tested date: 2026-03-08
Verdict: likely-redundant
