---
name: testing-guide
description: Provide testing workflow and best practices guidance
---

# Testing Guide Skill

Provide interactive guidance on iOS testing best practices based on `references/testing-guide.md`.

## When to Use

- User asks about testing approaches
- Setting up unit tests or UI tests
- Questions about mocking or TDD
- Test organization or coverage strategies

## Process

### 1. Identify Testing Scenario

Determine what the user needs:
- Unit test setup
- UI test setup
- Mocking strategy
- TDD workflow
- Test coverage goals

### 2. Read Relevant Section of Reference Guide

Grep for section markers:

```
Grep("<!-- section:", "references/testing-guide.md")
```

Read only the section matching the user's scenario:

```
Read("references/testing-guide.md", offset=<marker_line + 1>, limit=<lines_to_next_marker>)
```

Section-to-need mapping:
- Unit tests → section "1. Unit Test 组织"
- UI tests → section "2. UI Test 最佳实践"
- Mocking / DI → section "3. Mock 和 Dependency Injection"
- Async testing → section "4. 异步测试"
- TDD → section "5. TDD 流程"
- Coverage → section "6. 测试覆盖率"

### 3. Provide Contextual Guidance

Based on user's specific scenario:

**For Unit Tests**:
- Show Given-When-Then pattern from guide Section 1
- Demonstrate test naming conventions
- Explain setUp/tearDown usage

**For UI Tests**:
- Show Page Object pattern from guide Section 2
- Demonstrate wait strategies
- Explain element identification

**For Mocking**:
- Show protocol-based mocking from guide Section 3
- Explain test doubles (Dummy, Stub, Mock, Fake)
- Demonstrate dependency injection

**For TDD Workflow**:
- Explain Red-Green-Refactor from guide Section 5
- Show when to use TDD vs when to skip
- Demonstrate test-first development

**For Coverage**:
- Show coverage targets from guide Section 6
- Explain how to measure coverage
- Discuss what to prioritize

### 4. Provide Code Examples

Extract relevant testing patterns from the guide and adapt to user's code.

### 5. Common Testing Mistakes

- Testing implementation details instead of behavior
- Test interdependencies
- Not testing error paths
- Slow tests due to real network/database calls
- Flaky UI tests

## Success Criteria

- User can write effective tests for their scenario
- Tests follow best practices (isolated, fast, deterministic)
- Mocking strategy is appropriate
- Test coverage is meaningful, not just high percentage
