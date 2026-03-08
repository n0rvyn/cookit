# use-worktree Eval

## Trigger Tests
- "use worktree"
- "Start feature work in isolation"
- "Create a worktree for this branch"

## Negative Trigger Tests
- "Commit this change"
- "Switch branches"

## Output Assertions
- [ ] Output checks for existing worktree directories first
- [ ] Output creates worktree in .worktrees/ or worktrees/
- [ ] Output explains cleanup behavior on session exit

## Redundancy Risk
Baseline comparison: Base model can run git worktree commands but lacks structured directory selection and cleanup workflow
Last tested model: Opus 4.6
Last tested date: 2026-03-08
Verdict: likely-redundant
