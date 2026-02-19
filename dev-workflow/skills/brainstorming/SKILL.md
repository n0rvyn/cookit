---
name: brainstorming
description: "Use before any creative work — creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
user-invocable: false
---

## Hard Gate

Do NOT invoke any implementation skill, write code, or take implementation action until design is presented and user-approved.

## Division of Responsibility

- **brainstorming** = from zero to design (exploring, shaping, deciding)
- **making-design-decisions** = choosing between already-identified options

If the user already has 2+ concrete options and needs to pick one, use `dev-workflow:making-design-decisions` instead.

## Process

### 1. Explore Project Context

- Read relevant code, configs, and docs
- Understand what exists before proposing anything new

### 2. Ask Clarifying Questions

Ask **one question at a time**. Wait for the answer before asking the next.

Focus on:
- What problem are we solving?
- Who is the user? What do they care about?
- What constraints exist (tech stack, timeline, compatibility)?
- What does success look like?

### 3. Propose 2-3 Approaches

For each approach, provide:
- Summary (1-2 sentences)
- Key trade-offs
- When this approach is the right choice

Follow the comparison table format from CLAUDE.md Rule 13:

| Approach | Architecture Fit | Implementation Size | Risk/Cost | Best For |
|----------|-----------------|-------------------|-----------|----------|
| A | ... | ... | ... | ... |
| B | ... | ... | ... | ... |

Mark your recommendation and explain why in one sentence.

### 4. Present Design Incrementally

After the user picks a direction:
- Present design in sections of 200-300 words
- Get approval on each section before moving to the next
- Cover: data model, component structure, key interactions, edge cases

### 5. Save Design Document

Write the approved design to:

```
docs/06-plans/YYYY-MM-DD-<topic>-design.md
```

If the design is primarily architectural (data model, service layer, component boundaries), also save or symlink to `docs/02-architecture/` so it's discoverable alongside other architecture docs.

### 6. Next Steps

After design is approved, inform the user:
- Use `dev-workflow:writing-plans` to create a structured implementation plan
- Or use Claude `/plan` mode to plan and implement directly
