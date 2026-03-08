# Plugin Quality & Testing Infrastructure — Development Guide

**Design input:** Conversation audit of 2026-03-07 (6 plugins, 60+ skills/agents)
**User decisions:**
- Redundant skills: all retained, eval data decides
- Testing: skill-audit static review + Skill Creator dynamic eval, combined
- Language: English-first; Chinese keywords only where evaluated as necessary (mactools retains existing Chinese)
- Scope: all 6 plugins, phased

## Global Constraints

- This is a **prompt-level refactoring** project — no new runtime code, no new plugins
- All changes are to SKILL.md frontmatter/descriptions, agent.md descriptions, and skill-audit plugin capabilities
- Existing skill behavior (prompt body) is NOT modified unless a trigger description change requires adjusting the opening paragraph
- Language standard: English-first for all development skills; Chinese keywords only added where evaluation confirms necessity (mactools retains existing Chinese descriptions, adds English keywords where missing)
- No skill deletions in this project — redundancy is tracked via eval, not assumed
- Marketplace compatibility: all description changes must remain valid for Claude Code plugin registry format
- Existing hooks are not modified

## Architecture Decisions

- **Eval storage:** Eval prompts and assertions live inside each skill directory as `eval.md` (co-located, not centralized) — keeps eval close to the skill it tests, easy to maintain
- **skill-audit extension:** Add a new `trigger-review` dimension to the existing `plugin-reviewer` agent rather than creating a new agent — avoids agent proliferation
- **Blind comparison:** Deferred to Skill Creator plugin (external tool); this project only prepares the eval prompts that Skill Creator can consume
- **Redundancy tracking:** Each high-risk skill gets a `## Redundancy Risk` section in its eval.md with baseline comparison notes — machine-readable for future automation

---

## Phase 1: Trigger Description Standardization

**Status:** ✅ Completed — 2026-03-08

**Goal:** All 60+ skills and 20+ agents have clear, specific English descriptions with explicit trigger scenarios. mactools retains Chinese, adds English where missing.

**Depends on:** None

**Scope:**
- Audit every SKILL.md `description:` field across all 6 plugins
- Define the canonical description format:
  ```
  description: "Use when {trigger scenario}. {What it does in one sentence}."
  ```
- Fix the 5 worst descriptions identified in the audit:
  - `ios-development/design-review` — add trigger scenarios (currently just a vague noun phrase)
  - `ios-development/localization-setup` — add specificity (currently "Provide ... guidance")
  - `ios-development/testing-guide` — add trigger scenarios (currently "Provide ... guidance")
  - `ios-development/swiftdata-patterns` — add trigger scenarios (currently "Provide ... guidance")
  - `ios-development/execution-review` — add English trigger scenarios (currently Chinese-only)
- Standardize all remaining descriptions: every description must have a concrete trigger scenario, not just a capability statement
- For mactools skills: retain existing Chinese, add English trigger keywords where missing (for marketplace discoverability)
- For dev-workflow skills: most already good, tighten any vague ones
- For product-lens skills: already good, no major changes expected
- Update agent `.md` description fields: ensure each has trigger examples showing when to dispatch

**Acceptance criteria:**
- [x] Every SKILL.md across all 6 plugins has a `description:` starting with "Use when/for/after/before" or equivalent concrete trigger
- [x] No SKILL.md description contains words like "optional", "guidance", "best practices" as the ONLY content (without a concrete trigger scenario)
- [x] mactools skills all have both Chinese AND English in their descriptions
- [x] Every agent .md has at least one example in its description showing when to dispatch it
- [x] Grep verification: `grep -rL 'Use when\|Use for\|Use after\|Use before\|当.*时使用' */skills/*/SKILL.md` returns zero results

**Review checklist:**
- [x] /implementation-review (0 critical gaps, 1 standard gap accepted)

---

## Phase 2: Eval Infrastructure — eval.md per Skill

**Status:** ✅ Completed — 2026-03-08

**Goal:** Every high-frequency and high-risk skill has co-located eval prompts with assertions, ready for both skill-audit static review and Skill Creator dynamic testing.

**Depends on:** Phase 1 (descriptions must be stable before writing trigger evals)

**Scope:**
- Define the `eval.md` format spec:
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
- Create eval.md for P0 skills (daily use, 15 skills):
  - dev-workflow: `fix-bug`, `write-plan`, `verify-plan`, `execute-plan`, `commit`, `run-phase`, `brainstorm`, `design-decision`, `handoff`, `crystallize`
  - ios-development: `ios-swift-context`, `submission-preview`
  - product-lens: `evaluate`, `demand-check`
  - skill-audit: `plugin-review`
- Create eval.md for P1 skills (high-risk redundancy, 2 additional):
  - dev-workflow: `parallel-agents`, `use-worktree`
- Mark redundancy risk for the 6 identified high-risk skills:
  - `brainstorm`, `design-decision`, `parallel-agents`, `use-worktree`, `handoff`, `crystallize`

**Acceptance criteria:**
- [x] 17 skills have `eval.md` files co-located in their skill directory
- [x] Every eval.md has at least 2 trigger tests, 1 negative trigger test, and 2 output assertions
- [x] All 6 high-risk skills have a `## Redundancy Risk` section with `Verdict:` field
- [x] eval.md format is machine-parseable: trigger tests are `- "quoted"`, assertions are `- [ ] text`

**Review checklist:**
- [x] /implementation-review (0 gaps)

---

## Phase 3: skill-audit Plugin Extension — Trigger Quality Review

**Status:** ✅ Completed — 2026-03-08

**Goal:** The existing `plugin-reviewer` agent gains a new review dimension that checks trigger description quality, and can consume eval.md files for automated trigger accuracy testing.

**Depends on:** Phase 2 (eval.md format must be defined)

**Scope:**
- Extend `skill-audit/agents/plugin-reviewer.md` with a new section: **Trigger Quality Review**
  - Checks: description has bilingual content, trigger scenarios are specific, no vague words without concrete scenarios
  - Checks: if eval.md exists, verify trigger test prompts would plausibly match the description
  - Checks: negative trigger tests don't overlap with other skills' positive triggers (cross-skill conflict detection)
- Extend `skill-audit/skills/plugin-review/SKILL.md` to pass eval.md content to the agent when available
- Add a summary output section to plugin-reviewer: **Trigger Health Score** (pass/warn/fail per skill)
- Update skill-audit README.md with the new capability

**Acceptance criteria:**
- [x] `/plugin-review` on a plugin with eval.md files produces a Trigger Health Score section
- [x] Cross-skill trigger conflict detection flags at least one known ambiguity (e.g., `design-review` vs `ui-review` in ios-development)
- [x] Plugin review without eval.md files still works (graceful degradation, no errors)
- [x] README.md documents the new trigger review dimension

**Review checklist:**
- [x] /plugin-review (self-review: run the updated reviewer on skill-audit itself — pass)

---

## Phase 4: Remaining Plugin Coverage + Baseline Documentation

**Status:** ✅ Completed — 2026-03-08

**Goal:** All 6 plugins have complete eval coverage for their remaining skills, and a baseline document records the current state for future model upgrade comparisons.

**Depends on:** Phase 2 (format established), Phase 3 (reviewer can validate)

**Scope:**
- Create eval.md for all remaining skills not covered in Phase 2:
  - dev-workflow: `collect-lesson`, `design-drift`, `docs-rag`, `finish-branch`, `write-dev-guide`, `write-feature-spec`, `generate-vf-prompt`, `reviewing-rules`, `understand-design`, `generate-design-prompt`
  - ios-development: `design-review`, `feature-review`, `ui-review`, `appstoreconnect-review`, `localization-setup`, `testing-guide`, `swiftdata-patterns`, `fetch-swift-api-updates`, `generate-design-system`, `generate-stitch-prompts`, `setup-ci-cd`, `update-asc-docs`, `validate-design-tokens`, `project-kickoff`
  - mactools: `calendar`, `contacts`, `mail`, `notes`, `ocr`, `omnifocus`, `photos`, `reminders`, `safari`, `spotlight`
  - product-lens: `compare`, `feature-assess`, `teardown`
- Run `/plugin-review` on each of the 6 plugins with the enhanced trigger reviewer
- Create baseline document `docs/06-plans/2026-03-07-plugin-quality-baseline.md`:
  - Trigger Health Score per plugin
  - Redundancy verdicts for all 6 high-risk skills
  - Eval coverage percentage
  - Date and model version (Opus 4.6)
- This baseline is the reference point for future model upgrade comparisons

**Acceptance criteria:**
- [x] Every skill across all 6 plugins has an eval.md file (55/55 = 100%)
- [x] `/plugin-review` runs clean on all 6 plugins (0 fail-level trigger issues; 50 pass, 4 warn)
- [x] Baseline document exists with all sections populated (`docs/06-plans/2026-03-08-plugin-quality-baseline.md`)
- [x] Total eval.md count matches total SKILL.md count (55/55 = 1:1 coverage)

**Review checklist:**
- [x] /plugin-review (all 5 plugins with skills reviewed; 73 findings fixed in commit 83cfe4b)
- [ ] /execution-review (verify completeness against this dev-guide)
