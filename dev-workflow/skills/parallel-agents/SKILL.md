---
name: parallel-agents
description: "Use when facing 2+ independent tasks that can be worked on concurrently without shared state or sequential dependencies."
---

## When to Use

- 3+ test files failing with different root causes
- Multiple subsystems broken independently
- Each problem can be understood without context from the others
- No shared state between investigations

## When NOT to Use

- Failures are related (fixing one might fix others)
- Need to understand full system state first
- Agents would interfere with each other (modifying same files)

## The Pattern

### 1. Identify Independent Domains

Group work by what's broken or what needs building. Each domain must be independent.

### 2. Create Focused Agent Tasks

Each agent gets:
- **Specific scope:** one test file, one subsystem, one feature area
- **Clear goal:** what success looks like
- **Constraints:** what NOT to change
- **Expected output:** what the agent should report back

### 3. Dispatch in Parallel

Use the Task tool to launch all agents concurrently in a single message.

### 4. Review and Integrate

- Read each agent's summary
- Verify fixes don't conflict
- Run full test suite
- Integrate all changes

## Agent Prompt Guidelines

**Good prompt characteristics:**
1. **Focused** — one clear problem domain
2. **Self-contained** — all context the agent needs is in the prompt
3. **Specific about output** — what should the agent return?

**Common mistakes:**
- Too broad: "Fix all the tests" — agent doesn't know where to focus
- No context: agent doesn't know where the problem is
- No constraints: agent might refactor everything
- Vague output expectation: don't know what changed
