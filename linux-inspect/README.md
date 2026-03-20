# linux-inspect

Batch Linux host inspection plugin for Claude Code. Connects to remote hosts via SSH, runs security audits, vulnerability scans, log analysis, and compliance checks, then assembles a consolidated report.

## Quick Start

```
/inspect setup    # First-time setup — configure hosts and categories
/inspect          # Run inspection
/inspect report   # View last report
```

## Features

- **Ansible-compatible inventory** — use your existing `hosts` file or define hosts inline
- **6 inspection categories**: security, vulnerabilities, logs, system health, network, compliance
- **30+ check items** with severity levels (CRITICAL / HIGH / MEDIUM / LOW)
- **Parallel SSH execution** across multiple hosts
- **Compound risk detection** — cross-category pattern analysis
- **Fleet-wide scoring** — per-host and aggregate security posture
- **Markdown reports** with executive summary, priority actions, per-host details

## Architecture

```
/inspect (skill — sonnet)
  → host-connector (agent — haiku) — parallel SSH execution, raw data collection
  → security-auditor (agent — sonnet) — security/network/compliance analysis
  → log-analyzer (agent — sonnet) — logs/system/vulnerability analysis
  → report-assembler (agent — sonnet) — consolidated report generation
```

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
```

## Commands

| Command | Description |
|---------|-------------|
| `/inspect setup` | Initialize workspace, configure hosts |
| `/inspect` or `/inspect run` | Run full inspection |
| `/inspect status` | Show last run summary |
| `/inspect report` | Display most recent report |
| `/inspect config` | View/modify configuration |
| `/inspect help` | Show help |
