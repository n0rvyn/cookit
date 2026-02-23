---
name: demand-check
description: "Use for a quick demand reality check on a product idea or project. Runs only the demand validation dimension and Elevator Pitch test. Fast first-pass filter before committing to build."
---

## Overview

Lightweight evaluation: only runs Demand Authenticity and the Elevator Pitch test. No full agent dispatch; runs directly in the main context for speed. This is a 5-minute first-pass filter.

## Process

### Step 1: Quick Product Understanding

- **Local project:** Read README + scan top-level directory structure. Identify the core value proposition.
- **External app / idea:** Use the user's description. Do a single WebSearch for the product if needed.
- **No argument:** Use current working directory.

Do not deep-dive into code. This is a surface-level scan.

### Step 2: Detect Platform and Load Framework

Same platform detection logic as evaluate skill:
- Check for `.xcodeproj` / `Package.swift` → iOS
- Check for `package.json` → Web
- Otherwise ask or infer

Locate reference files by searching for `**/product-lens/references/dimensions/01-demand-authenticity.md`.

Read:
1. `dimensions/01-demand-authenticity.md` — extract:
   - Universal sub-questions
   - Platform-specific sub-questions (from `### iOS` if iOS detected, otherwise `### Default`)
   - Scoring anchors
2. `modules/elevator-pitch.md` — extract:
   - Default constraints
   - Platform-specific constraints (from `### iOS` under `## Platform Constraints` if iOS detected)
   - Judgment criteria

### Step 3: Demand Dimension Assessment

Answer the dimension's sub-questions using available evidence:
- README claims and problem statement
- Quick code structure scan (is 80% of code serving core value?)
- User's own description of the problem being solved

Score 1-5 stars with one-sentence justification.

### Step 4: Elevator Pitch Test

Attempt to write:
- Tagline (<=30 chars) — apply platform-specific constraints if iOS
- First description sentence

Judge: Clear / Vague / Cannot articulate

### Step 5: Quick Alternative Scan

Run 2-3 WebSearches:
- `"best [category] app [year]"`
- `"[problem description] alternative"`
- `"[category] indie app"` (if relevant)

Note top 3-5 alternatives and their approach. This is not a full market scan — just enough to answer "is someone already doing this well?"

### Step 6: Verdict

Output one of three verdicts:

| Verdict | Criteria | Meaning |
|---------|----------|---------|
| **Pass** | Demand >=3★ AND Pitch not "Cannot articulate" AND alternatives are beatable | Green light: proceed to full evaluation or building |
| **Caution** | Demand 3★ with Pitch "Cannot articulate", OR Demand 2★ with Pitch "Clear", OR dominant alternative exists but has clear gaps | Investigate further: run full `/evaluate` before committing |
| **Fail** | Demand <=2★ AND no differentiation angle, OR Pitch "Cannot articulate" AND problem already solved well by free tools | Reconsider: this idea needs significant rethinking |

### Validation Playbook (Caution verdict only)

When the verdict is **Caution**, append a `## Validation Playbook` section to the output. Select 2-3 methods from the list below based on what is uncertain:

- **If demand unclear:** "AI-analyze 200+ competitor 1★-3★ App Store reviews to extract unmet needs. Success: >=3 recurring complaint themes that this product addresses."
- **If differentiation unclear:** "Post pain-point description (not product pitch) in target community (Reddit/Discord). Success: >=20 upvotes or >=5 'I have this problem' replies within 48 hours."
- **If willingness-to-pay unclear:** "Soft-launch in a small market (e.g., New Zealand) at target price for 2 weeks. Success: >=3 paid conversions without promotion."
- **If dogfooding viable:** "Use your own product daily for 2 weeks, logging every friction point. Success: friction log has <=5 entries AND you genuinely miss the product when you stop."
- **If AI replacement risk unclear:** "Ask ChatGPT, Claude, and Perplexity to recommend tools for this product's core job. Success: AI tools recommend the category but can't fully replace it."

Each selected method must include: method description, success criteria, failure criteria, and timeline (all <=2 weeks).

### Step 7: Save Report

If the evaluation target is a local project:
1. Check if `docs/08-product-evaluation/` directory exists. If not, create it.
2. Save the report to `docs/08-product-evaluation/{YYYY-MM-DD}-demand-check.md`
3. Check for previous demand-check reports in the same directory. If found, note score changes in the verdict section.

## Output Format

```markdown
# Demand Check: [Product Name]

## Elevator Pitch
> **Tagline:** [<=30 chars]
> **Description:** [first sentence]
> **Verdict:** [Clear / Vague / Cannot articulate] — [reasoning]

## Demand Authenticity (需求真伪) [★★★☆☆]

[Sub-question answers with evidence]

## Alternatives Found

| Alternative | Approach | Pricing | Threat Level |
|-------------|----------|---------|--------------|
| [name] | [how it solves the problem] | [price] | [High/Medium/Low] |

## Verdict: [Pass / Caution / Fail]

[One paragraph explaining the verdict and suggested next steps]

## Validation Playbook
(Only present when verdict is Caution)

Before committing to build, validate these uncertainties:
1. **[Uncertainty]:** [Method] — Success: [criteria] / Fail: [criteria] — Timeline: [<=2 weeks]
2. **[Uncertainty]:** [Method] — Success: [criteria] / Fail: [criteria] — Timeline: [<=2 weeks]
```
