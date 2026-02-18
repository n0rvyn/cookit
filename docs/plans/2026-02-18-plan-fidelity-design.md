# Plan-to-Implementation Fidelity System

> Design Document | 2026-02-18
> Applies to: `dev-workflow` and `ios-development` plugins in cookit

## Problem

When Claude Code executes implementation plans, five types of gaps consistently appear between the design document and the final implementation:

| Type | Description | Example |
|------|-------------|---------|
| **A: Spec values wrong** | Implementation uses different values than design specifies | Design says maxTurns=50, code has maxTurns=10 |
| **B: Not wired** | New component exists but isn't connected to data flow | EventQueue pushes events but nothing notifies sidecar |
| **C: Old code not removed** | Design says delete X, but X still exists and may conflict | L2 summarizer still active after Perception agent replaces it |
| **D: Not built** | Design requires feature, plan omits it entirely | CEO periodic patrol timer missing from plan |
| **E: Degraded** | Feature implemented but as crude simplification of design's approach | Design specifies AsyncQueue + streamInput, implemented as sequential queries |

### Root Cause

The design doc **exits the context window during execution**. The workflow is:

```
Design Doc (500+ lines of intent, algorithms, parameter matrices)
     ↓ writing-plans / /plan compresses it
Plan (200 lines of tasks, steps, code snippets)
     ↓ executing-plans reads task by task
Task (30 lines — "do X in file Y")
     ↓ Claude implements
Code
```

Each stage is a lossy compression. By the time Claude writes code, it has only a task description with no access to the design doc's schema specs, parameter matrices, algorithm descriptions, or deletion requirements. When the task is ambiguous, Claude improvises from training data instead of flagging.

## Solution: Three-Layer Defense

### Layer 1: Enhanced Plan Verification (pre-execution)

**Component:** Enhanced `verifying-plans` skill in `dev-workflow`

Before execution begins, verify the plan against the design doc and enrich it with design references that survive into execution.

**Changes to existing `verifying-plans`:**

1. Add **DF (Design Faithfulness)** strategy — triggered when plan references a design document:
   - Bidirectional mapping: every design requirement → plan task, every plan task → design requirement
   - For each plan task, generate design anchors:
     - `Design ref:` — specific design doc file:line-range
     - `Expected values:` — concrete values from design (parameters, schemas, enums)
     - `Replaces:` — old code this task supersedes (file:line)
     - `Data flow:` — upstream→component→downstream path
     - `Quality markers:` — implementation approach from design (algorithms, data structures, patterns)
     - `Verify after:` — concrete post-implementation checks

2. Absorb **AR (Architecture Review)** strategy — from existing `reviewing-architecture` skill:
   - Entry point uniqueness check
   - Replacement completeness check
   - Data flow tracing
   - Fallback three-question validation

3. Update trigger to cover both plan modes:
   - After Claude Code `/plan` mode approval
   - After `superpowers:writing-plans` completion
   - Manual invocation

**Resulting strategy matrix:**

| Strategy | Trigger | Catches |
|----------|---------|---------|
| S1 (specific error candidates) | Always | Integration breaks, implicit dependencies, state reachability |
| S2 (failure reverse reasoning) | Multi-step plans | Build failures, runtime regressions |
| U1 (Design Token consistency) | UI plans | Visual inconsistency |
| DF (Design Faithfulness) | Plan references design doc | Gaps A, B, C, D, E |
| AR (Architecture Review) | Architectural changes | Parallel paths, incomplete replacements, dead fallbacks |

**What happens to `reviewing-architecture`:** Absorbed into `verifying-plans` as AR strategy. Can be deprecated as standalone skill (or kept for ad-hoc use).

### Layer 2: Execution-Time Guard (during execution)

**Component:** CLAUDE.md template addition via `project-kickoff.md`

When executing enriched plan tasks, Claude follows design anchor instructions.

**Addition to CLAUDE.md template (project-kickoff.md §8.2):**

```markdown
## Plan Execution with Design References

When executing a plan task that contains design anchor fields:

| Field | Action |
|-------|--------|
| `Design ref:` | Read the referenced design doc sections before implementing |
| `Expected values:` | After implementing, verify each value matches |
| `Replaces:` | After implementing, Grep for old code references, confirm handled |
| `Data flow:` | After implementing, trace path end-to-end, confirm connectivity |
| `Quality markers:` | During implementation, use specified approach, do not simplify |
| `Verify after:` | After implementing, execute each checklist item |

Gray areas not covered by the plan: ask the user, do not improvise.
```

This is also added directly to Archon's CLAUDE.md (since Archon is an existing project).

### Layer 3: Post-Execution Audit (after execution)

**Component:** New `implementation-reviewer` agent in `dev-workflow` + enhanced `execution-review` command

After all plan tasks complete, a comprehensive audit of the implementation against plan AND design doc.

**Agent: `dev-workflow/agents/implementation-reviewer.md`**

- Model: opus (deepest analysis)
- Tools: Glob, Grep, Read, Bash (read-only + build verification)
- Trigger: after plan execution completes, or manual invocation

**Agent scope** (merges existing `execution-review` + new design fidelity audit):

From existing `execution-review` (13 sections, all platform-agnostic):
1. Deletion verification
2. Struct/interface field comparison
3. UI element verification (when applicable)
4. "No matches found" = red flag
5. Integration point verification
6. Never trust existing code
7. 自作主张 detection
8. Conditional branch verification
9. Removal-replacement reachability
10. Term consistency after rename
11. ADR action completeness
12. Reverse regression reasoning
13. Rules compliance audit (R6, R9, decision authority)

New: Design fidelity audit (when design doc exists):
14. Spec value comparison (Gap A)
15. Data flow connectivity tracing (Gap B)
16. Old code removal completeness (Gap C)
17. Missing feature detection (Gap D)
18. Implementation quality comparison (Gap E)

**Output format for design fidelity:**

```
[A - Spec Value] {design:line} Expected: X, Actual: Y — ✅ / ❌
[B - Not Wired] {design:line} Component→downstream — ✅ connected / ❌ disconnected
[C - Old Code] {design:line} "Delete X" — ✅ removed / ❌ still at {file:line}
[D - Not Built] {design:line} Feature — ✅ found / ❌ missing
[E - Degraded] {design:line} Design: {approach}, Code: {actual} — ✅ faithful / ❌ simplified
```

**What happens to ios-development's `execution-review`:** Becomes a thin wrapper that:
1. Invokes `dev-workflow:implementation-reviewer` agent
2. Adds iOS-specific code scan (String(localized:), @MainActor, Protocol abstractions)

## Component Map

| Layer | Component | Location | Type | Status |
|-------|-----------|----------|------|--------|
| 1 | `verifying-plans` | dev-workflow/skills/ | skill | Modified: add DF + AR strategies |
| 1 | `reviewing-architecture` | dev-workflow/skills/ | skill | Absorbed into verifying-plans; keep or deprecate |
| 2 | CLAUDE.md template | ios-development/commands/project-kickoff.md §8.2 | template | Modified: add plan execution rules section |
| 2 | Project CLAUDE.md | Each project's CLAUDE.md | config | Modified: add plan execution rules |
| 3 | `implementation-reviewer` | dev-workflow/agents/ | agent | New |
| 3 | `execution-review` | ios-development/commands/ | command | Modified: thin wrapper around agent + iOS checks |

## How Each Gap Type Is Addressed

```
                    Layer 1              Layer 2              Layer 3
                    (verifying-plans)    (CLAUDE.md)          (implementation-reviewer)

A: Wrong values     DF catches missing   "Expected values"    Spec Value audit
                    value specs in plan  forces comparison    catches mismatches

B: Not wired        DF + AR trace data   "Data flow" forces   Not Wired audit
                    flow in plan         e2e check            traces connectivity

C: Old code         DF maps "delete X"   "Replaces" forces    Old Code audit +
                    to plan tasks        Grep verification    Deletion Verification

D: Not built        DF bidirectional     (Layer 1 prevents)   Not Built audit
                    mapping catches                           (defense in depth)

E: Degraded         DF "Quality markers" "Quality markers"    Degraded audit
                    specify approach     guides implementation compares design vs code
```

## Limitations

What this system CANNOT fully prevent:
- Claude may still not follow CLAUDE.md instructions (Layer 2 weakness)
- Auto-triggering of skills/agents is unreliable (Claude may not invoke them)
- Gap E (degraded implementation) requires understanding design intent — the hardest to catch mechanically
- The enriched plan adds overhead to plan writing time

Mitigations:
- Layer 3 (manual invocation) is the safety net for auto-trigger failures
- Quality markers in Layer 1 make Gap E more detectable (concrete patterns vs abstract intent)
- The overhead pays for itself by eliminating remediation rounds
