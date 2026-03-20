---
name: inspect
description: "Use when the user says 'inspect', 'inspection', 'linux inspection', 'host inspection', 'security audit', 'batch inspection', 'inspect hosts', 'inspect setup', 'inspect config', or asks about Linux host security checks. Single human-facing entry point for batch Linux host inspection: setup, run, status, report, and help."
model: sonnet
user-invocable: true
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/*) Bash(echo*) Bash(mkdir*) Bash(ls*) Bash(pwd*) Read Write
---

## Overview

The single interactive entry point for linux-inspect. Routes user requests to the appropriate action. Dispatches agents for heavy inspection work.

## Process

### Step 0: Resolve Working Directory and Check Config

```
Bash(command="pwd")
```

Store the result as `WD`. All file paths in this skill are relative to `WD`.

Read `{WD}/inspect-config.yaml`.
- If file does not exist AND user intent is NOT "setup" or "help" → output:
  ```
  [linux-inspect] Not initialized. Run /inspect setup in this directory.
  ```
  → **stop**

### Step 1: Parse Intent

Classify the user's input:

| Intent | Trigger Patterns | Requires config |
|--------|-----------------|-----------------|
| **help** | "help", "/inspect help", "how to use" | No |
| **setup** | "setup", "configure", "init", first run, no args + no config | No |
| **run** | "run", "start", "scan", "go", no args (if config exists) | Yes |
| **status** | "status", "last run", "history" | Yes |
| **report** | "report", "last report", "show report" | Yes |
| **config** | "config", "settings", "add host", "edit hosts" | Yes |

If config is required but `{WD}/inspect-config.yaml` does not exist → redirect to setup.

### Step 2: Execute by Intent

---

#### Intent: help

Output directly:

```
[linux-inspect] Help

Commands:
  /inspect setup    — Initialize this directory as an inspection workspace
  /inspect          — Run inspection on all configured hosts
  /inspect run      — Same as above
  /inspect status   — Show last inspection results summary
  /inspect report   — Show the most recent report
  /inspect config   — View or modify host configuration
  /inspect help     — Show this help

Configuration:
  inspect-config.yaml  — Host inventory and inspection settings (Ansible-compatible)
  Supports:
    - Inline host definitions (Ansible YAML inventory format)
    - External Ansible YAML inventory file (inventory_file: /path/to/hosts.yml)
    - Host groups, per-host variables, tags

Inspection Categories:
  security       — SSH config, SUID files, users, sudo, firewall, SELinux, permissions, passwords
  vulnerabilities — Kernel version, package updates, CVE patches, listening services, software versions
  logs           — Auth logs, system logs, audit logs, log rotation
  system         — Disk, memory, CPU, services, scheduled tasks
  network        — Network config, connections, DNS
  compliance     — File integrity, time sync, kernel parameters
```

→ **stop**

---

#### Intent: setup

Guided first-time configuration.

1. Check if `{WD}/inspect-config.yaml` already exists:
   - If yes and user did not explicitly say "setup": "Config exists. Use `/inspect config` to modify, or `/inspect` to run."
   - If yes and user explicitly asked for setup: ask "Config already exists. Reconfigure from scratch?" → proceed only if confirmed.

2. Read template:
   ```
   Read ${CLAUDE_PLUGIN_ROOT}/templates/default-config.yaml
   ```

3. Ask about inventory source using AskUserQuestion:
   - "Use an existing Ansible inventory file?"
   - Options:
     - "Yes, I have an Ansible YAML inventory file" → ask for path
     - "No, I'll define hosts here" → proceed with inline config

4. **If external inventory:**
   - Ask for inventory file path via AskUserQuestion (free text)
   - Verify the file exists: `Bash(command="ls -la <path>")`
   - If exists: set `inventory_file` in config and skip inline host definition
   - If not found: warn and fall back to inline definition

5. **If inline hosts:**
   Ask using AskUserQuestion:
   - "How many hosts to inspect?" (options: "1-3", "4-10", "10+")
   - For each host (or first 3 if many), ask:
     - Host name (label)
     - IP or hostname (ansible_host)
     - SSH user (default: root)
     - SSH port (default: 22)
     - SSH key path (default: ~/.ssh/id_rsa). Only key-based auth is supported (BatchMode=yes).
     - Need sudo? (yes/no)
     - Tags (optional, comma-separated)
   - If 10+: suggest creating an Ansible inventory file instead

6. Ask about inspection categories using AskUserQuestion (multiSelect):
   - Security (SSH, firewall, users, permissions)
   - Vulnerabilities (kernel, updates, CVE, services)
   - Logs (auth, system, audit, rotation)
   - System Health (disk, memory, CPU, services)
   - Network (config, connections, DNS)
   - Compliance (integrity, NTP, kernel params)
   Default: all selected.

7. Ask about minimum severity using AskUserQuestion:
   - "Minimum severity to report?"
   - Options: "LOW (all findings)", "MEDIUM", "HIGH", "CRITICAL (only critical)"

8. Generate `{WD}/inspect-config.yaml` from template with user selections.

9. Create output directory:
   ```
   Bash(command="mkdir -p ./reports")
   ```

10. **Test connectivity** — for each configured host (up to 3):
    ```
    echo "echo ok" | bash "${CLAUDE_PLUGIN_ROOT}/scripts/ssh_exec.sh" "<host>" "<port>" "<user>" "<key>" "10"
    ```
    Report result per host: ✓ reachable or ✗ unreachable (with error)

11. Output:
    ```
    [linux-inspect] Setup complete in {CWD}.
      Hosts: {N} ({N} reachable, {N} unreachable)
      Groups: {group names}
      Categories: {selected categories}
      Min Severity: {severity}
      Report Dir: ./reports/

    Next steps:
      /inspect          — Run your first inspection
      /inspect config   — View or modify configuration
    ```

---

#### Intent: run

Execute the full inspection pipeline.

1. Read `{WD}/inspect-config.yaml`

2. **Parse host inventory:**

   a. If `inventory_file` is set:
      - Read the inventory file (must be Ansible YAML inventory format)
      - Parse YAML structure and extract hosts with connection variables

   b. If inline hosts:
      - Parse the `all.children` structure
      - Merge `defaults` into each host's connection settings

3. **Resolve checks to run:**
   - Read `${CLAUDE_PLUGIN_ROOT}/references/checklist.md`
   - Filter by configured `categories`
   - Filter by `skip_checks` (remove specified IDs)
   - If `only_checks` is set, use only those IDs
   - Build final check list with: id, category, severity, commands

4. **Map checks to agents:**
   - Security checks (SEC-*), Network checks (NET-*), Compliance checks (CMP-*) → security-auditor
   - Log checks (LOG-*), System checks (SYS-*), Vulnerability checks (VUL-*) → log-analyzer

5. **Dispatch host-connector agent:**
   ```
   Dispatch the `host-connector` agent with:
   - **hosts**: parsed host list with connection details
   - **checks**: full list of checks to execute (all categories)
   - **ssh_script**: "${CLAUDE_PLUGIN_ROOT}/scripts/ssh_exec.sh"
   - **timeout**: from config defaults.timeout
   - **parallel**: from config defaults.parallel
   ```
   Wait for completion. The agent returns raw check results per host.

6. **Dispatch analysis agents in parallel** — for each reachable host:

   a. Dispatch `security-auditor` agent with:
      - **host**: host info
      - **check_results**: SEC-*, NET-*, CMP-* results for this host
      - **checklist**: checklist content for security/network/compliance sections
      - **min_severity**: from config

   b. Dispatch `log-analyzer` agent with:
      - **host**: host info
      - **check_results**: LOG-*, SYS-*, VUL-* results for this host
      - **checklist**: checklist content for logs/system/vulnerabilities sections
      - **min_severity**: from config

   Run both agents in parallel for each host. If multiple hosts, dispatch all agents at once.

7. **Dispatch report-assembler agent:**
   ```
   Dispatch the `report-assembler` agent with:
   - **security_results**: all security-auditor outputs
   - **log_results**: all log-analyzer outputs
   - **unreachable_hosts**: from host-connector
   - **config**: inspection config
   - **report_path**: "{WD}/reports/{YYYY-MM-DD}-inspection.md"
   - **timestamp**: current ISO timestamp
   ```
   Wait for completion.

8. **Save state:**
   Write `{WD}/.inspect-state.yaml`:
   ```yaml
   last_run: "YYYY-MM-DDTHH:MM:SS"
   last_report: "reports/YYYY-MM-DD-inspection.md"
   hosts_inspected: N
   hosts_unreachable: N
   total_findings: N
   fleet_score: N
   ```

9. **Output summary:**
   ```
   [linux-inspect] Inspection complete.
     Hosts: {N} inspected, {N} unreachable
     Findings: {critical} critical, {high} high, {medium} medium, {low} low
     Fleet Score: {score}/100 ({posture})
     Report: ./reports/{YYYY-MM-DD}-inspection.md

   Top issues:
     1. {title} — {hosts}
     2. {title} — {hosts}
     3. {title} — {hosts}

   Use /inspect report to view the full report.
   ```

---

#### Intent: status

Show last inspection summary.

1. Read `{WD}/.inspect-state.yaml`
   - If not found: "No inspection has been run yet. Use `/inspect` to start." → **stop**

2. Output:
   ```
   [linux-inspect] Status
     Last Run: {last_run}
     Hosts: {hosts_inspected} inspected, {hosts_unreachable} unreachable
     Findings: {total_findings}
     Fleet Score: {fleet_score}/100
     Report: {last_report}
   ```

---

#### Intent: report

Display the most recent report.

1. Read `{WD}/.inspect-state.yaml` to get `last_report` path
   - If not found: "No inspection has been run yet." → **stop**

2. Read the report file at `{WD}/{last_report}`
   - If not found: "Report file missing: {path}" → **stop**

3. Output the full report content.

---

#### Intent: config

View or modify configuration.

1. Read `{WD}/inspect-config.yaml`

2. Display current configuration:
   - Inventory source (inline or external file path)
   - Host count and group names
   - Per-host summary table: name, IP, port, user, become, tags
   - Active categories
   - Min severity
   - Skip checks list
   - Report directory

3. If user provided a modification request:
   - **add host**: ask for host details (name, IP, user, port, key, become, tags), add to appropriate group
   - **remove host**: remove from inventory
   - **add group**: create new group under `all.children`
   - **change category**: update `inspection.categories` list
   - **change severity**: update `inspection.min_severity`
   - **skip check**: add to `inspection.skip_checks`
   - **set inventory file**: update `inventory_file` path

4. After modification: write updated config to `{WD}/inspect-config.yaml`

5. Confirm: "Updated: {description of change}"
