# skill-audit

Review Claude Code plugins, skills, agents, hooks, and commands from the AI executor perspective.

## Claude Code

Install from indie-toolkit marketplace:

```bash
/plugin install skill-audit@indie-toolkit
```

## Usage

- `/plugin-review` — orchestrates plugin review across 9 dimensions with intelligent routing

## Architecture

The plugin-review skill detects whether the optional `plugin-dev` plugin is installed and routes accordingly:

**Strategy A** (plugin-dev available): dispatches `plugin-dev:plugin-validator` + `plugin-dev:skill-reviewer` + own `plugin-reviewer` in parallel, then merges into a unified report. Avoids redundant structural and trigger checks.

**Strategy B** (plugin-dev not installed): dispatches own `plugin-reviewer` with supporting files (`structural-validation.md`, `trigger-baseline.md`) to cover all 9 dimensions independently.

Both strategies produce identical report format.

## Agents

| Agent | Model | Description |
|-------|-------|-------------|
| plugin-reviewer | opus | Deep review from AI executor perspective: workflow logic, execution feasibility, edge cases, dispatch loops, spec compliance, metadata sync, eval.md validation, Trigger Health Score. Conditionally loads D1/D2 and baseline trigger checks from supporting files when plugin-dev is unavailable. |

### Supporting Files (not agents)

| File | Loaded when | Content |
|------|------------|---------|
| structural-validation.md | plugin-dev unavailable | D1 Structural Validation + D2 Reference Integrity |
| trigger-baseline.md | plugin-dev unavailable | D5.1-5.2 description overlap + D7.3 description quality + D9.1 trigger quality |

## Skills

| Skill | Description |
|-------|-------------|
| plugin-review | Orchestrates plugin review with Strategy A/B routing. Supports eval.md files for trigger plausibility checking. |

## Review Dimensions

| # | Dimension | Strategy A Owner | Strategy B Owner |
|---|-----------|-----------------|-----------------|
| D1 | Structural Validation | plugin-dev:plugin-validator | plugin-reviewer + structural-validation.md |
| D2 | Reference Integrity | plugin-dev:plugin-validator | plugin-reviewer + structural-validation.md |
| D3 | Workflow Logic | plugin-reviewer (core) | plugin-reviewer (core) |
| D4 | Execution Feasibility | plugin-reviewer (core) | plugin-reviewer (core) |
| D5 | Trigger & Routing | split: baseline → skill-reviewer; deep → plugin-reviewer | plugin-reviewer (full) |
| D6 | Edge Cases & False Results | plugin-reviewer (core) | plugin-reviewer (core) |
| D7 | Spec Compliance | split: D7.3 → skill-reviewer; rest → plugin-reviewer | plugin-reviewer (full) |
| D8 | Metadata & Docs | plugin-reviewer (core) | plugin-reviewer (core) |
| D9 | Trigger Quality | split: D9.1 → skill-reviewer; rest → plugin-reviewer | plugin-reviewer (full) |

## Trigger Health Score

After running `/plugin-review`, the report includes a per-skill trigger health assessment:

| Skill | Description Quality | Eval Coverage | Conflict Check | Verdict |
|-------|--------------------|---------------|----------------|---------|
| skill-name | pass/warn/fail | pass/fail/N/A | pass/warn/fail | overall |
