#!/usr/bin/env python3
"""profile_ops.py — Host profile CRUD for linux-inspect v2.

Subcommands:
  init <hostname> <discovery_json> <checks_yaml> <profiles_dir>
  get-checks <profile_path> <checks_yaml>
  get-checks --unfiltered <checks_yaml>
  apply-update <profile_path> <update_json>
  expire-suppressions <profile_path>
  read <profile_path>
  update-discovery <profile_path> <discovery_json> <checks_yaml>

Dependencies: PyYAML (pip install pyyaml)
"""

import json
import os
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

AUDIT_LOG_MAX = 100
PROFILE_VERSION = 2

# ── Utility ───────────────────────────────────────────────────────────────────


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: str, data: dict):
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def append_audit(profile: dict, action: str, detail: str, source: str = "auto"):
    if "audit_log" not in profile:
        profile["audit_log"] = []
    profile["audit_log"].append({
        "timestamp": now_iso(),
        "action": action,
        "detail": detail,
        "source": source,
    })
    # Rotate: keep last N entries
    if len(profile["audit_log"]) > AUDIT_LOG_MAX:
        profile["audit_log"] = profile["audit_log"][-AUDIT_LOG_MAX:]


# ── Check filtering logic ────────────────────────────────────────────────────


def matches_requires(check: dict, discovered: dict) -> bool:
    """Check if a check's requires conditions are met by the discovered host state."""
    requires = check.get("requires")
    if not requires:
        return True

    # os_family: host must be one of listed families
    if "os_family" in requires:
        if discovered.get("os_family") not in requires["os_family"]:
            return False

    # service: at least one listed service must be running (OR logic; handles distro name variants)
    if "service" in requires:
        host_services = set(discovered.get("services", []))
        if not any(svc in host_services for svc in requires["service"]):
            return False

    # security_framework: host must use one of listed frameworks
    if "security_framework" in requires:
        if discovered.get("security_framework") not in requires["security_framework"]:
            return False

    # command_exists: all listed commands must be available
    if "command_exists" in requires:
        host_cmds = set(discovered.get("installed_commands", []))
        for cmd in requires["command_exists"]:
            if cmd not in host_cmds:
                return False

    return True


def derive_applicable_checks(checks_data: dict, discovered: dict) -> list[str]:
    """Derive which check IDs apply to this host based on discovery data."""
    applicable = []
    for check in checks_data.get("checks", []):
        if matches_requires(check, discovered):
            # Also check if at least one command variant matches
            commands = check.get("commands", {})
            os_family = discovered.get("os_family", "unknown")
            if os_family in commands or "all" in commands:
                applicable.append(check["id"])
    return applicable


def resolve_command(check: dict, os_family: str) -> str | None:
    """Resolve the correct OS-variant command for a check."""
    commands = check.get("commands", {})
    # Exact OS family match first
    if os_family in commands:
        return commands[os_family]
    # Fallback to 'all'
    if "all" in commands:
        return commands["all"]
    return None


# ── Subcommand: init ──────────────────────────────────────────────────────────


def cmd_init(hostname: str, discovery_json_path: str, checks_yaml_path: str, profiles_dir: str):
    """Create initial profile from collector discovery output."""
    discovery = load_json(discovery_json_path)
    checks_data = load_yaml(checks_yaml_path)

    # Extract discovery section from collector output
    disc = discovery.get("discovery", discovery)

    applicable = derive_applicable_checks(checks_data, disc)

    profile = {
        "version": PROFILE_VERSION,
        "host": hostname,
        "last_updated": now_iso(),
        "discovered": {
            "os_family": disc.get("os_family", "unknown"),
            "os_version": disc.get("os_version", "unknown"),
            "distro": disc.get("distro", "unknown"),
            "kernel": disc.get("kernel", "unknown"),
            "arch": disc.get("arch", "unknown"),
            "init_system": disc.get("init_system", "unknown"),
            "security_framework": disc.get("security_framework", "none"),
            "security_mode": disc.get("security_mode", ""),
            "package_manager": disc.get("package_manager", "unknown"),
            "services": disc.get("services", []),
            "installed_commands": disc.get("installed_commands", []),
            "cpu_count": disc.get("cpu_count", 0),
            "memory_total_mb": disc.get("memory_total_mb", 0),
        },
        "applicable_checks": applicable,
        "excluded_checks": [],
        "baselines": {},
        "suppressions": [],
        "custom_checks": [],
        "last_run": None,
        "audit_log": [],
    }

    append_audit(profile, "profile_created",
                 f"Initial profile: {disc.get('distro', 'unknown')} {disc.get('os_version', '')}, "
                 f"{len(applicable)} applicable checks",
                 "discovery")

    os.makedirs(profiles_dir, exist_ok=True)
    output_path = os.path.join(profiles_dir, f"{hostname}.yaml")
    save_yaml(output_path, profile)
    print(json.dumps({"status": "created", "path": output_path, "applicable_checks": len(applicable)}))


# ── Subcommand: get-checks ────────────────────────────────────────────────────


def cmd_get_checks(profile_path: str | None, checks_yaml_path: str, unfiltered: bool = False):
    """Output checks.conf (bash-sourceable) for this host."""
    checks_data = load_yaml(checks_yaml_path)
    all_checks = checks_data.get("checks", [])

    if unfiltered:
        # First run: output all checks with all OS variants
        _output_checks_conf_unfiltered(all_checks)
    else:
        profile = load_yaml(profile_path)
        _output_checks_conf_filtered(all_checks, profile)


def _output_checks_conf_unfiltered(checks: list[dict]):
    """Output all checks with all OS variants (first run, no profile)."""
    lines = [
        "# Generated by profile_ops.py (unfiltered mode)",
        f"LI_TIMEOUT=60",
        f"LI_MAX_LINES=200",
        f"LI_CHECK_COUNT={len(checks)}",
    ]

    for i, check in enumerate(checks):
        lines.append(f"LI_CHECK_{i}_ID={shlex.quote(check['id'])}")
        lines.append(f"LI_CHECK_{i}_CAT={shlex.quote(check.get('category', 'unknown'))}")
        lines.append(f"LI_CHECK_{i}_SEV={shlex.quote(check.get('severity', 'MEDIUM'))}")

        commands = check.get("commands", {})
        if len(commands) == 1 and "all" in commands:
            # Single command, no variants needed
            lines.append(f"LI_CHECK_{i}_CMD={shlex.quote(commands['all'])}")
        else:
            # Output all variants
            for variant, cmd in commands.items():
                lines.append(f"LI_CHECK_{i}_CMD_{variant}={shlex.quote(cmd)}")

    print("\n".join(lines))


def _output_checks_conf_filtered(checks: list[dict], profile: dict):
    """Output filtered checks with resolved OS commands (profile exists)."""
    discovered = profile.get("discovered", {})
    os_family = discovered.get("os_family", "unknown")
    applicable = set(profile.get("applicable_checks", []))
    excluded = {e["id"] for e in profile.get("excluded_checks", [])}
    custom_checks = profile.get("custom_checks", [])

    # Filter to applicable - excluded
    filtered = [c for c in checks if c["id"] in applicable and c["id"] not in excluded]

    # Add custom checks
    total = filtered + custom_checks
    total_count = len(total)

    lines = [
        f"# Generated by profile_ops.py for {profile.get('host', 'unknown')} ({os_family})",
        f"LI_TIMEOUT=60",
        f"LI_MAX_LINES=200",
        f"LI_CHECK_COUNT={total_count}",
    ]

    for i, check in enumerate(total):
        lines.append(f"LI_CHECK_{i}_ID={shlex.quote(check['id'])}")
        lines.append(f"LI_CHECK_{i}_CAT={shlex.quote(check.get('category', 'unknown'))}")
        lines.append(f"LI_CHECK_{i}_SEV={shlex.quote(check.get('severity', 'MEDIUM'))}")

        # For standard checks, resolve OS variant
        if "commands" in check:
            cmd = resolve_command(check, os_family)
            if cmd:
                lines.append(f"LI_CHECK_{i}_CMD={shlex.quote(cmd)}")
            else:
                lines.append(f"LI_CHECK_{i}_CMD=''")
        elif "command" in check:
            # Custom check: single command
            lines.append(f"LI_CHECK_{i}_CMD={shlex.quote(check['command'])}")

    print("\n".join(lines))


# ── Subcommand: apply-update ──────────────────────────────────────────────────


def cmd_apply_update(profile_path: str, update_json_path: str):
    """Apply evolution proposals to profile."""
    profile = load_yaml(profile_path)
    updates = load_json(update_json_path)

    applied = 0
    for update in updates.get("updates", []):
        field = update.get("field", "")
        value = update.get("value")
        detail = update.get("audit_detail", f"Updated {field}")
        source = update.get("source", "auto")

        # Handle dotted field paths
        parts = field.split(".")
        target = profile
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]

        target[parts[-1]] = value
        append_audit(profile, "field_updated", detail, source)
        applied += 1

    profile["last_updated"] = now_iso()
    save_yaml(profile_path, profile)
    print(json.dumps({"status": "updated", "applied": applied}))


# ── Subcommand: expire-suppressions ──────────────────────────────────────────


def cmd_expire_suppressions(profile_path: str):
    """Remove expired suppressions."""
    profile = load_yaml(profile_path)
    suppressions = profile.get("suppressions", [])
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    active = []
    expired_count = 0
    for s in suppressions:
        expires = s.get("expires")
        if expires and str(expires) <= today:
            append_audit(profile, "suppression_expired",
                         f"Suppression {s.get('finding_id', '?')} expired (was: {expires})",
                         "auto")
            expired_count += 1
        else:
            active.append(s)

    profile["suppressions"] = active
    if expired_count > 0:
        profile["last_updated"] = now_iso()
        save_yaml(profile_path, profile)

    print(json.dumps({"status": "ok", "expired": expired_count, "remaining": len(active)}))


# ── Subcommand: read ──────────────────────────────────────────────────────────


def cmd_read(profile_path: str):
    """Output profile as JSON."""
    profile = load_yaml(profile_path)
    print(json.dumps(profile, default=str, indent=2))


# ── Subcommand: update-discovery ──────────────────────────────────────────────


def cmd_update_discovery(profile_path: str, discovery_json_path: str, checks_yaml_path: str):
    """Update discovered section from fresh collector discovery."""
    profile = load_yaml(profile_path)
    discovery = load_json(discovery_json_path)
    checks_data = load_yaml(checks_yaml_path)

    disc = discovery.get("discovery", discovery)
    old_disc = profile.get("discovered", {})

    # Track changes
    changes = []
    for key in ["os_family", "os_version", "distro", "kernel", "init_system",
                "security_framework", "security_mode", "package_manager",
                "cpu_count", "memory_total_mb"]:
        old_val = old_disc.get(key)
        new_val = disc.get(key)
        if old_val != new_val:
            changes.append(f"{key}: {old_val} -> {new_val}")

    # Check service changes
    old_services = set(old_disc.get("services", []))
    new_services = set(disc.get("services", []))
    added_services = new_services - old_services
    removed_services = old_services - new_services
    if added_services:
        changes.append(f"new services: {', '.join(sorted(added_services))}")
    if removed_services:
        changes.append(f"removed services: {', '.join(sorted(removed_services))}")

    # Check command changes
    old_cmds = set(old_disc.get("installed_commands", []))
    new_cmds = set(disc.get("installed_commands", []))
    added_cmds = new_cmds - old_cmds
    removed_cmds = old_cmds - new_cmds
    if added_cmds:
        changes.append(f"new commands: {', '.join(sorted(added_cmds))}")
    if removed_cmds:
        changes.append(f"removed commands: {', '.join(sorted(removed_cmds))}")

    # Update discovered section
    profile["discovered"] = {
        "os_family": disc.get("os_family", "unknown"),
        "os_version": disc.get("os_version", "unknown"),
        "distro": disc.get("distro", "unknown"),
        "kernel": disc.get("kernel", "unknown"),
        "arch": disc.get("arch", "unknown"),
        "init_system": disc.get("init_system", "unknown"),
        "security_framework": disc.get("security_framework", "none"),
        "security_mode": disc.get("security_mode", ""),
        "package_manager": disc.get("package_manager", "unknown"),
        "services": disc.get("services", []),
        "installed_commands": disc.get("installed_commands", []),
        "cpu_count": disc.get("cpu_count", 0),
        "memory_total_mb": disc.get("memory_total_mb", 0),
    }

    # Recalculate applicable checks
    old_applicable = set(profile.get("applicable_checks", []))
    new_applicable = derive_applicable_checks(checks_data, profile["discovered"])
    profile["applicable_checks"] = new_applicable

    added_checks = set(new_applicable) - old_applicable
    removed_checks = old_applicable - set(new_applicable)
    if added_checks:
        changes.append(f"new applicable checks: {', '.join(sorted(added_checks))}")
    if removed_checks:
        changes.append(f"removed applicable checks: {', '.join(sorted(removed_checks))}")

    if changes:
        append_audit(profile, "discovery_updated",
                     f"Discovery refreshed: {'; '.join(changes)}",
                     "discovery")
        profile["last_updated"] = now_iso()
        save_yaml(profile_path, profile)

    print(json.dumps({
        "status": "updated" if changes else "unchanged",
        "changes": changes,
        "applicable_checks": len(new_applicable),
    }))


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        print("Usage: profile_ops.py <subcommand> [args...]", file=sys.stderr)
        print("Subcommands: init, get-checks, apply-update, expire-suppressions, read, update-discovery",
              file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        if len(sys.argv) != 6:
            print("Usage: profile_ops.py init <hostname> <discovery_json> <checks_yaml> <profiles_dir>",
                  file=sys.stderr)
            sys.exit(1)
        cmd_init(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

    elif cmd == "get-checks":
        if "--unfiltered" in sys.argv:
            if len(sys.argv) != 4:
                print("Usage: profile_ops.py get-checks --unfiltered <checks_yaml>", file=sys.stderr)
                sys.exit(1)
            cmd_get_checks(None, sys.argv[3], unfiltered=True)
        else:
            if len(sys.argv) != 4:
                print("Usage: profile_ops.py get-checks <profile_path> <checks_yaml>", file=sys.stderr)
                sys.exit(1)
            cmd_get_checks(sys.argv[2], sys.argv[3])

    elif cmd == "apply-update":
        if len(sys.argv) != 4:
            print("Usage: profile_ops.py apply-update <profile_path> <update_json>", file=sys.stderr)
            sys.exit(1)
        cmd_apply_update(sys.argv[2], sys.argv[3])

    elif cmd == "expire-suppressions":
        if len(sys.argv) != 3:
            print("Usage: profile_ops.py expire-suppressions <profile_path>", file=sys.stderr)
            sys.exit(1)
        cmd_expire_suppressions(sys.argv[2])

    elif cmd == "read":
        if len(sys.argv) != 3:
            print("Usage: profile_ops.py read <profile_path>", file=sys.stderr)
            sys.exit(1)
        cmd_read(sys.argv[2])

    elif cmd == "update-discovery":
        if len(sys.argv) != 5:
            print("Usage: profile_ops.py update-discovery <profile_path> <discovery_json> <checks_yaml>",
                  file=sys.stderr)
            sys.exit(1)
        cmd_update_discovery(sys.argv[2], sys.argv[3], sys.argv[4])

    else:
        print(f"Unknown subcommand: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
