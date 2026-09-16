#!/usr/bin/env bash

LOG_FILE="$(pwd)/.codex/logs/hooks.log"
EXECUTOR="/usr/bin/python3"
EVENT_NAME="$1"
EVENT_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/hook_on_${EVENT_NAME}.py"

write_log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

if [ ! -f "$LOG_FILE" ]; then
    mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null
    write_log "PLUGIN_ROOT=$PLUGIN_ROOT"
    write_log "PLUGIN_DATA=$PLUGIN_DATA"
    write_log "EXECUTOR=$EXECUTOR"
fi

write_log "execute $EVENT_SCRIPT"
"$EXECUTOR" "$EVENT_SCRIPT" 2>> "$LOG_FILE"
HOOK_EXIT_CODE=$?

if [ "$HOOK_EXIT_CODE" -ne 0 ]; then
    write_log "hook failed with exit code $HOOK_EXIT_CODE"
fi

exit "$HOOK_EXIT_CODE"
