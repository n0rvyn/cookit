# Dimension 2: Journey Contribution (旅程贡献)

**Core question:** Does this feature strengthen the app's core loop, or does it create a tangential side branch?

## Universal Sub-Questions

1. **Core loop alignment:** Does the feature strengthen Entry -> Core Action -> Result -> Retention, or does it add a parallel path?
2. **Touch points:** Which existing screens/flows does this feature touch? Is it additive (new screen) or integrative (enhances existing screens)?
3. **Value proposition coherence:** Does the feature add a new "why someone uses this app", or does it support the existing "why"?
4. **Complexity budget impact:** How many new screens/states/navigation paths does this add? Does the total remain within one person's ability to maintain?

## Platform-Specific Sub-Questions

### Default

5. **Information architecture:** Does the feature fit naturally into the existing navigation structure, or does it require restructuring?

### iOS

> iOS core question variant: Does this feature integrate with the existing iOS user journey patterns (navigation, platform conventions), or does it fight them?

5. **Navigation integration:** Does the feature fit within the existing SwiftUI/UIKit navigation structure (NavigationStack, TabView), or does it require a new navigation paradigm?
6. **Platform feature extension:** Could this feature be delivered as a Widget, App Intent, or ShareSheet extension rather than an in-app screen? Would that be more natural?
7. **Cross-device impact:** If the app supports multiple Apple devices, does this feature need to work on all of them? Does it complicate Handoff/iCloud sync?

## Evidence Sources

- Local: Navigation graph (view hierarchy), data model relationships, existing screen count, view files that would need modification
- External: Competitor apps' feature organization, UX patterns in this app category

## Signal Anchors

| Signal | Anchor |
|--------|--------|
| Positive | Feature integrates into existing core loop; touches existing screens naturally; reinforces the current value proposition |
| Neutral | Feature is adjacent to core loop; adds moderate complexity; serves the same users but for a different task |
| Negative | Feature creates a side branch disconnected from core loop; requires significant navigation restructuring; introduces a new "why" that dilutes the existing one |
