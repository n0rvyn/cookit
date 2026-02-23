#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT="$SCRIPT_DIR/embed"

echo "Compiling embed.swift..."
swiftc \
    -O \
    -sdk "$(xcrun --show-sdk-path)" \
    -framework Foundation \
    -framework NaturalLanguage \
    "$SCRIPT_DIR/embed.swift" \
    -o "$OUTPUT"
echo "Built: $OUTPUT"
