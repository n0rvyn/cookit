---
name: evaluate
description: "Use when the user wants to evaluate a product — assess demand, market viability, moat, and execution quality from an indie developer perspective. Works on local projects (by reading code) or external apps (via web search)."
user-invocable: false
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

**If iOS detected:** set platform overlay to the plugin's `references/ios-overlay.md`.

### Step 3: Resolve Reference Paths

Locate the plugin's reference files by searching for `**/product-lens/references/frameworks.md`. Resolve absolute paths for:
- `frameworks.md` (always needed)
- `ios-overlay.md` (if iOS platform detected in Step 2)

These absolute paths will be passed to agents in subsequent steps.

### Step 4: Gather Market Context

Dispatch the `market-scanner` agent with:
- Product description (from README or user input)
- Target category (inferred from product description)
- Known competitors (if user mentioned any)
- Platform (from Step 2)

**Wait for market-scanner to complete before proceeding.** The evaluator needs this data.

### Step 5: Dispatch Evaluation

Dispatch the `product-evaluator` agent with:
- Product name and one-sentence description
- Evaluation type: `local` or `external`
- Project root path (if local)
- Frameworks reference path: absolute path resolved in Step 3
- Platform overlay path: absolute path resolved in Step 3, or "none"
- Market data: output from market-scanner (Step 4)
- Scope: `full`

### Step 6: Present Results

Display the full evaluation report from product-evaluator.

Post-processing:
1. **Highlight the Elevator Pitch result** — if "Cannot articulate", call it out prominently at the top
2. **Flag weak dimensions** — any dimension scored ≤2 stars gets an explicit warning
3. **Summarize actionable next steps** — based on the evaluation, what should the developer do first?
