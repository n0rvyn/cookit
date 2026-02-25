---
name: compare
description: "Use when the user wants to compare multiple products or projects to decide which to focus on. Evaluates each app and produces a scoring matrix with recommendations."
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

Locate the plugin's reference files by searching for `**/product-lens/references/_calibration.md`. From the same parent directory, resolve absolute paths to:

- `_calibration.md` (always)
- `_scoring.md` (always)
- `dimensions/01-demand-authenticity.md` through `dimensions/06-execution-quality.md` (all 6)
- `modules/kill-criteria.md`, `modules/feature-audit.md`, `modules/elevator-pitch.md`, `modules/pivot-directions.md`, `modules/validation-playbook.md` (all 5)

### Step 3: Parallel Evaluation Pipeline

Read `_calibration.md` once (shared across all evaluations).

**Stage 1: Market scanning (parallel)**

Dispatch `market-scanner` for each target in parallel. Wait for all to complete.

**Stage 2: Pre-merge sub-questions**

For each target product, determine its platform variant (iOS or Default). For each of the 6 dimension files, extract and merge sub-questions using the same logic as evaluate skill Step 5. Prepare market data excerpts per dimension per product.

**Stage 3: Dimension evaluation (parallel)**

Dispatch `dimension-evaluator` agents for all targets in parallel — N products x 6 dimensions = 6N calls in a single message. Each receives:
- Calibration context (from `_calibration.md`)
- Its dimension payload (pre-merged sub-questions, scoring anchors, evidence sources)
- Its product info (name, description, type, project root)
- Its market data excerpt
- Depth: `standard`

Wait for all to complete.

**Stage 4: Validation**

For each dimension result across all products, apply the same validation checks as evaluate skill Step 7 (section headers, star format, sub-question count, evidence fields, anchor match). Re-dispatch any failing dimensions once.

**Stage 5: Extras generation (parallel)**

Read and pre-merge the 5 module files (same as evaluate skill Step 8).

Dispatch `extras-generator` for each target in parallel — N calls. Each receives:
- Its product info
- Its 6 dimension scores and justifications
- Its weak dimensions list (scored <=2 for Kill Criteria; scored <=3 with Next Action text for Validation Playbook)
- Module instructions (pre-merged with platform additions)
- Its market data

Wait for all to complete. Validate extras output (same checks as evaluate skill Step 9).

**Stage 6: Assembly**

For each product, assemble its individual report (same format as evaluate skill Step 9). Read `_scoring.md` and compute weighted totals.

### Step 4: Build Comparison Matrix

Extract scores from each product's evaluation and build the matrix:

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

Apply significance threshold: if two products' weighted totals differ by <= 0.5, mark as "difference not significant — compare individual dimensions."

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

(If any pair of products has a score difference <= 0.5, note that the ranking
between them is not significant and the recommendation is based on dimension-level
analysis, not total score.)

## Development Maturity Signals
[from Step 5]

## Cross-Project Kill Criteria

Across all evaluated projects:
1. [Kill criterion that applies to multiple projects]
2. [Project-specific critical kill criterion]

## Individual Reports

[For each product, include the full evaluation report from Stage 6 assembly:
 Elevator Pitch Test, Evaluation Overview table, Priority Actions,
 Dimension Details (all 6 dimension results preserving internal structure),
 Feature Necessity Audit, Kill Criteria, Pivot Directions, Validation Playbook]
```

Post-processing:
- Flag any project where 2+ dimensions scored <=2 stars (strong stop signal)
- If all projects score poorly, say so directly — "none of these are strong candidates" is a valid conclusion

## Completion Criteria

- All target products individually evaluated (6 dimensions each)
- Scoring matrix with weighted totals presented
- Focus/Maintain/Stop recommendation provided
- Development maturity signals compared (for local projects)
- Individual reports included
