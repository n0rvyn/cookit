# Swift / SwiftUI API Changes — iOS 18 / Swift 6.0

Seed content for WWDC 2024 APIs. Used by `ios-swift-context` skill for section-targeted loading.

---

<!-- section: TabView keywords: TabView, Tab, tabItem, tab -->
## TabView Architecture (iOS 18)

**Minimum OS**: iOS 18.0

### New API: `Tab` type

iOS 18 introduces the `Tab` type to replace `.tabItem {}` modifier.

```swift
// ✅ iOS 18+ new API
TabView {
    Tab("Home", systemImage: "house") {
        HomeView()
    }
    Tab("Settings", systemImage: "gear") {
        SettingsView()
    }
}

// ⚠️ Old API — still works but deprecated in style
TabView {
    HomeView()
        .tabItem {
            Label("Home", systemImage: "house")
        }
}
```

**Key features**:
- `Tab` supports `value:` for programmatic selection
- `TabSection` groups tabs (sidebar-style on iPad)
- `Tab("title", systemImage: "icon", role: .search)` for special roles

**Backward compatibility**: `.tabItem {}` still compiles on iOS 18 — no forced migration.
New `Tab` type is only available iOS 18+.

**Common mistakes**:
- ❌ Mixing old `.tabItem` and new `Tab` in the same `TabView`
- ❌ Using `Tab` without `@available(iOS 18, *)` when supporting iOS 17
<!-- /section -->

---

<!-- section: Entry macro keywords: @Entry, Environment, FocusedValues, EnvironmentValues -->
## @Entry Macro (iOS 18)

**Minimum OS**: iOS 18.0

Replaces boilerplate `EnvironmentKey` / `FocusedValueKey` conformances.

```swift
// ✅ iOS 18+ — @Entry macro
extension EnvironmentValues {
    @Entry var appTheme: AppTheme = .default
}

// ❌ Old way — still valid pre-iOS 18
private struct AppThemeKey: EnvironmentKey {
    static let defaultValue: AppTheme = .default
}
extension EnvironmentValues {
    var appTheme: AppTheme {
        get { self[AppThemeKey.self] }
        set { self[AppThemeKey.self] = newValue }
    }
}
```

Also works for `FocusedValues`:
```swift
extension FocusedValues {
    @Entry var selectedItem: Item? = nil
}
```

**Common mistakes**:
- ❌ Forgetting `@available(iOS 18, *)` when minimum deployment target is lower
<!-- /section -->

---

<!-- section: Previewable keywords: @Previewable, Preview, @State, previews -->
## @Previewable Macro (iOS 18)

**Minimum OS**: iOS 18.0

Allows `@State` variables directly inside `#Preview` without a wrapper view.

```swift
// ✅ iOS 18+ — @Previewable
#Preview {
    @Previewable @State var isOn = false
    Toggle("Enable", isOn: $isOn)
}

// ❌ Old way — required wrapper view
struct TogglePreview: View {
    @State var isOn = false
    var body: some View {
        Toggle("Enable", isOn: $isOn)
    }
}
#Preview { TogglePreview() }
```

**Common mistakes**:
- ❌ Using `@State` directly in `#Preview` without `@Previewable` (compile error on iOS 17)
<!-- /section -->

---

<!-- section: MeshGradient keywords: MeshGradient, gradient, mesh -->
## MeshGradient (iOS 18)

**Minimum OS**: iOS 18.0

New gradient type with a grid of control points.

```swift
// ✅ iOS 18+
MeshGradient(
    width: 3,
    height: 3,
    points: [
        .init(0, 0), .init(0.5, 0), .init(1, 0),
        .init(0, 0.5), .init(0.5, 0.5), .init(1, 0.5),
        .init(0, 1), .init(0.5, 1), .init(1, 1)
    ],
    colors: [
        .red, .purple, .indigo,
        .orange, .white, .blue,
        .yellow, .green, .mint
    ]
)
```

**Common mistakes**:
- ❌ Mismatching point count with `width * height` (runtime crash)
- ❌ Using on iOS 17 without `@available` guard
<!-- /section -->

---

<!-- section: ScrollPosition keywords: scrollPosition, ScrollView, scrollTo -->
## ScrollPosition API (iOS 18)

**Minimum OS**: iOS 18.0 (enhanced; basic `scrollPosition(id:)` available iOS 17)

```swift
// ✅ iOS 18+ — ScrollPosition type
@State private var position = ScrollPosition(edge: .top)

ScrollView {
    ForEach(items) { item in
        ItemRow(item: item)
            .id(item.id)
    }
}
.scrollPosition($position)

// Programmatic scroll
Button("Scroll to top") {
    position.scrollTo(edge: .top)
}
```

**vs iOS 17 API**:
```swift
// iOS 17 — scrollPosition(id:)
@State private var scrolledID: Item.ID?
ScrollView {
    ForEach(items) { item in
        ItemRow(item: item).id(item.id)
    }
}
.scrollPosition(id: $scrolledID)
```

**Common mistakes**:
- ❌ Using `ScrollPosition` type on iOS 17 (type not available)
- ❌ Forgetting `.id()` on items when using id-based scroll position
<!-- /section -->

---

<!-- section: Observable SwiftData keywords: @Observable, @Model, SwiftData, Observation -->
## @Observable + SwiftData Integration (iOS 18)

**Minimum OS**: @Observable — iOS 17.0; SwiftData — iOS 17.0; Integration improvements — iOS 18.0

### iOS 18 SwiftData Improvements

- `#Predicate` now supports more operators and nested relationships
- `@Query` can be initialized with dynamic sort descriptors without full reinit
- `ModelContext.fetch(_:batchSize:)` for memory-efficient large dataset iteration
- Schema migrations are more reliable with `ModelContainer(for:migrationPlan:)`

### @Observable vs ObservableObject

```swift
// ✅ iOS 17+ — @Observable (preferred for new code)
@Observable
class ViewModel {
    var items: [Item] = []
    var isLoading = false
}

// Use in View — no property wrapper needed
struct MyView: View {
    var model: ViewModel  // not @ObservedObject
    var body: some View {
        if model.isLoading { ProgressView() }
    }
}

// ❌ Pre-iOS 17 pattern — ObservableObject
class ViewModel: ObservableObject {
    @Published var items: [Item] = []
}
```

**Common mistakes**:
- ❌ Adding `@Published` inside `@Observable` class (redundant, generates warning)
- ❌ Using `@StateObject` or `@ObservedObject` with `@Observable` class (use plain `@State` or `var`)
<!-- /section -->

---

<!-- section: ContainerValues keywords: ContainerValues, containerValue, container -->
## ContainerValues (iOS 18)

**Minimum OS**: iOS 18.0

Allows views to pass typed values up to container views (reverse of Environment).

```swift
extension ContainerValues {
    @Entry var badge: Int = 0
}

// In content view
SomeView()
    .containerValue(\.badge, 5)

// In container view body — read from subviews
ForEach(subviews) { subview in
    subview
    BadgeView(count: subview.containerValues.badge)
}
```
<!-- /section -->

---

<!-- section: Swift6 keywords: Swift 6, concurrency, Sendable, actor, complete concurrency -->
## Swift 6.0 Complete Concurrency

**Minimum**: Swift 6.0 (Xcode 16+)

Swift 6 enforces complete concurrency checking by default.

### Key Changes

**Actor isolation by default for SwiftUI views**:
```swift
// Swift 6 — View body runs on MainActor
// @State, @StateObject automatically MainActor-isolated

// ⚠️ Crossing actor boundaries requires explicit handling
struct MyView: View {
    var body: some View {
        Button("Fetch") {
            Task {
                // This runs on MainActor (inherited from button action)
                await viewModel.fetch()  // viewModel must be Sendable or MainActor-isolated
            }
        }
    }
}
```

**Sendable conformance**:
```swift
// ✅ Value types are Sendable by default
struct UserProfile: Sendable {
    let id: UUID
    let name: String
}

// ✅ Actors are Sendable
actor DataManager {
    func fetchData() async -> [Item] { ... }
}
```

**Common migration patterns**:
- `@MainActor` on ViewModel class to isolate all properties
- `nonisolated` for pure functions that don't need actor isolation
- `AsyncStream` for bridging callback-based APIs

**Common mistakes**:
- ❌ Passing non-Sendable types across actor boundaries (Swift 6 error)
- ❌ Storing mutable state in structs passed between actors
<!-- /section -->
