# Integration Map

**Purpose:** For GO verdicts -- provide a code-level map of where and how the feature integrates with the existing app.

**Constraint:** Only available for local projects (requires code access).

## Methodology

1. **Reusable infrastructure:** What existing code can the feature build on?
   - Existing data models that the feature extends
   - Existing services/managers the feature can use
   - Existing UI components/patterns the feature follows
2. **New infrastructure needed:** What must be built from scratch?
   - New data models
   - New services or managers
   - New UI screens/components
   - New dependencies
3. **Modification scope:** What existing code needs changes?
   - Files that need modification (list with brief description of the change)
   - Navigation structure changes
   - Data model migrations needed
4. **Integration points:** Where does the feature connect to the existing app?
   - Entry points (how users access the feature)
   - Data flow (where feature data comes from and goes to)
   - Side effects (what existing behavior changes when this feature is active)

## Output Format

```markdown
## Integration Map

### Reusable Infrastructure
- **[Component/Model/Service]:** [How the feature uses it] -- `[file path]`
- ...

### New Infrastructure Required
- **[New component]:** [Purpose] -- [complexity: low/medium/high]
- ...

### Modification Scope

| File | Change Type | Description |
|------|-------------|-------------|
| [path] | Extend | [what to add] |
| [path] | Modify | [what to change] |
| [path] | New | [what to create] |

### Integration Points
- **Entry:** [How users access the feature -- which screen, what trigger]
- **Data flow:** [Where data comes from -> where it goes]
- **Side effects:** [What existing behavior changes]

### Implementation Sequence
1. [First step -- usually data model]
2. [Second step -- usually service layer]
3. [Third step -- usually UI]
```

## Platform Additions

### iOS

Add these to the analysis:
- **SwiftUI vs UIKit:** Which approach matches existing codebase patterns? If mixed, which layer does this feature belong to?
- **Entitlements/capabilities:** New capabilities needed in the App ID
- **Info.plist changes:** New usage descriptions or configuration keys
- **App Store metadata:** Does the feature change the app's privacy labels or category?
