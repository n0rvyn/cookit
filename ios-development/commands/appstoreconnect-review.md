---
name: appstoreconnect-review
description: App Store Connect 上架材料逐项检查与填写指导。
---

# App Store Connect 上架填写指南

逐项指导 App Store Connect 中 iOS App 上架需要填写的内容。

---

## 第一部分：App Information 页面

### 1. Localizable Information（可本地化信息）

| 字段 | 类型 | 限制 | 填写说明 |
|------|------|------|----------|
| **Name** | 文本 | 最多 30 字符 | App 在 App Store 显示的名称。简洁有辨识度，避免通用词汇 |
| **Subtitle** | 文本 | 最多 30 字符 | 名称下方的副标题。突出核心价值或差异化卖点 |

### 2. General Information（通用信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| **Bundle ID** | 只读 | 从 Xcode 读取，无需填写 |
| **SKU** | 只读 | 创建 App 时设置，内部标识，用户不可见 |
| **Apple ID** | 只读 | 系统自动生成 |

### 3. Content Rights（内容权利）

**选项**：
- `Yes, this app has the necessary rights to its third-party content` — 如果 App 包含第三方内容（图片、数据库、API 数据、字体等）
- `No, it doesn't contain, show, or access third-party content` — 完全自己创作的内容

**常见需要选 Yes 的情况**：使用第三方 API、图标库、字体、数据库、SDK

### 4. License Agreement（许可协议）

**选项**：
- `Apple's Standard License Agreement` — 大多数 App 选这个
- `Custom App License Agreement` — 需要自定义条款时（如企业 App）

### 5. Primary Language（主要语言）

App Store 列表的默认语言。用户所在区域无本地化版本时显示此语言。

### 6. Category（类别）

选择最符合 App 核心功能的类别。可选一个主类别和一个次类别。

**常用类别**：
- Health & Fitness（健康与健身）
- Productivity（效率）
- Utilities（工具）
- Lifestyle（生活）
- Finance（财务）

### 7. Age Ratings（年龄分级）⚠️ 重要

需要回答一系列问题，系统自动计算分级。如实回答，错误可能导致拒审。

#### Step 1: Features（功能特性）
| 问题 | 说明 |
|------|------|
| Parental Controls | App 是否包含家长控制功能 |
| Age Assurance | App 是否验证用户年龄 |
| Unrestricted Web Access | App 是否允许访问任意网页 |
| User-Generated Content | App 是否有用户创建/分享内容的功能（社区、评论等） |
| Messaging and Chat | App 是否有用户间的即时通讯功能 |
| Advertising | App 是否包含广告 |

#### Step 2: Mature Themes（成人主题）
| 问题 | 选项说明 |
|------|----------|
| Profanity or Crude Humor | 脏话或粗俗幽默 |
| Horror/Fear Themes | 恐怖或惊悚内容 |
| Alcohol, Tobacco, or Drug Use | 酒精、烟草或毒品相关内容 |

**选项**：NONE（无）/ INFREQUENT（偶尔）/ FREQUENT（频繁）

#### Step 3: Medical or Wellness（医疗或健康）
| 问题 | 说明 |
|------|------|
| Medical or Treatment Information | 是否提供医疗或治疗信息 |
| Health or Wellness Topics | 是否涉及健康或养生话题 |

**健康类 App 注意**：涉及健康话题选 YES，通常会被评为 12+ 或 13+

#### Step 4: Sexuality or Nudity（性或裸露）
通常全部选 NONE

#### Step 5: Violence（暴力）
通常全部选 NONE

#### Step 6: Chance-Based Activities（随机性活动）
| 问题 | 说明 |
|------|------|
| Simulated Gambling | 模拟赌博（不涉及真钱） |
| Contests | 竞赛活动 |
| Gambling | 真实赌博（涉及真钱） |
| Loot Boxes | 抽卡/开箱机制 |

### 8. App Encryption Documentation（加密声明）

**在 Info.plist 中设置**：
```xml
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```

**选择 NO（false）的条件**：
- 仅使用 HTTPS
- 仅使用 iOS 系统加密 API（如 CryptoKit、Security framework）
- 不包含自定义加密算法

**需要选 YES 并上传文档的情况**：
- 使用自定义加密算法
- 使用非标准加密库

### 9. Digital Services Act（数字服务法案）

欧盟要求。选择是否以商业身份（Trader）发布 App。

---

## 第二部分：App Privacy（隐私标签）⚠️ 必须填写

App Store Connect 中独立的隐私信息页面。用户在 App Store 看到的「App 隐私」标签由此生成。

### 填写流程

1. 选择 App 收集的所有数据类型
2. 对每个数据类型回答三个问题：是否用于追踪、是否关联用户身份、收集目的
3. 发布后立即生效；移除数据类型也会立即更新

### 数据类型完整清单

逐项检查 App 是否收集以下数据。**判断标准**：数据是否离开设备（发送到你的服务器或第三方），或在设备上被用于追踪/广告目的。

**不需要声明的情况**：
- 仅在设备本地处理、从未发送到服务器的数据
- 仅发送给 Apple 自有服务的数据（WeatherKit、MapKit、Sign in with Apple、Apple Pay、iCloud 等）— Apple 在自己的隐私政策下处理这些数据
- 满足「可选披露」条件的数据（见下方）

#### Contact Info（联系信息）
| 数据类型 | 说明 | 常见场景 |
|---------|------|---------|
| Name | 姓名 | 注册/登录、个人资料 |
| Email Address | 邮箱（含哈希） | 注册/登录、通讯 |
| Phone Number | 电话（含哈希） | 注册/验证 |
| Physical Address | 物理地址 | 配送、账单 |
| Other User Contact Info | 其他联系方式 | 社交账号等 |

#### Health & Fitness（健康与健身）
| 数据类型 | 说明 | 常见场景 |
|---------|------|---------|
| Health | 健康医疗数据 | HealthKit API、Clinical Records、运动障碍 API |
| Fitness | 健身运动数据 | Motion and Fitness API、运动追踪 |

#### Financial Info（财务信息）
| 数据类型 | 说明 | 常见场景 |
|---------|------|---------|
| Payment Info | 支付信息 | 若由 Apple 处理（StoreKit），无需声明 |
| Credit Info | 信用信息 | 信用评分等 |
| Other Financial Info | 其他财务 | 收入、资产等 |

#### Location（位置）
| 数据类型 | 说明 | 常见场景 |
|---------|------|---------|
| Precise Location | 精确位置（≥3 位小数） | GPS 定位 |
| Coarse Location | 粗略位置 | IP 定位、城市级别 |

#### Sensitive Info（敏感信息）
种族、性取向、怀孕、残疾、宗教信仰、工会、政治观点、基因、生物识别数据。

#### Contacts（通讯录）
用户手机/地址簿/社交图谱中的联系人列表。

#### User Content（用户内容）
| 数据类型 | 说明 | 常见场景 |
|---------|------|---------|
| Emails or Text Messages | 邮件/消息内容 | 邮件客户端、聊天 App |
| Photos or Videos | 照片/视频 | 上传到服务器的媒体 |
| Audio Data | 语音/录音 | 语音识别、语音消息 |
| Gameplay Content | 游戏内容 | 用户创建的游戏内容 |
| Customer Support | 客服数据 | 用户发起的客服请求 |
| Other User Content | 其他内容 | 用户生成的任何其他内容 |

#### Browsing History（浏览历史）
用户在 App 外查看的网页内容。

#### Search History（搜索历史）
在 App 内的搜索记录。**注意**：仅在本地处理且不发送到服务器的搜索通常不需要声明。

#### Identifiers（标识符）
| 数据类型 | 说明 | 常见场景 |
|---------|------|---------|
| User ID | 用户级 ID | 账号 ID、用户名 |
| Device ID | 设备级 ID | 广告标识符、设备 ID |

#### Purchases（购买记录）
账号或个人的购买/消费倾向。**注意**：由 Apple StoreKit 处理的支付无需声明。

#### Usage Data（使用数据）
| 数据类型 | 说明 | 常见场景 |
|---------|------|---------|
| Product Interaction | 产品交互 | 启动、点击、滚动、播放 |
| Advertising Data | 广告数据 | 用户看过的广告 |
| Other Usage Data | 其他使用数据 | 任何其他活动数据 |

#### Diagnostics（诊断）
| 数据类型 | 说明 | 常见场景 |
|---------|------|---------|
| Crash Data | 崩溃日志 | Crashlytics、Sentry |
| Performance Data | 性能数据 | 启动时间、卡顿率 |
| Other Diagnostic Data | 其他诊断 | 技术诊断数据 |

#### Surroundings（环境）
环境扫描数据（网格、平面、场景分类、图像检测）。

#### Body（身体）
手部结构/运动、头部运动。

### 每个数据类型的三个问题

勾选某个数据类型后，需回答：

**1. Is this data used for tracking?（是否用于追踪）**
- Tracking = 将该数据与第三方数据关联用于广告/广告测量，或与数据经纪商共享
- 大多数非广告 App 选 NO

**2. Is this data linked to the user's identity?（是否关联用户身份）**
- 通过账号、设备或其他方式能将数据关联到特定用户
- 无账号系统且使用匿名标识 = NO

**3. What purposes is this data collected for?（收集目的）**

| 目的 | 说明 |
|------|------|
| Third-Party Advertising | 展示第三方广告 |
| Developer's Advertising or Marketing | 自有广告/营销 |
| Analytics | 分析用户行为 |
| Product Personalization | 个性化推荐 |
| App Functionality | App 核心功能所需 |
| Other Purposes | 其他用途 |

### 可选披露（Optional Disclosure）

满足以下**全部**条件的数据类型可以不声明：
1. 不用于追踪
2. 不用于广告或营销
3. 收集仅在非核心功能的偶发场景中发生，且对用户可选
4. 收集时界面上用户姓名/账号名显著可见，且每次都需用户主动选择

**典型可以不声明的例子**：可选的反馈表单、与 App 主功能无关的客服请求。

### 最终标签预览

填写完成后，App Store 会按以下分类展示：
- **Data Used to Track You** — 用于追踪的数据
- **Data Linked to You** — 关联到用户身份的数据
- **Data Not Linked to You** — 未关联到用户身份的数据

---

## 第三部分：iOS App Version 页面

### 1. Previews and Screenshots（预览和截图）⚠️ 必须准备

**必须准备的尺寸**：

| 设备 | 尺寸（px） | 说明 |
|------|-----------|------|
| **iPhone 6.7"** | 1290 × 2796 | iPhone 15 Pro Max, 16 Pro Max |
| **iPhone 6.5"** | 1242 × 2688 或 1284 × 2778 | iPhone 14 Plus, 15 Plus |
| **iPhone 5.5"** | 1242 × 2208 | iPhone 8 Plus（可选，向下兼容） |
| **iPad 12.9"** | 2048 × 2732 | 如支持 iPad |

**截图要求**：
- 每个尺寸最少 1 张，最多 10 张
- 前 3 张最重要（安装页面预览）
- 必须是真实 App 界面，不能是 mockup
- 建议展示核心功能流程

**App Preview 视频（可选）**：
- 15-30 秒
- 与截图相同尺寸
- 每个尺寸最多 3 个

### 2. Promotional Text（宣传文本）

| 限制 | 170 字符 |
|------|----------|
| 特点 | 随时可改，不需要新版本审核 |
| 用途 | 突出核心卖点，可用于限时促销 |

### 3. Description（详细描述）

| 限制 | 4000 字符 |
|------|----------|
| 特点 | 需要提交新版本才能修改 |

**结构建议**：
```
[一句话介绍核心价值]

【主要功能】
• 功能1
• 功能2
• 功能3

【特色亮点】
• 亮点1
• 亮点2

【适合人群】
• 人群1
• 人群2

【隐私与安全】（建议添加）
简述数据处理方式
```

### 4. Keywords（关键词）

| 限制 | 100 字符，逗号分隔 |
|------|-------------------|
| 技巧 | 不要重复 App 名称、不要用竞品名、用单词而非短语 |

### 5. URLs

| 字段 | 必填 | 说明 |
|------|------|------|
| **Support URL** | ✅ 必填 | 用户支持页面。可以是网页、社交媒体、或 GitHub Issues |
| **Marketing URL** | 可选 | 产品官网或落地页 |

### 6. Version & Copyright

| 字段 | 格式 | 示例 |
|------|------|------|
| **Version** | 与 Xcode 一致 | `1.0`, `1.0.1` |
| **Copyright** | © 年份 名称 | `© 2024 Your Name` |

### 7. Build

上传方式：
1. **Xcode**：Product → Archive → Distribute App → App Store Connect
2. **命令行**：`xcodebuild archive` + Transporter
3. **CI/CD**：Fastlane、GitHub Actions 等

### 8. App Review Information（审核信息）⚠️ 重要

#### Sign-In Information（登录信息）
| 情况 | 操作 |
|------|------|
| App 需要登录才能使用主要功能 | 提供测试账号和密码 |
| 无需登录即可使用 | 关闭 `Sign-in required` 开关 |
| 使用 Apple ID 登录 | 仍需提供测试账号或说明如何创建 |

#### Contact Information（联系信息）
| 字段 | 说明 |
|------|------|
| First Name / Last Name | 审核联系人姓名 |
| Phone Number | 电话（含国家代码，如 +86 138...） |
| Email | 审核相关邮件会发到这里 |

**注意**：审核员可能会在工作时间（美国时间）打电话

#### Notes（审核备注）
向审核员说明：
- App 主要功能
- 如何测试特定功能
- 需要特殊硬件或条件的功能说明
- 健康类 App 的医疗声明

#### Attachment（附件）
可上传截图或视频，用于：
- 演示特殊功能
- 说明需要特定条件才能触发的功能
- 提供测试用的二维码等

### 9. App Store Version Release（发布方式）

| 选项 | 说明 | 适用场景 |
|------|------|----------|
| **Manually release** | 审核通过后手动发布 | 首次上架、重大版本 |
| **Automatically release** | 审核通过后自动发布 | Bug 修复、小更新 |
| **Scheduled release** | 指定时间发布 | 配合市场活动 |

---

## 准备清单

### 必须准备的素材

- [ ] App 图标（1024×1024 PNG，无透明度，无圆角）
- [ ] iPhone 截图（至少 6.5" 或 6.7" 尺寸）
- [ ] iPad 截图（如支持 iPad）
- [ ] Support URL（支持页面链接）
- [ ] 隐私政策 URL（收集用户数据时必需）

### 必须填写的文本

- [ ] App Name（30 字符内）
- [ ] Subtitle（30 字符内）
- [ ] Description（4000 字符内）
- [ ] Keywords（100 字符内）
- [ ] Copyright
- [ ] 审核联系人信息

### 必须完成的选择

- [ ] Category 分类
- [ ] Age Rating 年龄分级问卷
- [ ] Content Rights 内容权利声明
- [ ] 加密声明（Info.plist 或上传文档）
- [ ] App Privacy 隐私标签（逐项数据类型声明）

---

## 代码层面必须实现的审核要求

> 以下是 App 代码中必须实现的功能，仅在 App Store Connect 配置不够，审核员会在 App 内逐项验证。

> **Review 不保证一次指出所有问题**：Apple 每次审核可能只检查部分 Guideline，上次通过的不代表下次不会被拒。每次提交前都应按此清单全量检查。

### 0. 未使用框架引用 (Guideline 2.5.1)

**要求**：App 不应引用未在主功能中使用的系统框架。import 即会被 App Review 检测。

**代码实现要点**：
- 删除功能时必须同时删除对应的 `import`、Info.plist 描述键、entitlements
- 提交前 Grep 检查：所有 `import HealthKit`、`import WeatherKit` 等框架引用是否仍有对应功能
- Info.plist 中的 `NSHealth*UsageDescription`、`NSLocation*UsageDescription` 等描述键必须与代码引用一致

### 1. 健康/营养信息引用来源 (Guideline 1.4.1)

**要求**：App 中展示的健康、营养、医疗相关信息必须附带**可点击的引用来源链接**。

**代码实现要点**：
- 所有营养分析结果页面底部必须有引用来源文本 + 可点击 `Link`（不只是纯文本书名号，Apple 要求 "links to sources"）
- AI 生成的健康建议卡片底部必须有引用来源
- AI 免责声明中必须包含具体参考文献名称
- 建议使用常量文件集中管理引用来源 URL 和文本

**关键位置**：
- 首页建议卡片、分析页面、健康洞察详情页、AI 免责声明组件
- 营养常量注释中不可引用非权威来源

### 2. 订阅页面法律链接 (Guideline 3.1.2)

**要求**：App 内的订阅购买页面必须包含**可点击的**隐私政策和用户协议链接，且位于购买按钮可视范围内。

**代码实现要点**：
- 订阅 Sheet 中购买按钮下方必须有：自动续费说明文案 + 隐私政策链接 + 用户协议链接
- 使用 `Link` 组件（不是 `Text`），确保可点击跳转浏览器
- 设置页也必须有隐私政策和用户协议入口
- 建议使用常量文件集中管理法律链接 URL（如 `LegalURLs.swift`）
- 如使用 `SubscriptionStoreView`（StoreKit 2），Apple 会自动添加条款链接；自定义 Paywall 则必须手动添加

### 3. AI/第三方数据共享明确同意 (Guideline 5.1.1(i) & 5.1.2(i))

**要求**：将用户数据发送给第三方 AI 服务前，必须获得用户**明确同意**（explicit consent）。

**代码实现要点**：
- **同意 Sheet**：中英双语（审核员是英语使用者），明确列出共享的数据类型、数据接收方（公司名）、数据用途
- **首次启动弹出**：在 `MainView.onAppear` 中检查同意状态，未同意时主动弹出同意 Sheet
- **API 层兜底**：所有 AI API 调用入口（`APIClient.request/streamRequest/streamChatRequest`）统一检查同意状态，未同意则 throw error
- **WebSocket 独立检查**：ASR 等不经过 APIClient 的路径需单独添加检查
- **UI 层优化**：AI 功能入口（对话、建议加载等）在调用前先检查，未同意时弹同意 Sheet 而非显示错误
- **设置页可撤回**：用户可在设置中查看同意详情和撤回同意
- **错误传播**：所有消费 AI API error 的 catch 路径必须处理 `consentRequired`（不能显示为"网络错误"或"获取失败"）
- 建议使用 `@AppStorage` + `UserDefaults` 管理同意状态，Service 层直接读取 `UserDefaults` 做阻断

### 4. Apple Weather 署名 (Guideline 5.2.5)

**要求**：使用 WeatherKit 时必须在 App 内显示 Apple Weather 商标（ + "Weather"）和法律归属链接。

**代码实现要点**：
- 使用天气数据的界面必须显示  Weather 署名 + 链接到 `weatherkit.apple.com/legal-attribution.html`
- 设置/关于页面必须有 Apple Weather 署名
- 使用 `apple.logo` SF Symbol（不是 `cloud.fill`），这是 Apple 商标要求
- 建议封装为可复用组件（如 `AppleWeatherAttribution`），在所有天气相关界面引用
- **仅在 App 实际使用 WeatherKit 时需要**；若已移除天气功能，此项跳过

### 5. App Description 末尾必须有法律链接

App Store Connect 中的 App 描述（Description）末尾必须添加隐私政策和用户协议 URL。这不在代码中，但属于提交审核前必做的配置。

### 6. 隐私政策必须与代码一致

**要求**：隐私政策文档中声明的数据收集类型必须与 App 实际代码一致。删除功能后必须同步更新隐私政策和 App Store Connect 的 Privacy Labels。

**常见问题**：
- 删除 HealthKit 功能后隐私政策仍提及"健康数据"
- 添加新的数据收集但隐私政策未更新
- Privacy Labels 声明了 App 实际不收集的数据类型

**检查流程**：
1. 对比代码中的 `import` 语句和 Info.plist 权限键，确认与隐私政策数据类型一致
2. 对比隐私政策声明的第三方服务与代码中实际调用的服务
3. 确认 App Store Connect Privacy Labels 与隐私政策一致

---

## Pre-Submission Code Audit（提交前代码审计）

每次提交审核前，运行以下 Grep 检查确认合规：

### 框架残留检查
```bash
# 检查是否有未使用框架的 import 残留
Grep "import HealthKit|import WeatherKit" --path <project_source>/
# 检查 Info.plist 权限键是否与实际功能一致
Grep "NSHealth|NSWeather" --path <project>.xcodeproj/
```

### Consent Flow 检查
```bash
# 确认 AI consent 阻断存在
Grep "hasAgreedToCloudAI|consentNotGranted" --path <project_source>/
# 确认 consent UI 存在
Grep "CloudAIConsentSheet" --path <project_source>/
```

### 法律链接检查
```bash
# 确认订阅页面有法律链接
Grep "LegalURLs\\.privacyPolicy|LegalURLs\\.termsOfUse" --path <project_source>/
# 确认 Link 组件（非纯 Text）
Grep "Link.*隐私政策|Link.*用户协议" --path <project_source>/
```

### 免责声明检查
```bash
# 确认洞察/AI 内容有免责声明
Grep "仅供.*参考|不构成.*建议" --path <project_source>/
```

### 隐私政策一致性检查
```bash
# 对比隐私政策中提及的数据类型与代码中的实际功能
# 手动核对：privacy-policy.md 中每个数据类型都有对应的代码功能
```

---

## ASC 文档检查

提交审核前，确认 `docs/10-app-store-connect/` 下 4 种文档齐全且与代码一致。

### 文档存在性

| 文件 | 必须存在 | 检查方式 |
|------|---------|---------|
| `privacy-policy.md` | 是 | `ls docs/10-app-store-connect/privacy-policy.md` |
| `terms-of-use.md` | 是 | `ls docs/10-app-store-connect/terms-of-use.md` |
| `support-page.md` | 是 | `ls docs/10-app-store-connect/support-page.md` |
| `market.md` | 是 | `ls docs/10-app-store-connect/market.md` |

### 隐私政策与代码一致性

1. **数据收集类型**：隐私政策中列出的每种数据类型（语音、文本、位置、健康等）必须在代码中有对应的收集逻辑；代码中收集但文档中未提及的 = 违规
2. **第三方服务**：隐私政策中列出的第三方服务名称和用途必须与代码中的实际调用一致
3. **权限声明**：Info.plist 中的权限描述键（`NS*UsageDescription`）必须与隐私政策中的权限列表匹配
4. **已移除功能**：代码中已删除的功能（如 HealthKit），隐私政策中不应再提及

### Notion 同步状态

如果使用 Notion 托管法律文档 public URL：
1. 确认 `.claude/notion-sync.local.md` 存在且配置正确
2. 确认 4 个文档都有对应的 Notion page ID
3. 使用 `/notion-page-sync` 确认 Notion 页面内容与本地文件一致

### App Store Connect 配置

以下项目需要在 ASC 后台手动验证：
- [ ] Privacy Policy URL 已填写且可访问
- [ ] App Description 末尾有隐私政策和用户协议链接
- [ ] Privacy Labels 与隐私政策一致
- [ ] 如有自定义 EULA，已在 App Information 中配置

**工具**：使用 `/update-asc-docs` 可自动审计代码并更新文档。

---

## 常见拒审原因

1. **截图与实际 App 不符** — 截图必须是真实 App 界面
2. **缺少隐私政策** — 收集任何用户数据（包括 Analytics）都需要
3. **权限说明不清** — Info.plist 中的权限描述要说明具体用途
4. **健康类 App 免责声明** — 建议在 App 内和描述中说明"仅供参考，不能替代专业医疗建议"
5. **后台 API 不可用** — 审核期间确保服务器正常运行
6. **Metadata rejected** — 名称、描述、截图不符合规范
7. **Guideline 4.2** — App 功能过于简单，建议丰富功能或做成网页
8. **登录问题** — 测试账号无效、登录流程有 bug
9. **健康/营养信息缺少引用来源** — Guideline 1.4.1 要求可点击链接，纯文本不够
10. **订阅页面缺少法律链接** — Guideline 3.1.2 要求隐私政策和用户协议在购买按钮附近
11. **AI 数据共享未获明确同意** — Guideline 5.1.1(i) 要求第三方数据共享前的 explicit consent
12. **第三方 API 商标缺失** — Guideline 5.2.5 要求 Apple Weather 等第三方服务署名

---

## 有用链接

- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [App Store Connect Help](https://developer.apple.com/help/app-store-connect/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
