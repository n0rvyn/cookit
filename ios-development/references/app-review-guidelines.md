# App Review Guidelines Reference

Structured reference for Apple App Store Review Guidelines sections 1–5.
Used by `submission-preview` skill as a supplementary reference file.

---

<!-- section: Safety keywords: UGC, kids, ads, safety -->
## Section 1: Safety

### 1.2 User-Generated Content

Apps enabling UGC must include:
- A method for filtering objectionable material before it goes live
- A mechanism for users to flag offensive content
- The ability to block abusive users from the service
- Published contact info for users to reach the developer

Apps with objectionable content in real-time communications (multiplayer games, chat) must provide:
- Means to report abusive behavior
- Means to block offensive users
- Moderated channels for kids

### 1.3 Kids Category

Apps in the Kids Category must not include:
- Third-party analytics or data collection
- Third-party advertising SDKs (including Firebase Analytics, Facebook SDK, AdMob)
- Links out of the app or other marketing unless placed behind a parental gate
- In-app purchases without parental gate
<!-- /section -->

---

<!-- section: Performance keywords: completeness, deprecated, background, crashes -->
## Section 2: Performance

### 2.1 App Completeness

- No placeholder text, stub functionality, or demo/test content in submitted builds
- No TODO / FIXME / Lorem Ipsum / TBD / placeholder strings visible to users
- All links must work; no broken buttons or empty views in the main flow
- Demo accounts (if required) must be provided in App Review Notes

### 2.3 Metadata

**2.3.3** Screenshots must show the actual experience of using the app, not splash screens,
login screens, or marketing assets.

**2.3.6** Age rating must accurately reflect the app's content (questionnaire answers must match).

**2.3.7** No competitor app icons or imagery in screenshots.

### 2.5.1 Deprecated APIs

Apps must not use deprecated or private APIs. Known deprecated patterns (iOS 17+ minimum):
- `UIAlertView`, `UIActionSheet` → use `UIAlertController`
- `UIWebView` → use `WKWebView`
- `NavigationView` (SwiftUI) → use `NavigationStack` / `NavigationSplitView`
- `.foregroundColor(` (SwiftUI) → use `.foregroundStyle(`
- `.navigationBarTitle(` → use `.navigationTitle(`

### 2.5.4 Background Modes

Each declared background mode (`UIBackgroundModes` in Info.plist) must have corresponding
implementation:
- `audio` → `AVAudioSession` with appropriate category
- `location` → `CLLocationManager` with `allowsBackgroundLocationUpdates = true`
- `fetch` → `BGAppRefreshTask`
- `processing` → `BGProcessingTask`
- `voip` → CallKit integration
- `remote-notification` → Push notification handling

Declaring unused background modes = automatic rejection.
<!-- /section -->

---

<!-- section: Business keywords: IAP, subscription, StoreKit, purchase, restore -->
## Section 3: Business

### 3.1.1 In-App Purchase

- Digital content, subscriptions, premium features MUST use StoreKit (not external payment)
- Exception: physical goods, real-world services (ride sharing, food delivery)
- Must implement restore purchases mechanism
- Acceptable: `AppStore.sync()`, `Transaction.currentEntitlements`, `restorePurchases()`

### 3.1.2 Subscriptions

**3.1.2(a)** Auto-renewable subscriptions must clearly state:
- Duration (weekly/monthly/annual)
- Renewal price
- Cancellation method ("Cancel anytime in Settings > Apple ID > Subscriptions")

**3.1.2(c)** Must display subscription information before purchase — this includes:
- Price per period
- Free trial duration (if any)
- Full price after trial

Preferred: use `SubscriptionStoreView` (automatically compliant).
If custom paywall: verify all required information is shown before the purchase button.

### 3.1.3 Reader Apps

Reader apps (Spotify, Netflix pattern) may link to external purchase if:
- No button/link in-app that goes to external website for IAP equivalent
- No "buy premium on our website" messaging
<!-- /section -->

---

<!-- section: Design keywords: minimum functionality, sign in with apple, SIWA, login -->
## Section 4: Design

### 4.2 Minimum Functionality

App must provide beyond-basic functionality:
- Not primarily a WebView wrapper for a website
- Not a simple ebook/PDF viewer without additional features
- Not a reskin of an existing app
- Not a collection of stock images without meaningful functionality

### 4.8 Sign In with Apple

If the app offers sign-in with any third-party account (Google, Facebook, Twitter, WeChat,
GitHub, etc.), it MUST also offer Sign In with Apple.

Exceptions: apps used exclusively by businesses/organizations (enterprise apps), apps where
login is of a specific third-party service (e.g., Facebook app itself).

Required implementation: `ASAuthorizationAppleIDProvider` or `SignInWithAppleButton`.
<!-- /section -->

---

<!-- section: Legal keywords: privacy, ATT, tracking, HealthKit, location, permission, GDPR -->
## Section 5: Legal / Privacy

### 5.1.1 Privacy Policy

**5.1.1(i)** Privacy policy URL is required in:
- Info.plist (`NSPrivacyUsageDescription` or a dedicated key)
- App Store Connect listing
- Accessible from within the app (settings screen, onboarding, or About page)

**5.1.1(ii)** Purpose strings (`NS*UsageDescription`) must be:
- Present for every permission the app requests
- Specific to the app's actual use case (not generic "We need access to improve your experience")
- Not empty or single-word values

**5.1.1(v)** If app offers account creation/sign-in, must offer account deletion:
- Accessible from within the app (Settings or Profile screen)
- Must actually delete user data, not just deactivate

### 5.1.2 Data Use and Sharing

**5.1.2(i)** App Tracking Transparency (ATT): if app collects IDFA (`ASIdentifierManager`) or
uses cross-app tracking SDKs, must request tracking permission via
`ATTrackingManager.requestTrackingAuthorization` before collecting data.

### 5.1.3 Health and Health Research

Apps using HealthKit:
- Must have a primary purpose related to health
- Cannot sell or disclose HealthKit data to third parties
- Must have a privacy policy

### 5.1.4 Kids and Privacy

Apps in Kids Category:
- No behavioral advertising
- No third-party analytics sending data off-device
- Parental consent required for data collection where applicable

### 5.1.5 Location Services

Location usage purpose string must be specific:
- ❌ "We need your location."
- ✅ "Your location is used to show nearby restaurants within 5km."

Apps requesting Always authorization must have a clear justification for background location.
<!-- /section -->
