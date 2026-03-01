# dev-workflow

Cross-stack development workflow plugin for Claude Code. Provides a full plan-execute-review lifecycle with context-efficient agent dispatching.

## Architecture

Heavy document-generation and analysis tasks run as **agents** (separate context windows) dispatched via the Task tool. Interactive tasks that need user input or write code stay as **skills** in the main context. The `run-phase` orchestrator dispatches agents and coordinates the sequence.

```
run-phase (orchestrator, main context)
  → design-analyzer agent (opus)       → design analysis file
  → plan-writer agent (sonnet)         → plan file on disk
  → plan-verifier agent (opus)         → verification report
  → execute-plan skill                 → code changes (main context)
  → feature-spec-writer agent (sonnet) → spec file
  → review agents (parallel)           → consolidated findings
  → fix gaps                           → Phase done
```

## Agents

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| design-analyzer | opus | Glob, Grep, Read, Write | Multi-modal design prototype analysis (dual-channel image+code) |
| design-drift-auditor | opus | Glob, Grep, Read, Bash | Design document vs codebase drift detection |
| flow-tracer | opus | Glob, Grep, Read, Bash | End-to-end call chain tracing with break detection |
| implementation-reviewer | opus | Glob, Grep, Read, Bash, Write | Plan-vs-code verification and design fidelity audit |
| plan-verifier | opus | Glob, Grep, Read, Bash, Write | Verification-first plan validation (S1/S2/U1/DF/AR) |
| plan-writer | sonnet | Glob, Grep, Read, Write | Structured implementation plan generation |
| dev-guide-writer | sonnet | Glob, Grep, Read, Write | Phased project development guide creation |
| feature-spec-writer | sonnet | Glob, Grep, Read, Write | Design-vs-implementation feature spec generation |
| rules-auditor | sonnet | Glob, Grep, Read | CLAUDE.md rules audit for conflicts and loopholes |

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| run-phase | orchestrator | Phase lifecycle: dispatch agents, coordinate sequence, manage state |
| execute-plan | interactive | Batch code execution with checkpoint approval |
| brainstorm | interactive | Design exploration before implementation |
| design-decision | interactive | Trade-off analysis with essential/accidental complexity |
| fix-bug | interactive | Systematic diagnosis with value domain tracing |
| finish-branch | interactive | Test, document, merge/PR/discard |
| parallel-agents | guide | Pattern for concurrent agent dispatch |
| use-worktree | guide | Git worktree setup and safety |
| commit | fork (haiku) | Conventional commit analysis and execution |
| handoff | fork (haiku) | Cold-start prompt generation for session transfer |
| generate-design-prompt | interactive | Generate Stitch/Figma prompts from project features; supports initial and refinement modes |
| understand-design | dispatcher | Dual-channel design prototype analysis, token extraction, platform translation |
| write-plan | dispatcher | Gathers context, dispatches plan-writer agent |
| verify-plan | dispatcher | Gathers context, dispatches plan-verifier agent |
| write-dev-guide | dispatcher | Gathers context, dispatches dev-guide-writer agent |
| write-feature-spec | dispatcher | Gathers context, dispatches feature-spec-writer agent |
| reviewing-rules | dispatcher | Gathers context, dispatches rules-auditor agent |
| design-drift | dispatcher | Design document vs codebase drift audit |
| crystallize | interactive | Lock settled decisions from current session into a persistent crystal file |
| collect-lesson | interactive | Capture development lessons learned |
| docs-rag | interactive | Documentation search and retrieval |
| generate-vf-prompt | interactive | Generate Verification-First prompts with falsifiable assertions |

## Hooks

| Event | Script | Purpose |
|-------|--------|---------|
| SessionStart | check-workflow-state.sh | Detects in-progress phase, prompts resume |
| PreToolUse (Bash) | scan-secrets.sh | Intercepts git commit, blocks if secrets detected in staged content |
| Stop | suggest-compact.sh | Suggests /compact at phase transitions when tool call count is high |
| UserPromptSubmit | suggest-skills.sh | Pattern-matches user prompt and suggests relevant skills |

## Workflow State

`run-phase` persists progress to `.claude/dev-workflow-state.yml`, enabling cross-session resume. The SessionStart hook detects this file and prompts the user to continue.

## Design Principles

- Bug fix, plan verification, and design decision skills use universal methodology (value domain tracing, reverse reasoning, entry point uniqueness, complexity analysis) that works across tech stacks.
- iOS-specific checks (Design Token consistency, Swift concurrency) are provided by the `ios-development` plugin's references.
- Document-generation tasks (plans, specs, guides, audits) run in separate agent contexts to preserve main context for code execution.
