# iOS Platform Overlay

> When evaluating an iOS app, **keep** each dimension's universal sub-questions from `frameworks.md` and **replace only the platform-specific sub-questions** with the following. This overlay is a partial replacement, not a full replacement.

---

## Usage

1. Detect iOS project: `.xcodeproj`, `.xcworkspace`, `Package.swift` with iOS platform, or user indicates iOS app
2. Load this file
3. For each dimension:
   - **Keep** the universal sub-questions from `frameworks.md` (they are platform-neutral)
   - **Replace** only the platform-specific sub-questions with this overlay's questions
4. Scoring anchors from `frameworks.md` still apply (they are platform-neutral)
5. Add iOS-specific Kill Criteria triggers to the Kill Criteria output

---

## Demand Authenticity (需求真伪)

**Core question:** Are iOS users willing to pay for this from an unknown indie developer, given higher quality expectations on the platform?

**Platform-specific sub-questions:** (replace the default platform-specific questions)
1. **iOS willingness-to-pay:** iOS users have higher payment intent than Android, but also higher quality bars. Is this product's polish level sufficient for iOS expectations?
2. **System capability overlap:** Can Shortcuts, Widgets, Focus Modes, or built-in system features solve this problem? What is the app's incremental value beyond what iOS provides for free?
3. **Platform-native job:** Is this a job that users specifically want to do on iPhone/iPad? Or is it better suited to web/desktop?
4. **App Store review signals:** What do negative reviews of competitors say? What jobs are underserved?
5. **Pain frequency on mobile:** Is this a problem users encounter while using their phone, or do they have to go out of their way to open this app?

---

## Journey Completeness (逻辑闭环)

**Core question:** Does the core journey use iOS platform capabilities naturally, or is it reinventing OS-level functionality?

**Platform-specific sub-questions:** (replace the default platform-specific questions)
1. **OS wheel reinvention:** Is any part of this app rebuilding what Shortcuts, Widgets, ShareSheet, or system apps already do? If yes, what's the justification?
2. **Platform integration depth:** Does the journey use iOS-native patterns (SwiftUI navigation, system share sheet, Spotlight indexing, Handoff) or fight against them?
3. **Widget/Shortcut extension:** Could the core action be a Widget or Shortcut Action instead of a full app? If yes, should it be?
4. **Notification-driven retention:** Does the retention loop use notifications appropriately, or does it rely on users remembering to open the app?
5. **Cross-device journey:** If user has iPhone + iPad + Mac, does the journey span devices naturally via iCloud/Handoff?

---

## Market Space (市场空间)

**Core question:** Is this App Store category viable for an indie, or is it dominated by mega-publishers with acquisition budgets?

**Platform-specific sub-questions:** (replace the default platform-specific questions)
1. **Category saturation:** How many apps in this App Store category? What's the quality bar of the top 10?
2. **ASO keyword competition:** Are the primary search keywords crowded with well-funded apps? Can you rank for long-tail keywords?
3. **Mega-publisher dominance:** Is this category controlled by companies with marketing budgets (Calm, Headspace pattern)? Or is it indie-friendly?
4. **App Store editorial potential:** Is this the type of app Apple features in "Apps We Love" or seasonal collections? (Design quality, platform integration, and privacy focus increase editorial chances)
5. **Geographic niche:** Is there a language/region-specific opportunity that global competitors ignore?
6. **New platform early-mover:** Is there a visionOS or watchOS version opportunity? Early presence on new Apple platforms significantly increases Apple editorial feature probability.

---

## Business Viability (商业可行)

**Core question:** After Apple's 30% cut (or 15% small business program), can this generate sustainable income through App Store-native discovery?

**Platform-specific sub-questions:** (replace the default platform-specific questions)
1. **Subscription vs. one-time purchase:** Which model fits the value delivery? Subscription requires ongoing value; one-time requires volume.
2. **After the cut:** At target price minus 30% (or 15%), how many paying users needed for $5K/month? Is that realistic given category download volume?
3. **App Store as discovery channel:** Can ASO alone drive sufficient installs, or does this require external marketing? Include In-App Events as a free visibility mechanism — scheduled content events that appear in App Store search and browse.
4. **Trial/paywall conversion:** What's the category-standard free trial length? Is the value demonstrable within that window?
5. **Family Sharing / volume impact:** Does Family Sharing (one purchase, 6 users) significantly impact unit economics?
6. **ATT impact:** If the app relies on advertising revenue, how does App Tracking Transparency affect the business model? Post-ATT, ad-supported indie apps face significantly reduced ad revenue.

---

## Moat (护城河)

**Core question:** What's the Sherlock risk, and what platform-depth advantages does this app have that Apple and big competitors can't easily replicate?

**Platform-specific sub-questions:** (replace the default platform-specific questions)
1. **Sherlock risk assessment:** What is the probability Apple builds this into the next iOS? Historical pattern: f.lux → Night Shift, Duet → Sidecar, battery apps → Battery Health, flashlight apps → Control Center. Does this app's core feature fit the pattern of "obvious utility Apple hasn't gotten to yet"?

   **Sherlock risk scoring methodology:**

   | Factor | Low Risk (1) | Medium Risk (2) | High Risk (3) |
   |--------|-------------|-----------------|----------------|
   | Feature type | Creative/professional tool | Productivity tool | Quality-of-life utility |
   | Android equivalent | No built-in equivalent | Partial equivalent | Fully built-in |
   | Recent WWDC signals | No related sessions | Adjacent technology shown | Directly related API introduced |
   | Apple hiring | No signals | Related domain roles | Specific feature-area roles |
   | Complexity | Requires deep domain expertise | Moderate complexity | Simple, well-defined scope |

   Sum factors: 5-7 = Low Sherlock risk, 8-11 = Medium, 12-15 = High.

2. **Platform integration depth:** Which iOS-exclusive APIs does this use (HealthKit, ARKit, CoreML, CallKit, WidgetKit, App Intents)? Deeper integration = harder to replicate on other platforms and harder for cross-platform competitors.
3. **CloudKit data lock-in:** Is user data stored in CloudKit (private database)? CloudKit data = high migration cost = strong retention moat.
4. **Ecosystem integration:** Does the app benefit from Apple ecosystem (Watch complication, Mac Catalyst/iPad, ShareSheet, Siri Shortcuts)? More touch points = stickier.
5. **AI disruption on iOS:** Can Apple Intelligence or on-device ML features absorb this app's core function?

---

## Execution Quality (执行质量)

**Core question:** Can one person keep pace with Apple's annual platform cadence without burning out?

**Platform-specific sub-questions:** (replace the default platform-specific questions)
1. **WWDC maintenance burden:** Each June, Apple announces new iOS. How much annual forced maintenance does this app require (new APIs, deprecations, new device sizes, new capabilities)?
2. **SwiftUI vs UIKit choice:** Does the app's UI require capabilities that SwiftUI still doesn't fully support (e.g., precise text editing control, custom layout engines, advanced collection view behaviors)? If not, SwiftUI is appropriate regardless of app complexity. Evaluate based on specific UI requirements, not a simple/complex dichotomy.
3. **Apple framework reliance:** Is the app built on stable Apple frameworks, or does it depend on frameworks Apple frequently changes (e.g., StoreKit 1 → 2, UIKit → SwiftUI transitions)?
4. **App Review compliance:** Are there any features that sit in App Review grey zones (web views, payment links, API usage that could be restricted)?
5. **One-person cadence:** Given the codebase size and technology choices, can one developer realistically ship the September iOS update + features + bug fixes?
6. **Privacy label maintenance:** How complex are the app's privacy nutrition labels? More features and third-party SDKs = more labels to maintain and audit. Incorrect labels = App Review rejection risk.

---

## iOS-Specific Kill Criteria Triggers

Add these to the Kill Criteria output when evaluating an iOS app:

1. **Apple announces competing feature at WWDC** — If Apple builds the core feature into iOS, the app loses its reason to exist within 3-6 months
2. **App Review rejects core functionality** — If the core feature depends on an API or mechanism that App Review blocks, and no workaround exists without gutting the product
3. **Category winner with network effects** — If a single app dominates the category through network effects (social/marketplace dynamics) and your app lacks network effects
4. **Apple Intelligence absorption** — If on-device ML features in a future iOS version can replicate the core value proposition without a third-party app

---

## iOS Elevator Pitch Test

Replace the generic Elevator Pitch constraints with:

**Constraints:**
- App Store subtitle: ≤30 characters
- First App Store description sentence: makes users tap "Get"
- Combined: a stranger browsing the App Store understands what this does AND why they need it

**Judgment:** Same Clear / Vague / Cannot articulate scale, but judged against App Store browsing context (users scanning quickly, not reading carefully).
