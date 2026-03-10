# Swift / SwiftUI API Changes — iOS 26 / Swift 6.x

Seed content for WWDC 2025 APIs. Used by `apple-swift-context` skill for section-targeted loading.

---

<!-- section: LiquidGlass keywords: glassEffect, LiquidGlass, glass, liquid, material platform: iOS -->
## Liquid Glass (iOS 26)

**Minimum OS**: iOS 26.0

iOS 26 introduces Liquid Glass as the primary visual material for the updated system design.

### Correct Usage

```swift
// ✅ Apply glassEffect to views — shape is the `in:` parameter
ZStack {
    // Background content (image, gradient, etc.)
    Image("background")
        .resizable()
        .scaledToFill()

    // Glass overlay on a container
    VStack { /* content */ }
        .padding()
        .glassEffect(.regular, in: RoundedRectangle(cornerRadius: 16))
}

// ✅ Use on toolbar/navigation backgrounds
.toolbarBackground(.glass, for: .navigationBar)
```

### Common Mistakes

```swift
// ❌ Applying glassEffect to content inside List/ScrollView (clips material)
List {
    ForEach(items) { item in
        ItemRow(item: item)
            .glassEffect()  // WRONG — applies inside list cell, clips material layer
    }
}

// ❌ Adding .shadow() on top of glass elements (doubles shadow)
VStack { /* content */ }
    .glassEffect(.regular, in: RoundedRectangle(cornerRadius: 16))
    .shadow(radius: 8)  // WRONG — glass already has built-in shadow

// ❌ Using .clipShape() at same layer as glassEffect (disrupts material rendering)
VStack { /* content */ }
    .glassEffect(.regular, in: RoundedRectangle(cornerRadius: 16))
    .clipShape(RoundedRectangle(cornerRadius: 16))  // WRONG

// ❌ Adding glass to every element on screen
// Glass should be used sparingly — typically 1-2 glass surfaces per screen
```

### GlassEffectContainer

```swift
// ✅ Multiple glass elements — wrap in GlassEffectContainer
// Glass cannot sample other glass — GlassEffectContainer shares the sampling region
GlassEffectContainer(spacing: 8) {
    Button("Action 1") { }.glassEffect()
    Button("Action 2") { }.glassEffect()
}

// ❌ Multiple glass elements without GlassEffectContainer
Button("Action 1") { }.glassEffect()  // glass samples glass — visual artifact
Button("Action 2") { }.glassEffect()
```

### Glass Variants

```swift
.glassEffect(.regular)      // Standard glass — most common
.glassEffect(.prominent)    // More opaque — for important UI surfaces
.glassEffect(.thin)         // More transparent — for subtle overlays
```

### Integration with Navigation

```swift
// iOS 26 navigation bars use glass by default
// Opt out with:
.toolbarBackground(.hidden, for: .navigationBar)

// Glass bottom bars (tab bars)
// iOS 26 tab bars automatically use glass material
// Custom bottom bars: apply glass to the container
```
<!-- /section -->

---

<!-- section: FoundationModels keywords: LanguageModel, FoundationModels, on-device, LLM, AI, GenAI -->
## Foundation Models (iOS 26)

**Minimum OS**: iOS 26.0 (requires Apple Intelligence)
**Framework**: `import FoundationModels`

On-device LLM API powered by Apple Intelligence.

### Basic Usage

```swift
import FoundationModels

// Check availability
switch SystemLanguageModel.default.availability {
case .available:
    // proceed with inference
case .unavailable(let reason):
    // handle unavailability — show fallback UI
    print("Foundation Models unavailable: \(reason)")
}

// Single generation — session is stateful (records all prompts and responses)
@State var session = LanguageModelSession {
    "Your system instructions here"
}

let response = try await session.respond(to: "Summarize this text: \(text)")
print(response.content)

// Streaming
let stream = session.streamResponse(to: prompt)
for try await partial in stream {
    updateUI(with: partial)
}
```

### Structured Output

```swift
// Generate structured data
@Generable
struct RecipeSuggestion {
    var name: String
    var ingredients: [String]
    var estimatedTime: Int
}

let suggestion = try await session.respond(
    to: "Suggest a quick dinner recipe",
    generating: RecipeSuggestion.self
)
```

### Privacy

- All inference runs on-device; no data sent to Apple servers
- Subject to Apple Intelligence availability (A17 Pro / M1+ chips)
- Not available in all regions (check `SystemLanguageModel.default.availability`)

### Common Mistakes

- ❌ Not checking `SystemLanguageModel.default.availability` before use (not all devices support Apple Intelligence)
- ❌ Running inference on MainActor without `.task {}` (blocks UI)
- ❌ Creating a new `LanguageModelSession` for every request (expensive — sessions are stateful, reuse them)
- ❌ Shipping without a fallback for unavailable Apple Intelligence
<!-- /section -->

---

<!-- section: Swift6x keywords: Swift 6, concurrency, isolated, Sendable, typed throws -->
## Swift 6.x Concurrency Updates

**Minimum**: Swift 6.1+ (Xcode 26+)

### Typed Throws

```swift
// ✅ Swift 6.0+ — typed throws
enum NetworkError: Error {
    case timeout
    case unauthorized
}

func fetchData() throws(NetworkError) -> Data {
    // Compiler knows only NetworkError can be thrown
}

// Catch must handle NetworkError specifically (no `catch let e as NetworkError` needed)
do {
    let data = try fetchData()
} catch .timeout {
    // handle timeout
} catch .unauthorized {
    // handle auth error
}
```

### Isolated Conformances (Swift 6.1+)

```swift
// Conform to non-Sendable protocol from MainActor-isolated type
@MainActor
class ViewModel: @MainActor SomeDelegate {
    func delegateCallback() {
        // Runs on MainActor — safe
    }
}
```

### Global Actor Improvements

```swift
// Swift 6.1 — nonisolated(unsafe) for migration
class LegacyManager {
    nonisolated(unsafe) var mutableState: [String] = []
}
```

### Common Mistakes

- ❌ Using `nonisolated(unsafe)` as a permanent fix instead of proper actor isolation
- ❌ Forgetting `throws(ErrorType)` syntax change from catch-all `throws`
<!-- /section -->

---

<!-- section: NavigationStack26 keywords: NavigationStack, NavigationSplitView, navigation, iOS 26 platform: iOS -->
## Navigation Updates (iOS 26)

**Minimum OS**: iOS 26.0

iOS 26 navigation bars have a new translucent glass appearance by default.

```swift
// Default: glass navigation bar (automatic on iOS 26)
NavigationStack {
    ContentView()
        .navigationTitle("Title")
}

// Opt out of glass:
.toolbarBackground(.ultraThinMaterial, for: .navigationBar)
// or
.toolbarBackground(Color(.systemBackground), for: .navigationBar)
```

### Tab Bar Glass

```swift
// iOS 26 tab bars automatically use glass material
// The appearance is managed by the system

TabView {
    Tab("Home", systemImage: "house") { HomeView() }
    Tab("Settings", systemImage: "gear") { SettingsView() }
}
// No additional modifiers needed for glass tab bar
```
<!-- /section -->
