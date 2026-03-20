# oss-audit Eval

## Trigger Tests
- "oss audit"
- "open source audit"
- "scan for open source compliance"
- "license check across our servers"
- "dependency audit"
- "oss governance"
- "开源治理"
- "合规扫描"
- "许可证检查"
- "check all our dependencies for license issues"

## Negative Trigger Tests
- "audit the CLAUDE.md rules" (→ dev-workflow:audit-rules)
- "inspect the servers" (→ linux-inspect)
- "security audit on hosts" (→ linux-inspect)
- "review my code" (→ apple-dev:apple-reviewer or similar)
- "check for security vulnerabilities in my code" (→ generic security, not OSS governance)

## Output Assertions

### Setup
- [ ] Detects if config exists and routes accordingly
- [ ] Asks about scan scope (local/remote/both)
- [ ] Generates valid YAML config file
- [ ] Tests SSH connectivity for remote hosts
- [ ] Detects available scanning tools
- [ ] Reports setup summary with next steps

### Run (Local)
- [ ] Discovers projects by scanning for package manager files
- [ ] Extracts dependencies from lockfiles/manifests
- [ ] Classifies each dependency license by risk category
- [ ] Detects license compatibility conflicts
- [ ] Generates compliance report in report_dir
- [ ] Report contains executive summary with compliance score
- [ ] Report contains license distribution table
- [ ] Report contains priority action items for each risk
- [ ] Saves state file with run summary

### Run (Remote)
- [ ] Connects to configured hosts via SSH
- [ ] Discovers projects on remote hosts
- [ ] Fetches lockfiles back to controller
- [ ] Aggregates results across all hosts
- [ ] Per-host breakdown in report
- [ ] Handles unreachable hosts gracefully

### Vulnerability Scanning
- [ ] Detects available scanning tools
- [ ] Runs appropriate scanner per PM type
- [ ] Deduplicates CVEs across projects
- [ ] Includes vulns in compliance report
- [ ] Skips gracefully when no tools available

### Status / Report
- [ ] Status shows last run summary
- [ ] Report displays full markdown report
- [ ] Both handle "no previous run" case

## Redundancy Risk
Baseline comparison: Base Claude can run npm audit, read package.json, and identify common licenses, but cannot orchestrate multi-host scans, maintain license compatibility matrices, or generate structured compliance reports.
Last tested model: —
Last tested date: —
Verdict: essential
