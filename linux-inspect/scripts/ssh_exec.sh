#!/usr/bin/env bash
# ssh_exec.sh — Execute a command on a remote host via SSH
#
# Usage: ssh_exec.sh <host> <port> <user> [key_file] [timeout] [become] [become_method]
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
# The command to execute is read from stdin.
#
# Exit codes:
#   0 - Success
#   1 - SSH connection failed
#   2 - Command execution failed
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

# Wrap command with privilege escalation if needed
if [[ "$BECOME" == "true" ]]; then
    if [[ "$BECOME_METHOD" == "sudo" ]]; then
        COMMAND="sudo -n bash -c '${COMMAND//\'/\'\\\'\'}'"
    elif [[ "$BECOME_METHOD" == "su" ]]; then
        COMMAND="su -c '${COMMAND//\'/\'\\\'\'}'"
    fi
fi

# Execute
ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" bash -c "'${COMMAND//\'/\'\\\'\'}'" 2>&1

exit_code=$?
if [[ $exit_code -ne 0 ]]; then
    echo "[ssh_exec] Connection to ${USER}@${HOST}:${PORT} failed with exit code ${exit_code}" >&2
    exit 1
fi
