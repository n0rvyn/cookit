#!/usr/bin/env bash
# collector.sh — Single-SSH Linux host inspection collector
#
# Runs on the REMOTE host. Collects discovery data and executes checks.
# No dependencies beyond coreutils + standard Linux tools.
# Uses python3 for JSON output if available; bash fallback otherwise.
#
# Usage: bash collector.sh <checks_conf_path>
#   checks_conf_path: bash-sourceable file defining checks to run
#
# Output: Structured JSON to stdout. All diagnostics go to stderr.

set -uo pipefail

CHECKS_CONF="${1:-}"
if [[ -z "$CHECKS_CONF" || ! -f "$CHECKS_CONF" ]]; then
    echo '{"error": "checks.conf not found or not specified"}' >&2
    exit 1
fi

# ── Source checks configuration ───────────────────────────────────────────────
# shellcheck source=/dev/null
source "$CHECKS_CONF"

LI_TIMEOUT="${LI_TIMEOUT:-60}"
LI_MAX_LINES="${LI_MAX_LINES:-200}"
LI_CHECK_COUNT="${LI_CHECK_COUNT:-0}"

# ── Utility functions ─────────────────────────────────────────────────────────

# Escape a string for JSON (handles quotes, backslashes, newlines, tabs, control chars)
json_escape() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    # Remove other control characters
    s=$(printf '%s' "$s" | tr -d '\000-\010\013\014\016-\037')
    printf '%s' "$s"
}

# Get current timestamp in ISO-8601
get_timestamp() {
    date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S'
}

# Get millisecond timestamp (for duration measurement)
get_ms() {
    if command -v python3 &>/dev/null; then
        python3 -c 'import time; print(int(time.time()*1000))'
    else
        # Fallback: seconds * 1000
        echo $(( $(date +%s) * 1000 ))
    fi
}

# ── Discovery phase ──────────────────────────────────────────────────────────

discover_os() {
    local os_family="" os_version="" distro="" kernel="" arch=""

    # OS family and distro from os-release
    if [[ -f /etc/os-release ]]; then
        # shellcheck source=/dev/null
        source /etc/os-release
        distro="${NAME:-unknown}"
        os_version="${VERSION_ID:-unknown}"

        case "${ID:-}" in
            ubuntu|debian|linuxmint|pop|kali|raspbian)
                os_family="debian" ;;
            centos|rhel|fedora|rocky|alma|ol|amzn)
                os_family="rhel" ;;
            sles|opensuse*)
                os_family="suse" ;;
            alpine)
                os_family="alpine" ;;
            arch|manjaro)
                os_family="arch" ;;
            *)
                # Try ID_LIKE as fallback
                case "${ID_LIKE:-}" in
                    *debian*|*ubuntu*) os_family="debian" ;;
                    *rhel*|*centos*|*fedora*) os_family="rhel" ;;
                    *suse*) os_family="suse" ;;
                    *) os_family="unknown" ;;
                esac
                ;;
        esac
    fi

    kernel=$(uname -r 2>/dev/null || echo "unknown")
    arch=$(uname -m 2>/dev/null || echo "unknown")

    echo "$os_family|$os_version|$distro|$kernel|$arch"
}

discover_init_system() {
    if command -v systemctl &>/dev/null && systemctl is-system-running &>/dev/null; then
        echo "systemd"
    elif [[ -f /sbin/openrc ]]; then
        echo "openrc"
    elif [[ -f /etc/init.d/rc ]]; then
        echo "sysvinit"
    else
        echo "unknown"
    fi
}

discover_security_framework() {
    local framework="none" mode=""
    if command -v getenforce &>/dev/null; then
        mode=$(getenforce 2>/dev/null || echo "")
        if [[ -n "$mode" && "$mode" != "Disabled" ]]; then
            framework="selinux"
            echo "selinux|$(echo "$mode" | tr '[:upper:]' '[:lower:]')"
            return
        fi
    fi
    if command -v aa-status &>/dev/null; then
        if aa-status &>/dev/null; then
            framework="apparmor"
            echo "apparmor|"
            return
        fi
    fi
    echo "none|"
}

discover_package_manager() {
    for pm in apt dnf yum zypper apk pacman; do
        if command -v "$pm" &>/dev/null; then
            echo "$pm"
            return
        fi
    done
    echo "unknown"
}

discover_services() {
    local services=""
    if command -v systemctl &>/dev/null; then
        services=$(systemctl list-units --type=service --state=running --no-legend --no-pager 2>/dev/null \
            | awk '{print $1}' | sed 's/\.service$//' | sort | tr '\n' ',' | sed 's/,$//')
    elif [[ -d /etc/init.d ]]; then
        services=$(ls /etc/init.d/ 2>/dev/null | grep -v README | sort | tr '\n' ',' | sed 's/,$//')
    fi
    echo "$services"
}

discover_commands() {
    local cmds=""
    for cmd in systemctl auditctl ausearch aide ss ip iptables nft firewall-cmd ufw docker podman; do
        if command -v "$cmd" &>/dev/null; then
            cmds="${cmds:+$cmds,}$cmd"
        fi
    done
    echo "$cmds"
}

discover_hardware() {
    local cpu_count mem_total_mb uptime_seconds
    cpu_count=$(nproc 2>/dev/null || grep -c ^processor /proc/cpuinfo 2>/dev/null || echo "0")
    mem_total_mb=$(awk '/MemTotal/{printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || echo "0")
    uptime_seconds=$(awk '{printf "%d", $1}' /proc/uptime 2>/dev/null || echo "0")
    echo "$cpu_count|$mem_total_mb|$uptime_seconds"
}

# ── Run discovery ─────────────────────────────────────────────────────────────

TIMESTAMP=$(get_timestamp)
HOSTNAME_FULL=$(hostname -f 2>/dev/null || hostname 2>/dev/null || echo "unknown")

IFS='|' read -r D_OS_FAMILY D_OS_VERSION D_DISTRO D_KERNEL D_ARCH <<< "$(discover_os)"
D_INIT=$(discover_init_system)
IFS='|' read -r D_SEC_FRAMEWORK D_SEC_MODE <<< "$(discover_security_framework)"
D_PKG_MGR=$(discover_package_manager)
D_SERVICES=$(discover_services)
D_COMMANDS=$(discover_commands)
IFS='|' read -r D_CPU D_MEM D_UPTIME <<< "$(discover_hardware)"

# ── Check execution phase ────────────────────────────────────────────────────

# Arrays to collect results
declare -a CHECK_RESULTS=()
TOTAL_EXECUTED=0
TOTAL_ERRORS=0
TOTAL_SKIPPED=0
TOTAL_START=$(get_ms)

for (( i=0; i<LI_CHECK_COUNT; i++ )); do
    # Read check fields from sourced variables
    id_var="LI_CHECK_${i}_ID"
    cat_var="LI_CHECK_${i}_CAT"
    sev_var="LI_CHECK_${i}_SEV"
    cmd_var="LI_CHECK_${i}_CMD"

    check_id="${!id_var:-}"
    check_cat="${!cat_var:-}"
    check_sev="${!sev_var:-}"
    check_cmd="${!cmd_var:-}"

    if [[ -z "$check_id" ]]; then
        continue
    fi

    # If no direct command, try OS-variant resolution
    if [[ -z "$check_cmd" ]]; then
        # Try exact OS family match
        variant_var="LI_CHECK_${i}_CMD_${D_OS_FAMILY}"
        check_cmd="${!variant_var:-}"

        # Fallback to 'all' variant
        if [[ -z "$check_cmd" ]]; then
            all_var="LI_CHECK_${i}_CMD_all"
            check_cmd="${!all_var:-}"
        fi

        # No matching command found
        if [[ -z "$check_cmd" ]]; then
            CHECK_RESULTS+=("{\"id\":\"$check_id\",\"category\":\"$check_cat\",\"severity\":\"$check_sev\",\"status\":\"skipped\",\"skip_reason\":\"no command for os_family=$D_OS_FAMILY\"}")
            TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
            continue
        fi
    fi

    # Execute the check command
    check_start=$(get_ms)
    check_output=""
    check_exit=0

    if command -v timeout &>/dev/null; then
        check_output=$(timeout "$LI_TIMEOUT" bash -c "$check_cmd" 2>&1) || check_exit=$?
    else
        check_output=$(bash -c "$check_cmd" 2>&1) || check_exit=$?
    fi

    check_end=$(get_ms)
    check_duration=$((check_end - check_start))

    # Truncate output
    if [[ $(echo "$check_output" | wc -l) -gt $LI_MAX_LINES ]]; then
        check_output=$(echo "$check_output" | head -n "$LI_MAX_LINES")
        check_output="${check_output}
... [truncated at ${LI_MAX_LINES} lines]"
    fi

    # Determine status
    local_status="ok"
    if [[ $check_exit -eq 124 ]]; then
        local_status="timeout"
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    elif [[ $check_exit -ne 0 ]]; then
        local_status="error"
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    fi

    escaped_output=$(json_escape "$check_output")

    CHECK_RESULTS+=("{\"id\":\"$check_id\",\"category\":\"$check_cat\",\"severity\":\"$check_sev\",\"status\":\"$local_status\",\"output\":\"$escaped_output\",\"exit_code\":$check_exit,\"duration_ms\":$check_duration}")
    TOTAL_EXECUTED=$((TOTAL_EXECUTED + 1))
done

TOTAL_END=$(get_ms)
TOTAL_DURATION=$((TOTAL_END - TOTAL_START))

# ── Output phase ──────────────────────────────────────────────────────────────

# Build services JSON array
build_json_array() {
    local csv="$1"
    if [[ -z "$csv" ]]; then
        echo "[]"
        return
    fi
    local result="["
    local first=true
    IFS=',' read -ra items <<< "$csv"
    for item in "${items[@]}"; do
        item=$(echo "$item" | xargs)  # trim whitespace
        if [[ -n "$item" ]]; then
            if [[ "$first" == "true" ]]; then
                first=false
            else
                result+=","
            fi
            result+="\"$(json_escape "$item")\""
        fi
    done
    result+="]"
    echo "$result"
}

# Build checks array
checks_json="["
for (( i=0; i<${#CHECK_RESULTS[@]}; i++ )); do
    if [[ $i -gt 0 ]]; then
        checks_json+=","
    fi
    checks_json+="${CHECK_RESULTS[$i]}"
done
checks_json+="]"

services_json=$(build_json_array "$D_SERVICES")
commands_json=$(build_json_array "$D_COMMANDS")

# Assemble the raw JSON using bash (discovery is safe; checks contain arbitrary output)
raw_json="{
  \"timestamp\": \"$TIMESTAMP\",
  \"discovery\": {
    \"hostname\": \"$(json_escape "$HOSTNAME_FULL")\",
    \"os_family\": \"$D_OS_FAMILY\",
    \"os_version\": \"$D_OS_VERSION\",
    \"distro\": \"$(json_escape "$D_DISTRO")\",
    \"kernel\": \"$D_KERNEL\",
    \"arch\": \"$D_ARCH\",
    \"init_system\": \"$D_INIT\",
    \"security_framework\": \"$D_SEC_FRAMEWORK\",
    \"security_mode\": \"$D_SEC_MODE\",
    \"package_manager\": \"$D_PKG_MGR\",
    \"services\": $services_json,
    \"installed_commands\": $commands_json,
    \"cpu_count\": $D_CPU,
    \"memory_total_mb\": $D_MEM,
    \"uptime_seconds\": $D_UPTIME
  },
  \"checks\": $checks_json,
  \"stats\": {
    \"total_checks\": $LI_CHECK_COUNT,
    \"executed\": $TOTAL_EXECUTED,
    \"skipped\": $TOTAL_SKIPPED,
    \"errors\": $TOTAL_ERRORS,
    \"total_duration_ms\": $TOTAL_DURATION
  }
}"

# Validate and pretty-print via python3 (pipe via stdin to avoid quoting issues)
# Fallback to raw output if python3 unavailable or fails
if command -v python3 &>/dev/null; then
    validated=$(printf '%s' "$raw_json" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(json.dumps(data, indent=2))
except Exception as e:
    print(sys.stdin.read(), file=sys.stderr)
    sys.exit(1)
" 2>/dev/null)
    if [[ $? -eq 0 && -n "$validated" ]]; then
        printf '%s\n' "$validated"
    else
        printf '%s\n' "$raw_json"
    fi
else
    printf '%s\n' "$raw_json"
fi
