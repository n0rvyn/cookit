# Testing Workflow Guide
<!-- SECTION MARKERS: Each "section" comment line immediately precedes the ##
     heading it labels. Use Grep("<!-- section:", file) to find sections, then
     Read(file, offset, limit) to fetch only the relevant lines. -->

iOS/Swift 测试最佳实践，涵盖 Unit Test、UI Test、Mock 模式和 TDD 流程。

<!-- section: 1. Unit Test 组织 keywords: unit test, Given-When-Then, setUp, tearDown, XCTestCase, naming -->
## 1. Unit Test 组织

### Given-When-Then 模式

```swift
import XCTest
@testable import MyApp

final class ItemServiceTests: XCTestCase {
    var sut: ItemService!  // System Under Test
    var mockRepository: MockItemRepository!

    override func setUp() {
        super.setUp()
        mockRepository = MockItemRepository()
        sut = ItemService(repository: mockRepository)
    }

    override func tearDown() {
        sut = nil
        mockRepository = nil
        super.tearDown()
    }

    func testCreateItem_WithValidName_InsertsItemAndSaves() {
        // Given
        let itemName = "Test Item"

        // When
        sut.createItem(name: itemName)

        // Then
        XCTAssertEqual(mockRepository.insertedItems.count, 1)
        XCTAssertEqual(mockRepository.insertedItems.first?.name, itemName)
        XCTAssertTrue(mockRepository.saveCalled)
    }
}
```

### 测试命名规范

**格式**: `test<MethodName>_<Scenario>_<ExpectedResult>`

```swift
func testLogin_WithValidCredentials_ReturnsSuccess()
func testLogin_WithInvalidPassword_ReturnsError()
func testLogin_WhenNetworkFails_ThrowsNetworkError()
```

### Setup 和 Teardown

```swift
final class ViewModelTests: XCTestCase {
    var sut: HomeViewModel!
    var mockService: MockDataService!

    // 每个测试前执行
    override func setUp() {
        super.setUp()
        mockService = MockDataService()
        sut = HomeViewModel(service: mockService)
    }

    // 每个测试后执行
    override func tearDown() {
        sut = nil
        mockService = nil
        super.tearDown()
    }

    // 所有测试前执行一次
    override class func setUp() {
        super.setUp()
        // 全局配置
    }
}
```

<!-- section: 2. UI Test 最佳实践 keywords: UI test, XCUITest, Page Object, element identification, wait -->
## 2. UI Test 最佳实践

### Page Object 模式

```swift
// LoginPage.swift
struct LoginPage {
    let app: XCUIApplication

    // Elements
    var emailField: XCUIElement {
        app.textFields["emailTextField"]
    }

    var passwordField: XCUIElement {
        app.secureTextFields["passwordTextField"]
    }

    var loginButton: XCUIElement {
        app.buttons["loginButton"]
    }

    var errorLabel: XCUIElement {
        app.staticTexts["errorLabel"]
    }

    // Actions
    func enterEmail(_ email: String) {
        emailField.tap()
        emailField.typeText(email)
    }

    func enterPassword(_ password: String) {
        passwordField.tap()
        passwordField.typeText(password)
    }

    func tapLogin() {
        loginButton.tap()
    }

    // Verifications
    func isDisplayed() -> Bool {
        emailField.exists && passwordField.exists && loginButton.exists
    }

    func errorMessage() -> String? {
        errorLabel.exists ? errorLabel.label : nil
    }
}

// LoginUITests.swift
final class LoginUITests: XCTestCase {
    var app: XCUIApplication!
    var loginPage: LoginPage!

    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
        loginPage = LoginPage(app: app)
    }

    func testLogin_WithValidCredentials_NavigatesToHome() {
        // Given
        XCTAssertTrue(loginPage.isDisplayed())

        // When
        loginPage.enterEmail("test@example.com")
        loginPage.enterPassword("password123")
        loginPage.tapLogin()

        // Then
        let homeTitle = app.navigationBars["Home"].exists
        XCTAssertTrue(homeTitle)
    }
}
```

### 等待策略

```swift
// ❌ 避免：固定延迟
sleep(2)

// ✅ 推荐：等待条件
func waitForElement(_ element: XCUIElement, timeout: TimeInterval = 5) {
    let predicate = NSPredicate(format: "exists == true")
    let expectation = XCTNSPredicateExpectation(predicate: predicate, object: element)
    let result = XCTWaiter().wait(for: [expectation], timeout: timeout)
    XCTAssertEqual(result, .completed)
}

// 使用
waitForElement(app.buttons["continueButton"])

// 或使用 XCUIElement 的内置等待
let button = app.buttons["continueButton"]
XCTAssertTrue(button.waitForExistence(timeout: 5))
```

### 截图和录屏

```swift
func testCriticalFlow() {
    // 截图
    let screenshot = app.screenshot()
    let attachment = XCTAttachment(screenshot: screenshot)
    attachment.name = "Login Screen"
    attachment.lifetime = .keepAlways
    add(attachment)

    // 继续测试...
}

// 启用录屏（在测试类级别）
override class func setUp() {
    super.setUp()
    // 录制失败的测试
    XCUIDevice.shared.recordingMode = .failuresOnly
}
```

<!-- section: 3. Mock 和 Dependency Injection keywords: mock, dependency injection, protocol, test double, stub, fake -->
## 3. Mock 和 Dependency Injection

### Protocol-based Mocking

```swift
// Service protocol
protocol ItemRepositoryProtocol {
    func fetchItems() async throws -> [Item]
    func saveItem(_ item: Item) async throws
}

// Production implementation
final class ItemRepository: ItemRepositoryProtocol {
    func fetchItems() async throws -> [Item] {
        // Real implementation
    }

    func saveItem(_ item: Item) async throws {
        // Real implementation
    }
}

// Mock implementation
final class MockItemRepository: ItemRepositoryProtocol {
    var items: [Item] = []
    var fetchItemsCalled = false
    var saveItemCalled = false
    var errorToThrow: Error?

    func fetchItems() async throws -> [Item] {
        fetchItemsCalled = true
        if let error = errorToThrow {
            throw error
        }
        return items
    }

    func saveItem(_ item: Item) async throws {
        saveItemCalled = true
        if let error = errorToThrow {
            throw error
        }
        items.append(item)
    }
}

// ViewModel with DI
@MainActor
final class ItemListViewModel: ObservableObject {
    private let repository: ItemRepositoryProtocol

    init(repository: ItemRepositoryProtocol) {
        self.repository = repository
    }

    func loadItems() async {
        do {
            let items = try await repository.fetchItems()
            // Update state
        } catch {
            // Handle error
        }
    }
}

// Test
final class ItemListViewModelTests: XCTestCase {
    @MainActor
    func testLoadItems_WithSuccessfulFetch_UpdatesItems() async {
        // Given
        let mockRepo = MockItemRepository()
        mockRepo.items = [Item(name: "Test")]
        let sut = ItemListViewModel(repository: mockRepo)

        // When
        await sut.loadItems()

        // Then
        XCTAssertTrue(mockRepo.fetchItemsCalled)
    }
}
```

### Test Doubles 类型

**Dummy**: 仅用于填充参数，不会被调用
```swift
final class DummyLogger: LoggerProtocol {
    func log(_ message: String) {
        // 什么都不做
    }
}
```

**Stub**: 返回预设的响应
```swift
final class StubAuthService: AuthServiceProtocol {
    func login() async -> Result<User, Error> {
        .success(User(id: "123", name: "Test"))
    }
}
```

**Mock**: 记录调用并验证行为
```swift
final class MockAnalytics: AnalyticsProtocol {
    var events: [String] = []

    func track(_ event: String) {
        events.append(event)
    }
}

// Test
XCTAssertEqual(mockAnalytics.events, ["screen_viewed", "button_tapped"])
```

**Fake**: 简化的可工作实现
```swift
final class FakeDatabase: DatabaseProtocol {
    private var storage: [String: Any] = [:]

    func save(_ value: Any, forKey key: String) {
        storage[key] = value
    }

    func load(forKey key: String) -> Any? {
        storage[key]
    }
}
```

<!-- section: 4. 异步测试 keywords: async test, await, XCTestExpectation, actor, concurrency testing -->
## 4. 异步测试

### async/await 测试

```swift
func testFetchData_WhenSuccessful_ReturnsItems() async throws {
    // Given
    let mockService = MockDataService()
    mockService.items = [Item(name: "Test")]
    let sut = DataManager(service: mockService)

    // When
    let items = try await sut.fetchItems()

    // Then
    XCTAssertEqual(items.count, 1)
    XCTAssertEqual(items.first?.name, "Test")
}
```

### XCTestExpectation

```swift
func testNotification_WhenPosted_TriggersCallback() {
    // Given
    let expectation = XCTestExpectation(description: "Notification received")
    var receivedNotification = false

    let observer = NotificationCenter.default.addObserver(
        forName: .dataUpdated,
        object: nil,
        queue: nil
    ) { _ in
        receivedNotification = true
        expectation.fulfill()
    }

    // When
    NotificationCenter.default.post(name: .dataUpdated, object: nil)

    // Then
    wait(for: [expectation], timeout: 1.0)
    XCTAssertTrue(receivedNotification)

    NotificationCenter.default.removeObserver(observer)
}
```

<!-- section: 5. TDD 流程 keywords: TDD, test-driven, red-green-refactor, test first -->
## 5. TDD 流程

### Red-Green-Refactor

**1. Red - 写失败的测试**
```swift
func testCalculateTotal_WithMultipleItems_ReturnsSum() {
    // Given
    let cart = ShoppingCart()
    cart.addItem(Item(price: 10.0))
    cart.addItem(Item(price: 15.0))

    // When
    let total = cart.calculateTotal()

    // Then
    XCTAssertEqual(total, 25.0)
}
// 运行：❌ 失败（方法不存在）
```

**2. Green - 实现最简单的代码让测试通过**
```swift
final class ShoppingCart {
    private var items: [Item] = []

    func addItem(_ item: Item) {
        items.append(item)
    }

    func calculateTotal() -> Double {
        items.reduce(0) { $0 + $1.price }
    }
}
// 运行：✅ 通过
```

**3. Refactor - 重构改进**
```swift
final class ShoppingCart {
    private var items: [Item] = []

    func addItem(_ item: Item) {
        items.append(item)
    }

    var total: Double {
        items.reduce(0) { $0 + $1.price }
    }
}
// 运行：✅ 仍然通过
```

### 测试先行的场景

**何时使用 TDD**：
- 业务逻辑复杂，边界条件多
- 算法实现（排序、过滤、计算）
- API 客户端（网络请求处理）
- 数据转换和验证

**何时跳过 TDD**：
- UI 布局（用 Preview 更快）
- 简单的 CRUD 操作
- 探索性编程（不确定最终方案）

<!-- section: 6. 测试覆盖率 keywords: coverage, test coverage, code coverage, metrics -->
## 6. 测试覆盖率

### 目标设定

| 代码类型 | 覆盖率目标 |
|---------|----------|
| 业务逻辑 | 80-100% |
| Service/Repository | 70-90% |
| ViewModel | 70-90% |
| Utility/Helper | 90-100% |
| UI Code | 0-30% (用 UI Test) |

### 查看覆盖率

```bash
# Xcode 中启用覆盖率
# Edit Scheme → Test → Options → Code Coverage

# 或使用命令行
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
  -enableCodeCoverage YES
```

### 关注未覆盖的关键路径

优先覆盖：
- 错误处理分支
- 边界条件（空数组、nil 值、极大/极小值）
- 权限处理（未登录、权限不足）

## 7. 常见陷阱

### 避免测试实现细节

```swift
// ❌ 脆弱：测试内部实现
func testLoadData_CallsFetchAndTransform() {
    sut.loadData()
    XCTAssertTrue(mockService.fetchCalled)
    XCTAssertTrue(mockTransformer.transformCalled)
}

// ✅ 健壮：测试行为和结果
func testLoadData_WhenSuccessful_UpdatesItems() async {
    await sut.loadData()
    XCTAssertEqual(sut.items.count, 3)
    XCTAssertEqual(sut.items.first?.name, "Item 1")
}
```

### 保持测试独立

```swift
// ❌ 错误：测试间有依赖
func test1_CreateItem() {
    sut.createItem("Item 1")
    // Test 2 依赖这个状态
}

func test2_DeleteItem() {
    sut.deleteItem(0)  // 假设 Item 1 存在
}

// ✅ 正确：每个测试独立设置
func testDeleteItem_WithExistingItem_RemovesIt() {
    // Given
    sut.createItem("Item 1")

    // When
    sut.deleteItem(0)

    // Then
    XCTAssertEqual(sut.items.count, 0)
}
```

## 参考

- [Apple Testing Documentation](https://developer.apple.com/documentation/xctest)
- [WWDC21: Meet async/await in Swift](https://developer.apple.com/videos/play/wwdc2021/10132/)
- [Test Driven Development: By Example - Kent Beck](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)
