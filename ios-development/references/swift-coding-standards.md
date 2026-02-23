# Swift/iOS 通用编码规范
<!-- SECTION MARKERS: Each "section" comment line immediately precedes the ##
     heading it labels. Use Grep("<!-- section:", file) to find sections, then
     Read(file, offset, limit) to fetch only the relevant lines. -->

> **适用**: Swift 6+ / iOS 18+ / SwiftUI / SwiftData
> **引用方式**: 项目级 coding-standards 引用本文件，只保留项目特定规则

---

<!-- section: 1. Swift 命名规范 keywords: naming, types, variables, functions, enums, protocols, lowerCamelCase, UpperCamelCase -->
## 1. Swift 命名规范

基于 [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)

### 1.1 类型命名

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| Class/Struct/Enum | UpperCamelCase | `TrainingLogViewModel` |
| Protocol | UpperCamelCase + Protocol 后缀 | `HealthKitServiceProtocol` |
| SwiftData Model | UpperCamelCase（项目可定前缀） | `CachedTrainingLog` |
| DTO | UpperCamelCase + DTO 后缀 | `TrainingLogDTO` |
| Mapper | UpperCamelCase + Mapper 后缀 | `TrainingLogMapper` |
| Mock | Mock 前缀 | `MockHealthKitService` |

### 1.2 变量/常量命名

```swift
// lowerCamelCase
let userName = "John"
var currentWeek = 1

// 布尔值：is/has/should/can 前缀
var isLoading = false
var hasCompletedOnboarding = true

// 集合：复数形式
var trainingLogs: [TrainingLog] = []

// 可选值：类型已说明可选性，名称不加 optional
var targetDate: Date?  // ✅
var optionalTargetDate: Date?  // ❌
```

### 1.3 函数命名

```swift
// lowerCamelCase + 动词开头
func fetchTrainingLogs() async throws -> [TrainingLog]
func calculateCTL(for logs: [TrainingLog]) -> Double

// 布尔返回值：is/has/can 前缀
func isValid() -> Bool
func hasCompletedOnboarding() -> Bool
```

### 1.4 枚举

```swift
enum GoalType {
    case race      // lowerCamelCase
    case habit
    case health
}

// 关联值带标签
enum NetworkError: Error {
    case timeout(duration: TimeInterval)
    case serverError(code: Int, details: String)
}
```

---

<!-- section: 2. 代码组织 keywords: file structure, MARK, organization, code layout -->
## 2. 代码组织

### 2.1 文件结构

```swift
import SwiftUI
import SwiftData

// MARK: - ViewModel
@MainActor
@Observable
final class TrainingLogViewModel {

    // MARK: - Properties
    private let service: HealthKitServiceProtocol
    var trainingLogs: [TrainingLog] = []
    var isLoading = false

    // MARK: - Initialization
    init(service: HealthKitServiceProtocol) {
        self.service = service
    }

    // MARK: - Public Methods
    func fetchLogs() async { ... }

    // MARK: - Private Methods
    private func processLogs() { ... }
}

// MARK: - Helpers
private extension TrainingLogViewModel { ... }
```

### 2.2 MARK 分组顺序

```swift
// MARK: - Properties
// MARK: - Computed Properties
// MARK: - Initialization
// MARK: - Lifecycle
// MARK: - Public Methods
// MARK: - Private Methods
// MARK: - Protocol Conformance
```

---

<!-- section: 3. 并发编程 (Swift 6+) keywords: concurrency, async, await, MainActor, actor, Swift 6, sendable -->
## 3. 并发编程 (Swift 6+)

### 3.1 核心原则

1. **单线程优先** - 默认代码运行在主线程
2. **显式标记并发** - 只有需要并发时才显式指定
3. **ViewModel 必须 @MainActor** - 所有 UI 相关代码

### 3.2 @MainActor 使用

```swift
// ✅ ViewModel 显式标记
@MainActor
@Observable
final class TrainingLogViewModel {
    var trainingLogs: [TrainingLog] = []

    func fetchLogs() async {
        let logs = try await service.fetchLogs()  // 后台执行
        trainingLogs = logs  // 回到主线程
    }
}

// ❌ 缺少 @MainActor
@Observable
final class TrainingLogViewModel { ... }  // 编译警告
```

### 3.3 SwiftData 并发（⚠️ 重要）

**核心问题**：`@Model` 不是 `Sendable`，不能跨 actor 边界传递。

```swift
// ❌ 错误：actor 内访问 @Model
actor MyService {
    func process(_ entry: FoodEntry) async { ... }
}

// ❌ 错误：Task 中捕获 @Model
func doSomething(entry: FoodEntry) {
    Task {
        let name = entry.name  // 编译错误
    }
}

// ✅ 正确：跨 Task 边界前提取值
func doSomething(entry: FoodEntry) {
    let id = entry.id
    let name = entry.name
    Task {
        await process(id: id, name: name)
    }
}

// ✅ 正确：访问 @Model 的 Service 使用 @MainActor
@MainActor
final class DataSyncService {
    static let shared = DataSyncService()

    func syncEntry(_ entry: FoodEntry) async throws {
        // 同在 MainActor，无隔离问题
    }
}
```

**Service 类型选择**：

| 场景 | 推荐类型 |
|------|----------|
| 访问 @Model | `@MainActor final class` |
| 纯网络请求 | `actor` 或 `@MainActor final class` |
| View 使用的 Service | `@MainActor final class` |
| 后台计算（无 UI） | `actor` |

### 3.4 Protocol 隔离

```swift
// ✅ 访问 @Model 的 Protocol 使用 @MainActor
@MainActor
protocol DataServiceProtocol {
    func fetch() async throws -> [Entry]
}
```

---

<!-- section: 4. SwiftUI 最佳实践 keywords: SwiftUI, view, state, binding, observable, environment -->
## 4. SwiftUI 最佳实践

### 4.1 View 命名

```swift
// ✅ View 后缀
struct TrainingLogView: View { }
struct TrainingLogCard: View { }

// ❌ 缺少后缀
struct TrainingLog: View { }
```

### 4.2 状态管理

```swift
// ViewModel：@Observable + @State
@MainActor
@Observable
final class TrainingLogViewModel { ... }

struct TrainingLogView: View {
    @State private var viewModel = TrainingLogViewModel()
}

// 简单局部状态：@State
@State private var email = ""
@State private var isShowingAlert = false

// 环境值
@Environment(\.modelContext) private var modelContext
```

### 4.3 View 分解

```swift
struct TrainingLogView: View {
    var body: some View {
        NavigationStack {
            contentView
                .navigationTitle("训练日志")
                .toolbar { toolbarContent }
        }
    }

    // 私有 computed property 分解
    private var contentView: some View { ... }

    @ToolbarContentBuilder
    private var toolbarContent: some ToolbarContent { ... }
}
```

---

<!-- section: 5. iOS 版本适配 keywords: version, compatibility, availability, iOS version, deprecation -->
## 5. iOS 版本适配

### 5.1 #available 检查

```swift
// iOS 26+ 特性（有降级方案）
if #available(iOS 26, *) {
    // iOS 26 特性
} else {
    // iOS 18 降级方案
}

// 标准组件自动适配新特性，无需额外代码
```

### 5.2 版本注释

```swift
// ⚠️ iOS 26+: Apple Intelligence Foundation Models
// ✅ iOS 18+: WorkoutKit 稳定版本
// ❌ iOS 17: 不支持（Observable 宏不稳定）
```

---

<!-- section: 6. Git 工作流 keywords: git, commit, branch, workflow, version control -->
## 6. Git 工作流

### 6.1 分支策略

```
main (production)
├── develop (主开发)
│   ├── feature/xxx (功能分支)
│   ├── fix/xxx (修复分支)
│   └── refactor/xxx (重构分支)
└── release/x.x.x (发布分支)
```

### 6.2 Commit 规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**:
- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 重构（无功能变化）
- `docs`: 文档
- `style`: 格式（不影响代码）
- `test`: 测试
- `chore`: 构建/工具

**示例**:
```
feat(training): 添加训练日志导出功能

- 支持 CSV 和 JSON 格式导出
- 添加日期范围选择器
- 支持后台导出大量数据

Closes #123
```

---

<!-- section: 7. 代码审查清单 keywords: code review, checklist, review -->
## 7. 代码审查清单

### 7.1 必查项

- [ ] 命名符合规范（驼峰、清晰、无缩写）
- [ ] ViewModel 有 @MainActor
- [ ] @Model 未跨 actor 边界传递
- [ ] UI 文本使用本地化
- [ ] 错误有 catch 处理
- [ ] 无硬编码（颜色、尺寸、API Key）

### 7.2 性能项

- [ ] List 使用 LazyVStack/LazyHStack
- [ ] 大量数据使用分页
- [ ] 图片使用异步加载
- [ ] 避免 body 中执行耗时操作

---

<!-- section: 8. 性能优化 keywords: performance, optimization, memory, lazy, profiling -->
## 8. 性能优化

### 8.1 SwiftUI 性能

```swift
// ✅ 使用 Lazy 容器
LazyVStack { ... }
LazyHStack { ... }

// ✅ 使用 id 优化 ForEach
ForEach(items, id: \.id) { item in ... }

// ✅ 避免 body 中计算
// 使用 computed property 或缓存

// ❌ 避免频繁创建新对象
var body: some View {
    let formatter = DateFormatter()  // ❌ 每次渲染都创建
}
```

### 8.2 SwiftData 性能

```swift
// ✅ 使用 @Query 的 filter 和 sort
@Query(filter: #Predicate { $0.date > threshold },
       sort: \.date, order: .reverse)
var recentLogs: [TrainingLog]

// ✅ 批量操作使用 transaction
try modelContext.transaction {
    for item in items {
        modelContext.insert(item)
    }
}

// ❌ 避免循环中单独 save
for item in items {
    modelContext.insert(item)
    try modelContext.save()  // ❌ 性能差
}
```

---

<!-- section: 9. 避坑指南 keywords: pitfalls, gotchas, common mistakes, warnings -->
## 9. 避坑指南

### 9.1 SwiftData 常见坑

```swift
// ❌ 坑：@Model 在 Task 中使用
Task {
    let name = entry.name  // 编译错误
}

// ✅ 解决：提取值后再使用
let name = entry.name
Task {
    await process(name: name)
}
```

### 9.2 并发常见坑

```swift
// ❌ 坑：default parameter 访问 @MainActor 属性
init(service: MyService = MyService.shared) { }

// ✅ 解决：使用 convenience init
init(service: MyService) { self.service = service }
convenience init() { self.init(service: MyService.shared) }
```

### 9.3 SwiftUI 常见坑

```swift
// ❌ 坑：在 body 中修改 @State
var body: some View {
    isLoading = true  // ❌ 禁止
}

// ✅ 解决：使用 .task 或 .onAppear
.task {
    isLoading = true
}
```

---

<!-- section: 10. 本地化规范 keywords: localization, strings, localized, l10n -->
## 10. 本地化规范

### 10.1 String Catalog

```swift
// ✅ 使用 String(localized:)
Text(String(localized: "保存", table: "Common"))

// ✅ 带参数
String(localized: "共 \(count) 条记录", table: "Transaction")

// ❌ 硬编码
Text("保存")
```

### 10.2 Table 命名

按功能模块命名：`Account`、`Transaction`、`Settings`、`Common` 等。

---

## 项目特定规则

以下内容放在项目级 `docs/08-guidelines/coding-standards.md` 或项目 `CLAUDE.md`：

1. **版本支持策略** - 具体支持的 iOS 版本（26/18/17）
2. **@Model 类型列表** - 项目的 SwiftData Model 类型
3. **Service 单例列表** - 项目的 Service 单例
4. **命名约定** - 项目特定前缀（如 Cached、App）
5. **本地化 Table** - 项目的模块名列表
6. **Design System** - 项目的颜色、间距、字体 Token
