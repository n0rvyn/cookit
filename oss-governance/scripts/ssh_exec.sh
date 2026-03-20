#!/usr/bin/env bash
# ssh_exec.sh — Execute a command on a remote host via SSH
#
# Usage: echo "<commands>" | ssh_exec.sh <host> <port> <user> [key_file] [timeout] [become] [become_method]
#
# Arguments:
#   host           - Hostname or IP
#   port           - SSH port
#   user           - SSH user
#   key_file       - Path to SSH private key (use "none" to skip)
#   timeout        - Connection timeout in seconds (default: 30)
#   become         - "true" to use privilege escalation (default: "false")
#   become_method  - "sudo" or "su" (default: "sudo")
#
# The command to execute is read from stdin and piped to the remote shell
# via `bash -s` (no quoting issues — stdin is not subject to shell expansion).
#
# NOTE: BatchMode=yes is set, so password-based SSH auth is NOT supported.
# Only key-based authentication works. For sudo, use NOPASSWD or pass
# credentials via ansible_become_pass (not recommended in plaintext).
#
# NOTE: StrictHostKeyChecking=accept-new auto-trusts unknown hosts on first
# connection. This is a TOFU (trust-on-first-use) model. For high-security
# environments, pre-populate known_hosts or set StrictHostKeyChecking=yes.
#
# Exit codes:
#   0 - Success
#   1 - SSH connection failed or command failed
#   3 - Invalid arguments

set -euo pipefail

if [[ $# -lt 3 ]]; then
    echo "Usage: ssh_exec.sh <host> <port> <user> [key_file] [timeout] [become] [become_method]" >&2
    exit 3
fi

HOST="$1"
PORT="$2"
USER="$3"
KEY_FILE="${4:-none}"
TIMEOUT="${5:-30}"
BECOME="${6:-false}"
BECOME_METHOD="${7:-sudo}"

# Read command from stdin
COMMAND=$(cat)

if [[ -z "$COMMAND" ]]; then
    echo "Error: No command provided on stdin" >&2
    exit 3
fi

# Build SSH options
SSH_OPTS=(
    -o "ConnectTimeout=${TIMEOUT}"
    -o "StrictHostKeyChecking=accept-new"
    -o "BatchMode=yes"
    -o "LogLevel=ERROR"
    -p "$PORT"
)

if [[ "$KEY_FILE" != "none" && -f "$KEY_FILE" ]]; then
    SSH_OPTS+=(-i "$KEY_FILE")
fi

# Wrap command with privilege escalation if needed.
# The command is piped via stdin to `bash -s` on the remote host,
# avoiding all shell quoting/escaping issues.
if [[ "$BECOME" == "true" ]]; then
    if [[ "$BECOME_METHOD" == "sudo" ]]; then
        COMMAND="sudo -n bash <<'INSPECT_EOF'
${COMMAND}
INSPECT_EOF"
    elif [[ "$BECOME_METHOD" == "su" ]]; then
        COMMAND="su -c bash <<'INSPECT_EOF'
${COMMAND}
INSPECT_EOF"
    fi
fi

# Execute via stdin pipe — no bash -c quoting needed
echo "$COMMAND" | ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" bash -s 2>&1
