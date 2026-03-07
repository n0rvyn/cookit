---
name: fetch-swift-api-updates
description: "Use when the user wants to check for latest Swift/SwiftUI API changes, or says 'fetch API updates', 'check WWDC changes'. Fetches latest Swift/SwiftUI API changes from WWDC session notes and updates project references."
user-invocable: true
---

## Overview

Fetches Swift/SwiftUI API changes for a given year and appends new sections to the appropriate
`ios-development/references/swift-api-changes-*.md` reference file.

## Process

### Step 1: Determine Target

Extract the target year from the invocation:
- If `/fetch-swift-api-updates 2025` → year = 2025, target file = `swift-api-changes-ios26.md`
- If `/fetch-swift-api-updates 2024` → year = 2024, target file = `swift-api-changes-ios18.md`
- If no argument → use current year

Map year to iOS version:
- 2025 → iOS 26 (WWDC 2025)
- 2024 → iOS 18 (WWDC 2024)
- 2023 → iOS 17 (WWDC 2023)

### Step 2: Search for New APIs

Run the following searches:

```
WebSearch: "WWDC {year} SwiftUI new API site:github.com"
WebSearch: "What's new SwiftUI {year} site:hackingwithswift.com OR site:swiftbysundell.com OR site:artemnovichkov.com"
WebSearch: "Swift {version} changelog release notes {year} wwdcnotes"
```

For each significant API found in search results, fetch from sources in priority order:

```
Priority 1: GitHub repositories (README, sample code)
  WebFetch: github.com URL for the API or sample project

Priority 2: Technical blogs
  WebFetch: artemnovichkov.com / swiftbysundell.com / hackingwithswift.com article

Priority 3: WWDC session notes (plain text)
  WebFetch: wwdcnotes.com session page

Priority 4: developer.apple.com (fallback — likely to fail due to JS rendering)
  WebFetch: developer.apple.com — if empty or JS error, fall back to search snippet
```

If all WebFetch attempts fail: use the WebSearch snippet directly
and note "⚠️ content from search snippet only, verify with full docs."

### Step 3: Extract API Information

For each significant API, extract:
- API name and type (macro, modifier, view, protocol)
- Correct usage pattern (with code example)
- Common mistakes (anti-patterns to flag in reviews)
- Minimum OS version
- Keywords for section targeting

### Step 4: Check for Duplicates

Before adding a section, check if it already exists in the target file:

```
Grep("<keyword>", "ios-development/references/swift-api-changes-{ios-version}.md")
```

If the keyword already exists in a `<!-- section:` marker → skip (already documented).

### Step 5: Format and Append

For each new API not already documented, format as:

```markdown
---

<!-- section: {APIName} keywords: {keyword1}, {keyword2}, {keyword3} -->
## {API Title} (iOS {version})

**Minimum OS**: iOS {version}

{Description}

### Correct Usage

```swift
// ✅ Correct pattern
{code example}
```

### Common Mistakes

```swift
// ❌ {mistake description}
{bad code}
```
<!-- /section -->
```

Append the formatted sections to the appropriate `swift-api-changes-*.md` file.

### Step 6: Report

Output a summary:

```
## Fetch Complete

Target: swift-api-changes-ios{version}.md
Year: {year}

### Added {N} new sections:
- {API name 1} — {brief description}
- {API name 2} — {brief description}

### Skipped (already documented):
- {API name} — already has section with keywords: {keywords}

### ⚠️ Content quality notes:
- {API name} — content from search snippet only; recommend verifying at developer.apple.com
```

## Graceful Degradation

If WebSearch returns few results (topic too new or obscure):
- Document what was found with a note: "⚠️ Limited information available — may need manual update after WWDC sessions are published."
- Do not fabricate API details. Only document what was found in search results.

If the target reference file doesn't exist yet:
- Create it with the standard header format (see existing files as template)
- Then append sections normally
