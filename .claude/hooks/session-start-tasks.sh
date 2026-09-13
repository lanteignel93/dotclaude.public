#!/usr/bin/env bash
# SessionStart hook: inject (1) overdue + due-today + lead-time tasks from
# ~/work-journal/tasks.md, (2) the ~/work-journal/projects.md block for the
# repo this session opened in, and (3) continuity — the newest journal
# entry's Next / Open-blocked bullets for this repo. Composition happens in
# session_context.py; tasks.py hook-context stays the tasks source.
# Gates silently when python3 or the journal is absent — non-work machines
# are unaffected.

set -euo pipefail

TASKS_FILE="$HOME/work-journal/tasks.md"
ENGINE="$HOME/dotclaude/.claude/bin/tasks.py"
CTX="$HOME/dotclaude/.claude/bin/session_context.py"

command -v python3 >/dev/null 2>&1 || { cat >/dev/null 2>&1 || true; exit 0; }

# Keep the harness payload (it carries the session cwd) for session_context.
payload=$(cat 2>/dev/null || true)

tasks_json=""
if [ -f "$TASKS_FILE" ] && [ -f "$ENGINE" ]; then
    tasks_json=$(python3 "$ENGINE" hook-context 2>/dev/null || true)
fi

if [ -f "$CTX" ]; then
    printf '%s' "$payload" | python3 "$CTX" --tasks-json "$tasks_json" 2>/dev/null \
        || printf '%s' "$tasks_json"
else
    printf '%s' "$tasks_json"
fi
