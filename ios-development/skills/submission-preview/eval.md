# submission-preview Eval

## Trigger Tests
- "submission preview"
- "Will this pass App Store review?"
- "pre-submit check"

## Negative Trigger Tests
- "Update ASC docs"
- "Review my plugin"

## Output Assertions
- [ ] Output checks app code against App Review Guidelines sections 1-5
- [ ] Output distinguishes from appstoreconnect-review (store materials vs code)
- [ ] Output flags common rejection reasons (permissions, private APIs, crashes)

## Redundancy Risk
Baseline comparison: Base model knows App Store guidelines but lacks systematic checklist approach
Last tested model: Opus 4.6
Last tested date: 2026-03-08
Verdict: essential
