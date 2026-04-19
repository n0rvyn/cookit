# Decision Points: Presentation & Recording

This reference is consumed by skill DP handling steps. Not user-facing.

**Consuming skills** (as of this writing):
- `write-plan` Step 3 #2 — plan file, mode `full`, recording default
- `verify-plan` Step 3 #5 — verification report, mode `mixed`, recording default
- `run-phase` Step 2 #9 — plan file, mode `full`, recording default
- `run-phase` Step 6 #6 — spec file, mode `full`, recording default
- `run-phase` Step 7 #8 — review report, mode `mixed`, recording default
- `understand-design` — design-analysis file, mode `mixed`, recording default
- `design-drift` — drift report, mode `mixed`, recording `conversation-only`
- `write-feature-spec` — spec file, mode `mixed`, recording default
- `audit-rules` — audit report, mode `mixed`, recording `conversation-only`
- `execute-plan` Step 1 #3 — plan file, **inline short-form** (see §"Note on inline variant"), recording default

Each consuming skill declares its parameters (source file path, mode, recording) at the DP handling step and points here for execution.

`execute-plan` intentionally inlines a short-form variant on the mechanical execution hot path — see §"Note on inline variant" below.

**Non-consumers** (intentionally excluded):
- `write-dev-guide` uses a custom table-based DP UX (方案/描述与代价 columns, per-decision AskUserQuestion with "(推荐)" marker on the recommended label) that does not match the group-batching flow described here. It remains an independent pattern.
- `next-increment` documents a mini-spec artifact format that happens to use `**Chosen:**` in its template — it is not a DP handling step.

## Core Principle

**Source files** (plan / spec / report) hold DP blocks in professional format:

```
### [DP-NNN] {title} ({blocking | recommended})

**Context:** ...
**Options:**
- A: ... — {trade-off}
- B: ... — {trade-off}
**Recommendation:** ... — {reason, 1 sentence}
```

This format is the **durable record** for `execute-plan`, `plan-verifier`, and future readers. **Do not modify** Context / Options / evidence body. The `**Recommendation:**` line is replaced with `**Chosen:**` only after the user decides (see §Recording).

The `question` field of `AskUserQuestion` is **a conversation, not a spec dump**. Translate the DP to plain language for the question field only. Never paste verbatim DP Markdown into the `question` field — formal blocks cause users to skim and click "accept all" without engaging.

## Modes

### `full`

For DPs representing real architectural, scope, product, or design tradeoffs the user must weigh. Rewrite each DP inside the `question` field as four lines:

1. **Why this choice matters** — one line on the user-visible or operational consequence, not the technical context.
2. **Each option** — one line per option describing what concretely happens, prefixed with the original `A:` / `B:` / `C:` label. **Always preserve the label** so the user's answer maps back to the source file.
3. **Recommended + why** — one line of practical reason, not architectural reasoning.
4. **Tradeoff** — one line on what is given up if the recommendation is accepted.

### `short`

For routine verifier/reviewer findings in confirm/reject style (e.g., "add this missing test", "tighten this assertion"). A one-line summary of what the verifier/reviewer recommends + options with original `A:` / `B:` / `C:` labels. Full translation is not needed — the user is mostly confirming the finding.

### `mixed`

Classify each DP at read time:
- Options are different approaches / scope tradeoffs → apply `full`.
- Options are "fix now / defer" or "accept / reject finding" style → apply `short`.

When uncertain, default to `full` — over-translating is less harmful than under-translating.

## Language Rule

Use the conversation's language. If the ongoing conversation has been in Chinese, write the question in Chinese; if English, English. **Do not mix CN and EN within a single presentation.**

## Presentation Flow

### Blocking decisions

Each `blocking` decision is presented individually via its own `AskUserQuestion` using the translated form.

### Recommended decisions

Present as a group via a single `AskUserQuestion`. **Critical constraints:**

- All translated content must be inside the `question` field. Text printed before `AskUserQuestion` gets visually covered by the widget.
- Separate multiple DPs with `\n---\n`.
- End the `question` field with: `\n\n全部接受推荐，还是逐个审查？`

If the user does **not** choose "accept all": present each DP individually via separate `AskUserQuestion` calls. **Do not assume any DP is accepted** until the user explicitly confirms it.

### User pushback

If the user pushes back **before answering** with signals like "说人话" / "explain plainly" / "I don't understand" / "再说一次": the translation was weak. Redo it — re-read the DP body, rewrite with more concrete user-facing consequences — and re-ask.

If the user pushes back **after answering**: treat as a new round of questions on the same DP, not a retranslation. Do not overwrite the recorded choice unless the user explicitly says to.

## Recording Choices

### Default recording (`recording: default`)

Edit the source file; replace `**Recommendation:**` or `**Recommendation (unverified):**` with:

```
**Chosen:** Option {A | B | C}
```

Use the original A/B/C label the DP was written with. **Do not modify** the DP's Context / Options / evidence body — they remain for future readers.

This is what downstream consumers depend on:
- `execute-plan` (the skill) edits the plan file to record `**Chosen:**` *before* dispatching the agent, so every Task the agent executes sees settled decisions. Future audits and resumed sessions also read these lines.
- `plan-verifier` agent reads `**Chosen:**` entries as "Previously resolved decisions" to avoid re-asking settled questions on re-verification.

### Conversation-only recording (`recording: conversation-only`)

Some skills (`design-drift`, `audit-rules`) produce DPs from transient findings — drift items or rule-audit recommendations — that don't belong in a long-lived plan or spec. For these:

- Record the user's choice in the ongoing conversation only (note which option was chosen for each DP).
- **Do not write `**Chosen:**` back to the source file.**
- Downstream handling varies by skill:
  - **Same-skill consumption**: `audit-rules` Step 4-5 reads the conversation record to decide which fixes to apply in the current run.
  - **Advisory handoff**: `design-drift` ends after presenting findings; the user carries the choices forward into follow-up work (doc updates, issue creation) outside this skill.

## Note on Inline Variant

`execute-plan/SKILL.md` intentionally inlines a ~7-line **short-form** DP handler for pre-dispatch DP resolution. Rationale:

- execute-plan is the mechanical executor — its ethos is "no judgment calls." Reading this reference file on a hot dispatch path adds indirection without much benefit, since by the time execute-plan runs, most DPs have already been resolved by `write-plan` or `verify-plan`. The inline block is the dispatcher of last resort.
- The inline handler applies `short` mode + `default` recording; it does NOT paste verbatim DP Markdown into the `question` field (that rule from §"Core Principle" binds everywhere, including execute-plan).

**When the rules in this file evolve** (presentation flow, recording format, A/B/C label convention, short-form shape), **check `execute-plan/SKILL.md` Step 1 #3** and keep it in sync manually. The execute-plan inline block should remain a lean subset of this reference, not a divergent fork.
