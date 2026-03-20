#!/usr/bin/env bash
# collect-manifests.sh — Find package manager files on a host
#
# Usage: collect-manifests.sh <scan_paths> <depth> [exclude_patterns]
#
# Arguments:
#   scan_paths       - Colon-separated list of directories to scan (e.g., /home:/opt:/srv)
#   depth            - Max directory recursion depth (default: 4)
#   exclude_patterns - Colon-separated directory names to exclude (default: node_modules:.git:vendor:__pycache__:.venv)
#
# Output: JSON lines to stdout, one per discovered manifest file.
# Each line: {"path":"/opt/app","file":"package-lock.json","pm":"npm"}
#
# Exit codes:
#   0 - Success (even if no manifests found)
#   1 - Invalid arguments
#
# Designed to run on remote hosts via SSH stdin pipe. Uses only POSIX tools
# plus bash builtins — no jq, python, or other dependencies required.

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: collect-manifests.sh <scan_paths> [depth] [exclude_patterns]" >&2
    exit 1
fi

SCAN_PATHS="$1"
DEPTH="${2:-4}"
EXCLUDES="${3:-node_modules:.git:vendor:__pycache__:.venv:.tox:dist:build}"

IFS=':' read -ra PATHS <<< "$SCAN_PATHS"
IFS=':' read -ra EXCL <<< "$EXCLUDES"

# Validate at least one scan path exists
VALID_PATHS=()
for p in "${PATHS[@]}"; do
    if [[ -d "$p" ]]; then
        VALID_PATHS+=("$p")
    fi
done

if [[ ${#VALID_PATHS[@]} -eq 0 ]]; then
    # No valid paths; output empty result and exit cleanly
    exit 0
fi

# Build find prune arguments for excluded directories
PRUNE_ARGS=""
for e in "${EXCL[@]}"; do
    if [[ -n "$PRUNE_ARGS" ]]; then
        PRUNE_ARGS="$PRUNE_ARGS -o"
    fi
    PRUNE_ARGS="$PRUNE_ARGS -name $e"
done

# Manifest files to search for, ordered by preference (lockfile first)
# When both manifest and lockfile exist, the lockfile is preferred for analysis
MANIFEST_NAMES=(
    "package-lock.json"
    "package.json"
    "yarn.lock"
    "pnpm-lock.yaml"
    "Cargo.lock"
    "Cargo.toml"
    "go.sum"
    "go.mod"
    "Pipfile.lock"
    "poetry.lock"
    "requirements.txt"
    "pyproject.toml"
    "Gemfile.lock"
    "Gemfile"
    "composer.lock"
    "composer.json"
    "Podfile.lock"
    "Podfile"
    "Package.resolved"
    "Package.swift"
    "pom.xml"
    "build.gradle"
    "build.gradle.kts"
)

# Build find -name arguments
NAME_ARGS=""
for name in "${MANIFEST_NAMES[@]}"; do
    if [[ -n "$NAME_ARGS" ]]; then
        NAME_ARGS="$NAME_ARGS -o"
    fi
    NAME_ARGS="$NAME_ARGS -name $name"
done

# Execute find with prune + name filter
# Using eval because the prune/name args are built as strings
eval "find ${VALID_PATHS[*]} -maxdepth $DEPTH \
    \\( $PRUNE_ARGS \\) -prune -o \
    \\( $NAME_ARGS \\) -print 2>/dev/null" | while IFS= read -r filepath; do

    dir=$(dirname "$filepath")
    file=$(basename "$filepath")

    # Determine package manager type
    case "$file" in
        package-lock.json|package.json|yarn.lock|pnpm-lock.yaml)
            pm="npm"
            ;;
        Cargo.lock|Cargo.toml)
            pm="cargo"
            ;;
        go.sum|go.mod)
            pm="go"
            ;;
        Pipfile.lock|poetry.lock|requirements.txt|pyproject.toml)
            pm="pip"
            ;;
        Gemfile.lock|Gemfile)
            pm="ruby"
            ;;
        composer.lock|composer.json)
            pm="composer"
            ;;
        Podfile.lock|Podfile)
            pm="cocoapods"
            ;;
        Package.resolved|Package.swift)
            pm="swift"
            ;;
        pom.xml)
            pm="maven"
            ;;
        build.gradle|build.gradle.kts)
            pm="gradle"
            ;;
        *)
            pm="unknown"
            ;;
    esac

    # Escape any quotes in path for valid JSON
    escaped_dir="${dir//\"/\\\"}"
    escaped_file="${file//\"/\\\"}"

    echo "{\"path\":\"$escaped_dir\",\"file\":\"$escaped_file\",\"pm\":\"$pm\"}"
done
