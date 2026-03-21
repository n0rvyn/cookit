---
name: verify-plan
description: "Use when a plan has been written and needs validation before execution, or the user says 'verify plan', 'check the plan', 'review the plan', 'validate plan', '检查计划', '验证计划'. Applies Verification-First method with falsifiable error candidates, failure reverse reasoning, optional Design Token consistency checks, Design Faithfulness anchoring, and Architecture Review."
---

## Overview

This skill dispatches the `dev-workflow:plan-verifier` agent to validate an implementation plan in a separate context so it starts with a fresh, unbiased perspective.

**Optional flag: `--fast`**
When passed: use Sonnet instead of Opus for verification.
Appropriate for plans with < 5 tasks or simple single-concern changes.
Default (no flag): Opus for thorough verification.

## Process

### Step 1: Gather Context

Collect the following before dispatching:

1. **Plan file path** — identify from:
   - Most recent `write-plan` output in conversation
   - User-specified path
   - Search `docs/06-plans/*-plan.md` for recent plan files
2. **Design doc path** — check the plan header for a `Design doc:` reference; if none, set to "none"
3. **Design analysis path** — check the plan header for a `Design analysis:` reference; if none, search `docs/06-plans/*-design-analysis.md`; if none found, set to "none"
4. **Crystal file path** — resolve in this order:
   - If the plan header has a `Crystal file:` reference → use that path
   - Else search `docs/11-crystals/*-crystal.md`: if exactly 1 file → use it automatically
   - If multiple files → ask the user which one applies
   - If no files → set to "none"
5. **Project root** — current working directory

If the plan file path is unclear, ask the user.

### Step 1.5: Retrieve Error Patterns (if search tool available)

After collecting plan and design doc paths, extract technical keywords from the plan (framework names, API names, component names found in the plan file) and search for known error patterns:

1. Call `search(query="<technical keywords from plan>", source_type=["error", "lesson"], project_root="<cwd>")`
2. If results are returned: collect them as `retrieved_context` — a compact list of (source_path, section, content preview) for each hit
3. If the search tool is unavailable or returns no results: set `retrieved_context` to empty and continue

### Step 2: Dispatch Agent

Use the Task tool to launch the `dev-workflow:plan-verifier` agent:
- Default (no --fast): add `model: "opus"` to the Task tool call
- With --fast flag: add `model: "sonnet"` to the Task tool call

Note: must explicitly set model; the parent session runs Sonnet and inheritance gives Sonnet, not Opus.

Before dispatching, extract any **previously resolved decisions** from the plan file:
- Search the plan's `## Decisions` section for entries with `**Chosen:**` (not just `**Recommendation:**`)
- Build a summary list: `DP-xxx: Title → User chose Option {A|B|C}`
- If no resolved decisions exist, set to "none"

Structure the task prompt as:

```
Verify this implementation plan:

Plan file: {path}
Design doc: {path or "none"}
Design analysis: {path or "none"}
Crystal file: {path or "none"}
Project root: {path}

Plugin agents dir: !`echo "${CLAUDE_PLUGIN_ROOT}/agents"`
Previously resolved decisions (do not re-ask these):
{List of "DP-xxx: Title → Chosen Option X" or "none"}

Retrieved error patterns and lessons (from knowledge base):
{retrieved_context — one entry per line, or "none" if empty}
```

### Step 3: Present Results

When the agent completes:

1. The agent returns a compact summary with verdict, issue counts, and report file path
2. Present the summary to the user
3. Report the verdict:
   - **Approved** — proceed to Step 4
   - **Must revise** — the summary includes revision items; apply revisions to the plan, then re-dispatch the verifier (max 2 revision cycles)
4. For detailed analysis: read the full report at the path returned by the agent
5. **Decision Points:** Check the agent's return for `Decisions:` count.
   - If Decisions > 0: read the `## Decisions` section from the verification report
   - For each `blocking` decision: present to user via AskUserQuestion with options from the decision point
   - For `recommended` decisions: present as a group via a single AskUserQuestion. **Critical:** all DP summaries must be inside the `question` field text — text printed before AskUserQuestion gets visually covered by the question widget. Format the question field as:
     ```
     验证发现 {N} 个推荐决策：\n\n- DP-xxx: {title} → 推荐 {option} ({reason})\n- DP-yyy: {title} → 推荐 {option} ({reason})\n\n全部接受默认还是逐个审查？
     ```
   - If the user does NOT choose "Accept all defaults": present each DP individually via separate AskUserQuestion calls. Do not assume any DP is accepted until the user explicitly confirms it
   - Record user choices: edit the verification report, replace `**Recommendation:**` with `**Chosen:** {user's choice}`
   - Then proceed to Step 4

### Step 4: Mark Verified

When the plan is approved:

1. Append a verification marker to the end of the plan file:

```markdown

---
## Verification
- **Verdict:** Approved
- **Date:** {YYYY-MM-DD}
```

2. Suggest next step: `dev-workflow:execute-plan`

## Completion Criteria

- Plan file has `## Verification` section with `Verdict: Approved` appended
- Or: user explicitly chose to proceed after 2 revision cycles (verdict noted as "partial")
