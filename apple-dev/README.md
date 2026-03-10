# Apple Dev Plugin

Complete iOS/macOS/iPadOS development workflow plugin.

## Install

```bash
/plugin install apple-dev@indie-toolkit
```

For Codex/OpenCode: see `.codex/INSTALL.md` or `.opencode/INSTALL.md`.

## Skills (16)

| Skill | Trigger | Description |
|-------|---------|-------------|
| apple-swift-context | Auto (Swift files) | Loads platform-specific rules from reference docs |
| ui-review | `/ui-review` | SwiftUI UI + interaction compliance review |
| design-review | `/design-review` | Visual hierarchy, color, spacing quality review |
| feature-review | `/feature-review` | Product + UX completeness from user journey perspective |
| execution-review | `/execution-review` | Plan-vs-code verification + Swift code scan |
| validate-design-tokens | `/validate-design-tokens` | Design token compliance check |
| submission-preview | `/submission-preview` | App Review Guidelines pre-check |
| appstoreconnect-review | `/appstoreconnect-review` | ASC submission material check |
| testing-guide | `/testing-guide` | Interactive testing best practices guidance |
| swiftdata-patterns | `/swiftdata-patterns` | SwiftData best practices guidance |
| localization-setup | `/localization-setup` | String Catalogs + localization guidance |
| fetch-swift-api-updates | `/fetch-swift-api-updates` | Fetch latest WWDC API changes |
| generate-design-system | `/generate-design-system` | Generate SwiftUI design system from tokens |
| generate-stitch-prompts | `/generate-stitch-prompts` | Generate UI prompts from requirements |
| project-kickoff | `/project-kickoff` | New project feasibility + requirements |
| setup-ci-cd | `/setup-ci-cd` | Fastlane + GitHub Actions for TestFlight |

## Agents (4)

| Agent | Description |
|-------|-------------|
| apple-reviewer | Code review for iOS/macOS Swift projects |
| ui-reviewer | UI + UX compliance review (fresh context) |
| design-reviewer | Visual quality review (fresh context) |
| feature-reviewer | Product completeness review (fresh context) |

## Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| protect-pbxproj | PreToolUse | Prevents direct editing of `.xcodeproj/project.pbxproj` files |

## References (12)

Platform-specific sections are tagged with `platform: iOS` or `platform: macOS`. Sections without a tag apply to both platforms.

| File | Content |
|------|---------|
| apple-swift-rules.md | Swift dev rules (build cycle, concurrency, UI, macOS patterns) |
| apple-ui-checklist.md | UI code compliance checklist (iOS + macOS sections) |
| ui-design-principles.md | Professional UI design principles |
| apple-hig-design-tokens.md | Parameterizable design token system |
| swift-coding-standards.md | Swift naming and code organization |
| swiftdata-guide.md | SwiftData best practices |
| testing-guide.md | Unit test, UI test, TDD |
| localization-guide.md | String Catalogs, pluralization |
| app-review-guidelines.md | Apple App Review Guidelines |
| macos-distribution-guide.md | Notarization, sandboxing, Sparkle |
| swift-api-changes-ios18.md | iOS 18 / WWDC 2024 APIs |
| swift-api-changes-ios26.md | iOS 26 / WWDC 2025 APIs |
