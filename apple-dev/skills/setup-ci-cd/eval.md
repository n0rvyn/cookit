# setup-ci-cd Eval

## Trigger Tests
<!-- Prompts that SHOULD trigger this skill -->
- "Set up CI/CD for my iOS project"
- "Configure Xcode Cloud and auto versioning"
- "配置自动上传 TestFlight"
- "Set up automatic version bumping"
- "配置版本自动化"
- "Setup CI for my Xcode project"

## Negative Trigger Tests
<!-- Prompts that should NOT trigger this skill -->
- "Write a plan"
- "Review my code"
- "Fix this build error"
- "Bump the version manually"

## Output Assertions
<!-- What must be true in the skill's output -->
- [ ] Output detects .xcodeproj and lists all targets with current version numbers
- [ ] Output fixes version mismatches across targets (MARKETING_VERSION and CURRENT_PROJECT_VERSION)
- [ ] Output enables Apple Generic versioning if not already enabled
- [ ] Output creates .github/workflows/auto-version.yml with conventional commit detection
- [ ] Output creates ci_scripts/ci_post_clone.sh with agvtool and CI_BUILD_NUMBER
- [ ] Output verifies agvtool works (what-version and what-marketing-version)
- [ ] Output provides Xcode Cloud workflow configuration guidance (Dev to TestFlight, Main to App Store)
- [ ] Output explains version management: MARKETING_VERSION by GitHub Actions, CURRENT_PROJECT_VERSION by Xcode Cloud

## Redundancy Risk
Baseline comparison: Base model can write CI scripts but lacks Xcode-native versioning integration, project detection, and multi-target version synchronization
Last tested model: Opus 4.6
Last tested date: 2026-03-26
Verdict: essential
