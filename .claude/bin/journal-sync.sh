#!/usr/bin/env bash
# journal-sync.sh — commit/pull/push ~/work-journal between boxes.
# Conflict policy: .gitattributes union merge (*.md, *.tsv) keeps both
# sides' lines. Any conflict union can't cover -> abort the merge, keep
# the local commit, log loudly, and let the next interactive session
# resolve. Never rebases, never force-pushes, never drops a side.
# Scheduled: journal-sync.timer (18:30/22:30 M-F; deploy/install-systemd-timers.sh),
# or cron `30 18 * * 1-5 ...` on boxes without a systemd user manager.
# Manual: run it any time you want a cross-box sync.
#
# Exit codes: 0 = synced or transient skip (network, lock); 1 = a human
# must act (stuck merge, conflict beyond union, commit failure). Under
# systemd, exit 1 fires OnFailure=ntfy-alert@ -> phone alert.

set -u
REPO="$HOME/work-journal"
LOG_DIR="$HOME/.local/state"
LOG="$LOG_DIR/journal-sync.log"
LOCK="$LOG_DIR/journal-sync.lock"
mkdir -p "$LOG_DIR"

log() { printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }

exec 9>"$LOCK"
if ! flock -n 9; then log "SKIP: another sync is running"; exit 0; fi

cd "$REPO" || { log "FATAL: $REPO missing"; exit 1; }

# Never touch a repo mid-merge/rebase from cron.
if [ -e .git/MERGE_HEAD ] || [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
    log "SKIP: repo has an unfinished merge/rebase — resolve interactively"
    exit 1
fi

# 1. Commit local state if dirty.
if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -q -m "sync: $(hostname -s) $(date '+%Y-%m-%d %H:%M')" \
        && log "committed local changes" \
        || { log "FATAL: commit failed"; exit 1; }
fi

# 2. Pull (union driver auto-keeps both sides for *.md / *.tsv).
if ! git pull --no-rebase -q 2>>"$LOG"; then
    if [ -e .git/MERGE_HEAD ]; then
        # Conflicts beyond what union covers (delete/modify, binary, ...).
        conflicted=$(git diff --name-only --diff-filter=U | tr '\n' ' ')
        git merge --abort
        log "CONFLICT beyond union on: ${conflicted:-unknown} — merge aborted, local commit kept, push skipped; resolve interactively (keep both sides)"
        exit 1
    fi
    log "WARN: pull failed (network/remote?) — push skipped"
    exit 0
fi

# 3. Push, with one retry around a push race.
for _ in 1 2; do
    if git push -q 2>>"$LOG"; then
        log "synced OK ($(git rev-parse --short HEAD))"
        break
    fi
    git pull --no-rebase -q 2>>"$LOG" || { log "WARN: retry pull failed"; exit 0; }
done

# 4. Sanity + ghost dedup: union merges can double-append edited-in-place
# lines in tasks.md. tasks_dedup.py removes only provable ghosts (same
# section, same core text, status-divergent or byte-identical; recurring
# lines never touched) and reports each drop. Anything ambiguous is left
# for /task to sort out interactively.
if command -v python3 >/dev/null && [ -f "$HOME/dotclaude/.claude/bin/tasks.py" ]; then
    if [ -f "$HOME/dotclaude/.claude/bin/tasks_dedup.py" ]; then
        dd=$(python3 "$HOME/dotclaude/.claude/bin/tasks_dedup.py" tasks.md 2>&1)
        case "$dd" in
            "clean — no ghosts") : ;;
            *) log "dedup: $dd"
               if [ -n "$(git status --porcelain tasks.md)" ]; then
                   git add tasks.md
                   git commit -q -m "sync: dedup union-merge ghosts in tasks.md" \
                       && git push -q 2>>"$LOG" \
                       && log "dedup commit pushed"
               fi ;;
        esac
    fi
    if ! chk=$(python3 "$HOME/dotclaude/.claude/bin/tasks.py" check 2>&1); then
        log "WARN: tasks.py check failed after sync: $chk"
    fi
fi
exit 0
