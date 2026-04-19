---
name: understand-design
description: "Use when the user has a design prototype (from Stitch, Figma, or any tool) and wants AI to analyze it. Works standalone for daily development or in pipeline mode with a design doc. Handles images, HTML/CSS, or both."
---

## Overview

This skill dispatches the `dev-workflow:design-analyzer` agent to perform multi-modal analysis of design prototypes. It handles input acquisition (MCP tools or manual file paths), detects the run mode (pipeline vs standalone), and presents structured results.

## Two Run Modes

- **Pipeline mode** — a design doc with UX Assertions exists from a prior `brainstorm`. The analysis validates the prototype against the design doc, maps UX assertions, and produces structured output for `write-plan`.
- **Standalone mode** — no design doc. The user has a design (screenshot, HTML export, Figma frame) and wants AI to understand it for implementation guidance.

Mode is auto-detected but user can override.

## Process

### Step 0: Detect Mode

1. Search `docs/06-plans/*-design.md` for design documents in the current project
2. If found: read each and check for a `## UX Assertions` section with at least one assertion row
3. If a design doc with UX Assertions exists → **pipeline mode**; note the design doc path
4. If no design doc found → **standalone mode**
5. Report detected mode to the user. User can override (e.g., "just analyze it standalone").

If multiple design docs exist, present the list and ask the user which one to validate against.

### Step 1: Acquire Design Artifacts

Determine the design source. If the user provided file paths or MCP identifiers in the invocation, use those directly. Otherwise, ask.

**Path A — Stitch MCP**

Check if `get_screen_code` and `get_screen_image` tools are available.

If available:
1. Ask the user for the project ID and screen name/ID
2. Call `get_screen_image` → if it returns base64 data, write to a temporary file (`/tmp/design-screenshot-{timestamp}.png`) to avoid prompt bloat
3. Call `get_screen_code` → save HTML content to a temporary file (`/tmp/design-code-{timestamp}.html`)
4. Channel availability: `dual`

**Path B — Figma MCP**

Check if `get_design_context` and `get_variable_defs` tools are available.

If available:
1. Ask the user for the Figma file key and node ID
2. Call `get_design_context` → save structured output to a temporary file
3. Call `get_variable_defs` (if available) → save token definitions to a temporary file
4. Channel availability: `code-only` (Figma MCP returns structured descriptions, not screenshots)
5. If the user also provides a screenshot: upgrade to `dual`

**Path C — Manual file paths**

If no MCP tools are available, or the user prefers manual input:
1. Ask the user to provide:
   - Image file path(s) — screenshots, exported PNGs, photos of sketches
   - Code file path(s) — HTML files, CSS files, exported code
   - Or both
2. Validate that at least one file exists and is readable
3. Channel availability: determined by which files are provided

**Channel determination summary:**
- Image + code provided → `dual`
- Image only → `image-only`
- Code only → `code-only`
- Neither → stop and ask user for at least one input

### Step 2: Gather Project Context

Collect context for the agent regardless of mode:

1. **Tech stack detection:**
   - Read `CLAUDE.md` or `docs/00-AI-CONTEXT.md` for explicit tech stack declarations
   - If not found: check file extensions — `.swift` files → SwiftUI; `package.json` → React/Web; `pubspec.yaml` → Flutter
   - If still unclear: ask the user

2. **Existing token system:**
   - Glob for token definition files:
     - iOS: `**/DesignSystem*.swift`, `**/AppSpacing*`, `**/DesignTokens*`, `**/AppCornerRadius*`
     - Web: `**/design-tokens.*`, `**/theme.*`, `tailwind.config.*`
   - If found: note the path(s) for the agent

3. **Token strategy:**
   - If token files were found in item 2: ask the user — "Found tokens in {file}. Match design values against these existing tokens, or generate a fresh token proposal from the design? (match/propose)"
   - If no token files found: default to `propose`
   - User can override via explicit instruction in the invocation (e.g., "use propose mode", "match against my tokens")

4. **Design doc path** (pipeline mode): from Step 0

### Step 3: Dispatch Agent

Use the Task tool to launch the `dev-workflow:design-analyzer` agent with `model: "opus"`.

**Dispatch prompt structure:**

```
Analyze this design prototype.

Mode: {pipeline / standalone}
Design doc: {path or "none"}
Project root: {path}
Tech stack: {detected stack}
Existing tokens file: {path or "none"}
Token strategy: {match / propose}

Channel availability: {dual / image-only / code-only}
Image: {file path or "none"}
Code: {file path or "none"}
```

**Add for pipeline mode:**
```
UX Assertions from design doc:
{paste the full UX Assertions table from the design doc}
```

**Add any additional context:**
```
Additional context:
{user-specified focus areas, specific screens to analyze, known constraints}
```

### Step 4: Present Results

When the agent completes:
- If the agent's return contains a file path (e.g., `docs/06-plans/*-design-analysis.md`): read that file
- If no file path in return: search `docs/06-plans/*-design-analysis.md` for the most recent file. If found with `**Status:** in-progress`, the agent was truncated — use the partial results.
- If no file found at all: fall back to parsing the agent's return text as the analysis summary

**Pipeline mode presentation:**

1. **UX Assertion validation** — show the assertion table with ✅/❌/⚠️ status
2. **Token summary** — match mode: "{N} matched, {M} new candidates"; propose mode: "Token proposal: {N} values across {M} categories"
3. **Conflicts** (if any) — list ⚠️ Conflicting items from cross-validation; ask user: follow the prototype or the design doc?
4. **Platform translation highlights** — key mapping patterns
5. **Iteration suggestions** (if any) — present follow-up prompts; ask "Iterate on the design, or proceed?"
6. On confirmation: report the analysis file path and suggest `/write-plan`

**Standalone mode presentation:**

1. **Full analysis summary** — visual intent + structural facts + token mapping (or token proposal) + platform translation
2. **Iteration suggestions** (if any) — present follow-up prompts
3. Report the analysis file path
4. Suggest: "Use this analysis as reference when running `/brainstorm` or `/write-plan`."

**Decision Points:** After presenting the summary, check the agent's return for `Decisions:` count.
- If Decisions > 0:
  - First time this session: Read `${CLAUDE_PLUGIN_ROOT}/references/decision-points.md`
  - Apply the rules with parameters:
    - Source file: the analysis file
    - Mode: `mixed`
    - Recording: `default`
- Then proceed to next step (suggest /write-plan or provide guidance)

## Completion Criteria

- Design analysis file saved to `docs/06-plans/YYYY-MM-DD-<topic>-design-analysis.md`
- User has reviewed the analysis summary
- Next step communicated (pipeline: `/write-plan`; standalone: guidance provided)
