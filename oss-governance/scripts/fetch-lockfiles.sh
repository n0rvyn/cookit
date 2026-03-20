#!/usr/bin/env bash
# fetch-lockfiles.sh — Archive discovered manifest/lockfiles for transfer
#
# Usage: echo '<json_lines>' | fetch-lockfiles.sh [output_archive]
#
# Reads JSON lines from stdin (output of collect-manifests.sh), extracts
# file paths, and creates a tar.gz archive containing all manifests plus
# any LICENSE files found in the same directories.
#
# Arguments:
#   output_archive - Path for the output archive (default: /tmp/oss-manifests.tar.gz)
#
# Output: JSON line with archive path and file count
#   {"archive":"/tmp/oss-manifests.tar.gz","file_count":42}
#
# Exit codes:
#   0 - Success
#   1 - Error creating archive

set -euo pipefail

OUTPUT="${1:-/tmp/oss-manifests.tar.gz}"
TMPLIST=$(mktemp /tmp/oss-filelist.XXXXXX)

trap 'rm -f "$TMPLIST"' EXIT

FILE_COUNT=0

# Read JSON lines from stdin, extract file paths
while IFS= read -r line; do
    # Extract path and file fields using shell string manipulation
    # Avoids dependency on jq or python
    dir=""
    file=""

    # Parse "path" field
    case "$line" in
        *\"path\":\"*)
            dir="${line#*\"path\":\"}"
            dir="${dir%%\"*}"
            ;;
    esac

    # Parse "file" field
    case "$line" in
        *\"file\":\"*)
            file="${line#*\"file\":\"}"
            file="${file%%\"*}"
            ;;
    esac

    if [[ -z "$dir" || -z "$file" ]]; then
        continue
    fi

    full_path="$dir/$file"

    # Add the manifest/lockfile itself
    if [[ -f "$full_path" ]]; then
        echo "$full_path" >> "$TMPLIST"
        ((FILE_COUNT++)) || true
    fi

    # Also grab LICENSE and related files from the same directory
    for lf in LICENSE LICENSE.md LICENSE.txt LICENSE-MIT LICENSE-APACHE COPYING NOTICE; do
        if [[ -f "$dir/$lf" ]]; then
            echo "$dir/$lf" >> "$TMPLIST"
            ((FILE_COUNT++)) || true
        fi
    done

    # For npm: grab the project's own package.json if we found a lockfile
    if [[ "$file" == "package-lock.json" && -f "$dir/package.json" ]]; then
        echo "$dir/package.json" >> "$TMPLIST"
        ((FILE_COUNT++)) || true
    fi

    # For cargo: grab Cargo.toml if we found Cargo.lock
    if [[ "$file" == "Cargo.lock" && -f "$dir/Cargo.toml" ]]; then
        echo "$dir/Cargo.toml" >> "$TMPLIST"
        ((FILE_COUNT++)) || true
    fi

    # For go: grab go.mod if we found go.sum
    if [[ "$file" == "go.sum" && -f "$dir/go.mod" ]]; then
        echo "$dir/go.mod" >> "$TMPLIST"
        ((FILE_COUNT++)) || true
    fi
done

# Deduplicate the file list
sort -u "$TMPLIST" -o "$TMPLIST"
FILE_COUNT=$(wc -l < "$TMPLIST" | tr -d ' ')

if [[ "$FILE_COUNT" -eq 0 ]]; then
    echo "{\"archive\":\"\",\"file_count\":0}"
    exit 0
fi

# Create the archive
# Use --transform to preserve directory structure relative to /
tar czf "$OUTPUT" -T "$TMPLIST" 2>/dev/null || {
    echo "{\"archive\":\"\",\"file_count\":0,\"error\":\"tar failed\"}" >&2
    exit 1
}

echo "{\"archive\":\"$OUTPUT\",\"file_count\":$FILE_COUNT}"
