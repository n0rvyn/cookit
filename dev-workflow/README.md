# dev-workflow

Cross-stack development workflow plugin for Claude Code. Provides a full plan-execute-review lifecycle with context-efficient agent dispatching.

## Architecture

Heavy document-generation and analysis tasks run as **agents** (separate context windows) dispatched via the Task tool. Interactive tasks that need user input or write code stay as **skills** in the main context. The `running-phase` orchestrator dispatches agents and coordinates the sequence.

```
running-phase (orchestrator, main context)
  → plan-writer agent (sonnet)        → plan file on disk
  → plan-verifier agent (opus)        → verification report
  → executing-plans skill             → code changes (main context)
  → feature-spec-writer agent (sonnet) → spec file
  → review agents (parallel)          → consolidated findings
  → fix gaps                          → Phase done
```

## Agents

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| implementation-reviewer | opus | Glob, Grep, Read, Bash | Plan-vs-code verification and design fidelity audit |
| plan-writer | sonnet | Glob, Grep, Read, Write | Structured implementation plan generation |
| plan-verifier | opus | Glob, Grep, Read, Bash | Verification-first plan validation (S1/S2/U1/DF/AR) |
| dev-guide-writer | sonnet | Glob, Grep, Read, Write | Phased project development guide creation |
| feature-spec-writer | sonnet | Glob, Grep, Read, Write | Design-vs-implementation feature spec generation |
| rules-auditor | sonnet | Glob, Grep, Read | CLAUDE.md rules audit for conflicts and loopholes |

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| running-phase | orchestrator | Phase lifecycle: dispatch agents, coordinate sequence, manage state |
| executing-plans | interactive | Batch code execution with checkpoint approval |
| brainstorming | interactive | Design exploration before implementation |
| making-design-decisions | interactive | Trade-off analysis with essential/accidental complexity |
| fixing-bugs | interactive | Systematic diagnosis with value domain tracing |
| finishing-branch | interactive | Test, document, merge/PR/discard |
| parallel-agents | guide | Pattern for concurrent agent dispatch |
| using-worktrees | guide | Git worktree setup and safety |
| committing-changes | fork (haiku) | Conventional commit analysis and execution |
| handing-off | fork (haiku) | Cold-start prompt generation for session transfer |
| writing-plans | dispatcher | Gathers context, dispatches plan-writer agent |
| verifying-plans | dispatcher | Gathers context, dispatches plan-verifier agent |
| writing-dev-guide | dispatcher | Gathers context, dispatches dev-guide-writer agent |
| writing-feature-spec | dispatcher | Gathers context, dispatches feature-spec-writer agent |
| reviewing-rules | dispatcher | Gathers context, dispatches rules-auditor agent |

## Hooks

| Event | Script | Purpose |
|-------|--------|---------|
| SessionStart | check-workflow-state.sh | Detects in-progress phase, prompts resume |

## Workflow State

`running-phase` persists progress to `.claude/dev-workflow-state.yml`, enabling cross-session resume. The SessionStart hook detects this file and prompts the user to continue.

## Design Principles

- Bug fix, plan verification, and design decision skills use universal methodology (value domain tracing, reverse reasoning, entry point uniqueness, complexity analysis) that works across tech stacks.
- iOS-specific checks (Design Token consistency, Swift concurrency) are provided by the `ios-development` plugin's references.
- Document-generation tasks (plans, specs, guides, audits) run in separate agent contexts to preserve main context for code execution.
