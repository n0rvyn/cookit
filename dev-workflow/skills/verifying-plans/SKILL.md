---
name: verifying-plans
description: "Use when a plan has been written and is about to be executed, or the user says 'verify plan'. Applies Verification-First method with falsifiable error candidates, failure reverse reasoning, optional Design Token consistency checks, Design Faithfulness anchoring, and Architecture Review."
---

## Trigger

- Plan mode: plan written, about to execute
- User says "verify plan", "check the plan", "验证一下计划"
- After Claude Code `/plan` mode approval
- After `superpowers:writing-plans` completion

## Principle

Verification (backward reasoning) has lower cognitive load than generation (forward reasoning), and produces information complementary to forward reasoning. Criticizing external input activates critical thinking more than self-review. Therefore: **make concrete falsifiable assertions, not abstract checklists.**

## Process

### 1. Plan Classification

Read the current plan, classify (may overlap):

| Type | Signal | Strategies |
|------|--------|------------|
| Architecture change | New Service/Agent/Tool, data flow change, new entry point, component replacement | S1 + S2 + AR |
| Feature development | New/modified feature, changed existing behavior | S1 |
| UI development | New/modified View, component styling, layout | S1 + U1 |
| Multi-step execution | Steps >= 5 with compile/runtime dependencies | S2 |
| Design-backed plan | Plan references a design document | DF |

### 2. Execute Applicable Strategies

---

#### S1. Specific Error Candidate Verification

**Purpose:** Trigger backward reasoning by verifying specific error assertions.

Steps:
1. Based on plan content and codebase state, **generate 3-5 specific, falsifiable error assertions**
2. Each assertion must include: specific step number + specific file/function + specific failure consequence
3. Verify each by reading code, citing file:line

**Assertion generation rules:**
- Must be specific enough to prove/disprove by reading code ("might have edge case issues" = too abstract, forbidden)
- Cover these dimensions (pick the weakest 3-5):
  - Integration break: Does step X's output get correctly referenced by step Y's consumer?
  - Implicit dependency: Does step X assume a precondition the plan doesn't establish?
  - Old code impact: In files the plan modifies, do unmentioned functions get affected?
  - State reachability: Do existing switch/if statements cover new state values the plan introduces?
  - Deletion omission: Plan says "replace X" but doesn't list all reference sites of X?

**Output:**

```
[Assertion 1] Step {N}: {specific error, e.g. "FeynmanStudentAgent not registered in LearningOrchestrator.registerAgents(), so it won't be invoked in Feynman mode"}
Verification: Read {file:line}
Result: ✅ assertion disproved ({evidence}) / ❌ assertion confirmed → plan needs: {specific revision}

[Assertion 2] ...
```

**Key:** Even if all assertions are disproved, the verification process itself produced reasoning paths not covered by forward planning. If disproving an assertion reveals a **different problem**, record it.

---

#### S2. Failure Reverse Reasoning

**Purpose:** Reason backward from execution results to plan defects, catching step dependencies and ordering issues.

Steps:
1. Assume plan executed but build fails — what is the most likely compile error? (cite specific steps and files)
2. Assume build passes but runtime regression occurs — what is the most likely regression? (cite specific user action paths)
3. For each inferred failure, check if plan already covers it

**Output:**

```
[Build Failure Reasoning]
Hypothetical failure: {specific error, e.g. "Step 3's new Protocol requires Step 5's class to conform, but Step 5 modifies that class after Step 3"}
Plan coverage: ✅ Step {N} handles this / ❌ not covered → plan needs: {specific revision}

[Runtime Regression Reasoning]
Hypothetical regression: {specific scenario, e.g. "User taps Ask in Feynman mode, but new guard check returns early when session.state == .paused, making button unresponsive"}
Action path: {user action} → {code entry file:line} → {failure point file:line}
Plan coverage: ✅ / ❌ → plan needs: {specific revision}
```

---

#### U1. Design Token Consistency Verification (UI plans)

**Purpose:** Verify all visual values in UI plans have token backing.

Steps:
1. Read `DesignTokens.swift` (or project's design system file)
2. Extract all UI-related steps from plan, list each step's sizes/spacing/colors/font sizes
3. Look up each value in the design token system

**Output:**

```
[Token Check]
| Step | UI Value | Token | Status |
|------|----------|-------|--------|
| Step 3 | Card corner radius | CardStyle.cornerRadius | ✅ |
| Step 3 | Card padding | — | ⚠️ missing |
| Step 5 | Title font | .headline | ✅ |

Missing items:
- Card padding: plan must specify — new token or reuse from Spacing?
```

Supplementary check (when existing Views of the same type exist in the directory):
- Read existing peer components, extract their spacing/color/corner radius patterns
- Verify plan's new component follows the same patterns
- Inconsistency: intentional deviation / omission

---

#### DF. Design Faithfulness Verification (design-backed plans)

**Purpose:** Ensure the plan faithfully represents the design doc. Catch gaps A-E before execution begins.

**Prerequisite:** Read the referenced design document in full.

Steps:

**Step 1: Bidirectional Mapping**

Build two lists:
- Forward: Every requirement in the design doc → which plan task covers it
- Backward: Every plan task → which design requirement it implements

```
[DF Mapping]
Design requirements: N
Mapped to plan tasks: M
Unmapped (Gap D candidates): {list with design_file:line}

Plan tasks: P
Mapped to design requirements: Q
Unmapped (outside design scope): {list — verify intentional}
```

**Step 2: Design Anchors**

For each plan task mapped to a design requirement, verify or generate these anchor fields:

| Anchor | What to check |
|--------|--------------|
| `Design ref:` | Does the plan task cite the specific design doc section? If not, add it |
| `Expected values:` | Does the design specify concrete values (parameters, schemas, enums) for this task? If yes, are they in the plan? |
| `Replaces:` | Does this task supersede old code? If yes, does the plan list the old code locations? |
| `Data flow:` | Does the design specify upstream→component→downstream? If yes, is it in the plan? |
| `Quality markers:` | Does the design specify an algorithm, data structure, or approach? If yes, is it in the plan? |
| `Verify after:` | What concrete checks should the implementer run after this task? |

**Output per task:**

```
[DF Anchors] Task {N}: {task title}
Design ref: {design_file:line-range} — ✅ cited / ⚠️ missing, should be: {ref}
Expected values: {value list} — ✅ in plan / ⚠️ missing: {values}
Replaces: {old code} — ✅ listed / ⚠️ missing: {locations found by Grep}
Data flow: {path} — ✅ specified / ⚠️ missing: {path from design}
Quality markers: {approach} — ✅ specified / ⚠️ missing: {approach from design}
Verify after: {checks} — ✅ present / ⚠️ suggest: {checks}
```

**Step 3: Gap Scan**

Specifically check for each gap type:
- **Gap A (wrong values):** Any design value not mentioned in the plan
- **Gap B (not wired):** Any component in the plan without explicit data flow path
- **Gap C (old code):** Any "replace/delete" in the design without a corresponding plan task listing removal targets
- **Gap D (not built):** Any design requirement without a plan task (from Step 1)
- **Gap E (degraded):** Any design algorithm/approach where the plan's task description is vague enough to allow simplification

---

#### AR. Architecture Review (architectural changes)

**Purpose:** Detect parallel paths, incomplete replacements, and dead fallbacks. Absorbed from `reviewing-architecture` skill.

**AR.1 Entry Point Uniqueness Check**

For each new entry point (trigger, scheduler, observer, event handler) in the plan:
- Identify the core function this entry point ultimately calls
- Grep for all existing callers of that core function AND its key sub-functions

```
[Entry Point Check] Plan adds: {new entry point}
Target core function: {function name}
Existing callers:
- {file:line} — {caller description}
- {file:line} — {caller description}
Conclusion: ✅ no parallel paths / ⚠️ {N} existing paths — need merge or coexistence justification
```

If existing callers found on different upstream paths and plan doesn't address it → stop, report conflict.

**AR.2 Replacement Completeness Check**

For each "replace/deprecate/supersede" in the plan or referenced ADRs:
- List concrete items to delete/modify:

```
[Replacement Checklist] {old component} → {new component}
Delete:
- [ ] {file}: {method/config} — {purpose}
- [ ] {file}: {registration/import} — {purpose}
Modify:
- [ ] {file:line}: {old reference} → {new reference}
```

If the plan lacks this checklist → flag as incomplete, build the checklist by Grep.

**AR.3 Data Flow Tracing**

For the primary data being modified:
- Trace from source to sink:

```
[Data Flow] {data name}
Produced: {file:line} ({how})
Processed: {file:line} → {file:line} ({transformations})
Persisted: {file:line} ({storage})
Displayed: {file:line} ({UI})
```

At each node, search for other upstream callers (= parallel paths). Parallel path without coordination = architectural conflict.

**AR.4 Fallback Validation**

For any "keep as fallback" in the plan or existing code:

```
[Fallback Three Questions] {component kept as fallback}
1. Coordination: Who decides which path? — {specific code location / "none"}
2. Trigger: What condition activates the old path? — {evaluable boolean / "none"}
3. Removal: When to delete? — {verifiable milestone / "none"}
Conclusion: ✅ all three answered / ❌ {N} unanswered → recommend user decide whether to delete old implementation
```

"Runtime decides" / "when new path fails" / "after testing passes" = descriptive answer = no answer.

---

### 3. Summary and Plan Revision Recommendations

```
## Plan Verification Summary

### Strategies Executed
- S1 Specific error candidates: generated {N}, confirmed {M}
- S2 Failure reverse reasoning: build failures {N}, runtime regressions {N}
- U1 Token consistency: checked {N}, missing {M}
- DF Design Faithfulness: requirements mapped {N}/{total}, anchors missing {M}
- AR Architecture Review: entry point conflicts {N}, replacement checklists {complete/incomplete}

### Must Revise (verification-confirmed issues)
1. [Step X] {specific revision}
   Basis: {which S1/S2/U1/DF/AR check}

### Recommended Additions (risks exposed during verification)
1. [Step X] {addition}
   Basis: {information discovered during verification}

### No Revision Needed (verification-passed items)
- {list key assertions that passed, proving the plan is adequate in these areas}
```

---

## Principles

1. **Specific > Abstract:** Every assertion must be provable/disprovable by reading code. "Might have issues" = invalid assertion
2. **Code-anchored:** All verification results must cite file:line, never speculation
3. **Wrong is still useful:** Disproved assertions are not failures; the reasoning paths they produce are the value
4. **Does not replace other reviews:** This verifies plan completeness and correctness only, not code quality, UI compliance, or architecture (those are `/code-review`, `/ui-review`, and the `implementation-reviewer` agent's jobs)
5. **Recommend, don't execute:** Output revision recommendations only. User confirms before updating the plan
