---
name: submission-preview
description: "Use before submitting to App Store, or when the user says 'submission preview', 'pre-submit check', 'will this pass review'. Checks app code against Apple's App Review Guidelines to catch common rejection reasons."
---

## Division of Responsibility

- **submission-preview** (this skill): checks **App code** against App Review Guidelines (sections 1-5)
- **appstoreconnect-review**: checks **store listing materials** (ASC form fields, descriptions, screenshots)

Run both before submission. They don't overlap.

## Process

### Step 1: Load Reference

Search for the reference file:
```
Glob("**/ios-development/references/app-review-guidelines.md")
```
If found: Read it.
If not found: proceed using the embedded checklist in this skill (sections 1-5 are fully
embedded in Steps 3-4 below — the reference file is a convenience copy only).

### Step 2: Detect Project Characteristics

Read project code and configuration to determine which checks apply:

```
[Project Characteristics]
- Has user accounts: {yes/no} → triggers 5.1.1(v), 4.8
- Has IAP/subscriptions: {yes/no} → triggers 3.1.1, 3.1.2
- Has UGC: {yes/no} → triggers 1.2
- Has third-party SDKs: {yes/no} → triggers 5.1.2
- Has background modes: {yes/no} → triggers 2.5.4
- Has location services: {yes/no} → triggers 5.1.5
- Has HealthKit: {yes/no} → triggers 5.1.3
- Has Kids Category: {yes/no} → triggers 1.3, 5.1.4
- Has third-party login: {yes/no} → triggers 4.8
- Has tracking/ads: {yes/no} → triggers 5.1.2(i)
```

**Detection method**: read Info.plist, scan imports/frameworks, search for SDK integration patterns.

Only run checks relevant to detected characteristics. Skip the rest.

### Step 3: Code Verification Checks

---

#### Section 1: Safety

**1.2 — UGC Moderation** (if has UGC)

Check: Does the app include filtering, reporting, and blocking mechanisms?

Method: Search for report/block/flag/filter UI elements and backing logic.

```
[1.2] UGC moderation — ✅ found {report: file:line, block: file:line} / ❌ missing {which mechanism}
```

**1.3 — Kids Category** (if targeting kids)

Check: No third-party analytics or advertising SDKs.

Method: Search imports for analytics/ad frameworks (Firebase Analytics, Facebook SDK, AdMob, etc.).

```
[1.3] Kids third-party SDKs — ✅ none found / ❌ found {SDK name} at {file:line}
```

---

#### Section 2: Performance

**2.1 — App Completeness**

Check: No placeholder text, TODO comments in user-facing strings, empty views.

Method: Grep for `TODO`, `FIXME`, `placeholder`, `Lorem`, `TBD`, `xxx` in .swift files. Check for Views with only `Text("")` or `EmptyView()` as body.

```
[2.1] Placeholder content — ✅ none / ❌ found at {file:line}: "{text}"
```

**2.3 — Metadata Completeness**

Check: ASC marketing materials exist.

Method: Check if `docs/10-app-store-connect/market.md` exists and has content beyond template placeholders.

```
[2.3] Store metadata — ✅ complete / ❌ {market.md missing or has placeholders}
```

**2.5.1 — Deprecated APIs**

Check: No use of deprecated APIs.

Method: Grep for known deprecated patterns: `NavigationView`, `.foregroundColor(`, `UIAlertView`, `UIActionSheet`, `UIWebView`, `.navigationBarTitle(`.

```
[2.5.1] Deprecated APIs — ✅ none / ⚠️ {API} at {file:line}
```

**2.5.4 — Background Modes** (if has background modes)

Check: Each declared background mode has corresponding implementation.

Method: Read Info.plist `UIBackgroundModes` array. For each mode, search for its API usage (e.g., `audio` → AVAudioSession, `location` → CLLocationManager with allowsBackgroundLocationUpdates, `fetch` → BGAppRefreshTask).

```
[2.5.4] Background mode "{mode}" — ✅ implemented at {file:line} / ❌ declared but no implementation found
```

---

#### Section 3: Business

**3.1.1 — IAP for Digital Content** (if has IAP)

Check: Digital content unlocking uses StoreKit. Restore purchases mechanism exists.

Method: Search for StoreKit imports and `restorePurchases` / `AppStore.sync()` / `Transaction.currentEntitlements`.

```
[3.1.1] IAP implementation — ✅ StoreKit at {file:line}, restore at {file:line} / ❌ {missing component}
```

**3.1.2(c) — Subscription Information** (if has subscriptions)

Check: Before purchase, user sees renewal term, price, cancellation method.

Method: Search for `SubscriptionStoreView` (preferred) or custom paywall View. If custom, check for price/term display.

```
[3.1.2c] Subscription info — ✅ SubscriptionStoreView at {file:line} / ⚠️ custom paywall, verify terms shown at {file:line}
```

---

#### Section 4: Design

**4.2 — Minimum Functionality**

Check: App is not primarily a WebView wrapper.

Method: Analyze main View hierarchy. If primary content is WKWebView/SFSafariViewController with no native UI, flag.

```
[4.2] Minimum functionality — ✅ native UI / ❌ primarily WebView at {file:line}
```

**4.8 — Sign In with Apple** (if has third-party login)

Check: If app offers Google/Facebook/WeChat/other third-party login, SIWA must also be offered.

Method: Search for third-party auth SDKs (GoogleSignIn, FBSDKLoginKit, etc.) and for `ASAuthorizationAppleIDProvider` or `SignInWithAppleButton`.

```
[4.8] SIWA — ✅ found at {file:line} / ❌ third-party login at {file:line} but no SIWA
```

---

#### Section 5: Legal / Privacy

**5.1.1(i) — Privacy Policy**

Check: Info.plist has privacy policy URL. App has accessible privacy policy link in UI.

Method: Read Info.plist for privacy policy URL key. Search UI for privacy policy link/button.

```
[5.1.1i] Privacy policy — ✅ plist: {URL}, UI: {file:line} / ❌ {missing where}
```

**5.1.1(ii) — Permission Purpose Strings**

Check: Every NS*UsageDescription in Info.plist exists and has meaningful text (not placeholder).

Method: Read Info.plist, list all `*UsageDescription` keys and their values. Flag empty, single-word, or generic values ("We need this permission").

```
[5.1.1ii] Purpose strings:
- NSCameraUsageDescription: "..." — ✅ specific / ⚠️ too generic
- NSLocationWhenInUseUsageDescription: "..." — ✅ / ❌ missing
```

**5.1.1(v) — Account Deletion** (if has user accounts)

Check: If app has sign up/login, it must offer account deletion.

Method: Search for account deletion UI (delete account button, settings section).

```
[5.1.1v] Account deletion — ✅ found at {file:line} / ❌ has login at {file:line} but no deletion option
```

**5.1.2(i) — App Tracking Transparency** (if has tracking/ads)

Check: If app uses tracking SDKs (AdSupport, IDFA), ATTrackingManager must be implemented.

Method: Search for `import AdSupport`, `ASIdentifierManager`, tracking SDK imports. Then search for `ATTrackingManager.requestTrackingAuthorization`.

```
[5.1.2i] ATT — ✅ implemented at {file:line} / ❌ tracking SDK at {file:line} but no ATT
```

**5.1.5 — Location Purpose** (if has location services)

Check: Location usage description exists and explains purpose clearly.

Method: Check Info.plist for `NSLocationWhenInUseUsageDescription` / `NSLocationAlwaysUsageDescription`. Verify description is specific to the app's use case.

```
[5.1.5] Location purpose — ✅ "{description}" / ❌ missing or generic
```

---

### Step 4: Output Report

```
## Submission Preview Report

### Project Characteristics
{detected characteristics list}

### Code Verification

#### 🔴 High Risk (likely rejection)
- [Guideline X.X.X] {issue}
  Location: {file:line}
  Fix: {specific fix}

#### 🟡 Medium Risk (possible rejection)
- [Guideline X.X.X] {issue}
  Location: {file:line}
  Fix: {specific fix}

#### ✅ Passed
- [Guideline X.X.X] {check description}

### Manual Verification Checklist

These items cannot be verified through code and need device/ASC confirmation:

- [ ] [2.1] App runs without crashes on all supported devices
- [ ] [2.3.3] Screenshots show actual app usage (not splash/login screens)
- [ ] [2.3.6] Age rating questionnaire answered accurately
- [ ] [4.1] App is not a copycat of an existing app
- [ ] [5.1.1] Privacy policy URL is accessible and matches actual data collection
- [ ] {project-specific items based on characteristics}

### Pre-Submission Checklist (from Guidelines "Before You Submit")

- [ ] Test app for crashes and bugs
- [ ] All metadata complete and accurate
- [ ] Contact information updated
- [ ] Demo account provided in App Review Notes (if app has login)
- [ ] Backend services live and accessible
- [ ] Non-obvious features explained in App Review Notes
- [ ] {if has IAP: IAP items visible and testable}

### Summary
- 🔴 High risk: N items
- 🟡 Medium risk: N items
- ✅ Passed: N items
- Manual verification: N items
```

Report ends with:
> Code compliance check complete. Run `/appstoreconnect-review` to check store listing materials.

---

## Principles

1. **Only check what's relevant**: detect project characteristics first, skip inapplicable checks
2. **Code evidence required**: every finding must reference file:line
3. **Don't guess visual compliance**: App Store screenshots, UI appearance, crash behavior → manual checklist
4. **Guidelines reference**: every finding cites the specific guideline number
5. **Actionable fixes**: every issue includes a specific fix, not "fix this"

## Completion Criteria

- Project characteristics detected (Step 2)
- All applicable guideline sections checked with code evidence
- Report delivered with severity classification (High/Medium/Passed)
- Manual verification checklist generated
- 串联提示 to `/appstoreconnect-review` included
