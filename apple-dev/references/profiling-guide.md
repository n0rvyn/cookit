# Performance Profiling Guide
<!-- SECTION MARKERS: Each "section" comment line immediately precedes the ##
     heading it labels. Use Grep("<!-- section:", file) to find sections, then
     Read(file, offset, limit) to fetch only the relevant lines. -->

iOS/macOS 性能分析最佳实践，涵盖 OSSignposter 插桩、MetricKit 集成、XCTest 性能测试、反模式扫描和 Instruments 工作流。

<!-- section: 1. OSSignposter 插桩 keywords: os_signpost, OSSignposter, signpost, interval, beginInterval, endInterval, emitEvent, animation -->
## 1. OSSignposter 插桩

### 创建 Signposter

```swift
import os

// 使用 subsystem + category（推荐）
let signposter = OSSignposter(subsystem: "com.myapp.networking", category: "URLSession")

// 从 Logger 创建（共享 subsystem/category）
let logger = Logger(subsystem: "com.myapp", category: "ImageLoading")
let signposter = OSSignposter(logger: logger)

// 禁用（Release build 中条件关闭）
let signposter: OSSignposter = isProfilingEnabled ? OSSignposter(subsystem: "com.myapp", category: "Debug") : .disabled
```

### beginInterval / endInterval 配对

```swift
let signposter = OSSignposter(subsystem: "com.myapp.networking", category: "API")

func fetchData(from url: URL) async throws -> Data {
    let signpostID = signposter.makeSignpostID()
    let state = signposter.beginInterval("FetchData", id: signpostID)

    defer { signposter.endInterval("FetchData", state) }

    let (data, _) = try await URLSession.shared.data(from: url)
    return data
}
```

### 携带 Metadata 的 Interval

```swift
func fetchUser(id: String) async throws -> User {
    let signpostID = signposter.makeSignpostID()
    let state = signposter.beginInterval("FetchUser", id: signpostID, "\(id, privacy: .public)")

    let user = try await api.getUser(id: id)

    signposter.endInterval("FetchUser", state, "status: \(user != nil ? "found" : "not found")")
    return user
}
```

### withIntervalSignpost 闭包测量

```swift
// 自动管理 begin/end，适合同步或 throws 代码
let result = signposter.withIntervalSignpost("ParseJSON", id: signposter.makeSignpostID()) {
    try JSONDecoder().decode(Response.self, from: data)
}
```

### beginAnimationInterval 动画测量

```swift
// 专用于动画的 signpost，Instruments 中以动画轨道显示
let state = signposter.beginAnimationInterval("CardFlip", id: signposter.makeSignpostID())

withAnimation(.spring(duration: 0.5)) {
    isFlipped.toggle()
}

// 动画完成后结束（通常在 completion 或 Transaction.addAnimationCompletion 中）
signposter.endInterval("CardFlip", state)
```

### emitEvent 标记兴趣点

```swift
// 标记单一时间点（无持续时间），用于按钮点击、状态变化等
signposter.emitEvent("UserTappedCheckout", id: signposter.makeSignpostID())

// 带 metadata
signposter.emitEvent("CacheHit", id: signposter.makeSignpostID(), "key: \(cacheKey, privacy: .public)")
```

### 并发环境下的 SignpostID

```swift
// 多个同名 interval 同时 in-flight 时，必须用不同 SignpostID
func loadImages(_ urls: [URL]) async {
    await withTaskGroup(of: Void.self) { group in
        for url in urls {
            group.addTask {
                let id = signposter.makeSignpostID()
                let state = signposter.beginInterval("LoadImage", id: id)
                defer { signposter.endInterval("LoadImage", state) }

                _ = try? await URLSession.shared.data(from: url)
            }
        }
    }
}

// 从对象派生 SignpostID（同一对象始终得到同一 ID）
let id = signposter.makeSignpostID(from: viewModel)
```

<!-- section: 2. MetricKit 集成 keywords: MetricKit, MXMetricManager, MXDiagnosticPayload, MXMetricPayload, metric report, subscriber -->
## 2. MetricKit 集成

### MXMetricManagerSubscriber 实现

```swift
import MetricKit

final class MetricsCollector: NSObject, MXMetricManagerSubscriber {
    static let shared = MetricsCollector()

    func startCollecting() {
        MXMetricManager.shared.add(self)
    }

    func stopCollecting() {
        MXMetricManager.shared.remove(self)
    }

    // 每 24 小时最多调用一次，包含前一天的聚合指标
    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            processMetricPayload(payload)
        }
    }

    // iOS 15+: 诊断报告立即送达（crash、hang、CPU exception、disk write）
    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        for payload in payloads {
            processDiagnosticPayload(payload)
        }
    }
}
```

### 关键 Metric 类

```swift
func processMetricPayload(_ payload: MXMetricPayload) {
    // 启动耗时
    if let launchMetric = payload.applicationLaunchMetrics {
        let histogram = launchMetric.histogrammedTimeToFirstDraw
        // histogram.bucketEnumerator 遍历各桶
    }

    // 响应性（hang 时间）
    if let responsiveness = payload.applicationResponsivenessMetrics {
        let hangTime = responsiveness.histogrammedApplicationHangTime
    }

    // CPU 使用
    if let cpu = payload.cpuMetrics {
        let cumulativeCPUTime = cpu.cumulativeCPUTime
    }

    // 内存
    if let memory = payload.memoryMetrics {
        let peakMemory = memory.peakMemoryUsage
    }

    // 磁盘 IO
    if let diskIO = payload.diskIOMetrics {
        let cumulativeWrites = diskIO.cumulativeLogicalWrites
    }

    // 自定义 Signpost 指标
    if let signpostMetrics = payload.signpostMetrics {
        for metric in signpostMetrics {
            print("Signpost: \(metric.signpostName), count: \(metric.totalCount)")
            print("  duration: \(metric.signpostIntervalDuration)")
        }
    }

    // 导出为 JSON 用于上报
    let jsonData = payload.jsonRepresentation()
}
```

### 诊断报告处理

```swift
func processDiagnosticPayload(_ payload: MXDiagnosticPayload) {
    // Crash 诊断
    if let crashes = payload.crashDiagnostics {
        for crash in crashes {
            let callStack = crash.callStackTree
            let jsonData = callStack.jsonRepresentation()
            // 上报到后端
        }
    }

    // Hang 诊断（主线程阻塞 > 250ms）
    if let hangs = payload.hangDiagnostics {
        for hang in hangs {
            let duration = hang.hangDuration
            let callStack = hang.callStackTree
        }
    }

    // CPU Exception
    if let cpuExceptions = payload.cpuExceptionDiagnostics {
        for exception in cpuExceptions {
            let totalCPUTime = exception.totalCPUTime
            let totalSampledTime = exception.totalSampledTime
        }
    }

    // 启动诊断（iOS 16+）
    if let launchDiagnostics = payload.appLaunchDiagnostics {
        for launch in launchDiagnostics {
            let launchDuration = launch.launchDuration
        }
    }
}
```

### MXSignpostMetric 自定义指标

```swift
// 在代码中使用 os_signpost 插桩
let signposter = OSSignposter(subsystem: "com.myapp", category: .pointsOfInterest)

func checkout() async throws {
    let state = signposter.beginInterval("Checkout")
    defer { signposter.endInterval("Checkout", state) }

    try await processPayment()
}

// MetricKit 自动收集 .pointsOfInterest category 下的 signpost
// 在 didReceive(_: [MXMetricPayload]) 中通过 payload.signpostMetrics 获取

// 创建自定义 log handle 用于 MetricKit 收集
let metricLog = MXMetricManager.makeLogHandle(category: "Checkout")
// 使用 mxSignpost API（兼容旧版 os_signpost 样式）
```

<!-- section: 3. XCTest 性能测试 keywords: measure, XCTMetric, performance test, baseline, XCTOSSignpostMetric, XCTHitchMetric, XCTApplicationLaunchMetric -->
## 3. XCTest 性能测试

### measure {} 基础用法

```swift
func testSortPerformance() {
    let data = (0..<10000).map { _ in Int.random(in: 0..<10000) }

    measure {
        _ = data.sorted()
    }
    // Xcode 自动运行多次，计算平均值和标准差
    // 首次运行后设置 baseline，后续检测回归
}
```

### XCTMetric 家族

```swift
// CPU 指标
func testCPUUsage() {
    let metrics: [any XCTMetric] = [
        XCTCPUMetric(),          // CPU 时间和指令数
        XCTClockMetric(),        // 挂钟时间
        XCTMemoryMetric(),       // 物理内存使用
        XCTStorageMetric(),      // 磁盘写入量
    ]

    measure(metrics: metrics) {
        performHeavyComputation()
    }
}

// 手动控制测量范围
func testDatabaseInsert() {
    let items = generateTestItems(count: 1000)

    measure(metrics: [XCTClockMetric()]) {
        // setUp 不计入测量
        let context = createInMemoryContext()

        startMeasuring()  // 从这里开始计时

        for item in items {
            context.insert(item)
        }
        try! context.save()

        stopMeasuring()  // 在这里结束计时

        // tearDown 不计入测量
        context.rollback()
    }
}
```

### XCTOSSignpostMetric

```swift
// 测量自定义 signpost 区间
func testCheckoutSignpost() {
    let metric = XCTOSSignpostMetric(
        subsystem: "com.myapp",
        category: "Checkout",
        name: "ProcessPayment"
    )

    measure(metrics: [metric]) {
        // 触发包含 signpost 的代码路径
        app.buttons["Pay Now"].tap()
        app.staticTexts["Payment Complete"].waitForExistence(timeout: 10)
    }
}

// 内置导航转场指标
func testNavigationTransition() {
    let metric = XCTOSSignpostMetric.navigationTransitionMetric

    measure(metrics: [metric]) {
        app.buttons["Settings"].tap()
        app.navigationBars["Settings"].waitForExistence(timeout: 5)
    }
}

// 滚动指标
func testScrollPerformance() {
    let metric = XCTOSSignpostMetric.scrollingAndDecelerationMetric

    measure(metrics: [metric]) {
        let list = app.collectionViews.firstMatch
        list.swipeUp(velocity: .fast)
    }
}
```

### XCTApplicationLaunchMetric

```swift
// 测量 app 启动到首帧
func testLaunchPerformance() {
    measure(metrics: [XCTApplicationLaunchMetric()]) {
        XCUIApplication().launch()
    }
}

// 测量启动到可交互（包含所有 extended launch task）
func testLaunchUntilResponsive() {
    measure(metrics: [XCTApplicationLaunchMetric(waitUntilResponsive: true)]) {
        XCUIApplication().launch()
    }
}
```

### XCTHitchMetric (iOS 26+)

```swift
// 测量 UI hitch（帧丢失）
// Hitch = app 未能在下一帧更新前准备好内容
@available(iOS 26.0, *)
func testScrollHitches() {
    let app = XCUIApplication()
    app.launch()

    let hitchMetric = XCTHitchMetric(application: app)

    measure(metrics: [hitchMetric]) {
        let list = app.collectionViews.firstMatch
        list.swipeUp(velocity: .fast)
        list.swipeUp(velocity: .fast)
        list.swipeDown(velocity: .fast)
    }
}
```

### 性能基线与 CI 回归检测

```swift
// 设置自定义基线（而非依赖 Xcode 自动基线）
func testAPIResponseTime() {
    let options = XCTMeasureOptions()
    options.iterationCount = 10  // 默认 5 次

    measure(options: options) {
        // 测试代码
    }
    // Xcode 中：Editor → Set Baseline → 选择目标值
    // CI 中：基线存储在 xcbaseline 文件中，随代码版本管理
}
```

<!-- section: 4. 性能反模式扫描 keywords: anti-pattern, main thread, re-render, performance issue, blocking, memory leak -->
## 4. 性能反模式扫描

### Main Thread Blocking

```swift
// ❌ 主线程同步网络请求
func loadData() {
    let data = try! Data(contentsOf: url)  // 阻塞主线程
    self.items = parse(data)
}

// ✅ 异步加载
func loadData() async {
    let (data, _) = try await URLSession.shared.data(from: url)
    self.items = parse(data)
}

// ❌ 主线程重计算
var body: some View {
    let sorted = items.sorted { $0.date > $1.date }  // 每次 body 都排序
    List(sorted) { item in ItemRow(item: item) }
}

// ✅ 预计算或缓存
@State private var sortedItems: [Item] = []

var body: some View {
    List(sortedItems) { item in ItemRow(item: item) }
}
.onChange(of: items) { _, newValue in
    sortedItems = newValue.sorted { $0.date > $1.date }
}
```

### SwiftUI Body 过度重计算

```swift
// ❌ 巨型 body：任何状态变化都触发整体重计算
var body: some View {
    VStack {
        HeaderView(title: title)
        // ... 200 行 View 代码 ...
        FooterView(count: items.count)
    }
}

// ✅ 提取子 View，缩小重计算范围
var body: some View {
    VStack {
        HeaderView(title: title)
        ContentSection(items: items)
        FooterView(count: items.count)
    }
}

// ❌ 在 body 中创建重对象
var body: some View {
    let formatter = DateFormatter()  // 每次 body 都创建
    formatter.dateStyle = .medium
    Text(formatter.string(from: date))
}

// ✅ 静态 formatter
private static let dateFormatter: DateFormatter = {
    let f = DateFormatter()
    f.dateStyle = .medium
    return f
}()
```

### 大图未降采样

```swift
// ❌ 加载原图到小 ImageView（内存浪费）
Image(uiImage: UIImage(named: "photo")!)
    .resizable()
    .frame(width: 100, height: 100)

// ✅ 降采样加载
func downsample(imageAt url: URL, to pointSize: CGSize, scale: CGFloat) -> UIImage? {
    let imageSourceOptions = [kCGImageSourceShouldCache: false] as CFDictionary
    guard let imageSource = CGImageSourceCreateWithURL(url as CFURL, imageSourceOptions) else { return nil }

    let maxDimensionInPixels = max(pointSize.width, pointSize.height) * scale
    let downsampleOptions = [
        kCGImageSourceCreateThumbnailFromImageAlways: true,
        kCGImageSourceShouldCacheImmediately: true,
        kCGImageSourceCreateThumbnailWithTransform: true,
        kCGImageSourceThumbnailMaxPixelSize: maxDimensionInPixels
    ] as CFDictionary

    guard let downsampledImage = CGImageSourceCreateThumbnailAtIndex(imageSource, 0, downsampleOptions) else { return nil }
    return UIImage(cgImage: downsampledImage)
}
```

### N+1 Fetch

```swift
// ❌ SwiftData relationship 循环访问（每次访问触发 fault）
for order in customer.orders {        // 1 次查询 customer
    for item in order.items {          // N 次查询 order.items
        print(item.name)
    }
}

// ✅ 预加载 relationship 或使用 FetchDescriptor
var descriptor = FetchDescriptor<Order>(
    predicate: #Predicate { $0.customer == targetCustomer }
)
descriptor.relationshipKeyPathsForPrefetching = [\.items]
let orders = try context.fetch(descriptor)
```

### 不必要的 @Published 触发

```swift
// ❌ 频繁触发 @Published（如搜索输入）
@Published var searchText = ""  // 每个字符都触发 UI 更新 + 搜索

// ✅ debounce
@Published var searchText = ""
private var searchCancellable: AnyCancellable?

init() {
    searchCancellable = $searchText
        .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
        .removeDuplicates()
        .sink { [weak self] query in
            self?.performSearch(query)
        }
}
```

### Timer/Observer 泄漏

```swift
// ❌ 未清理的 Timer
class ViewModel {
    var timer: Timer?

    func start() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            self.refresh()  // strong reference cycle
        }
    }
}

// ✅ weak self + 清理
class ViewModel {
    var timer: Timer?

    func start() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            self?.refresh()
        }
    }

    deinit {
        timer?.invalidate()
    }
}
```

<!-- section: 5. Instruments 工作流 keywords: Instruments, Time Profiler, Allocations, Leaks, template, xctrace -->
## 5. Instruments 工作流

### Template 选择指南

| 场景 | Template | 关注指标 |
|------|----------|----------|
| CPU 瓶颈 | Time Profiler | 热函数、调用栈权重 |
| 内存增长 | Allocations | 堆增长曲线、大分配 |
| 内存泄漏 | Leaks | 引用环、未释放对象 |
| SwiftUI 渲染 | SwiftUI | body 调用次数、更新频率 |
| 动画卡顿 | Animation Hitches | Hitch rate、commit duration |
| 网络请求 | Network | 请求时序、并发数、数据量 |
| 磁盘 IO | File Activity | 读写频率、同步 IO |
| App 启动 | App Launch | 启动阶段耗时分解 |

### Instruments CLI (xctrace)

```bash
# 录制 trace（使用 Time Profiler template）
xctrace record --device "iPhone" \
    --template "Time Profiler" \
    --attach "com.myapp.bundleid" \
    --output ~/Desktop/trace.trace \
    --time-limit 30s

# 使用自定义 template
xctrace record --template "/path/to/MyTemplate.tracetemplate" \
    --launch "com.myapp.bundleid" \
    --output ~/Desktop/trace.trace

# 导出 trace 数据为 XML
xctrace export --input ~/Desktop/trace.trace \
    --output ~/Desktop/trace-export

# 列出可用 template
xctrace list templates

# 列出可用设备
xctrace list devices
```

### 与 os_signpost 联动

1. 在代码中添加 OSSignposter 插桩（见 Section 1）
2. 打开 Instruments → 选择 os_signpost instrument（或 Logging → os_signpost）
3. 设置 filter 为你的 subsystem（如 `com.myapp.networking`）
4. 录制 → 在 timeline 上查看自定义 interval
5. 点击 interval 查看 metadata 和嵌套关系

### SwiftUI Instruments 分析要点

- **View Body**：关注 body 调用次数，高频调用 = 过度重计算
- **View Updates**：识别意外的更新来源（哪个 @State/@Binding 触发）
- **Core Animation Commits**：commit 耗时 > 16.67ms = 丢帧风险

<!-- section: 6. Signpost + MetricKit + XCTest 联动 keywords: integration, end-to-end profiling, workflow, full cycle -->
## 6. Signpost + MetricKit + XCTest 联动

### 三阶段闭环

```
开发阶段          测试阶段              生产阶段
─────────        ────────             ─────────
OSSignposter  →  XCTOSSignpostMetric  →  MetricKit
 ↓                ↓                      ↓
Instruments     性能回归检测            MXSignpostMetric
 ↓                ↓                      ↓
定位热点         CI 拦截退化             线上聚合监控
```

### 完整示例：监控图片加载性能

**Step 1: 开发 — 添加 Signpost 插桩**

```swift
import os

enum ImageLoaderSignposts {
    static let signposter = OSSignposter(subsystem: "com.myapp", category: "ImageLoading")

    static func trackLoad(url: URL) -> (OSSignpostIntervalState, StaticString) {
        let name: StaticString = "LoadImage"
        let state = signposter.beginInterval(name, id: signposter.makeSignpostID(),
            "\(url.lastPathComponent, privacy: .public)")
        return (state, name)
    }

    static func endLoad(state: OSSignpostIntervalState, name: StaticString, size: CGSize) {
        signposter.endInterval(name, state, "size: \(Int(size.width))x\(Int(size.height))")
    }
}
```

**Step 2: 测试 — 添加性能回归测试**

```swift
final class ImageLoadingPerformanceTests: XCTestCase {
    func testImageLoadPerformance() {
        let metric = XCTOSSignpostMetric(
            subsystem: "com.myapp",
            category: "ImageLoading",
            name: "LoadImage"
        )

        measure(metrics: [metric]) {
            let app = XCUIApplication()
            app.launch()
            app.buttons["Load Gallery"].tap()
            // 等待图片加载完成
            app.images["galleryImage_9"].waitForExistence(timeout: 10)
        }
    }
}
```

**Step 3: 生产 — MetricKit 自动收集**

```swift
// MetricKit 自动收集 .pointsOfInterest category 的 signpost
// 如果使用自定义 category，需要通过 MXMetricManager.makeLogHandle

func didReceive(_ payloads: [MXMetricPayload]) {
    for payload in payloads {
        if let signpostMetrics = payload.signpostMetrics {
            let imageMetrics = signpostMetrics.filter {
                $0.signpostName == "LoadImage"
            }
            for metric in imageMetrics {
                analytics.track("image_load_perf", properties: [
                    "count": metric.totalCount,
                    "avg_duration": metric.signpostAverageInterval,
                ])
            }
        }
    }
}
```

## 参考

- [Apple: Recording Performance Data](https://developer.apple.com/documentation/os/logging/recording_performance_data)
- [Apple: MetricKit](https://developer.apple.com/documentation/metrickit)
- [Apple: Writing Performance Tests](https://developer.apple.com/documentation/xcode/writing-and-running-performance-tests)
- [WWDC21: Diagnose Power and Performance Regressions in your App](https://developer.apple.com/videos/play/wwdc2021/10087/)
- [WWDC22: Track down hangs with Xcode and on-device detection](https://developer.apple.com/videos/play/wwdc2022/10082/)

### 相关 Skill

- `/testing-guide` — Unit Test、Mock/DI、TDD 基础
- `/xc-ui-test` — XCUITest 高级用法（多屏幕旅程、网络 stub、snapshot、CI 集成）
