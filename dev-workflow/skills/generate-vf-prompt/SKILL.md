---
name: generate-vf-prompt
description: "Use when you need to create a verification prompt with falsifiable assertions for a plan, code change, or session response. Generates structured prompts that enable rigorous verification."
user-invocable: true
---

## Overview

Generate a VF/DF verification prompt based on actual code analysis. The user copies the output and pastes it into the target session (e.g., a native `/plan` session, an execution session, or any other conversation).

Theoretical basis: verification (backward reasoning) has lower cognitive load than generation (forward reasoning), and the resulting reasoning paths are complementary to forward chain-of-thought. Critiquing external input overcomes egocentric bias. (Wu & Yao, "Asking LLMs to Verify First is Almost Free Lunch", 2025)

**This skill only generates prompts. It does not execute verification.**

## Process

### Step 1: Input Collection

Determine what to verify. The user provides one of:

- **Plan file path** — native `/plan` output, `docs/06-plans/*.md`, or any plan document
- **Design doc path** — optional; triggers DF strategies when provided alongside a plan
- **`--diff` flag** — use `git diff` for code change verification
- **Pasted text** — another session's response or any content to challenge

If the input is a plan file, check its header for a `Design doc:` reference. If found, treat as "design doc exists".

If unclear what to verify, ask the user.

### Step 2: Context Analysis

Auto-detect content type and verification focus — do not ask the user:

| Signal | Determination |
|---|---|
| Input is a plan file | Stage = plan verification |
| Design doc exists (provided or found in plan header) | Stage += design faithfulness |
| Git diff has content + `--diff` flag | Stage = implementation verification |
| Plan/change involves View, UI, layout, styling | Content = UI |
| Plan/change involves Service, Agent, Tool, data flow, event entry points | Content = architecture |
| Plan/change has >= 5 steps with inter-step dependencies | Content = multi-step |
| Plan/change modifies existing code behavior | Content = behavioral change |

### Step 3: Strategy Selection

Auto-select applicable strategies (can overlap):

| Context | VF Strategies | DF Strategies |
|---|---|---|
| Plan + behavioral change | S1 | — |
| Plan + architecture | S1 + S3 | — |
| Plan + UI | S1 + U1 + U2 | — |
| Plan + multi-step | S2 | — |
| Plan + design doc exists | S1 | D1 + selected D2-D5 |
| Code change (`--diff`) | R1 | — |

DF sub-strategy selection (when design doc exists):
- **D1 (bidirectional mapping)**: always selected
- **D2 (hallucination detection)**: when plan contains decisions not obviously derived from design
- **D3 (implicit context)**: when design doc has preconditions, constraints, or business rules
- **D4 (granularity audit)**: when plan step count differs significantly from design requirement count
- **D5 (boundary scenarios)**: when design doc mentions edge cases, error flows, or extreme conditions

### Step 4: Read & Generate

1. Read the plan/diff/pasted content
2. Read relevant code files — files modified by the plan, files referenced, downstream consumers
3. If design doc exists: read the design doc
4. For each selected strategy, generate **3-5 concrete, falsifiable assertions** based on actual code content
5. Assemble all assertions into a single prompt, grouping by strategy

**Critical rule**: Every assertion must reference actual file paths, function names, or line numbers from the code read in this step. Generic placeholders like "some file" or "a function" are prohibited.

### Step 5: Output

Output the assembled prompt in this format:

````
## VF Prompt

**Input**: {description of what was analyzed}
**Design doc**: {path or "none"}
**Strategies**: {list of selected strategy codes, e.g., S1 + S2 + D1}

---

**Copy the following and paste into the target session:**

```
{assembled prompt with all assertions}
```
````

---

## Strategy Templates

Each template below shows the structure. When generating, replace all `{...}` with content derived from actual code analysis.

### VF Strategies

#### S1 — Candidate Errors

Trigger: plan + behavioral change (always applicable to plans).

```
An external reviewer examined this plan against the codebase. Verify each claim (cite file:line), fix the plan if confirmed:

1. Step {N}'s {specific operation} will break {file}'s {function} because {reason from actual code reading}
2. Step {N} assumes {precondition}, but {file:line} shows this precondition is not established by any prior step
3. Step {N} modifies {file}, but {other_file:line} also depends on the same {entity} and is not addressed in the plan

After verifying the above, check if similar issues exist elsewhere in the codebase.
```

Assertion dimensions (pick the weakest 3-5 areas of the plan):
- **Integration breakage**: does step X's output get consumed correctly by step Y?
- **Implicit dependency**: does step X assume something the plan doesn't establish?
- **Collateral damage**: do unmentioned functions in modified files break?
- **State reachability**: do new state values get handled in all existing switch/if?
- **Deletion omission**: does "replace X" list all of X's reference sites?

#### S2 — Failure Reverse Reasoning

Trigger: plan + multi-step (>= 5 steps with dependencies).

```
Assume this plan has been fully executed:

1. Build failed. Given step dependencies, the most likely compile error is: {specific error, e.g., "Step 3 adds a Protocol requirement that Step 5's class must conform to, but Step 5 runs after Step 3 without adding the conformance"}. Which file reports the error? Is this covered by the plan?

2. Build passed, but a user performing {core operation from plan} hits a regression. Trace backward: {user action} → {code entry point file:line} → {failure point file:line}. The most likely regression is: {specific scenario}. Is this covered by the plan?

For each, cite the specific plan step. Uncovered items need plan updates.
```

#### S3 — Adversarial Architecture Review

Trigger: plan + architecture changes.

```
A tech lead familiar with this codebase reviewed this plan:

1. "{new entry point from plan} and the existing {old_entry_file:line} are two independent paths calling {core_function}. The plan doesn't describe a coordination mechanism."
2. "{replaced component} still has references at {file:line} and {file:line}. The plan's replacement checklist is incomplete."
3. "Step {N} adds a new {field/enum case} to {Model}, but {consumer_file:line}'s switch/if doesn't handle this new value."

Verify each (cite file:line). Confirmed items need plan updates.
```

#### U1 — Token Consistency

Trigger: plan + UI.

```
Verify all UI steps in this plan:

1. List every size, spacing, color, and font value each step will use
2. Check each against {DesignTokens file path}
3. Compare against {existing similar component path}'s patterns — identify inconsistencies

Output: | Step | UI Value | Token | Status |
Missing or inconsistent items need plan updates.
```

#### U2 — Extreme Rendering

Trigger: plan + UI.

```
Assume this plan is implemented. A user opens the screen with:
- Dynamic Type at AX5 (maximum accessibility size)
- Dark Mode
- iPhone SE (smallest screen)
- {data condition from plan, e.g., "list has 50 items" or "text is 500 Chinese characters"}

Walk through each UI component in the plan: which overflows? which text truncates? which spacing collapses to unusable? Cite specific plan steps and propose fixes.
```

#### R1 — Runtime Regression

Trigger: code change (`--diff` flag).

```
These code changes are complete (from git diff):

{key change summary: filename + what changed, 1 line per file}

A user performs {core operation affected by changes} but hits a runtime bug (not a compile error).

1. Most likely bug? Trace backward from user action to the changed code lines.
2. Do changes affect other features that depend on the same data/state but weren't modified?
3. Cold start (first launch, no existing data) vs hot path (existing data) — do changes behave consistently?

Cite specific file:line for each.
```

### DF Strategies

All DF strategies require a design document. If no design doc exists, skip all DF strategies.

#### D1 — Bidirectional Mapping

Trigger: design doc exists (always selected when DF applies).

```
A requirements analyst traced this plan against the design document. Verify each claim, then update the plan:

[Completeness: Design → Plan]
1. Design doc {section/paragraph ref} requires "{specific requirement text}", but no plan step covers this
2. Design doc {section} specifies {value/parameter/schema}, but the plan doesn't mention this value

[Fidelity: Plan → Design]
3. Plan step {N}'s {operation} reinterprets design doc {section}'s requirement — design says "{quote}", plan says "{plan text}"
4. Plan step {N} introduces {decision} that changes the design's intended {behavior/flow}

After verifying, build a complete bidirectional trace table:
| Design Requirement | Plan Step | Status (covered / missing / deviated) |
```

#### D2 — Hallucination Detection

Trigger: plan contains decisions not obviously derived from design.

```
A requirements analyst flagged plan decisions with no design doc basis. For each, verify (cite design doc section) whether it's "design left blank — ask user" or "design already specified — plan ignored it":

1. Plan step {N} decided {specific decision}, but design doc {section} does not authorize this. Design says: "{quote}"
2. Plan step {N} introduces {tech choice / interaction / default value} not covered in design
3. {assertion}

For each unauthorized decision, label:
- Design left blank → ask user before implementing
- Design already specified → update plan to match design
- Reasonable implementation detail → keep but label "implementation decision"
```

#### D3 — Implicit Context Extraction

Trigger: design doc has preconditions, constraints, or business rules.

```
A requirements analyst extracted implicit assumptions from the design doc that the plan doesn't address. Verify each:

[Implicit Preconditions]
1. Design doc {section}'s "{text}" implies precondition: {extracted assumption}. No plan step establishes this.
2. {assertion}

[Business Rules]
3. Design doc {section} describes rule "{rule content}", but plan step {N}'s implementation doesn't account for it.
4. {assertion}

After verification, list all implicit assumptions from the design doc and confirm plan coverage for each.
```

#### D4 — Granularity Audit

Trigger: plan step count differs significantly from design requirement count.

```
A requirements analyst compared step granularity between design doc and plan. Verify each:

[Improper Merging]
1. Design doc {section} describes {A → B → C} as three stages. Plan merges them into step {N}, losing {constraint/checkpoint from stage B}.
2. {assertion}

[Improper Splitting]
3. Design doc {section} treats {X} as an atomic operation. Plan splits it into steps {N} and {M}, introducing intermediate state "{description}" not considered in design.

For each granularity mismatch: what constraint is lost or what risk is introduced?
```

#### D5 — Boundary Scenario Coverage

Trigger: design doc mentions edge cases, error flows, or extreme conditions.

```
A requirements analyst extracted boundary scenarios from the design doc that the plan doesn't handle. Verify each:

1. Design doc {section} mentions {boundary scenario}, but plan step {N} only handles the happy path
2. Design doc {section}'s {requirement} under {extreme condition} — behavior undefined in plan
3. {assertion}

After verification, check if the design doc contains other boundary/error/edge scenarios not covered by the plan.
```

---

## Principles

1. **Assertions must be code-anchored**: every assertion must reference actual file paths, function names, or values from code read during generation. No generic placeholders.
2. **Specific > comprehensive**: 3 concrete assertions beat 10 vague ones.
3. **Generate only, never execute**: this skill outputs a prompt. Verification happens when the user pastes it into the target session.
4. **Strategies combine into one prompt**: when multiple strategies are selected, merge all assertions into a single output prompt (not multiple separate prompts).
5. **Assertion diversity**: assertions within one prompt should cover different dimensions (integration / state / deletion / dependency), not repeat the same type.
6. **Role separation strengthens VF**: each prompt template uses a different external role ("reviewer", "tech lead", "requirements analyst") to maximize the egocentric bias override.
