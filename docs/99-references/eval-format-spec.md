# Eval.md Format Specification

## Canonical Format

```markdown
# {skill-name} Eval

## Trigger Tests
<!-- Prompts that SHOULD trigger this skill -->
- "{prompt 1}"
- "{prompt 2}"

## Negative Trigger Tests
<!-- Prompts that should NOT trigger this skill -->
- "{prompt that might false-positive}"

## Output Assertions
<!-- What must be true in the skill's output -->
- [ ] {assertion 1}
- [ ] {assertion 2}

## Redundancy Risk
<!-- For capability-uplift skills only -->
Baseline comparison: {notes on whether base model can do this without the skill}
Last tested model: {model version}
Last tested date: {date}
Verdict: {essential / monitor / likely-redundant}
```

## Format Components

### 1. Trigger Tests (Required, minimum 2)
- Format: `- "prompt text"` (quoted, list item)
- Purpose: Prompts that SHOULD trigger this skill
- Derive from skill description's "Use when" clause
- Include variations the skill should recognize

### 2. Negative Trigger Tests (Required, minimum 1)
- Format: `- "prompt text"` (quoted, list item)
- Purpose: Prompts that should NOT trigger this skill (false positive prevention)
- Include prompts that might match but should dispatch to different skill

### 3. Output Assertions (Required, minimum 2)
- Format: `- [ ] assertion text` (checkbox, list item)
- Purpose: What must be true in the skill's output
- Cover: file creation, structure, key content, verification gates

### 4. Redundancy Risk (Conditional)
- For: capability-uplift skills only (skills that teach techniques model might now know)
- Fields:
  - `Baseline comparison:` Can base model do this without the skill?
  - `Last tested model:` Model version when tested
  - `Last tested date:` Date of last comparison
  - `Verdict:` essential | monitor | likely-redundant

## Machine Parseable Format

**Trigger tests:** Lines matching `^- ".*"` under `## Trigger Tests`
**Negative triggers:** Lines matching `^- ".*"` under `## Negative Trigger Tests`
**Assertions:** Lines matching `^- \[ \] .*$` under `## Output Assertions`

## Example (fix-bug)

```markdown
# fix-bug Eval

## Trigger Tests
- "I'm getting this error: [stack trace]"
- "The app crashes when I tap save, here's a screenshot"
- "Build fails with 'ambiguous reference' after my changes"

## Negative Trigger Tests
- "Add a new feature to export data"
- "Refactor this code to be cleaner"

## Output Assertions
- [ ] Output includes Step 7 mandatory gate: plan created before any fix is applied
- [ ] Output includes Step 10 tradeoff report for the proposed fix
- [ ] Root cause includes code evidence (file:line references)

## Redundancy Risk
Baseline comparison: Base model can diagnose errors but lacks systematic value-domain tracing and parallel path detection methodology
Last tested model: Opus 4.6
Last tested date: 2026-03-08
Verdict: essential
```
