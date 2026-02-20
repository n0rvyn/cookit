---
name: compare
description: "Use when the user wants to compare multiple products or projects to decide which to focus on. Evaluates each app and produces a scoring matrix with recommendations."
user-invocable: false
---

## Process

### Step 1: Collect Targets

Parse arguments to build a target list. Arguments can be a mix of:
- Local project paths (e.g., `/path/to/app1 /path/to/app2`)
- External app names (e.g., `"Bear" "Notion"`)
- Mixed (e.g., `/path/to/my-app "Bear" "Notion"`)

For each target:
1. Determine type: local (path exists on filesystem) or external (name/URL)
2. Detect platform (same logic as evaluate skill Step 2)
3. Get one-sentence product description (from README or user input)

Confirm the target list with the user before proceeding: "I'll evaluate these N products: [list]. Correct?"

### Step 2: Resolve Reference Paths

Locate the plugin's reference files by searching for `**/product-lens/references/frameworks.md`. Resolve absolute paths for:
- `frameworks.md` (always needed)
- `ios-overlay.md` (if any target is iOS)

### Step 3: Parallel Evaluation

For each target, dispatch the full evaluation flow:

1. Dispatch `market-scanner` for each target (in parallel where possible). Wait for all to complete.
2. Dispatch `product-evaluator` for each target (in parallel where possible), passing:
   - Product info
   - Evaluation type
   - Project root (if local)
   - Frameworks reference path (from Step 2)
   - Platform overlay path (from Step 2, if iOS)
   - Market data from its market-scanner run
   - Scope: `full`

Collect all evaluation reports.

### Step 4: Build Comparison Matrix

Extract scores from each evaluation report and build the matrix:

```markdown
## Scoring Matrix

| Dimension | [App A] | [App B] | [App C] |
|-----------|---------|---------|---------|
| Demand Authenticity (需求真伪) | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |
| Journey Completeness (逻辑闭环) | ★★★☆☆ | ★★★★☆ | ★★★☆☆ |
| Market Space (市场空间) | ★★★☆☆ | ★★☆☆☆ | ★★★★☆ |
| Business Viability (商业可行) | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |
| Moat (护城河) | ★★☆☆☆ | ★★★☆☆ | ★★★☆☆ |
| Execution Quality (执行质量) | ★★★★☆ | ★★★☆☆ | ★★★☆☆ |
| **Weighted Total** | **X.X** | **X.X** | **X.X** |
```

Ask the user if they want custom weights or a weight preset (validation/growth/maintenance phase). Otherwise use default equal weights.

Rank by weighted total score (highest first).

Apply significance threshold: if two products' weighted totals differ by ≤ 0.5, mark as "difference not significant — compare individual dimensions."

### Step 5: Development Maturity Signals

For each **local** project (skip for external apps), observe maturity signals:

1. **Observable signals per project:**
   - TODO/FIXME count (high = early stage)
   - Test coverage presence (tests exist = more mature)
   - Feature list (README/docs) vs implemented features (code)
   - Monetization code present? (paywall/StoreKit = closer to launch)
   - App Store assets present? (screenshots, metadata = launch-ready)
2. **Primary blocker:** What must be solved before the next milestone?
3. Do NOT estimate completion percentages or hours — list observable signals only

```markdown
## Development Maturity Signals

| Signal | [App A] | [App B] |
|--------|---------|---------|
| TODO/FIXME count | 23 | 5 |
| Tests present | No | Yes |
| Monetization code | No | StoreKit 2 |
| App Store assets | No | Screenshots exist |
| Primary blocker | Core data model incomplete | App Review grey zone on X feature |
```

### Step 6: Present Results

Output the full comparison report:

```markdown
# Product Lens: Portfolio Comparison

## Scoring Matrix
[from Step 4]

## Recommendation

**Focus:** [App] — [reason: highest score + best maturity signals]
**Maintain:** [App] — [conditional reason]
**Stop:** [App] — [reason: lowest score or kill criteria triggered]

(If any pair of products has a score difference ≤ 0.5, note that the ranking
between them is not significant and the recommendation is based on dimension-level
analysis, not total score.)

## Development Maturity Signals
[from Step 5]

## Cross-Project Kill Criteria

Across all evaluated projects:
1. [Kill criterion that applies to multiple projects]
2. [Project-specific critical kill criterion]

## Individual Reports

[Link or expand each full evaluation report below]
```

Post-processing:
- Flag any project where 2+ dimensions scored ≤2 stars (strong stop signal)
- If all projects score poorly, say so directly — "none of these are strong candidates" is a valid conclusion
