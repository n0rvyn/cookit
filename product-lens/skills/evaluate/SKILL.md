---
name: evaluate
description: "Use when the user wants to evaluate a product — assess demand, market viability, moat, and execution quality from an indie developer perspective. Works on local projects (by reading code) or external apps (via web search)."
disable-model-invocation: true
---

## Process

### Step 1: Determine Target

Parse the input to determine evaluation target:

- **Path argument provided** → local project (e.g., `/path/to/project`)
- **Name or URL argument provided** → external app (e.g., `"Bear"`, `"Notion"`)
- **No argument** → local project at current working directory

If the target is a local project, read its README (or equivalent top-level docs) to understand what it does. If no README exists or the product purpose is unclear, ask the user for a one-sentence product description.

### Step 2: Detect Platform

**Local project — check for platform indicators:**
- `.xcodeproj`, `.xcworkspace`, `Package.swift` with iOS platform → iOS
- `package.json`, `next.config`, `vite.config` → Web
- `pubspec.yaml` → Flutter (cross-platform)
- `android/` directory → Android
- Ambiguous → ask the user

**External app:**
- If user specified platform, use it
- If app name is well-known, infer (but confirm if uncertain)
- Otherwise, ask

### Step 3: Resolve Reference Paths

Locate the plugin's reference files by searching for `**/product-lens/references/_calibration.md`. From the same parent directory, resolve absolute paths to:

- `_calibration.md` (always)
- `_scoring.md` (always)
- `dimensions/01-demand-authenticity.md` through `dimensions/06-execution-quality.md` (all 6)
- `modules/kill-criteria.md`, `modules/feature-audit.md`, `modules/elevator-pitch.md`, `modules/pivot-directions.md`, `modules/validation-playbook.md` (all 5)

### Step 4: Gather Market Context

Dispatch the `market-scanner` agent with:
- Product description (from README or user input)
- Target category (inferred from product description)
- Known competitors (if user mentioned any)
- Platform (from Step 2)

**Wait for market-scanner to complete before proceeding.** The dimension evaluators need this data.

### Step 5: Pre-merge Sub-Questions

Read `_calibration.md` once — this will be injected as preamble into every dimension-evaluator prompt.

Determine the platform variant to use:
- iOS detected → extract `### iOS` sections from each dimension file
- Otherwise → extract `### Default` sections

For each of the 6 dimension files, read the file and extract:
1. **Core question** (the line after `**Core question:**`)
2. **Universal sub-questions** (the numbered list under `## Universal Sub-Questions`)
3. **Platform-specific sub-questions** (the numbered list under the correct `### [Platform]` section within `## Platform-Specific Sub-Questions`). If iOS, also extract the iOS core question variant (the blockquote under the `### iOS` heading).
4. **Scoring anchors** (the table under `## Scoring Anchors`)
5. **Evidence sources** (the content under `## Evidence Sources`)

For each dimension, merge the universal + platform-specific sub-questions into a single numbered list (universal questions first, then platform-specific, numbered sequentially).

Result: 6 self-contained dimension payloads.

Also prepare market data excerpts per dimension from the market-scanner output:
- **Demand Authenticity:** full market data
- **Journey Completeness:** "none" (code analysis dimension)
- **Market Space:** Direct Competitors + Market Signals + Pricing Landscape sections
- **Business Viability:** Pricing Landscape + Discovery Channels sections
- **Moat:** Risk Signals + Direct Competitors sections
- **Execution Quality:** "none" (code analysis dimension)

### Step 6: Dispatch 6x dimension-evaluator (parallel)

Dispatch all 6 `dimension-evaluator` agents **in a single message** (parallel execution). Each agent receives:

- **Calibration context:** full content of `_calibration.md`
- **Dimension name** (English + Chinese) and core question
- **Sub-questions:** the merged numbered list from Step 5
- **Scoring anchors:** the table from Step 5
- **Evidence source hints:** from Step 5
- **Product info:** name, one-sentence description, evaluation type (local/external), project root path
- **Market data excerpt:** the dimension-relevant excerpt from Step 5
- **Depth mode:** `standard`

Wait for all 6 to complete.

### Step 7: Collect and Validate Dimension Results

For each of the 6 returned results, verify:

1. Section header `## [Dimension Name` exists
2. Score line contains star characters (★/☆), not X/10 or other scales
3. Count of `### Q` sub-sections matches the expected sub-question count for that dimension
4. Each sub-section contains `**Evidence:**` and `**Assessment:**` fields
5. `**Anchor match:**` field exists in the Dimension Score section
6. `### Next Action` section exists after `### Dimension Score`

**If any dimension fails validation:**
- Re-dispatch that single dimension-evaluator with a correction note prepended to the original prompt: "Your previous output had these issues: [list specific failures]. Produce the corrected output following the template exactly."
- Maximum 1 retry per dimension
- If still non-compliant after retry: include with warning annotation `> ⚠️ This dimension's output did not fully comply with the evaluation template.`

Extract from each valid result:
- Dimension star score (for the overview table and extras-generator)
- One-sentence justification (for the overview table)
- Next Action text (for Priority Actions section in the final report)

### Step 8: Dispatch extras-generator

Read the 5 module files from `references/modules/`. For each module file that has a `## Platform Additions` or `## Platform Constraints` section:
- If iOS: extract the `### iOS` section and append it to the module's base instructions
- Otherwise: use the base instructions only

Dispatch the `extras-generator` agent with:
- **Product info:** name, description, evaluation type, project root path, platform
- **Dimension scores:** all 6 dimension names with their star scores and one-sentence justifications
- **Weak dimensions:** list of dimensions scored <=2
- **Dimensions scored <=3:** list of dimensions scored <=3, with their Next Action text (for Validation Playbook)
- **Module instructions:** the 5 module files' content (pre-merged with platform additions)
- **Market data excerpt:** full market-scanner output (for Pivot Directions context)

Wait for completion.

### Step 9: Assemble Final Report

Read `_scoring.md`. Compute the weighted total from the 6 dimension scores using default equal weights (or a user-specified preset if requested).

Assemble the final report by combining dimension results and extras output:

```markdown
# Product Lens: [Product Name]

> [One-sentence product description]

## Elevator Pitch Test
[from extras-generator output — the Elevator Pitch Test section]

## Evaluation Overview

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Demand Authenticity (需求真伪) | [stars] | [justification from dimension result] |
| Journey Completeness (逻辑闭环) | [stars] | [justification] |
| Market Space (市场空间) | [stars] | [justification] |
| Business Viability (商业可行) | [stars] | [justification] |
| Moat (护城河) | [stars] | [justification] |
| Execution Quality (执行质量) | [stars] | [justification] |
| **Weighted Total** | **X.X** | |

## Priority Actions

[Ordered list of Next Actions from dimensions scored ≤3★, sorted by score ASC (lower = more urgent).
Each item: "**[Dimension Name] (N★):** [Next Action text from dimension-evaluator output]"
If no dimensions scored ≤3★, write: "All dimensions scored ≥4★. See individual dimension Next Actions for consolidation opportunities."]

## Dimension Details

[All 6 dimension evaluation results in order, each preserving its internal structure
 (## heading, ### QN sections, ### Dimension Score)]

## Feature Necessity Audit
[from extras-generator output]

## Kill Criteria
[from extras-generator output]

## Pivot Directions
[from extras-generator output]

## Validation Playbook
[from extras-generator output — experiments targeting dimensions scored ≤3★]
```

Validate extras output:
- `## Elevator Pitch Test` section exists with `**Verdict:**` field
- `## Kill Criteria` section exists with >=3 numbered items
- `## Feature Necessity Audit` section exists (content or skip notice)
- `## Pivot Directions` section exists with >=2 named directions
- `## Validation Playbook` section exists with >=2 numbered experiments (each with Do/Success/Fail/Timeline fields), or a skip notice if all dimensions scored >=4★

If validation fails: re-dispatch extras-generator once with a correction note. If still non-compliant, include with warning annotation.

### Step 9.5: Save Report

If the evaluation target is a local project:
1. Check if `docs/08-product-evaluation/` directory exists. If not, create it.
2. Save the report to `docs/08-product-evaluation/{YYYY-MM-DD}-evaluate.md`
3. Check for previous reports in the same directory (files matching `*-evaluate.md`). If found, append a `## Changes Since Last Evaluation` section comparing dimension scores and highlighting movements >=1★.
   - Format: `| Dimension | Previous | Current | Change |` table
   - Only include dimensions with score movement >=1★
   - If this is the first report, omit this section

### Step 10: Present Results

Display the assembled report.

Post-processing:
1. **Highlight the Elevator Pitch result** — if "Cannot articulate", call it out prominently at the top
2. **Flag weak dimensions** — any dimension scored <=2 stars gets an explicit warning
3. **Verify Priority Actions section** — confirm it lists all dimensions scored ≤3★ in ascending score order, each with its Next Action from the dimension-evaluator output. This replaces generic "next steps" with specific, dimension-derived actions.
