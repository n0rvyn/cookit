# Localization Workflow Guide
<!-- SECTION MARKERS: Each "section" comment line immediately precedes the ##
     heading it labels. Use Grep("<!-- section:", file) to find sections, then
     Read(file, offset, limit) to fetch only the relevant lines. -->

iOS/Swift 本地化最佳实践，涵盖 .xcstrings 管理、String Catalogs 和本地化验证。

<!-- section: 1. String Catalogs (.xcstrings) keywords: String Catalog, xcstrings, localization setup, language, translation -->
## 1. String Catalogs (.xcstrings)

### 创建和管理

**在 Xcode 中创建**：
1. File → New → File → String Catalog
2. 命名规则：按模块命名（如 `Settings.xcstrings`, `Onboarding.xcstrings`）
3. 添加到目标（Target）

**文件结构**：
```json
{
  "sourceLanguage" : "zh-Hans",
  "strings" : {
    "Hello, World!" : {
      "localizations" : {
        "en" : {
          "stringUnit" : {
            "state" : "translated",
            "value" : "Hello, World!"
          }
        },
        "zh-Hans" : {
          "stringUnit" : {
            "state" : "translated",
            "value" : "你好，世界！"
          }
        }
      }
    }
  },
  "version" : "1.0"
}
```

### 多语言支持

**添加新语言**：
1. Project Settings → Info → Localizations → "+"
2. 选择语言（如 English, Japanese）
3. Xcode 自动在 .xcstrings 中添加该语言

**支持的语言代码**：
- `zh-Hans`: 简体中文
- `zh-Hant`: 繁体中文
- `en`: 英语
- `ja`: 日语
- `ko`: 韩语
- `es`: 西班牙语
- `fr`: 法语
- `de`: 德语

### 导出和导入

**导出 XLIFF**（用于翻译服务）：
```bash
xcodebuild -exportLocalizations \
  -localizationPath ./Localizations \
  -project MyApp.xcodeproj
```

**导入翻译**：
```bash
xcodebuild -importLocalizations \
  -localizationPath ./Localizations/zh-Hant.xliff \
  -project MyApp.xcodeproj
```

<!-- section: 2. String(localized:) 最佳实践 keywords: String(localized:), LocalizedStringKey, table parameter, comment -->
## 2. String(localized:) 最佳实践

### 基本用法

```swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            // 最简单用法（使用默认 table）
            Text(String(localized: "Hello, World!"))

            // 等价于（推荐明确指定）
            Text("Hello, World!")
        }
    }
}
```

**Xcode 自动提取**：
- SwiftUI `Text("文本")` 会自动提取到默认的 `Localizable.xcstrings`
- 手动提取：Editor → Export For Localization

### table 参数（按模块组织）

```swift
// Settings.xcstrings
Text(String(localized: "Account", table: "Settings"))
Text(String(localized: "Privacy", table: "Settings"))

// Onboarding.xcstrings
Text(String(localized: "Welcome", table: "Onboarding"))
Text(String(localized: "Get Started", table: "Onboarding"))

// Profile.xcstrings
Text(String(localized: "Edit Profile", table: "Profile"))
```

**优点**：
- 按功能模块分离翻译
- 避免单个文件过大
- 便于团队协作（不同人负责不同模块）

### comment 参数

```swift
// 为译者提供上下文
String(
    localized: "Cancel",
    table: "Common",
    comment: "按钮文本：取消操作"
)

String(
    localized: "Settings",
    table: "TabBar",
    comment: "标签栏项目：设置"
)
```

**在 .xcstrings 中显示**：
```json
"Settings" : {
  "comment" : "标签栏项目：设置",
  "localizations" : { ... }
}
```

### LocalizedStringResource

```swift
// 定义本地化字符串资源
struct Strings {
    static let welcome = LocalizedStringResource(
        "Welcome to MyApp",
        table: "Onboarding",
        comment: "欢迎页标题"
    )

    static let getStarted = LocalizedStringResource(
        "Get Started",
        table: "Onboarding"
    )
}

// 使用
Text(Strings.welcome)
Button(Strings.getStarted) { }
```

<!-- section: 3. 复数和变量处理 keywords: pluralization, inflect, variables, plural rules -->
## 3. 复数和变量处理

### Pluralization

```swift
// 在代码中
func itemCountText(_ count: Int) -> String {
    String(
        localized: "^[\(count) item](inflect: true)",
        table: "Shopping"
    )
}

// 在 .xcstrings 中自动生成复数规则
{
  "^[%lld item](inflect: true)" : {
    "localizations" : {
      "en" : {
        "variations" : {
          "plural" : {
            "one" : {
              "stringUnit" : {
                "state" : "translated",
                "value" : "%lld item"
              }
            },
            "other" : {
              "stringUnit" : {
                "state" : "translated",
                "value" : "%lld items"
              }
            }
          }
        }
      },
      "zh-Hans" : {
        "stringUnit" : {
          "state" : "translated",
          "value" : "%lld 个项目"
        }
      }
    }
  }
}
```

**中文无复数变化**：
```swift
// 英文：1 item / 2 items
// 中文：1 个项目 / 2 个项目
itemCountText(1)  // "1 个项目"
itemCountText(5)  // "5 个项目"
```

### String Interpolation

```swift
// 带变量的本地化
func greetingText(name: String) -> String {
    String(
        localized: "Hello, \(name)!",
        table: "Greetings"
    )
}

// .xcstrings 中
{
  "Hello, %@!" : {
    "localizations" : {
      "en" : {
        "stringUnit" : {
          "state" : "translated",
          "value" : "Hello, %@!"
        }
      },
      "zh-Hans" : {
        "stringUnit" : {
          "state" : "translated",
          "value" : "你好，%@！"
        }
      }
    }
  }
}
```

### Format Specifiers

```swift
// 整数
String(localized: "You have \(count) messages", table: "Messages")
// → "You have %lld messages"

// 浮点数
String(localized: "Price: $\(price, format: .number.precision(.fractionLength(2)))")
// → "Price: $%.2f"

// 日期
String(localized: "Last updated: \(date, format: .dateTime)")
```

<!-- section: 4. 组织策略 keywords: organization, module, naming, file structure, reuse -->
## 4. 组织策略

### 推荐的文件结构

```
MyApp/
├── Resources/
│   └── Localizations/
│       ├── Localizable.xcstrings       // 通用文本
│       ├── TabBar.xcstrings            // 标签栏
│       ├── Settings.xcstrings          // 设置页面
│       ├── Onboarding.xcstrings        // 引导页
│       ├── Errors.xcstrings            // 错误消息
│       └── Notifications.xcstrings     // 通知文本
```

### 命名约定

**Key 命名**：
- 使用有意义的英文 key（不用中文 key）
- 描述性而非翻译性

```swift
// ✅ 推荐
String(localized: "settings.account.title", table: "Settings")
String(localized: "onboarding.welcome.headline", table: "Onboarding")

// ❌ 避免
String(localized: "账户", table: "Settings")  // Key 是中文
String(localized: "text1", table: "Settings") // 无意义
```

### 复用策略

**Common.xcstrings 存放通用词汇**：
```swift
// Common.xcstrings
"OK"
"Cancel"
"Save"
"Delete"
"Close"
"Confirm"
```

**避免重复定义**：
```swift
// ✅ 推荐：复用通用词
Button(String(localized: "Cancel", table: "Common")) { }

// ❌ 避免：每个模块都定义 "Cancel"
// Settings.xcstrings 有 "Cancel"
// Profile.xcstrings 也有 "Cancel"
// → 维护麻烦
```

<!-- section: 5. 本地化验证 keywords: validation, pseudolocalization, preview, testing localization -->
## 5. 本地化验证

### Xcode 预览不同语言

```swift
#Preview {
    ContentView()
        .environment(\.locale, Locale(identifier: "zh-Hans"))
}

#Preview("English") {
    ContentView()
        .environment(\.locale, Locale(identifier: "en"))
}

#Preview("Japanese") {
    ContentView()
        .environment(\.locale, Locale(identifier: "ja"))
}
```

### 运行时切换语言（测试用）

```swift
// ⚠️ 仅用于开发测试，不要在生产代码中使用
struct LanguageSwitcher: View {
    @State private var selectedLanguage = "zh-Hans"

    var body: some View {
        VStack {
            Picker("Language", selection: $selectedLanguage) {
                Text("简体中文").tag("zh-Hans")
                Text("English").tag("en")
            }
            .pickerStyle(.segmented)

            ContentView()
                .environment(\.locale, Locale(identifier: selectedLanguage))
        }
    }
}
```

### 模拟器测试

**切换语言**：
1. Settings → General → Language & Region
2. Preferred Languages → 添加语言
3. 重启 App

**伪本地化（Pseudolocalization）**：
```bash
# 在 Scheme 中启用
# Edit Scheme → Run → Options
# App Language → Double-Length Pseudolanguage

# 效果：所有文本变为双倍长度
"Save" → "[!!! Śàvè !!!]"
```

<!-- section: 6. 常见问题 keywords: common issues, truncation, RTL, hardcoded strings, missing translations -->
## 6. 常见问题

### 文本截断

```swift
// ❌ 问题：德语文本可能很长
Text("Save")
    .frame(width: 60)  // 可能截断

// ✅ 解决：使用 .lineLimit 和 .minimumScaleFactor
Text("Save")
    .lineLimit(1)
    .minimumScaleFactor(0.5)
    .frame(minWidth: 60)
```

### 文本方向（RTL 语言）

SwiftUI 自动处理 RTL（如阿拉伯语、希伯来语），但需注意：

```swift
// ✅ 自动翻转
HStack {
    Image(systemName: "chevron.right")
    Text("Next")
}
// RTL 语言中自动变为：Text "Next" + chevron.left

// ❌ 需要手动处理的场景
Image("custom-arrow")  // 自定义图片不会自动翻转
    .environment(\.layoutDirection, .rightToLeft)  // 手动设置
```

### 日期和数字格式

```swift
// ✅ 使用系统格式化器（自动适配地区）
Text(date, style: .date)
Text(price, format: .currency(code: "USD"))

// ❌ 避免硬编码格式
Text("\(month)/\(day)/\(year)")  // 美国格式，其他地区不适用
```

## 7. 本地化检查清单

### 开发阶段

- [ ] 所有 UI 文本使用 `String(localized:)`
- [ ] 按模块使用不同的 `table`
- [ ] 为复杂文本添加 `comment`
- [ ] 日期/数字使用系统格式化器
- [ ] 图片资源有本地化变体（如需要）

### 提交前

- [ ] 运行 `xcodebuild -exportLocalizations` 检查缺失翻译
- [ ] 预览所有目标语言
- [ ] 测试最长文本的 UI（德语、俄语通常最长）
- [ ] 测试 RTL 语言布局（如支持阿拉伯语）
- [ ] 确认复数规则正确

### 发布前

- [ ] 在真实设备上测试所有语言
- [ ] 检查字体在各语言下的渲染
- [ ] 验证 App Store 描述和截图的本地化
- [ ] 测试语言切换后 App 重启的行为

## 参考

- [Apple Localization Documentation](https://developer.apple.com/documentation/xcode/localization)
- [WWDC23: Discover String Catalogs](https://developer.apple.com/videos/play/wwdc2023/10155/)
- [Internationalization and Localization Guide](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPInternational/)
