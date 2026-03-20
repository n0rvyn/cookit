#!/usr/bin/env bash
# suggest-oss-audit.sh — Suggest /oss-audit when user mentions relevant keywords
# Called by UserPromptSubmit hook

set -euo pipefail

INPUT="${CLAUDE_USER_PROMPT:-}"

# Check for relevant keywords (case-insensitive)
if echo "$INPUT" | grep -qiE '(开源治理|合规扫描|许可证检查|license.*(check|scan|audit|compliance)|dependency.*(audit|scan|check)|oss.*(audit|governance|compliance)|open.source.*(audit|compliance|governance|scan)|sbom|software.bill.of.materials)'; then
    echo "[skill-hint] Related: /oss-audit — scan hosts for open source compliance, license risks, and vulnerability audit"
fi
