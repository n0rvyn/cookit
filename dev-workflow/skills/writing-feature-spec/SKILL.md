---
name: writing-feature-spec
description: "Generate feature spec (docs/05-features/) capturing what was built, design decisions made, and user journeys completed. Use for cross-session context recovery, publication notes, or as input for external review. Not a prerequisite for self-review."
user-invocable: false
---

## Overview

This skill dispatches the `feature-spec-writer` agent to generate a feature spec in a separate context, keeping the main conversation lean.

## Process

### Step 0: Resolve Feature Identity (dispatcher-side interaction)

Before dispatching, confirm with the user:

1. **Feature name** — use context clues to suggest candidates:
   - Current branch name
   - Recent commits (`git log --oneline -20`)
   - Files changed on this branch vs base
2. **Feature scope** — brief description of what the feature covers

If the user hasn't specified a feature, ask before proceeding.

### Step 1: Gather Context

Collect the following:

1. **Feature name** — confirmed in Step 0
2. **Feature scope** — confirmed in Step 0
3. **Design doc paths** — search `docs/06-plans/*-design.md` for sections related to this feature
4. **Dev-guide path** — search `docs/06-plans/*-dev-guide.md` and identify the relevant Phase
5. **Key implementation files** — search for files related to the feature (by name, imports, or recent modifications)
6. **Project root** — current working directory

### Step 2: Dispatch Agent

Use the Task tool to launch the `feature-spec-writer` agent with all gathered context. Structure the task prompt as:

```
Generate a feature spec with the following inputs:

Feature name: {name}
Feature scope: {scope}
Design doc paths:
- {path 1} § {relevant section}
- {path 2} § {relevant section}
Dev-guide: {path} Phase {N}
Key implementation files:
- {file 1}
- {file 2}
Project root: {path}
```

### Step 3: Present Results

When the agent completes:

1. **If the agent reports "no design source found, stopped":**
   - Ask the user to either provide a design document path, or describe the expected behavior for this feature
   - If user provides a description: re-dispatch the agent with the user's description as additional context
   - If user provides a document path: re-dispatch with the corrected path
2. **Otherwise**, present a summary to the user:
   - Spec file path
   - User Story status counts (✅ / ⚠️ / ❌)
   - Number of deviations detected
3. If deviations were found, briefly list them
4. After spec is saved, offer:
   "Spec saved at {path}. This can be used to:"
   - "Quickly restore context in a future session (share spec with new Claude session)"
   - "Document the feature for changelog or release notes"
   - "Feed to an external reviewer for independent review:
      Dispatch via Task tool with:
        subagent_type: 'ios-development:feature-reviewer'
        prompt: 'Review feature: {name}. Spec: {path}. Key files: {files list}. Project root: {root}'"
