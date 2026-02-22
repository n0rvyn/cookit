---
name: feature-assess
description: "Use when the user wants to evaluate whether an existing app should add a specific feature. Analyzes demand fit, journey contribution, build cost, and strategic value. Produces a GO/DEFER/KILL verdict with conditional follow-up: integration map (GO) or alternative directions (DEFER/KILL). Works on local projects only (requires code access)."
disable-model-invocation: true
---

## Process

### Step 1: Parse Input

Parse the input to identify:

1. **Project path** — where the app's code is located
   - Path argument provided → use that path
   - No argument → current working directory
   - If no project files found at path, stop and ask the user

2. **Feature description** — what feature is being evaluated
   - Quoted string in the argument → use as feature description
   - If not provided or unclear → ask the user: "What feature do you want to evaluate? Describe it in 1-2 sentences."

This skill requires a local project with code access. If the user specifies an external app name without a path, inform them: "Feature assessment requires code access to analyze build cost and integration points. Please provide a path to a local project."

Read the project's README (or equivalent top-level docs) to confirm the product description. If unclear, ask for a one-sentence product description.

### Step 2: Detect Platform

**Check for platform indicators:**
- `.xcodeproj`, `.xcworkspace`, `Package.swift` with iOS platform → iOS
- `package.json`, `next.config`, `vite.config` → Web
- `pubspec.yaml` → Flutter (cross-platform)
- `android/` directory → Android
- Ambiguous → ask the user

### Step 3: Resolve Reference Paths

Locate the plugin's reference files by searching for `**/product-lens/references/feature-assess/_calibration.md`. From the same parent directory, resolve absolute paths to:

- `_calibration.md` (always)
- `_verdict.md` (always)
- `dimensions/01-demand-fit.md` through `dimensions/04-strategic-value.md` (all 4)
- `modules/integration-map.md` (always)
- `modules/alternative-directions.md` (always)

### Step 4: Scan App Context and Gather Market Context (parallel)

Dispatch two agents **in a single message** (parallel execution):

**Agent 1: `app-context-scanner`** with:
- Project root path
- Platform (from Step 2)
- Product description (from README or user input)
- Proposed feature description (from Step 1)

**Agent 2: `market-scanner`** with:
- Product description (from README or user input)
- Target category (inferred from product description)
- Platform (from Step 2)
- In the dispatch prompt, add feature-scoped search focus: "In addition to general market research, specifically investigate whether competitors in this category offer [feature description] and how users discuss the need for [feature description]."

**Wait for both agents to complete before proceeding.** The dimension evaluators need both the app context and market data.

### Step 5: Pre-merge Sub-Questions

Read `_calibration.md` once — this will be injected as preamble into every feature-dimension-evaluator prompt.

Determine the platform variant to use:
- iOS detected → extract `### iOS` sections from each dimension file
- Otherwise → extract `### Default` sections

For each of the 4 dimension files, read the file and extract:
1. **Core question** (the line after `**Core question:**`)
2. **Universal sub-questions** (the numbered list under `## Universal Sub-Questions`)
3. **Platform-specific sub-questions** (the numbered list under the correct `### [Platform]` section within `## Platform-Specific Sub-Questions`). If iOS, also extract the iOS core question variant (the blockquote under the `### iOS` heading).
4. **Signal anchors** (the table under `## Signal Anchors`)
5. **Evidence sources** (the content under `## Evidence Sources`)

For each dimension, merge the universal + platform-specific sub-questions into a single numbered list (universal questions first, then platform-specific, numbered sequentially).

Result: 4 self-contained dimension payloads.

Also prepare market data excerpts per dimension from the market-scanner output:
- **Demand Fit:** full market data (competitor features, user signals, community discussions)
- **Journey Contribution:** "none" (code analysis dimension)
- **Build Cost:** "none" (code analysis dimension)
- **Strategic Value:** Risk Signals + Direct Competitors sections

### Step 6: Dispatch 4x feature-dimension-evaluator (parallel)

Dispatch all 4 `feature-dimension-evaluator` agents **in a single message** (parallel execution). Each agent receives:

- **Calibration context:** full content of `_calibration.md`
- **Dimension name** (English + Chinese) and core question
- **Sub-questions:** the merged numbered list from Step 5
- **Signal anchors:** the table from Step 5
- **Evidence source hints:** from Step 5
- **App context:** full output from app-context-scanner (Step 4)
- **Proposed feature:** the feature description from Step 1
- **Product info:** app name, one-sentence description, project root path
- **Market data excerpt:** the dimension-relevant excerpt from Step 5

Wait for all 4 to complete.

### Step 7: Collect and Validate Dimension Results

For each of the 4 returned results, verify:

1. Section header `## [Dimension Name` exists
2. Signal line contains exactly one of: `Positive`, `Neutral`, `Negative`
3. Confidence line contains exactly one of: `High`, `Medium`, `Low`
4. Count of `### Q` sub-sections matches the expected sub-question count for that dimension
5. Each sub-section contains `**Evidence:**` and `**Assessment:**` fields
6. `**Anchor match:**` field exists in the Dimension Signal section

**If any dimension fails validation:**
- Re-dispatch that single feature-dimension-evaluator with a correction note prepended: "Your previous output had these issues: [list specific failures]. Produce the corrected output following the template exactly."
- Maximum 1 retry per dimension
- If still non-compliant after retry: include with warning annotation `> ⚠️ This dimension's output did not fully comply with the evaluation template.`

Extract from each valid result:
- Dimension signal (Positive / Neutral / Negative)
- Dimension confidence (High / Medium / Low)
- Key evidence sentence

### Step 8: Compute Verdict

Read `_verdict.md`. Apply the verdict rules to the 4 dimension signals:

**KILL** if ANY of:
- Any dimension has signal=Negative AND confidence=High
- Two or more dimensions have signal=Negative (regardless of confidence)

**GO** if ALL of:
- No dimension has signal=Negative with confidence=High
- At most one dimension has signal=Negative (with confidence Medium or Low)
- At least two dimensions have signal=Positive

**DEFER** if:
- Neither KILL nor GO conditions are met

For DEFER: list the conditions that could flip the verdict. Identify which Low-confidence signals are most likely to change with more information.

### Step 9: Dispatch Follow-up Module (conditional)

Read the appropriate module file from `references/feature-assess/modules/`. If the module has platform additions (`### iOS`), extract them and append to the base instructions.

**If verdict is GO:**
Dispatch `feature-followup-generator` with:
- Module type: "Integration Map"
- Module instructions: content of `integration-map.md` (pre-merged with platform additions)
- Product info: app name, description, project root path, platform
- App context: full output from app-context-scanner (Step 4)
- Proposed feature: the feature description from Step 1
- Dimension signals: all 4 dimensions with their signals, confidence levels, and key evidence
- Verdict: GO with reasoning
- Market data excerpt: full market-scanner output

**If verdict is DEFER or KILL:**
Dispatch `feature-followup-generator` with:
- Module type: "Alternative Directions"
- Module instructions: content of `alternative-directions.md`
- Product info: app name, description, project root path, platform
- App context: full output from app-context-scanner (Step 4)
- Proposed feature: the feature description from Step 1
- Dimension signals: all 4 dimensions with their signals, confidence levels, and key evidence
- Verdict: DEFER or KILL with reasoning
- Market data excerpt: full market-scanner output

Wait for completion.

### Step 10: Validate Follow-up Output

**If Integration Map:** verify:
- `## Integration Map` section exists
- `### Reusable Infrastructure` section exists
- `### New Infrastructure Required` section exists
- `### Modification Scope` section with table exists
- `### Integration Points` section exists
- `### Implementation Sequence` section with numbered steps exists

**If Alternative Directions:** verify:
- `## Alternative Directions` section exists
- At least one of: `### Lower-Cost Variants`, `### Complementary Features`, `### Clarify Before Deciding`
- Each direction references specific existing assets/code

If validation fails: re-dispatch once with correction note. If still non-compliant, include with warning annotation.

### Step 11: Assemble Final Report

Assemble the final report:

```markdown
# Feature Assessment: [Feature Name] for [App Name]

> **Feature:** [feature description]
> **App:** [app name] — [one-sentence app description]
> **Platform:** [platform]

## Verdict: [GO / DEFER / KILL]

[One paragraph explaining the verdict, citing the key signals that drove it]

(If DEFER: list the conditions that could flip the verdict)

## Signal Overview

| Dimension | Signal | Confidence | Key Evidence |
|-----------|--------|------------|--------------|
| Demand Fit (需求契合) | [signal] | [confidence] | [key evidence] |
| Journey Contribution (旅程贡献) | [signal] | [confidence] | [key evidence] |
| Build Cost (实现代价) | [signal] | [confidence] | [key evidence] |
| Strategic Value (战略价值) | [signal] | [confidence] | [key evidence] |

## Dimension Details

[All 4 dimension evaluation results in order, each preserving its internal structure
 (## heading, ### QN sections, ### Dimension Signal)]

## [Integration Map OR Alternative Directions]
[from feature-followup-generator output]
```

### Step 12: Present Results

Display the assembled report.

Post-processing:
1. **Highlight the verdict** — if KILL, call it out prominently with the fatal flaw
2. **Flag High-confidence Negative dimensions** — these are the blockers
3. **Flag Low-confidence dimensions** — these are the investigation opportunities
4. **If GO: highlight the first implementation step** from the Integration Map
5. **If DEFER: highlight what to investigate first** to resolve uncertainty
