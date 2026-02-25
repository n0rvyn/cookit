---
name: design-decision
description: "Use when facing multiple design or product options, the user is stuck between approaches, or asks 'how should I design this'. Analyzes trade-offs by separating essential from accidental complexity."
---

## Input

Trigger this command when:
- User presents multiple options and asks which is better
- User is stuck between approaches
- User asks "how should I design this"

Required context:
- What problem are we solving?
- Who is the user?
- What are the constraints?

If context is missing, ask before analyzing.

## Analysis Framework

### Step 1: Understand the Complexity Source

Before applying simplicity principles, determine:
- **Essential complexity**: Inherent to the problem domain (e.g., tax rules are complex because taxes are complex)
- **Accidental complexity**: Added by the solution (e.g., over-abstraction, premature optimization)

Only accidental complexity should be eliminated. Essential complexity must be managed, not hidden.

### Step 2: Apply Simplicity Principles

1. **Simplicity is the ultimate sophistication** - If it can be simpler, it should be
2. **Subtract, don't add** - Ask "what to remove" before "what to add"
3. **No thinking required** - Users should understand by instinct
4. **Consistency > Features** - One coherent system beats scattered features

### Step 3: Evaluate Each Option

For each option, ask:
- Can it be simpler without losing essential function?
- Does it require explanation to use?
- Does it break existing consistency?
- Is it adding accidental or essential complexity?

## Output

1. Restate the core problem (one sentence)
2. For each option: pros, cons, complexity type
3. Recommendation with clear reasoning
4. If no option is good: suggest a different framing

## Red Flags

- "Users will learn..." → They rarely do
- "We can add a setting for..." → Settings are failure of design
- "It's complex but powerful..." → Power users are 1%

## Balance Check

Before rejecting a complex option, verify:
- Is this complexity from the problem or the solution?
- Would a "simpler" option actually solve the problem?
- Am I over-applying simplicity dogma?

User knows their domain better than I do. If they insist on an approach I find complex, ask why before pushing back.

## Completion Criteria

- Comparison table presented (Rule 13 format)
- User has selected an approach
- If no option is suitable: alternative framing proposed and user acknowledged
