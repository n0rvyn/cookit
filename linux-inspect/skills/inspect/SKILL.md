---
name: inspect
description: "Use when the user says 'inspect', 'inspection', 'linux inspection', 'host inspection', 'security audit', 'batch inspection', 'inspect hosts', 'inspect setup', 'inspect config', or asks about Linux host security checks. Single human-facing entry point for batch Linux host inspection: setup, run, status, report, and help."
model: sonnet
user-invocable: true
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/*) Bash(mkdir*) Bash(ls*) Bash(pwd*) Bash(which*) Read Write
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
    - SSH key or password authentication (password auth requires sshpass)

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

3. Ask how to define hosts using AskUserQuestion:
   - "How would you like to add hosts?"
   - Options:
     - "Quick — just hostnames (uses SSH config)" → go to step 4
     - "Detailed — specify connection settings per host" → go to step 5
     - "Ansible inventory file — I have one already" → go to step 5b

4. **Quick path** (SSH config already works):
   - Ask one free-text question: "Enter hostnames, comma-separated (e.g. web1, db1, 10.0.0.5):"
   - If parsed list is empty (blank input or only whitespace/commas): re-prompt "No hostnames provided. Enter at least one hostname."
   - Parse the comma-separated list into individual hosts.
   - For each hostname: set `ansible_host: <hostname>`, no explicit user/port/key (relies on user's `~/.ssh/config`).
   - Do NOT set `ansible_user` or `ansible_port` per-host; the SSH config and `defaults` section handle this.
   - Ask one follow-up using AskUserQuestion:
     - "Do these hosts need sudo for inspection?"
     - Options:
       - "Yes, sudo with NOPASSWD" → set `ansible_become: true` in defaults
       - "Yes, sudo with password" → ask for sudo password once (applied to all hosts via `ansible_become_pass` in defaults)
       - "No, running as root or no sudo needed"
   - Go to step 6.

5. **Detailed path:**
   - Ask one free-text question: "Enter hostnames, comma-separated:"
   - If parsed list is empty: re-prompt (same as step 4).
   - If more than 10 hosts: output "For 10+ hosts, use an Ansible inventory file for efficiency." and redirect to step 5b. Do NOT proceed with per-host questions for more than 10 hosts.
   - For each host, ask ONE combined AskUserQuestion:
     - "Host: {name} — connection settings"
     - Options:
       - "Use defaults (hostname as-is, SSH config)" → no per-host overrides
       - "Custom settings" → ask ONE free-text follow-up: "Enter settings for {name} — format: `user=X port=Y key=/path sudo=yes/no` (or `password=XXX` instead of key). Omit fields to keep defaults."
         Parse the key=value pairs. Unrecognized or missing fields use template defaults.
   - Go to step 6.

5b. **Ansible inventory file:**
   - Ask for inventory file path via AskUserQuestion (free text)
   - Verify the file exists: `Bash(command="ls -la <path>")`
   - If exists: set `inventory_file` in config and go to step 6
   - If not found: warn and redirect to step 4 (Quick path)

6. Ask about inspection scope using AskUserQuestion:
   - "What to inspect?"
   - Options:
     - "All categories (recommended)" → security, vulnerabilities, logs, system, network, compliance; severity = LOW
     - "Custom selection" → follow up with multiSelect: Security, Vulnerabilities, Logs, System Health, Network, Compliance.
       Then ask "Minimum severity?" with options: LOW (all), MEDIUM, HIGH, CRITICAL

7. Generate `{WD}/inspect-config.yaml` from template with user selections.

8. Create output directory:
   ```
   Bash(command="mkdir -p ./reports")
   ```

9. **Check sshpass** — if any host uses password auth (`ansible_ssh_pass` is set):
    ```
    Bash(command="which sshpass")
    ```
    - If not found: ask the user via AskUserQuestion:
      - "sshpass is required for password-based SSH but is not installed. Install it?"
      - Options:
        - "Yes, install sshpass" → the user approves the install command (brew/apt) manually
        - "No, switch to SSH key auth" → go back and reconfigure affected hosts with key-based auth
    - If found: proceed.

10. **Test connectivity** — for each configured host (up to 3):
    ```
    bash "${CLAUDE_PLUGIN_ROOT}/scripts/ssh_exec.sh" "<host>" "<port>" "<user>" "<key>" "<timeout>" "false" "sudo" "<password>" <<< "echo ok"
    ```
    - For fields not set on the host, use values from the `defaults` section in the generated config.
    - `<port>`: host's `ansible_port`, or `defaults.ansible_port` (22).
    - `<user>`: host's `ansible_user`, or `defaults.ansible_user` (root).
    - `<key>`: host's `ansible_ssh_private_key_file`, or `none` if not configured (SSH agent/config handles auth).
    - `<timeout>`: from `defaults.timeout` in the config.
    - `<password>`: host's `ansible_ssh_pass`, or empty string if using key auth.
    - Report result per host: ✓ reachable or ✗ unreachable (with error)

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
   - Any check ID not matching a known prefix → log-analyzer (fallback)

5. **Dispatch host-connector agent:**
   ```
   Dispatch the `host-connector` agent with:
   - **hosts**: parsed host list with connection details (including ansible_ssh_pass, ansible_become_pass if configured)
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

   Run both agents in parallel for each host. If multiple hosts, dispatch analysis agents in batches of 3 hosts at a time. Collect all results from one batch before dispatching the next.

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
   - **add host**: ask for host details (name, IP, user, port, key or password, become, tags), add to appropriate group
   - **remove host**: remove from inventory
   - **add group**: create new group under `all.children`
   - **change category**: update `inspection.categories` list
   - **change severity**: update `inspection.min_severity`
   - **skip check**: add to `inspection.skip_checks`
   - **set inventory file**: update `inventory_file` path

4. After modification: write updated config to `{WD}/inspect-config.yaml`

5. Confirm: "Updated: {description of change}"
