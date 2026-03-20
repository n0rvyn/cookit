# linux-inspect v2

Adaptive Linux host inspection plugin for Claude Code. Single SSH connection per host, per-host profiles that evolve over time, structured analysis with delta awareness.

## Quick Start

```
/inspect setup    # First-time setup — configure hosts and categories
/inspect          # Run inspection (creates profiles on first run)
/inspect report   # View last report
/inspect profile  # View host profiles
```

## Features

- **Single SSH per host** — collector script runs all checks in one session (replaces N per-check connections)
- **Per-host profiles** — auto-discovery of OS, services, and capabilities; profiles evolve across runs
- **Delta awareness** — reports show new, resolved, and changed findings since last run
- **Baseline + suppression** — known-good values and acknowledged issues tracked per host
- **Profile evolution** — AI proposes and auto-applies non-sensitive updates; sensitive changes need confirmation
- **Structured analysis** — collector outputs JSON; AI agents consume structured data, not raw text
- **29 check items** across 6 categories with OS-variant commands
- **Ansible-compatible inventory**
- **Fleet-wide scoring** with trend tracking

## Architecture

```
/inspect (skill — sonnet)
  → collector.sh (bash) — single SSH per host, structured JSON output
  → profile_ops.py (python3) — profile CRUD, check filtering, audit logging
  → security-auditor (agent — sonnet) — SEC/NET/CMP analysis + delta
  → log-analyzer (agent — sonnet) — LOG/SYS/VUL analysis + delta
  → profile-evolver (agent — sonnet) — profile evolution proposals
  → report-assembler (agent — sonnet) — consolidated report + trends
```

### Three-Layer Design

```
Layer 3: AI Analysis          — structured JSON in, findings + deltas out
Layer 2: Host Profile Store   — {WD}/profiles/{hostname}.yaml
Layer 1: Collector Script     — single SSH, discovery + checks → JSON
```

### Inspection Flow

```
First run (no profile):
  → Collector discovers OS/services + runs ALL checks
  → Profile created from discovery
  → AI analyzes results, reports everything

Subsequent runs (profile exists):
  → Collector runs discovery refresh + applicable checks only
  → AI compares with baselines, reports deltas
  → Profile-evolver proposes updates (auto-apply or confirm)
```

## Commands

| Command | Description |
|---------|-------------|
| `/inspect setup` | Initialize workspace, configure hosts |
| `/inspect` or `/inspect run` | Run full inspection |
| `/inspect status` | Show last run summary |
| `/inspect report` | Display most recent report |
| `/inspect config` | View/modify configuration |
| `/inspect profile` | List/manage host profiles |
| `/inspect profile <host>` | Show profile detail |
| `/inspect profile <host> suppress <id>` | Suppress a finding |
| `/inspect profile <host> reset` | Delete profile |
| `/inspect help` | Show help |

## Configuration

`inspect-config.yaml` — Ansible-compatible YAML:

```yaml
defaults:
  ansible_user: root
  ansible_port: 22
  timeout: 30
  parallel: 5

all:
  children:
    webservers:
      hosts:
        web1:
          ansible_host: 192.168.1.10
          tags: [production, nginx]

inspection:
  categories: [security, vulnerabilities, logs, system, network, compliance]
  min_severity: LOW

profiles:
  dir: ./profiles
  auto_evolve: true
  auto_apply_non_sensitive: true
```

## Profile Evolution

After each inspection, the profile-evolver agent analyzes results and proposes updates:

| Proposal Type | Auto-Apply | Needs Confirmation |
|--------------|------------|-------------------|
| Discovery update (OS, services) | Yes | |
| Non-security baseline | Yes | |
| Security baseline | | Yes |
| Check exclusion | | Yes |
| Custom check (additive) | Yes | |
| Suppression changes | | Yes |

All profile changes are recorded in an audit log (capped at 100 entries).

## Dependencies

- **Local**: python3, PyYAML (`pip install pyyaml`)
- **Remote**: bash, coreutils (python3 optional, improves JSON output)
- **Password auth**: sshpass (SSH key auth preferred)
