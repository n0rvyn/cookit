# Dimension 3: Build Cost (实现代价)

**Core question:** What is the architectural invasiveness, maintenance burden, and opportunity cost of adding this feature?

## Universal Sub-Questions

1. **Architectural invasiveness:** Does this require new data models, new services, new permissions, or new third-party dependencies? Or can it be built on existing infrastructure?
2. **Maintenance burden:** How many new states, edge cases, and failure modes does this introduce? Can one person keep up with the added surface area?
3. **Opportunity cost:** What else could be built with the same effort? Is this the highest-value use of development time?
4. **Reversibility:** If the feature fails, how hard is it to remove? Does it touch core data models (hard to reverse) or is it isolated (easy to remove)?

## Platform-Specific Sub-Questions

### Default

5. **Dependency risk:** Does this feature require new third-party libraries? What is their maintenance status?

### iOS

> iOS core question variant: What iOS-specific costs does this feature introduce (new frameworks, entitlements, App Review considerations)?

5. **New framework adoption:** Does this require adopting new Apple frameworks (HealthKit, ARKit, StoreKit 2, etc.)? Each framework adds entitlements, review scrutiny, and annual maintenance.
6. **Entitlements and capabilities:** Does this feature require new App ID capabilities (push notifications, in-app purchase, CloudKit, etc.)? Each capability adds provisioning complexity.
7. **App Review risk:** Does this feature sit in App Review grey zones (web views, third-party payment, background processing)?
8. **WWDC maintenance multiplier:** How much does this feature increase the annual WWDC-driven maintenance burden? (New API adoptions, deprecation tracking)

## Evidence Sources

- Local: Existing data models (would feature need new models or extend existing?), service layer architecture, dependency manifest (Package.swift, Podfile, package.json), permission declarations (Info.plist, entitlements)
- External: Framework documentation complexity, App Review guidelines for the feature area

## Signal Anchors

| Signal | Anchor |
|--------|--------|
| Positive | Feature builds on existing infrastructure; isolated from core data models; minimal new dependencies; reversible |
| Neutral | Some new infrastructure needed but manageable; moderate edge cases; one new dependency or permission |
| Negative | Requires significant new infrastructure (new service, new data model at core level); multiple new dependencies; hard to reverse; substantially increases maintenance surface |
