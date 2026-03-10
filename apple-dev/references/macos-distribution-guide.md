# macOS Distribution Guide
<!-- SECTION MARKERS: Each "section" comment line immediately precedes the ##
     heading it labels. Use Grep("<!-- section:", file) to find sections, then
     Read(file, offset, limit) to fetch only the relevant lines. -->

> macOS app 的分发、签名、公证和沙箱指南。
> 适用：macOS 14+（Sonoma）/ Xcode 16+

---

<!-- section: Notarization keywords: notarytool, stapling, Developer ID, notarization, codesign platform: macOS -->
## Notarization（公证）

Apple 公证确保 app 不含已知恶意软件。非 Mac App Store 分发的 app 必须公证。

### 流程

1. **签名**：用 Developer ID Application 证书签名 app
   ```bash
   codesign --deep --force --options runtime \
     --sign "Developer ID Application: Your Name (TEAM_ID)" \
     YourApp.app
   ```

2. **创建 ZIP 或 DMG**
   ```bash
   ditto -c -k --keepParent YourApp.app YourApp.zip
   ```

3. **提交公证**
   ```bash
   xcrun notarytool submit YourApp.zip \
     --apple-id "your@email.com" \
     --team-id "TEAM_ID" \
     --password "@keychain:AC_PASSWORD" \
     --wait
   ```

4. **Staple**（将公证结果附加到 app）
   ```bash
   xcrun stapler staple YourApp.app
   ```

### 常见 rejection 原因

| 原因 | 解决方案 |
|------|---------|
| 未启用 hardened runtime | 签名时加 `--options runtime` |
| 包含未签名的第三方 framework | 对每个 framework 单独签名 |
| 使用了不允许的 entitlement | 检查 entitlements 文件，移除不必要的权限 |
| 缺少 timestamp | 签名时不要加 `--timestamp=none` |

<!-- section: Distribution Channels keywords: Mac App Store, direct, Developer ID, distribution channel platform: macOS -->
## Distribution Channels

| | Mac App Store | 直接分发（Developer ID） |
|---|---|---|
| **审核** | Apple 审核流程 | 仅公证（自动化检查） |
| **收入** | Apple 抽成 30%/15% | 全额自留 |
| **沙箱** | 强制 | 可选（但推荐） |
| **更新** | App Store 自动更新 | 需自行实现（Sparkle 等） |
| **支付** | App Store IAP | 自选（Stripe、Paddle 等） |
| **发现性** | App Store 搜索 | 需自行推广 |
| **签名证书** | Apple Distribution | Developer ID Application |
| **适用场景** | 面向大众、需要曝光 | 需要沙箱外权限、自控定价、B2B |

选择建议：
- 优先 Mac App Store：用户信任度高，更新方便
- 直接分发：需要完整文件系统访问、内核扩展、或不接受抽成时
- 双轨发布：两个渠道同时分发，用不同 bundle ID

<!-- section: Sandboxing & Entitlements keywords: sandbox, entitlement, file access, network, App Sandbox platform: macOS -->
## Sandboxing & Entitlements

### macOS vs iOS 沙箱差异

| 维度 | iOS | macOS |
|------|-----|-------|
| 沙箱 | 强制 | MAS 强制，直接分发可选 |
| 文件访问 | 仅 app container | 沙箱内：container + 用户选择的文件；沙箱外：全文件系统 |
| 网络 | 默认允许 | 沙箱内需 entitlement |
| IPC | 受限 | 沙箱内受限，沙箱外宽松 |

### 常用 Entitlements

```xml
<!-- 网络访问 -->
<key>com.apple.security.network.client</key>
<true/>

<!-- 文件访问：用户选择的文件（通过 NSOpenPanel） -->
<key>com.apple.security.files.user-selected.read-write</key>
<true/>

<!-- 文件访问：下载目录 -->
<key>com.apple.security.files.downloads.read-write</key>
<true/>

<!-- 摄像头 -->
<key>com.apple.security.device.camera</key>
<true/>

<!-- Apple Events（自动化其他 app） -->
<key>com.apple.security.automation.apple-events</key>
<true/>
```

### Security-Scoped Bookmarks

用户通过 NSOpenPanel 选择文件后，app 重启会丢失访问权。用 security-scoped bookmarks 持久化：

```swift
// 保存 bookmark
let bookmarkData = try url.bookmarkData(
    options: .withSecurityScope,
    includingResourceValuesForKeys: nil,
    relativeTo: nil
)

// 恢复访问
var isStale = false
let resolvedURL = try URL(
    resolvingBookmarkData: bookmarkData,
    options: .withSecurityScope,
    relativeTo: nil,
    bookmarkDataIsStale: &isStale
)
_ = resolvedURL.startAccessingSecurityScopedResource()
defer { resolvedURL.stopAccessingSecurityScopedResource() }
```

<!-- section: Auto-Update keywords: Sparkle, software update, auto-update, direct distribution platform: macOS -->
## Auto-Update（自动更新）

Mac App Store app 自动获得更新机制。直接分发的 app 需要自行实现。

### Sparkle Framework

[Sparkle](https://sparkle-project.org) 是 macOS 生态最成熟的自动更新框架。

集成步骤：
1. 通过 SPM 添加 `https://github.com/sparkle-project/Sparkle`
2. 在 Info.plist 中配置 `SUFeedURL`（指向 appcast.xml）
3. 添加 `SPUStandardUpdaterController` 到 app

```swift
import Sparkle

@main
struct MyApp: App {
    private let updaterController: SPUStandardUpdaterController

    init() {
        updaterController = SPUStandardUpdaterController(
            startingUpdater: true,
            updaterDelegate: nil,
            userDriverDelegate: nil
        )
    }

    var body: some Scene {
        WindowGroup { ContentView() }
            .commands {
                CommandGroup(after: .appInfo) {
                    CheckForUpdatesView(updater: updaterController.updater)
                }
            }
    }
}
```

Appcast 生成：
```bash
# 使用 Sparkle 自带工具生成 appcast
./bin/generate_appcast /path/to/releases/
```

注意事项：
- 更新包必须签名（与 app 相同的 Developer ID 证书）
- 支持 delta updates（仅下载差异）
- appcast.xml 托管在 HTTPS 上
- 沙箱 app 需要使用 `XPCServices` 模式的 Sparkle
