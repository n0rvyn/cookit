---
name: teardown
description: "Use when the user wants a deep dive into a specific evaluation dimension for a product. Example: teardown moat, teardown journey. Goes deeper than the standard evaluation on one dimension."
---

## Process

### Step 1: Parse Dimension

Accept the dimension argument in both Chinese and English. Mapping:

| English | Chinese | Dimension | File |
|---------|---------|-----------|------|
| demand | 需求真伪 | Demand Authenticity | `01-demand-authenticity.md` |
| journey | 逻辑闭环 | Journey Completeness | `02-journey-completeness.md` |
| market | 市场空间 | Market Space | `03-market-space.md` |
| business | 商业可行 | Business Viability | `04-business-viability.md` |
| moat | 护城河 | Moat | `05-moat.md` |
| execution | 执行质量 | Execution Quality | `06-execution-quality.md` |

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

### Step 3: Detect Platform and Resolve Paths

1. Detect platform (iOS / Web / etc.)
2. Locate reference files by searching for `**/product-lens/references/_calibration.md`. From the same parent directory, resolve the path to:
   - `_calibration.md`
   - The single dimension file matching the target dimension (from the mapping in Step 1)

### Step 4: Pre-merge Sub-Questions

Read `_calibration.md` (preamble for the evaluator).

Read the target dimension file. Extract:
1. Core question
2. Universal sub-questions
3. Platform-specific sub-questions (from `### iOS` if iOS detected, otherwise `### Default`)
4. Scoring anchors
5. Evidence sources

If iOS detected and the dimension has an iOS core question variant (blockquote under `### iOS`), note it for the evaluator.

Merge universal + platform-specific into a single numbered list.

### Step 5: Gather Market Context (if applicable)

For dimensions that benefit from market data (**Market Space**, **Business Viability**, **Moat**):
- Dispatch `market-scanner` agent with product info
- Wait for completion

For other dimensions (**Demand Authenticity**, **Journey Completeness**, **Execution Quality**):
- Skip market-scanner; these are primarily code/product analysis

### Step 6: Deep Evaluation

Dispatch a single `dimension-evaluator` agent with:
- **Calibration context:** full content of `_calibration.md`
- **Dimension name** (English + Chinese) and core question
- **Sub-questions:** the merged numbered list from Step 4
- **Scoring anchors** from Step 4
- **Evidence source hints** from Step 4
- **Product info:** name, description, type, project root
- **Market data:** from Step 5 (or "none")
- **Depth mode:** `deep`

Wait for completion.

### Step 7: Present Results

Display the deep-dive report from the dimension-evaluator. The deep mode output includes:
- Per-sub-question analysis with sub-scores
- Evidence summary table
- Dimension score with anchor match
- Prioritized recommendations
- Related dimensions observations

Post-processing:
- If the dimension scored <=2, highlight this prominently
- If Related Dimensions section identifies signals for other dimensions, suggest running `/evaluate` for the full picture or `/teardown [other dimension]` for a focused follow-up
