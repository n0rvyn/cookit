# dev-workflow

Cross-stack development workflow plugin for Claude Code. Provides a full plan-execute-review lifecycle with model-appropriate task routing.

## Architecture

**Opus thinks, Sonnet does, Opus reviews.** Judgment-intensive steps (planning, fixing) run in main context with Opus and full conversation history. Mechanical execution runs as a dispatched Sonnet agent. Reviews run as dispatched Opus agents for unbiased assessment.

```
run-phase (orchestrator, main context — opus)
  → write plan (main context — opus, full user intent)
  → plan-verifier agent (opus)         → verification report
  → execute-plan agent (sonnet)        → code changes + build/test results
  → feature-spec-writer agent (sonnet) → spec file
  → review agents (parallel — opus)    → consolidated findings
  → fix all issues (main context — opus: execution failures + review gaps)
  → Phase done

finalize (after all phases complete)
  → full test suite (0 fail, 0 skip)
  → cross-phase criteria regression
  → cumulative test coverage audit     → validation report
```

## Agent Dispatch Guidelines

### Explore-Intent Dispatch

When dispatching a subagent (via Agent tool) for exploration/understanding purposes, include this instruction in the dispatch prompt:

> Return your findings as:
> 1. Summary (3-5 sentences): what you found, key patterns, notable concerns
> 2. Key files (5-10): `{file_path} — {one-line relevance}`
> 3. Do NOT paste full file contents into your response.

The main context reads specific files as needed based on the returned list.

This pattern applies to "understand X" / "explore Y" dispatches. Verification agents ("verify X" / "audit Y") should continue returning inline evidence.

## Agents

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| execute-plan | sonnet | Glob, Grep, Read, Write, Edit, Bash, LSP | Mechanical plan execution — follows verified plan tasks (includes full build/test via final verification task) |
| design-analyzer | opus | Glob, Grep, Read, Write | Multi-modal design prototype analysis (dual-channel image+code) |
| design-drift-auditor | opus | Glob, Grep, Read | Design document vs codebase drift detection (read-only) |
| flow-tracer | opus | Glob, Grep, Read | End-to-end call chain tracing with break detection (read-only) |
| implementation-reviewer | opus | Glob, Grep, Read, Bash, Write | Plan-vs-code verification and design fidelity audit |
| plan-verifier | opus | Glob, Grep, Read, Bash, Write | Verification-first plan validation (S1/S2/U1/DF/CF/AR) |
| dev-guide-verifier | opus | Glob, Grep, Read, Bash, Write | Dev-guide quality verification (coverage, dependencies, data flow, code overlap, terms, criteria, structure) |
| feature-spec-writer | sonnet | Glob, Grep, Read, Write | Design-vs-implementation feature spec generation |
| rules-auditor | sonnet | Glob, Grep, Read | CLAUDE.md rules audit for conflicts and loopholes (read-only) |
| distill-discussion-reader | sonnet | Read, Glob, Grep | Discussion file classification and structured extraction (read-only) |

### Supporting Files (not agents)

| File | Loaded by | Content |
|------|-----------|---------|
| design-faithfulness.md | plan-verifier | DF strategy: design document faithfulness verification procedure |
| crystal-fidelity.md | plan-verifier | CF strategy: crystal file decision fidelity verification procedure |
| architecture-review.md | plan-verifier | AR strategy: architecture change completeness review procedure |

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| run-phase | orchestrator | Phase lifecycle: write plan, dispatch agents, coordinate sequence, manage state |
| execute-plan | dispatcher | Dispatches sonnet execute-plan agent for mechanical plan execution |
| brainstorm | interactive | Design exploration before implementation |
| design-decision | interactive | Trade-off analysis with essential/accidental complexity |
| fix-bug | interactive | Systematic diagnosis with value domain tracing |
| issue | interactive | GitHub Issue unified entry point: list, read, create with prior hypotheses |
| finish-branch | interactive | Test, document, merge/PR/discard |
| parallel-agents | guide | Pattern for concurrent agent dispatch |
| use-worktree | guide | Git worktree setup and safety |
| commit | fork (haiku) | Conventional commit analysis and execution |
| handoff | fork (sonnet) | Cold-start prompt generation for cross-day/cross-person session transfer |
| generate-design-prompt | interactive | Generate Stitch/Figma prompts from project features; supports initial and refinement modes |
| understand-design | dispatcher | Dual-channel design prototype analysis, token extraction, platform translation |
| write-plan | interactive | Writes implementation plan in main context (full conversation context) |
| verify-plan | dispatcher | Gathers context, dispatches plan-verifier agent |
| write-dev-guide | interactive | Writes phased dev-guide in main context, dispatches verifier agent |
| next-increment | interactive | Proposes 3-5 archetype-diverse next-step candidates for mature codebases, writes mini-spec for chosen one |
| write-feature-spec | dispatcher | Gathers context, dispatches feature-spec-writer agent |
| audit-rules | dispatcher | Gathers context, dispatches rules-auditor agent |
| design-drift | dispatcher | Design document vs codebase drift audit |
| crystallize | interactive | Lock settled decisions from current session into a persistent crystal file |
| collect-lesson | interactive | Capture development lessons learned |
| kb | interactive | Cross-project knowledge base search with freshness indicators |
| distill-discussion | interactive | Extract structured outputs (crystals, lessons) from raw discussion files |
| generate-vf-prompt | interactive | Generate Verification-First prompts with falsifiable assertions |
| finalize | interactive | Cross-phase validation: full test suite, acceptance criteria regression, cumulative coverage audit |

## Hooks

| Event | Script | Purpose |
|-------|--------|---------|
| SessionStart | check-workflow-state.sh | Detects in-progress phase, prompts resume |
| PreToolUse (Bash) | scan-secrets.sh | Intercepts git commit, blocks if secrets detected in staged content |
| UserPromptSubmit | suggest-skills.sh | Pattern-matches user prompt and suggests relevant skills |

## Workflow State

`run-phase` persists progress to `.claude/dev-workflow-state.yml`, enabling cross-session resume. The SessionStart hook detects this file and prompts the user to continue.

## Design Principles

- **Opus thinks, Sonnet does, Opus reviews** — model routing based on task type, not context conservation
- Bug fix, plan verification, and design decision skills use universal methodology (value domain tracing, reverse reasoning, entry point uniqueness, complexity analysis) that works across tech stacks
- iOS-specific checks (Design Token consistency, Swift concurrency) are provided by the `apple-dev` plugin's references
- Review agents run in separate contexts for unbiased assessment; writing tasks run in main context to benefit from full conversation history
