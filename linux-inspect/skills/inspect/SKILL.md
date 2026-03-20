---
name: inspect
description: "Use when the user says 'inspect', 'inspection', 'linux inspection', 'host inspection', 'security audit', 'batch inspection', 'inspect hosts', 'inspect setup', 'inspect config', 'inspect profile', or asks about Linux host security checks. Single human-facing entry point for batch Linux host inspection: setup, run, status, report, profile, and help."
model: sonnet
user-invocable: true
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/*) Bash(python3*) Bash(mkdir*) Bash(ls*) Bash(pwd*) Bash(which*) Bash(cat*) Bash(rm*) Read Write
---

## Overview

Single interactive entry point for linux-inspect v2. Routes user requests to the appropriate action. Uses bash scripts for data collection and AI agents for analysis.

Architecture: Collector script (single SSH per host) → Host profiles (per-host state) → AI analysis (structured JSON).

## Process

### Step 0: Resolve Working Directory and Check Config

```
Bash(command="pwd")
```

Store the result as `WD`. All file paths are relative to `WD`.

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
| **profile** | "profile", "profiles", "baseline", "suppress" | Yes |

### Step 2: Execute by Intent

---

#### Intent: help

Output directly:

```
[linux-inspect] Help

Commands:
  /inspect setup      — Initialize inspection workspace
  /inspect            — Run inspection on all configured hosts
  /inspect run        — Same as above
  /inspect status     — Show last inspection results
  /inspect report     — Show the most recent report
  /inspect config     — View or modify host configuration
  /inspect profile    — View or manage host profiles
  /inspect help       — Show this help

Profile Commands:
  /inspect profile                        — List all profiles
  /inspect profile <host>                 — Show profile detail
  /inspect profile <host> suppress <id>   — Add suppression
  /inspect profile <host> baseline ...    — Set baseline
  /inspect profile <host> exclude <id>    — Exclude check
  /inspect profile <host> reset           — Delete profile (recreated on next run)

Architecture:
  collector.sh    — Single SSH per host, structured JSON output
  profiles/       — Per-host YAML profiles (auto-evolving)
  AI agents       — Structured analysis + delta reporting + profile evolution
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
   - If parsed list is empty: re-prompt.
   - For each hostname: set `ansible_host: <hostname>`, no explicit user/port/key.
   - Ask sudo configuration via AskUserQuestion:
     - "Do these hosts need sudo for inspection?"
     - Options:
       - "Yes, sudo with NOPASSWD" → set `ansible_become: true` in defaults
       - "Yes, sudo with password" → ask for sudo password
       - "No, running as root or no sudo needed"
   - Go to step 6.

5. **Detailed path:**
   - Ask for hostnames, comma-separated.
   - If > 10 hosts: redirect to step 5b.
   - For each host: ask connection settings.
   - Go to step 6.

5b. **Ansible inventory file:**
   - Ask for path, verify exists, set `inventory_file` in config.

6. Ask about inspection scope using AskUserQuestion:
   - "What to inspect?"
   - Options:
     - "All categories (recommended)"
     - "Custom selection"

7. Generate `{WD}/inspect-config.yaml`.

8. Create directories:
   ```
   Bash(command="mkdir -p ./reports ./profiles")
   ```

9. **Check dependencies:**
   - If any host uses password auth: verify `sshpass` installed
   - Verify `python3` available locally:
     ```
     Bash(command="python3 -c 'import yaml; print(\"ok\")' 2>&1")
     ```
     If fails: "PyYAML required. Install: pip install pyyaml"

10. **Test connectivity** (up to 3 hosts):
    Test with a simple SSH echo command using run_host.sh patterns.

11. Output setup summary.

---

#### Intent: run

Execute the full inspection pipeline.

**Step R1: Read config, resolve hosts**

Read `{WD}/inspect-config.yaml`.

Parse host inventory:
- If `inventory_file` is set: read the external file
- If inline hosts: parse `all.children` structure, merge `defaults`

Store the resolved host list. Each host has: name, host, port, user, key, password, become, become_pass, timeout.

**Step R2: Check profiles**

For each host, check if `{WD}/profiles/{hostname}.yaml` exists.
Split into: `hosts_with_profile` and `hosts_without_profile`.

**Step R3: Generate checks.conf per host**

For hosts WITH profile:
```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile_ops.py expire-suppressions {WD}/profiles/{hostname}.yaml")
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile_ops.py get-checks {WD}/profiles/{hostname}.yaml ${CLAUDE_PLUGIN_ROOT}/references/checks.yaml > /tmp/li-checks-{hostname}.conf")
```

For hosts WITHOUT profile:
```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile_ops.py get-checks --unfiltered ${CLAUDE_PLUGIN_ROOT}/references/checks.yaml > /tmp/li-checks-{hostname}.conf")
```

**Step R4: Execute collector on each host (parallel)**

For each host, create a host JSON file and run:
```
Bash(command="cat > /tmp/li-host-{hostname}.json << 'EOF'
{\"name\":\"{name}\",\"host\":\"{ip}\",\"port\":{port},\"user\":\"{user}\",\"key\":\"{key}\",\"password\":\"{password}\",\"become\":{become},\"become_pass\":\"{become_pass}\",\"timeout\":{timeout}}
EOF
bash ${CLAUDE_PLUGIN_ROOT}/scripts/run_host.sh /tmp/li-host-{hostname}.json ${CLAUDE_PLUGIN_ROOT}/scripts/collector.sh /tmp/li-checks-{hostname}.conf {WD}/.inspect-output")
```

Run multiple hosts in parallel (use separate Bash tool calls). Wait for all to complete.

**Step R5: Parse results, create/update profiles**

For each host, read `{WD}/.inspect-output/{hostname}.json`.

For hosts WITHOUT profile (first run):
```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile_ops.py init {hostname} {WD}/.inspect-output/{hostname}.json ${CLAUDE_PLUGIN_ROOT}/references/checks.yaml {WD}/profiles")
```

For hosts WITH profile (update discovery):
```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile_ops.py update-discovery {WD}/profiles/{hostname}.yaml {WD}/.inspect-output/{hostname}.json ${CLAUDE_PLUGIN_ROOT}/references/checks.yaml")
```

**Step R6: Dispatch analysis agents (parallel)**

For each reachable host, read the collector output and profile, then dispatch:

a. `security-auditor` agent with:
   - host: host info
   - check_results: SEC-*, NET-*, CMP-* results from collector JSON
   - checks_reference: relevant sections from checks.yaml
   - profile: read via `python3 profile_ops.py read {WD}/profiles/{hostname}.yaml`
   - is_first_run: whether this host had no profile before
   - min_severity: from config

b. `log-analyzer` agent with:
   - host: host info
   - check_results: LOG-*, SYS-*, VUL-* results from collector JSON
   - checks_reference: relevant sections from checks.yaml
   - profile: same as above
   - is_first_run: same
   - min_severity: from config

Run security-auditor and log-analyzer in parallel for each host. If multiple hosts, batch analysis agents (3 hosts at a time).

**Step R7: Save findings snapshots**

For each host, extract `findings_snapshot` from both analysis agents and save to profile:

Write a JSON update file with the combined findings snapshot and scores, then:
```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile_ops.py apply-update {WD}/profiles/{hostname}.yaml /tmp/li-snapshot-{hostname}.json")
```

**Step R8: Dispatch profile-evolver (parallel per host)**

For each host with an existing profile (not first-run hosts), dispatch `profile-evolver` agent:
- profile: current profile
- security_results: from Step R6
- log_results: from Step R6
- discovery: from collector output

**Step R9: Process evolution proposals**

Collect proposals from all profile-evolver agents.

For non-sensitive proposals (`sensitive: false`):
- Auto-apply via `profile_ops.py apply-update`
- Record in evolution_summary as "auto_applied"

For sensitive proposals (`sensitive: true`):
- Batch them per host and present to user via AskUserQuestion:
  - "Profile evolution proposals for {hostname}:" (list proposals)
  - Options: "Apply all", "Review individually", "Skip all"
- Apply confirmed proposals
- Record in evolution_summary as "applied" or "rejected"

**Step R10: Dispatch report-assembler**

Dispatch `report-assembler` agent with:
- security_results: all security-auditor outputs
- log_results: all log-analyzer outputs
- unreachable_hosts: hosts with error JSON
- evolution_summary: per-host summary of proposals and actions
- config: inspection config
- report_path: `{WD}/reports/{YYYY-MM-DD}-inspection.md`
- timestamp: current ISO timestamp
- previous_state: from `.inspect-state.yaml` (null if first run)

**Step R11: Save state and output summary**

Write `{WD}/.inspect-state.yaml`:
```yaml
last_run: "YYYY-MM-DDTHH:MM:SS"
last_report: "reports/YYYY-MM-DD-inspection.md"
hosts_inspected: N
hosts_unreachable: N
total_findings: N
fleet_score: N
profile_count: N
delta_new: N
delta_resolved: N
```

Clean up temp files:
```
Bash(command="rm -rf {WD}/.inspect-output /tmp/li-host-*.json /tmp/li-checks-*.conf /tmp/li-snapshot-*.json")
```

Output:
```
[linux-inspect] Inspection complete.
  Hosts: {N} inspected, {N} unreachable
  Findings: {critical} critical, {high} high, {medium} medium, {low} low
  Suppressed: {N}
  Fleet Score: {score}/100 ({posture})
  Delta: +{N} new, -{N} resolved
  Profiles: {N} ({N} evolved)
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
     Profiles: {profile_count}
     Delta: +{delta_new} new, -{delta_resolved} resolved
     Report: {last_report}
   ```

---

#### Intent: report

Display the most recent report.

1. Read `.inspect-state.yaml` to get `last_report` path.
2. Read the report file.
3. Output the full report content.

---

#### Intent: config

View or modify configuration. Same as v1 but with `profiles.dir` field added.

---

#### Intent: profile

Manage host profiles.

**No args / "profile"**: List all profiles.
```
Bash(command="ls {WD}/profiles/*.yaml 2>/dev/null")
```
For each, show: hostname, OS, applicable checks count, suppressions count, last updated.

**profile <hostname>**: Show profile detail.
```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/profile_ops.py read {WD}/profiles/{hostname}.yaml")
```
Display formatted: discovered info, applicable checks, excluded checks, baselines, suppressions, recent audit log.

**profile <hostname> suppress <finding_id>**: Add suppression.
- Ask for reason and expiry date via AskUserQuestion
- Apply via profile_ops.py apply-update
- Must be approved by user (this is always a sensitive operation)

**profile <hostname> baseline <check_id> <key> <value>**: Set baseline.
- Apply via profile_ops.py apply-update

**profile <hostname> exclude <check_id>**: Exclude a check.
- Ask for reason
- Apply via profile_ops.py apply-update

**profile <hostname> reset**: Delete profile.
- Confirm with user
- Delete `{WD}/profiles/{hostname}.yaml`
- "Profile deleted. A fresh profile will be created on next inspection run."
