# SwiftData Best Practices
<!-- SECTION MARKERS: Each "section" comment line immediately precedes the ##
     heading it labels. Use Grep("<!-- section:", file) to find sections, then
     Read(file, offset, limit) to fetch only the relevant lines. -->

SwiftData 是 Apple 在 iOS 17+ / macOS 14+ 引入的声明式数据持久化框架，替代 Core Data。

<!-- section: 1. @Model 定义 keywords: @Model, SwiftData model, properties, optional, @Transient, @Attribute -->
## 1. @Model 定义

### 基本类型

```swift
import SwiftData

@Model
final class Item {
    var name: String
    var timestamp: Date
    var isCompleted: Bool = false  // 默认值

    init(name: String, timestamp: Date) {
        self.name = name
        self.timestamp = timestamp
    }
}
```

### 可选属性处理

```swift
@Model
final class Task {
    var title: String
    var notes: String?  // 可选
    var dueDate: Date?

    init(title: String) {
        self.title = title
    }
}
```

### 不持久化属性

```swift
@Model
final class Product {
    var name: String
    var price: Double

    @Transient var displayPrice: String {
        String(format: "$%.2f", price)
    }
}
```

### 唯一性约束

```swift
@Model
final class User {
    @Attribute(.unique) var email: String
    var name: String

    init(email: String, name: String) {
        self.email = email
        self.name = name
    }
}
```

<!-- section: 2. 关系定义 keywords: relationships, one-to-many, many-to-many, @Relationship, inverse, delete rule, cascade -->
## 2. 关系定义

### 一对多

```swift
@Model
final class Category {
    var name: String
    @Relationship(deleteRule: .cascade) var items: [Item] = []
}

@Model
final class Item {
    var name: String
    var category: Category?
}
```

**删除规则**：
- `.cascade`：删除父对象时删除所有子对象
- `.nullify`：删除父对象时将子对象的关系设为 nil（默认）
- `.deny`：如果有子对象，拒绝删除父对象

### 多对多

```swift
@Model
final class Student {
    var name: String
    var courses: [Course] = []
}

@Model
final class Course {
    var title: String
    var students: [Student] = []
}
```

### 反向关系

```swift
@Model
final class Post {
    var title: String
    @Relationship(deleteRule: .cascade, inverse: \Comment.post)
    var comments: [Comment] = []
}

@Model
final class Comment {
    var content: String
    var post: Post?
}
```

<!-- section: 3. 查询 keywords: @Query, predicate, filter, sort, FetchDescriptor, dynamic query -->
## 3. 查询

### @Query 基础

```swift
import SwiftUI
import SwiftData

struct ItemListView: View {
    @Query var items: [Item]

    var body: some View {
        List(items) { item in
            Text(item.name)
        }
    }
}
```

### Filter descriptor

```swift
// 简单过滤
@Query(filter: #Predicate<Item> { item in
    item.isCompleted == false
}) var activeItems: [Item]

// 字符串包含
@Query(filter: #Predicate<Item> { item in
    item.name.contains("important")
}) var importantItems: [Item]

// 日期范围
@Query(filter: #Predicate<Item> { item in
    item.timestamp > Date().addingTimeInterval(-86400)
}) var recentItems: [Item]

// 组合条件
@Query(filter: #Predicate<Item> { item in
    !item.isCompleted && item.priority > 5
}) var highPriorityActive: [Item]
```

### Sort descriptor

```swift
// 单字段排序
@Query(sort: \Item.timestamp, order: .reverse) var items: [Item]

// 多字段排序
@Query(sort: [
    SortDescriptor(\Item.isCompleted),
    SortDescriptor(\Item.timestamp, order: .reverse)
]) var items: [Item]
```

### 组合 Filter + Sort

```swift
@Query(
    filter: #Predicate<Item> { $0.isCompleted == false },
    sort: \Item.timestamp,
    order: .reverse
) var activeItems: [Item]
```

### 动态查询

```swift
struct ItemListView: View {
    @State private var searchText = ""

    var body: some View {
        ItemListContent(searchText: searchText)
            .searchable(text: $searchText)
    }
}

struct ItemListContent: View {
    let searchText: String

    @Query private var items: [Item]

    init(searchText: String) {
        self.searchText = searchText

        let predicate = #Predicate<Item> { item in
            searchText.isEmpty || item.name.contains(searchText)
        }

        _items = Query(filter: predicate, sort: \.timestamp)
    }

    var body: some View {
        List(items) { item in
            Text(item.name)
        }
    }
}
```

<!-- section: 4. 数据迁移 keywords: migration, versioned schema, ModelMigrationPlan, lightweight migration -->
## 4. 数据迁移

### Schema version

```swift
enum ItemSchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)

    static var models: [any PersistentModel.Type] {
        [Item.self]
    }

    @Model
    final class Item {
        var name: String
        var timestamp: Date
    }
}

enum ItemSchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)

    static var models: [any PersistentModel.Type] {
        [Item.self]
    }

    @Model
    final class Item {
        var name: String
        var timestamp: Date
        var isCompleted: Bool = false  // 新增字段
    }
}
```

### Migration plan

```swift
enum ItemMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] {
        [ItemSchemaV1.self, ItemSchemaV2.self]
    }

    static var stages: [MigrationStage] {
        [migrateV1toV2]
    }

    static let migrateV1toV2 = MigrationStage.custom(
        fromVersion: ItemSchemaV1.self,
        toVersion: ItemSchemaV2.self,
        willMigrate: nil,
        didMigrate: { context in
            // 数据转换逻辑（如需要）
            let items = try context.fetch(FetchDescriptor<Item>())
            for item in items {
                // 自定义迁移逻辑
            }
            try context.save()
        }
    )
}
```

### 轻量级迁移

对于简单的架构变更（添加可选字段、添加默认值），SwiftData 自动处理，无需编写 migration plan。

**支持自动迁移的场景**：
- 添加新的可选属性
- 添加带默认值的属性
- 删除属性
- 重命名实体或属性（使用 `@Attribute(.originalName:)` 标记）

<!-- section: 5. 并发安全 keywords: concurrency, ModelContext, thread safety, MainActor, background task -->
## 5. 并发安全

### @MainActor 使用

```swift
@MainActor
final class ItemService {
    private let modelContext: ModelContext

    init(modelContext: ModelContext) {
        self.modelContext = modelContext
    }

    func createItem(name: String) {
        let item = Item(name: name, timestamp: .now)
        modelContext.insert(item)
        try? modelContext.save()
    }

    func deleteItem(_ item: Item) {
        modelContext.delete(item)
        try? modelContext.save()
    }
}
```

### ModelContext 线程安全

```swift
// ❌ 错误：跨线程使用 ModelContext
Task.detached {
    modelContext.insert(item)  // Crash!
}

// ✅ 正确：在后台线程创建新的 ModelContext
Task.detached {
    let backgroundContext = ModelContext(modelContainer)
    let item = Item(name: "Background", timestamp: .now)
    backgroundContext.insert(item)
    try? backgroundContext.save()
}
```

### 后台任务处理

```swift
@MainActor
final class DataImportService {
    private let modelContainer: ModelContainer

    init(modelContainer: ModelContainer) {
        self.modelContainer = modelContainer
    }

    func importLargeDataset() async {
        await Task.detached { [modelContainer] in
            let context = ModelContext(modelContainer)

            // 执行大量数据插入
            for i in 0..<10000 {
                let item = Item(name: "Item \(i)", timestamp: .now)
                context.insert(item)

                // 定期保存以避免内存过大
                if i % 100 == 0 {
                    try? context.save()
                }
            }

            try? context.save()
        }.value
    }
}
```

### Actor 隔离

```swift
actor BackgroundProcessor {
    private let modelContainer: ModelContainer

    init(modelContainer: ModelContainer) {
        self.modelContainer = modelContainer
    }

    func processItems() async throws {
        let context = ModelContext(modelContainer)
        let items = try context.fetch(FetchDescriptor<Item>())

        for item in items {
            // 处理逻辑
            item.isCompleted = true
        }

        try context.save()
    }
}
```

<!-- section: 6. 性能优化 keywords: performance, lazy loading, batch, memory, optimization -->
## 6. 性能优化

### 批量操作

```swift
// ✅ 推荐：批量插入后保存
func insertBatch(_ names: [String]) {
    for name in names {
        let item = Item(name: name, timestamp: .now)
        modelContext.insert(item)
    }
    try? modelContext.save()  // 一次保存
}

// ❌ 避免：每次插入都保存
func insertOneByOne(_ names: [String]) {
    for name in names {
        let item = Item(name: name, timestamp: .now)
        modelContext.insert(item)
        try? modelContext.save()  // 性能差
    }
}
```

### 限制查询结果

```swift
// 使用 fetchLimit 避免加载过多数据
var descriptor = FetchDescriptor<Item>()
descriptor.fetchLimit = 50
let items = try? modelContext.fetch(descriptor)
```

### 惰性加载关系

SwiftData 默认惰性加载关系，只在访问时加载。保持这个默认行为。

<!-- section: 7. 测试 keywords: testing, in-memory, ModelContainer, unit test, SwiftData testing -->
## 7. 测试

### 内存数据库

```swift
@MainActor
final class ItemServiceTests: XCTestCase {
    var modelContainer: ModelContainer!
    var modelContext: ModelContext!

    override func setUp() async throws {
        // 使用内存配置进行测试
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        modelContainer = try ModelContainer(
            for: Item.self,
            configurations: config
        )
        modelContext = ModelContext(modelContainer)
    }

    func testCreateItem() {
        let item = Item(name: "Test", timestamp: .now)
        modelContext.insert(item)
        try? modelContext.save()

        let items = try? modelContext.fetch(FetchDescriptor<Item>())
        XCTAssertEqual(items?.count, 1)
    }
}
```

## 参考

- [Apple SwiftData Documentation](https://developer.apple.com/documentation/swiftdata)
- [WWDC23: Meet SwiftData](https://developer.apple.com/videos/play/wwdc2023/10187/)
- [WWDC23: Model your schema with SwiftData](https://developer.apple.com/videos/play/wwdc2023/10195/)
