---
name: oss-audit
description: "Use when the user says 'oss audit', 'open source audit', 'license check', 'compliance scan', 'dependency audit', 'oss governance', '开源治理', '合规扫描', '许可证检查', or wants to scan hosts for open source compliance. Single entry point for OSS governance: setup, run, status, report, config, help."
model: sonnet
user-invocable: true
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/*) Bash(echo*) Bash(mkdir*) Bash(ls*) Bash(pwd*) Bash(scp*) Bash(which*) Bash(tar*) Bash(rm*) Bash(cat*) Bash(python3*) Read Write
---

## Overview

The single interactive entry point for oss-governance. Routes user requests to the appropriate action. Dispatches agents for heavy scanning and analysis work.

## Process

### Step 0: Resolve Working Directory and Check Config

```
Bash(command="pwd")
```

Store the result as `WD`. All file paths in this skill are relative to `WD`.

Read `{WD}/oss-audit-config.yaml`.
- If file does not exist AND user intent is NOT "setup" or "help" → output:
  ```
  [oss-governance] Not initialized. Run /oss-audit setup in this directory.
  ```
  → **stop**

### Step 1: Parse Intent

Classify the user's input:

| Intent | Trigger Patterns | Requires config |
|--------|-----------------|-----------------|
| **help** | "help", "/oss-audit help", "how to use" | No |
| **setup** | "setup", "configure", "init", first run, no args + no config | No |
| **run** | "run", "start", "scan", "go", no args (if config exists), "开始扫描" | Yes |
| **status** | "status", "last run", "history", "上次结果" | Yes |
| **report** | "report", "last report", "show report", "查看报告" | Yes |
| **config** | "config", "settings", "add host", "edit hosts", "修改配置" | Yes |

If config is required but `{WD}/oss-audit-config.yaml` does not exist → redirect to setup.

### Step 2: Execute by Intent

---

#### Intent: help

Output directly:

```
[oss-governance] Help

Commands:
  /oss-audit setup    — Initialize this directory as an OSS audit workspace
  /oss-audit          — Run compliance scan on all configured hosts
  /oss-audit run      — Same as above
  /oss-audit status   — Show last scan results summary
  /oss-audit report   — Show the most recent compliance report
  /oss-audit config   — View or modify host/scan configuration
  /oss-audit help     — Show this help

Configuration:
  oss-audit-config.yaml  — Host inventory and scan settings (Ansible-compatible)
  Supports:
    - Inline host definitions (Ansible YAML inventory format)
    - External Ansible YAML inventory file (inventory_file: /path/to/hosts.yml)
    - Host groups, per-host variables, tags

Scan Capabilities:
  License Compliance    — Identify all dependency licenses, classify risk, detect conflicts
  Vulnerability Audit   — CVE scanning via grype/trivy/npm-audit/pip-audit (optional)
  Multi-Host            — Scan multiple hosts via SSH, aggregate results

Supported Package Managers:
  npm, pip, cargo, go, maven, gradle, swift, cocoapods, ruby, composer

Reports:
  Compliance report with executive summary, risk matrix, per-host breakdown,
  priority actions, and full dependency inventory. Saved as Markdown.
```

→ **stop**

---

#### Intent: setup

Guided first-time configuration.

1. Check if `{WD}/oss-audit-config.yaml` already exists:
   - If yes and user did not explicitly say "setup": "Config exists. Use `/oss-audit config` to modify, or `/oss-audit` to run."
   - If yes and user explicitly asked for setup: ask "Config already exists. Reconfigure from scratch?" → proceed only if confirmed.

2. Read template:
   ```
   Read ${CLAUDE_PLUGIN_ROOT}/templates/default-config.yaml
   ```

3. Ask about scan scope using AskUserQuestion:
   - "What do you want to scan?"
   - Options:
     - "Local machine only" → skip SSH setup, scan local paths
     - "Remote hosts via SSH" → proceed with host configuration
     - "Both local and remote" → configure both

4. **If remote hosts:**

   Ask about inventory source using AskUserQuestion:
   - "How will you provide the host list?"
   - Options:
     - "I have an Ansible inventory file" → ask for path, verify it exists
     - "I'll define hosts here" → proceed with inline config

5. **If inline hosts:**
   Ask using AskUserQuestion:
   - "How many hosts to scan?" (options: "1-3", "4-10", "10+")
   - For each host (or first 3 if many), ask:
     - Host name (label)
     - IP or hostname (ansible_host)
     - SSH user (default: root)
     - SSH port (default: 22)
     - SSH key path (default: ~/.ssh/id_rsa). Only key-based auth is supported (BatchMode=yes).
     - Need sudo? (yes/no)
     - Tags (optional, comma-separated)
   - If 10+: suggest creating an Ansible inventory file instead

6. Ask about scan paths using AskUserQuestion:
   - "Which directories to scan on each host?"
   - Options:
     - "Default (/home, /opt, /srv, /var/www)" (Recommended)
     - "Custom paths" → ask for colon-separated list

7. Ask about vulnerability scanning using AskUserQuestion:
   - "Enable vulnerability scanning (CVE detection)?"
   - Options:
     - "Yes (Recommended)" — requires grype, trivy, or language-specific audit tools
     - "No, license compliance only"

8. **Detect available tools:**
   ```bash
   echo "=== Available Tools ===" && \
   which grype 2>/dev/null && echo "grype: YES" || echo "grype: NO" && \
   which trivy 2>/dev/null && echo "trivy: YES" || echo "trivy: NO" && \
   which npm 2>/dev/null && echo "npm: YES" || echo "npm: NO" && \
   which pip-audit 2>/dev/null && echo "pip-audit: YES" || echo "pip-audit: NO" && \
   which cargo-audit 2>/dev/null && echo "cargo-audit: YES" || echo "cargo-audit: NO" && \
   which python3 2>/dev/null && echo "python3: YES" || echo "python3: NO"
   ```
   Report what's available. If vuln scanning requested but no tools found, warn and suggest:
   ```
   No vulnerability scanning tools detected.
   Install one: brew install grype  OR  brew install trivy
   Continuing with license compliance only.
   ```

9. Generate `{WD}/oss-audit-config.yaml` from template with user selections.

10. Create output directory:
    ```
    Bash(command="mkdir -p {WD}/reports")
    ```

11. **Test connectivity** (if remote hosts configured) — for each configured host (up to 3):
    ```
    echo "echo ok" | bash "${CLAUDE_PLUGIN_ROOT}/scripts/ssh_exec.sh" "<host>" "<port>" "<user>" "<key>" "10"
    ```
    Report result per host: connected or unreachable (with error)

12. Output:
    ```
    [oss-governance] Setup complete in {WD}.
      Mode: {local / remote / both}
      Hosts: {N} ({N} reachable, {N} unreachable)
      Scan Paths: {paths}
      Vuln Scanning: {enabled/disabled}
      Available Tools: {list}
      Report Dir: ./reports/

    Next steps:
      /oss-audit          — Run your first compliance scan
      /oss-audit config   — View or modify configuration
    ```

---

#### Intent: run

Execute the full compliance scan pipeline.

1. **Read config:**
   Read `{WD}/oss-audit-config.yaml`

2. **Parse host inventory:**

   a. If `inventory_file` is set:
      - Read the inventory file
      - Parse YAML structure and extract hosts with connection variables

   b. If inline hosts:
      - Parse the `all.children` structure
      - Merge `defaults` into each host's connection settings

   c. If local-only mode (no hosts configured):
      - Use localhost with scan paths from config
      - Skip SSH — run collect-manifests.sh directly

3. **Detect available tools** (for vuln scanning):
   ```bash
   which grype trivy npm pip-audit cargo-audit 2>/dev/null
   ```

4. **Phase 1 — Collection:**

   **For remote hosts:** Dispatch the `oss-governance:host-collector` agent with:
   - **hosts**: parsed host list with connection details
   - **scan_config**: paths, depth, exclude, package_managers from config
   - **ssh_script**: `${CLAUDE_PLUGIN_ROOT}/scripts/ssh_exec.sh`
   - **collect_script**: `${CLAUDE_PLUGIN_ROOT}/scripts/collect-manifests.sh`
   - **staging_dir**: `/tmp/oss-audit-{timestamp}/`

   Wait for completion. The agent returns per-host project lists and local paths to fetched files.

   **For local-only:** Run collect-manifests.sh directly:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/collect-manifests.sh" "<paths_colon_separated>" "<depth>" "<excludes_colon_separated>"
   ```
   Parse JSON lines output. Copy/symlink discovered files to staging dir.

   **Progress output:**
   ```
   [oss-governance] Collection complete.
     Hosts: {N} scanned, {N} unreachable
     Projects: {N} discovered ({breakdown by PM})
   ```

5. **Phase 2 — License Analysis:**

   Read the reference files:
   - `${CLAUDE_PLUGIN_ROOT}/references/license-categories.md`
   - `${CLAUDE_PLUGIN_ROOT}/references/package-managers.md`
   - `${CLAUDE_PLUGIN_ROOT}/references/license-compatibility.md`

   Dispatch the `oss-governance:dependency-analyzer` agent with:
   - **projects**: full project list from host-collector output
   - **license_categories**: content of license-categories.md
   - **package_managers**: content of package-managers.md
   - **license_compatibility**: content of license-compatibility.md

   For large fleets (> 20 projects), split into batches by host and dispatch multiple dependency-analyzer agents in parallel (one per host).

   Wait for completion.

   **Progress output:**
   ```
   [oss-governance] License analysis complete.
     Dependencies: {N} total ({N} unique)
     Risk items: {critical} critical, {high} high, {medium} medium
   ```

6. **Phase 3 — Vulnerability Scan (optional):**

   If vuln scanning is enabled AND at least one scanning tool is available:

   Dispatch the `oss-governance:vuln-scanner` agent with:
   - **projects**: project list with local paths
   - **min_severity**: from config
   - **available_tools**: detected tool list

   Wait for completion.

   **Progress output:**
   ```
   [oss-governance] Vulnerability scan complete.
     Vulnerabilities: {critical} critical, {high} high, {medium} medium
   ```

   If vuln scanning is disabled or no tools available:
   ```
   [oss-governance] Vulnerability scanning skipped (no tools available).
   ```

7. **Phase 4 — Report Assembly:**

   Dispatch the `oss-governance:compliance-reporter` agent with:
   - **dependency_results**: from dependency-analyzer
   - **vuln_results**: from vuln-scanner (or null if skipped)
   - **unreachable_hosts**: from host-collector
   - **config**: scan configuration
   - **report_path**: `{WD}/reports/{YYYY-MM-DD}-compliance.md`
   - **timestamp**: current ISO timestamp
   - **license_compatibility**: content of license-compatibility.md

   Wait for completion.

8. **Save state:**
   Write `{WD}/.oss-audit-state.yaml`:
   ```yaml
   last_run: "YYYY-MM-DDTHH:MM:SS"
   last_report: "reports/YYYY-MM-DD-compliance.md"
   mode: local | remote | both
   hosts_scanned: N
   hosts_unreachable: N
   projects_found: N
   total_deps: N
   unique_deps: N
   risk_items: N
   vulns: N
   compliance_score: N
   ```

9. **Output summary:**
   ```
   [oss-governance] Compliance scan complete.
     Hosts: {N} scanned, {N} unreachable
     Projects: {N} ({PM breakdown})
     Dependencies: {N} total ({N} unique)
     Compliance Score: {score}/100 ({posture})
     Report: ./reports/{YYYY-MM-DD}-compliance.md

   Top risk items:
     1. {dependency} ({license}) — {conflict} [{N} projects]
     2. {dependency} ({license}) — {issue} [{N} projects]
     3. {dependency} (UNKNOWN) — license not detected [{N} projects]

   Use /oss-audit report to view the full report.
   ```

10. **Cleanup staging:**
    ```bash
    rm -rf /tmp/oss-audit-{timestamp}/
    ```

---

#### Intent: status

Show last scan summary.

1. Read `{WD}/.oss-audit-state.yaml`
   - If not found: "No scan has been run yet. Use `/oss-audit` to start." → **stop**

2. Output:
   ```
   [oss-governance] Status
     Last Scan: {last_run}
     Mode: {mode}
     Hosts: {hosts_scanned} scanned, {hosts_unreachable} unreachable
     Projects: {projects_found}
     Dependencies: {total_deps} ({unique_deps} unique)
     Risk Items: {risk_items}
     Vulnerabilities: {vulns}
     Compliance Score: {compliance_score}/100
     Report: {last_report}
   ```

---

#### Intent: report

Display the most recent report.

1. Read `{WD}/.oss-audit-state.yaml` to get `last_report` path
   - If not found: "No scan has been run yet." → **stop**

2. Read the report file at `{WD}/{last_report}`
   - If not found: "Report file missing: {path}" → **stop**

3. Output the full report content.

---

#### Intent: config

View or modify configuration.

1. Read `{WD}/oss-audit-config.yaml`

2. Display current configuration:
   - Inventory source (inline or external file path)
   - Host count and group names
   - Per-host summary table: name, IP, port, user, become, tags
   - Scan paths
   - Package managers
   - Exclude patterns
   - Vuln scanning: enabled/disabled
   - Min severity
   - Report directory

3. If user provided a modification request:
   - **add host**: ask for host details (name, IP, user, port, key, become, tags), add to appropriate group
   - **remove host**: remove from inventory
   - **add group**: create new group under `all.children`
   - **change paths**: update `scan.paths`
   - **change PM list**: update `scan.package_managers`
   - **toggle vuln scan**: update `vuln_scan.enabled`
   - **change severity**: update `vuln_scan.min_severity`
   - **set inventory file**: update `inventory_file` path

4. After modification: write updated config to `{WD}/oss-audit-config.yaml`

5. Confirm: "Updated: {description of change}"
