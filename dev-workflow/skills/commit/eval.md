# commit Eval

## Trigger Tests
- "commit"
- "Save my progress"
- "Commit the changes"

## Negative Trigger Tests
- "Push to remote"
- "Create a pull request"

## Output Assertions
- [ ] Output analyzes uncommitted changes with git status/diff
- [ ] Output groups changes logically by concern
- [ ] Output uses conventional commit format (type(scope): description)
- [ ] git status clean after all commits completed

## Redundancy Risk
Baseline comparison: Base model can commit but lacks conventional commit format enforcement and logical grouping methodology
Last tested model: haiku 4.5
Last tested date: 2026-03-08
Verdict: monitor
