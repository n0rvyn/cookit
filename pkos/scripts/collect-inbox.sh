#!/bin/bash
# Collect pending items from all PKOS inbox sources.
# Outputs summary counts to stdout.
# Usage: collect-inbox.sh [reminders|notes|voice|all]

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MACTOOLS_ROOT="$(ls -d "$PLUGIN_ROOT/../../mactools"/*/ 2>/dev/null | sort -V | tail -1)"
MACTOOLS_ROOT="${MACTOOLS_ROOT%/}"
if [ -z "$MACTOOLS_ROOT" ] || [ ! -d "$MACTOOLS_ROOT" ]; then
    echo "ERROR: mactools plugin not found at $PLUGIN_ROOT/../../mactools/" >&2
    exit 1
fi
VOICE_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/PKOS/voice"
SOURCE="${1:-all}"

reminder_count=0
note_count=0
voice_count=0

# Reminders
if [ "$SOURCE" = "all" ] || [ "$SOURCE" = "reminders" ]; then
    if [ -f "$MACTOOLS_ROOT/skills/reminders/scripts/reminders.sh" ]; then
        reminder_output=$(bash "$MACTOOLS_ROOT/skills/reminders/scripts/reminders.sh" list "PKOS Inbox" 2>/dev/null || echo "")
        if [ -n "$reminder_output" ]; then
            reminder_count=$(echo "$reminder_output" | grep -c "^  " 2>/dev/null || true)
            reminder_count=${reminder_count:-0}
        fi
    fi
fi

# Notes
if [ "$SOURCE" = "all" ] || [ "$SOURCE" = "notes" ]; then
    if [ -f "$MACTOOLS_ROOT/skills/notes/scripts/notes.sh" ]; then
        note_output=$(bash "$MACTOOLS_ROOT/skills/notes/scripts/notes.sh" list "PKOS Inbox" 2>/dev/null || echo "")
        if [ -n "$note_output" ]; then
            note_count=$(echo "$note_output" | grep -c "^  " 2>/dev/null || true)
            note_count=${note_count:-0}
        fi
    fi
fi

# Voice files
if [ "$SOURCE" = "all" ] || [ "$SOURCE" = "voice" ]; then
    if [ -d "$VOICE_DIR" ]; then
        voice_count=$(find "$VOICE_DIR" -maxdepth 1 -name "*.m4a" 2>/dev/null | wc -l | tr -d '[:space:]')
        voice_count=${voice_count:-0}
    fi
fi

total=$((reminder_count + note_count + voice_count))

echo "PKOS Inbox: $total items pending"
echo "  Reminders: $reminder_count"
echo "  Notes: $note_count"
echo "  Voice: $voice_count"

exit 0
