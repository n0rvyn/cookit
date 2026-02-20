---
name: teardown
description: "Use when the user wants a deep dive into a specific evaluation dimension for a product. Example: teardown moat, teardown journey. Goes deeper than the standard evaluation on one dimension."
user-invocable: false
---

## Process

### Step 1: Parse Dimension

Accept the dimension argument in both Chinese and English. Mapping:

| English | Chinese | Dimension |
|---------|---------|-----------|
| demand | 需求真伪 | Demand Authenticity |
| journey | 逻辑闭环 | Journey Completeness |
| market | 市场空间 | Market Space |
| business | 商业可行 | Business Viability |
| moat | 护城河 | Moat |
| execution | 执行质量 | Execution Quality |

Also accept partial matches and common aliases:
- `need` / `needs` / `demand` / `jtbd` → Demand Authenticity
- `loop` / `journey` / `flow` / `ux` → Journey Completeness
- `market` / `space` / `competition` → Market Space
- `business` / `revenue` / `money` / `viability` → Business Viability
- `moat` / `defensibility` / `sherlock` → Moat
- `execution` / `quality` / `tech` / `debt` → Execution Quality

If the argument doesn't match any dimension, list the available options and ask the user to choose.

### Step 2: Determine Target

Same logic as evaluate skill:
- Path argument → local project
- Name/URL argument → external app
- No argument → current working directory

### Step 3: Detect Platform, Resolve Paths, and Load Framework

1. Detect platform (iOS / Web / etc.)
2. Locate reference files by searching for `**/product-lens/references/frameworks.md`. Resolve absolute paths.
3. If iOS: load the specified dimension from both `references/frameworks.md` (universal questions) and `references/ios-overlay.md` (platform-specific replacement questions)
4. Otherwise: load the specified dimension from `references/frameworks.md` (both universal and default platform-specific)

### Step 4: Gather Market Context (if applicable)

For dimensions that benefit from market data (Market Space, Business Viability, Moat):
- Dispatch `market-scanner` agent with product info
- Use the market data to enrich the analysis

For other dimensions (Demand Authenticity, Journey Completeness, Execution Quality):
- Skip market-scanner; these are primarily code/product analysis

### Step 5: Deep Evaluation

Dispatch `product-evaluator` agent with:
- Product info
- Evaluation type (local/external)
- Project root (if local)
- Frameworks reference path (absolute, from Step 3)
- Platform overlay path (absolute, from Step 3; if iOS)
- Market data (if gathered in Step 4)
- **Scope: single dimension name only**

The evaluator will go deeper on this single dimension than in a full evaluation because it can dedicate full attention to it.

### Step 6: Present Results

Output a focused deep-dive report:

```markdown
# Teardown: [Dimension Name] — [Product Name]

## Overall Score: [★★★☆☆]

[One-paragraph summary of this dimension's assessment]

## Sub-Question Analysis

### [Sub-question 1]
[Detailed analysis with evidence]
**Sub-score:** [★★★★☆]

### [Sub-question 2]
[Detailed analysis with evidence]
**Sub-score:** [★★★☆☆]

[... repeat for all sub-questions]

## Evidence Summary

| Evidence | Source | Implication |
|----------|--------|-------------|
| [finding] | [file:line or URL] | [what it means] |

## Actionable Recommendations

1. **[Priority 1]:** [Specific action to improve this dimension]
2. **[Priority 2]:** [Specific action]
3. **[Priority 3]:** [Specific action]

## Related Dimensions

This teardown surfaced signals relevant to other dimensions:
- [Dimension X]: [observation that affects it]
- [Dimension Y]: [observation that affects it]
```
